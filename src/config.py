import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hunter:password@localhost:5432/polymarket_db")

# Polygon RPC
RPC_URL = os.getenv("RPC_URL", "https://polygon-rpc.com/")

# CTF Exchange Contract Address
CTF_EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Whale threshold (USD)
WHALE_THRESHOLD = 1000
