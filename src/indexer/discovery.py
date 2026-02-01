"""市场发现模块 - 从 Gamma API 获取 Polymarket 市场数据"""
import json
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import Market

settings = get_settings()


class MarketDiscovery:
    """市场发现服务"""

    # 允许的政治类 category（来自 Polymarket 官方分类）
    POLITICS_CATEGORIES = [
        "politics",
        "political",
        "us-current-affairs",
        "us politics",
        "world politics",
        "elections",
        "government",
    ]

    # 排除的非政治类 category
    EXCLUDED_CATEGORIES = [
        "sports",
        "nfl",
        "nba",
        "mlb",
        "soccer",
        "football",
        "basketball",
        "baseball",
        "hockey",
        "tennis",
        "golf",
        "mma",
        "ufc",
        "boxing",
        "esports",
        "gaming",
        "crypto",
        "cryptocurrency",
        "bitcoin",
        "ethereum",
        "defi",
        "nft",
        "tech",
        "technology",
        "entertainment",
        "movies",
        "music",
        "tv",
        "celebrity",
        "science",
        "weather",
        "finance",
        "stocks",
        "business",
    ]

    # 地缘政治关键词
    GEOPOLITICS_KEYWORDS = [
        # 军事冲突
        "war", "conflict", "military", "invasion", "attack", "strike",
        "missile", "nuclear", "weapon", "troops", "army", "nato",
        # 国际关系
        "china", "russia", "ukraine", "taiwan", "israel", "palestine",
        "gaza", "iran", "north korea", "syria", "afghanistan",
        # 地缘事件
        "ceasefire", "peace deal", "sanctions", "embargo", "treaty",
        "territorial", "border", "annexation", "occupation",
        # 中文关键词
        "战争", "冲突", "军事", "入侵", "导弹", "核",
        "乌克兰", "台湾", "以色列", "巴勒斯坦", "伊朗", "朝鲜",
    ]

    # 国际政治关键词 (选举、政策等)
    POLITICS_KEYWORDS = [
        # 选举
        "election", "vote", "poll", "primary", "nominee", "candidate",
        "president", "prime minister", "governor", "senator", "congress",
        # 政党
        "republican", "democrat", "conservative", "labour", "party",
        # 政策
        "policy", "legislation", "bill", "act", "reform", "tax",
        "impeachment", "resignation", "approval rating",
        # 中文关键词
        "选举", "投票", "总统", "首相", "议会", "政党",
    ]

    def __init__(self):
        self.base_url = settings.GAMMA_API_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    def _is_politics_market(self, category: str, tags: list, question: str) -> bool:
        """
        判断是否为政治类市场

        Args:
            category: Polymarket 官方分类
            tags: 标签列表
            question: 市场问题

        Returns:
            是否为政治类市场
        """
        category_lower = category.lower() if category else ""
        question_lower = question.lower() if question else ""
        tags_text = " ".join(tags).lower()

        # 1. 首先检查是否在排除列表中（体育、加密货币等）
        for excluded in self.EXCLUDED_CATEGORIES:
            if excluded in category_lower:
                return False
            # 也检查问题中是否包含体育相关词汇
            if excluded in ["nfl", "nba", "mlb", "ufc", "mma"] and excluded in question_lower:
                return False

        # 2. 检查 category 是否为政治类
        for politics_cat in self.POLITICS_CATEGORIES:
            if politics_cat in category_lower:
                return True

        # 3. 检查 tags 中是否包含政治关键词
        for keyword in ["politics", "political", "election", "government"]:
            if keyword in tags_text:
                return True

        # 4. 检查问题内容是否包含政治关键词（作为后备）
        for keyword in self.POLITICS_KEYWORDS + self.GEOPOLITICS_KEYWORDS:
            if keyword in question_lower:
                return True

        return False

    def _classify_politics_category(self, question: str, tags: list) -> str:
        """
        根据问题内容和标签分类市场

        Args:
            question: 市场问题（小写）
            tags: 标签列表（小写）

        Returns:
            "地缘政治" 或 "国际政治"
        """
        text = question + " " + " ".join(tags)

        # 检查是否包含地缘政治关键词
        for keyword in self.GEOPOLITICS_KEYWORDS:
            if keyword in text:
                return "地缘政治"

        # 默认归类为国际政治
        return "国际政治"

    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()

    async def fetch_politics_markets(self, limit: int = 100) -> List[Dict]:
        """
        获取政治类活跃市场

        Args:
            limit: 获取数量限制

        Returns:
            市场数据列表
        """
        # Gamma API 参数
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit,
        }

        try:
            response = await self.client.get(
                f"{self.base_url}/markets",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            markets = []
            for m in data:
                # 获取 category 和 tags
                category = m.get("category", "")
                tags = m.get("tags", [])
                tag_names = [t.get("label", "").lower() if isinstance(t, dict) else str(t).lower() for t in tags]
                question = m.get("question", "")

                # 使用新的筛选函数判断是否为政治类市场
                if not self._is_politics_market(category, tag_names, question):
                    continue

                # 解析 clobTokenIds (可能是 JSON 字符串或列表)
                clob_token_ids_raw = m.get("clobTokenIds", "[]")
                if isinstance(clob_token_ids_raw, str):
                    try:
                        clob_token_ids = json.loads(clob_token_ids_raw)
                    except json.JSONDecodeError:
                        clob_token_ids = []
                else:
                    clob_token_ids = clob_token_ids_raw

                if not isinstance(clob_token_ids, list) or len(clob_token_ids) < 2:
                    continue

                # 根据内容区分 国际政治 vs 地缘政治
                question_lower = question.lower()
                market_category = self._classify_politics_category(question_lower, tag_names)

                markets.append({
                    "slug": m.get("slug", ""),
                    "condition_id": m.get("conditionId", ""),
                    "yes_token_id": clob_token_ids[0],
                    "no_token_id": clob_token_ids[1],
                    "category": market_category,
                    "question": question,
                    "active": m.get("active", True),
                })

            return markets

        except httpx.HTTPError as e:
            print(f"获取市场数据失败: {e}")
            return []

    async def fetch_all_active_markets(self, limit: int = 200) -> List[Dict]:
        """
        获取所有活跃市场（不限类别，用于 token 匹配）

        Args:
            limit: 获取数量限制

        Returns:
            市场数据列表
        """
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit,
        }

        try:
            response = await self.client.get(
                f"{self.base_url}/markets",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            markets = []
            for m in data:
                # 解析 clobTokenIds (可能是 JSON 字符串或列表)
                clob_token_ids_raw = m.get("clobTokenIds", "[]")
                if isinstance(clob_token_ids_raw, str):
                    try:
                        clob_token_ids = json.loads(clob_token_ids_raw)
                    except json.JSONDecodeError:
                        clob_token_ids = []
                else:
                    clob_token_ids = clob_token_ids_raw

                if not isinstance(clob_token_ids, list) or len(clob_token_ids) < 2:
                    continue

                markets.append({
                    "slug": m.get("slug", ""),
                    "condition_id": m.get("conditionId", ""),
                    "yes_token_id": clob_token_ids[0],
                    "no_token_id": clob_token_ids[1],
                    "category": m.get("category", "Other"),
                    "question": m.get("question", ""),
                    "active": m.get("active", True),
                })

            return markets

        except httpx.HTTPError as e:
            print(f"获取市场数据失败: {e}")
            return []

    async def sync_markets_to_db(self, session: AsyncSession, markets: List[Dict]) -> int:
        """
        同步市场数据到数据库

        Args:
            session: 数据库会话
            markets: 市场数据列表

        Returns:
            新增/更新的市场数量
        """
        count = 0

        for market_data in markets:
            slug = market_data.get("slug")
            if not slug:
                continue

            # 检查是否已存在
            result = await session.execute(
                select(Market).where(Market.slug == slug)
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有记录
                existing.condition_id = market_data.get("condition_id", existing.condition_id)
                existing.yes_token_id = market_data.get("yes_token_id", existing.yes_token_id)
                existing.no_token_id = market_data.get("no_token_id", existing.no_token_id)
                existing.question = market_data.get("question", existing.question)
                existing.active = market_data.get("active", existing.active)
                existing.updated_at = datetime.utcnow()
            else:
                # 创建新记录
                new_market = Market(
                    slug=slug,
                    condition_id=market_data.get("condition_id", ""),
                    yes_token_id=market_data.get("yes_token_id", ""),
                    no_token_id=market_data.get("no_token_id", ""),
                    category=market_data.get("category", "Politics"),
                    question=market_data.get("question", ""),
                    active=market_data.get("active", True),
                )
                session.add(new_market)
                count += 1

        await session.commit()
        return count

    async def get_token_to_market_map(self, session: AsyncSession) -> Dict[str, Dict]:
        """
        构建 token_id 到市场的映射表

        Returns:
            {token_id: {"slug": ..., "outcome": "YES"/"NO"}}
        """
        result = await session.execute(select(Market).where(Market.active == True))
        markets = result.scalars().all()

        token_map = {}
        for m in markets:
            token_map[m.yes_token_id] = {"slug": m.slug, "outcome": "YES"}
            token_map[m.no_token_id] = {"slug": m.slug, "outcome": "NO"}

        return token_map
