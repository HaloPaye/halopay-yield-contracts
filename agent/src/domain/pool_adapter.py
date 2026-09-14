from decimal import Decimal
from typing import Dict, Any, List


class PoolAdapter:
    """Standardizes heterogeneous Soroban DeFi liquidity pool telemetry."""

    def __init__(self, protocol_name: str = "Soroswap") -> None:
        self.protocol_name = protocol_name

    def normalize_pool_metrics(self, raw_pool: Dict[str, Any]) -> Dict[str, Any]:
        pool_id = str(raw_pool.get("id", "unknown"))
        reserve_a = Decimal(str(raw_pool.get("reserve_a", 0)))
        reserve_b = Decimal(str(raw_pool.get("reserve_b", 0)))
        fee_bps = int(raw_pool.get("fee_bps", 30))

        tvl = reserve_a + reserve_b
        return {
            "protocol": self.protocol_name,
            "pool_id": pool_id,
            "reserve_a": reserve_a,
            "reserve_b": reserve_b,
            "fee_rate": Decimal(fee_bps) / Decimal("10000"),
            "tvl_estimate": tvl,
        }

    def rank_pools_by_depth(self, pools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = [self.normalize_pool_metrics(p) for p in pools]
        return sorted(normalized, key=lambda p: p["tvl_estimate"], reverse=True)
