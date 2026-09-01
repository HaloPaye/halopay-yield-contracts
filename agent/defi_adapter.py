# DeFi Protocol Adapter with slippage boundary protection
class DeFiProtocolAdapter:
    def __init__(self, protocol_name: str, max_slippage_bps: int = 50):
        self.protocol_name = protocol_name
        self.max_slippage_bps = max_slippage_bps

    def validate_quote(self, expected_amount: float, minimum_amount: float) -> bool:
        if expected_amount <= 0:
            return False
        slippage_bps = ((expected_amount - minimum_amount) / expected_amount) * 10000
        return slippage_bps <= self.max_slippage_bps
