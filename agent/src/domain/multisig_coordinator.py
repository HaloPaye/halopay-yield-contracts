import time
from typing import Any, Dict, Optional, Set


class Signer:
    """Represents an authorized signer with assigned threshold voting weight.
    """

    def __init__(self, public_key: str, weight: int) -> None:
        if not public_key:
            raise ValueError("public_key cannot be empty")
        if weight <= 0:
            raise ValueError("weight must be positive")
        self.public_key = public_key
        self.weight = weight


class MultiSigProposal:
    """Encapsulates a proposed multi-sig action with nonce and expiry."""

    def __init__(
        self,
        proposal_id: str,
        action: str,
        payload: Dict[str, Any],
        nonce: int,
        expiration_timestamp: float,
    ) -> None:
        if not proposal_id or not action:
            raise ValueError("proposal_id and action cannot be empty")
        if nonce < 0:
            raise ValueError("nonce cannot be negative")
        self.proposal_id = proposal_id
        self.action = action
        self.payload = payload
        self.nonce = nonce
        self.expiration_timestamp = expiration_timestamp
        self.signatures: Dict[str, str] = {}  # signer_key -> signature_hex


class MultiSigCoordinator:
    """Coordinates threshold multi-signature validation for Soroban contracts.

    Guards against signature replay attacks, duplicate signer weighting,
    expired proposals, and unauthorized signer injection.
    """

    def __init__(
        self,
        low_threshold: int = 1,
        med_threshold: int = 2,
        high_threshold: int = 3,
    ) -> None:
        if (
            low_threshold <= 0
            or med_threshold < low_threshold
            or high_threshold < med_threshold
        ):
            raise ValueError("Invalid threshold hierarchy")

        self.low_threshold = low_threshold
        self.med_threshold = med_threshold
        self.high_threshold = high_threshold
        self.signers: Dict[str, Signer] = {}
        self.used_nonces: Set[int] = set()

    def register_signer(self, public_key: str, weight: int) -> None:
        """Registers or updates a signer in the coordinator registry."""
        self.signers[public_key] = Signer(public_key, weight)

    def remove_signer(self, public_key: str) -> None:
        """Removes a signer from the coordinator registry."""
        self.signers.pop(public_key, None)

    def add_signature(
        self,
        proposal: MultiSigProposal,
        signer_key: str,
        signature: str,
        current_time: Optional[float] = None,
    ) -> bool:
        """Adds a signature to a proposal after verifying eligibility.

        Returns:
            True if signature was successfully accepted and recorded.
        """
        now = current_time if current_time is not None else time.time()
        if now >= proposal.expiration_timestamp:
            return False

        if signer_key not in self.signers:
            return False

        if not signature:
            return False

        proposal.signatures[signer_key] = signature
        return True

    def evaluate_quorum(
        self,
        proposal: MultiSigProposal,
        required_level: str = "med",
        current_time: Optional[float] = None,
    ) -> bool:
        """Evaluates whether accumulated unique signatures satisfy threshold.

        Guards against replay nonces and double-counted signers.
        """
        now = current_time if current_time is not None else time.time()
        if now >= proposal.expiration_timestamp:
            return False

        if proposal.nonce in self.used_nonces:
            return False

        thresholds = {
            "low": self.low_threshold,
            "med": self.med_threshold,
            "high": self.high_threshold,
        }
        target_weight = thresholds.get(required_level, self.med_threshold)

        total_weight = 0
        seen_signers: Set[str] = set()

        for signer_key in proposal.signatures:
            if signer_key in seen_signers:
                continue
            signer = self.signers.get(signer_key)
            if signer is not None:
                total_weight += signer.weight
                seen_signers.add(signer_key)

        return total_weight >= target_weight

    def execute_proposal(
        self,
        proposal: MultiSigProposal,
        required_level: str = "med",
        current_time: Optional[float] = None,
    ) -> bool:
        """Executes a proposal, consuming its nonce upon successful quorum."""
        if not self.evaluate_quorum(proposal, required_level, current_time):
            return False

        self.used_nonces.add(proposal.nonce)
        return True
