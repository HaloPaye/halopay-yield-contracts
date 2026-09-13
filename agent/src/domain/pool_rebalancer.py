from decimal import Decimal
from typing import Dict, List, Tuple


class PoolRebalancer:
    def __init__(self, dead_zone_pct: Decimal = Decimal("0.02")) -> None:
        self.dead_zone_pct = dead_zone_pct

    def compute_rebalance_actions(
        self,
        current_balances: Dict[str, Decimal],
        target_weights: Dict[str, Decimal],
    ) -> List[Tuple[str, Decimal]]:
        total_value = sum(current_balances.values())
        if total_value <= Decimal("0"):
            return []

        actions: List[Tuple[str, Decimal]] = []
        for asset, target_weight in target_weights.items():
            current_amount = current_balances.get(asset, Decimal("0"))
            current_weight = current_amount / total_value
            weight_diff = target_weight - current_weight

            if abs(weight_diff) >= self.dead_zone_pct:
                delta_amount = weight_diff * total_value
                actions.append((asset, delta_amount.quantize(Decimal("0.0000001"))))

        return actions
