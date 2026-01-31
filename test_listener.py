"""Test blockchain listener functionality"""
import asyncio
import sys
from datetime import datetime

from src.config import get_settings
from src.db import init_db, close_db, AsyncSessionLocal
from src.indexer.listener import TradeListener
from web3 import Web3

settings = get_settings()


async def test_listener():
    """Test listener configuration and connectivity"""
    print("=" * 80)
    print("BLOCKCHAIN LISTENER DIAGNOSTICS")
    print("=" * 80)

    # Step 1: Check Web3 connection
    print("\n[1] Checking RPC connection...")
    print(f"    RPC URL: {settings.POLYGON_RPC_URL}")

    w3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL))

    try:
        connected = w3.is_connected()
        print(f"    Connected: {connected}")

        if connected:
            latest_block = w3.eth.block_number
            print(f"    Latest block: {latest_block}")

            # Get block info
            block = w3.eth.get_block(latest_block)
            block_time = datetime.utcfromtimestamp(block['timestamp'])
            print(f"    Block time: {block_time}")
            print(f"    Transactions in block: {len(block['transactions'])}")
    except Exception as e:
        print(f"    [ERROR] Connection failed: {e}")
        return

    # Step 2: Check database
    print("\n[2] Checking database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        from sqlalchemy import text

        # Count trades
        result = await session.execute(text("SELECT COUNT(*) FROM trades"))
        trade_count = result.scalar()
        print(f"    Total trades in DB: {trade_count}")

        # Count markets
        result = await session.execute(text("SELECT COUNT(*) FROM markets"))
        market_count = result.scalar()
        print(f"    Total markets in DB: {market_count}")

        # Latest trade
        result = await session.execute(
            text("SELECT timestamp FROM trades ORDER BY timestamp DESC LIMIT 1")
        )
        latest_trade = result.scalar()
        if latest_trade:
            print(f"    Latest trade time: {latest_trade}")
        else:
            print(f"    No trades found")

    # Step 3: Check listener configuration
    print("\n[3] Checking listener configuration...")
    print(f"    Exchange address: {settings.CTF_EXCHANGE_ADDRESS}")
    print(f"    Whale threshold: ${settings.WHALE_THRESHOLD}")

    # Step 4: Test listener initialization
    print("\n[4] Testing listener initialization...")
    try:
        listener = TradeListener(AsyncSessionLocal)
        print(f"    Listener created successfully")

        # Refresh token map
        await listener.refresh_token_map()
        print(f"    Token mappings loaded: {len(listener.token_map)}")

        if len(listener.token_map) == 0:
            print("    [WARNING] No token mappings found!")
            print("    Run: py -m src.main sync-markets")
        else:
            # Show sample mappings
            sample_tokens = list(listener.token_map.items())[:3]
            print("\n    Sample token mappings:")
            for token_id, info in sample_tokens:
                print(f"      {token_id[:20]}... -> {info['slug']} ({info['outcome']})")

    except Exception as e:
        print(f"    [ERROR] Listener initialization failed: {e}")
        import traceback
        traceback.print_exc()

    # Step 5: Test fetching recent logs
    print("\n[5] Testing log fetch (last 100 blocks)...")
    try:
        from src.indexer.decoder import ORDER_FILLED_TOPIC

        latest_block = w3.eth.block_number
        from_block = latest_block - 100

        logs = w3.eth.get_logs({
            "address": Web3.to_checksum_address(settings.CTF_EXCHANGE_ADDRESS),
            "topics": [ORDER_FILLED_TOPIC],
            "fromBlock": from_block,
            "toBlock": latest_block,
        })

        print(f"    Blocks range: {from_block} - {latest_block}")
        print(f"    OrderFilled events found: {len(logs)}")

        if len(logs) > 0:
            print(f"\n    Sample events:")
            for i, log in enumerate(logs[:3], 1):
                print(f"      Event {i}:")
                print(f"        Block: {log['blockNumber']}")
                print(f"        Tx: {log['transactionHash'].hex()}")
        else:
            print(f"    [INFO] No recent trades in last 100 blocks")
            print(f"    This might be normal if Polymarket is quiet")

    except Exception as e:
        print(f"    [ERROR] Log fetch failed: {e}")
        import traceback
        traceback.print_exc()

    await close_db()

    print("\n" + "=" * 80)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 80)

    print("\nRecommendations:")
    print("1. If token mappings = 0: Run 'py -m src.main sync-markets'")
    print("2. If no recent events: Polymarket might be quiet, this is normal")
    print("3. To start listener: Run 'py -m src.main serve' (runs in background)")
    print("4. To manually test: Uncomment the manual listener test below")


async def manual_listener_test():
    """Manual listener test - runs for 60 seconds"""
    print("\n[MANUAL TEST] Starting listener for 60 seconds...")
    print("Press Ctrl+C to stop early\n")

    await init_db()
    listener = TradeListener(AsyncSessionLocal)

    # Start listener in background
    listener_task = asyncio.create_task(listener.start())

    try:
        # Wait for 60 seconds
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        await listener.stop()
        await listener_task
        await close_db()

    print("\nListener test complete")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run diagnostics
    asyncio.run(test_listener())

    # Uncomment to run manual test:
    # asyncio.run(manual_listener_test())
