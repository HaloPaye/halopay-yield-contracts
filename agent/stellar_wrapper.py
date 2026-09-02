# Hardened Stellar SDK Wrapper with Sanity Checks
class StellarSDKWrapper:
    @staticmethod
    def validate_public_key(pubkey: str) -> bool:
        return isinstance(pubkey, str) and len(pubkey) == 56 and pubkey.startswith('G')

    @staticmethod
    def validate_contract_id(contract_id: str) -> bool:
        return isinstance(contract_id, str) and len(contract_id) == 56 and contract_id.startswith('C')
