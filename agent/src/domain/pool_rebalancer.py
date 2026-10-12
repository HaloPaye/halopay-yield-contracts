from decimal import Decimal
from typing import Dict, List, Tuple


class PoolRebalancer:
    """Computes rebalance actions for a portfolio of assets based on target
    weights and dead-zone drift thresholds.
    """

    def __init__(
        self,
        dead_zone_pct: Decimal = Decimal("0.02"),
        min_trade_size: Decimal = Decimal("0.0000001"),
    ) -> None:
        if dead_zone_pct < Decimal("0"):
            raise ValueError("dead_zone_pct cannot be negative")
        if min_trade_size < Decimal("0"):
            raise ValueError("min_trade_size cannot be negative")
        self.dead_zone_pct = dead_zone_pct
        self.min_trade_size = min_trade_size

    def compute_rebalance_actions(
        self,
        current_balances: Dict[str, Decimal],
        target_weights: Dict[str, Decimal],
    ) -> List[Tuple[str, Decimal]]:
        """Computes rebalance actions for assets whose drift exceeds the dead
        zone.

        Args:
            current_balances: Mapping of asset symbol to current balance
                amount.
            target_weights: Mapping of asset symbol to target portfolio weight.

        Returns:
            List of (asset, delta_amount) pairs. Positive delta indicates buy/
            deposit; negative indicates sell/withdraw.
        """
        # Validate inputs
        if not current_balances and not target_weights:
            return []

        # Check for negative balances
        for asset, balance in current_balances.items():
            if balance < Decimal("0"):
                raise ValueError(
                    f"Balance for asset {asset} cannot be negative"
                )

        # Check for negative weights
        for asset, weight in target_weights.items():
            if weight < Decimal("0"):
                raise ValueError(
                    f"Target weight for asset {asset} cannot be negative"
                )

        total_value = sum(current_balances.values())
        if total_value <= Decimal("0"):
            return []

        # Validate target weights sum (within tolerance if weights are given)
        weight_sum = sum(target_weights.values())
        if weight_sum <= Decimal("0"):
            return []

        # Normalize target weights to 1.0 if not already normalized
        normalized_weights: Dict[str, Decimal] = {}
        for asset, weight in target_weights.items():
            normalized_weights[asset] = weight / weight_sum

        # Union of all assets in both current balances and target weights
        all_assets = set(current_balances.keys()) | set(
            normalized_weights.keys()
        )

        actions: List[Tuple[str, Decimal]] = []
        for asset in sorted(all_assets):
            current_amount = current_balances.get(asset, Decimal("0"))
            current_weight = current_amount / total_value
            target_weight = normalized_weights.get(asset, Decimal("0"))
            weight_diff = target_weight - current_weight

            if abs(weight_diff) >= self.dead_zone_pct:
                delta_amount = weight_diff * total_value
                rounded_delta = delta_amount.quantize(Decimal("0.0000001"))
                if abs(rounded_delta) >= self.min_trade_size:
                    actions.append((asset, rounded_delta))

        return actions
