import pytest
from src.domain.multisig_coordinator import (
    MultiSigCoordinator,
    MultiSigProposal,
)


def test_multisig_init_validation() -> None:
    with pytest.raises(ValueError, match="Invalid threshold hierarchy"):
        MultiSigCoordinator(low_threshold=3, med_threshold=2, high_threshold=1)


def test_multisig_duplicate_signer_deduplication() -> None:
    coordinator = MultiSigCoordinator(low_threshold=1, med_threshold=2)
    coordinator.register_signer("signerA", weight=1)
    coordinator.register_signer("signerB", weight=1)

    proposal = MultiSigProposal(
        proposal_id="p1",
        action="rebalance",
        payload={"target": "pool1"},
        nonce=1,
        expiration_timestamp=1000.0,
    )

    # Signer A submits signature
    assert coordinator.add_signature(
        proposal, "signerA", "sigA", current_time=500.0
    )

    # Threshold for 'med' is 2, currently only 1
    assert not coordinator.evaluate_quorum(
        proposal, required_level="med", current_time=500.0
    )

    # Signer A submits again (duplicate) -> should not double-count!
    assert coordinator.add_signature(
        proposal, "signerA", "sigA_v2", current_time=500.0
    )
    assert not coordinator.evaluate_quorum(
        proposal, required_level="med", current_time=500.0
    )

    # Signer B submits signature -> total weight = 2, satisfies 'med'
    assert coordinator.add_signature(
        proposal, "signerB", "sigB", current_time=500.0
    )
    assert coordinator.evaluate_quorum(
        proposal, required_level="med", current_time=500.0
    )


def test_multisig_replay_protection() -> None:
    coordinator = MultiSigCoordinator(low_threshold=1)
    coordinator.register_signer("signerA", weight=1)

    proposal = MultiSigProposal(
        proposal_id="p1",
        action="rebalance",
        payload={},
        nonce=42,
        expiration_timestamp=1000.0,
    )
    coordinator.add_signature(proposal, "signerA", "sigA", current_time=500.0)

    # First execution succeeds
    assert coordinator.execute_proposal(
        proposal, required_level="low", current_time=500.0
    )

    # Second execution of same proposal/nonce fails due to replay protection
    assert not coordinator.execute_proposal(
        proposal, required_level="low", current_time=500.0
    )


def test_multisig_expiration() -> None:
    coordinator = MultiSigCoordinator(low_threshold=1)
    coordinator.register_signer("signerA", weight=1)

    proposal = MultiSigProposal(
        proposal_id="p1",
        action="rebalance",
        payload={},
        nonce=10,
        expiration_timestamp=100.0,
    )

    # Attempting to sign after expiry fails
    assert not coordinator.add_signature(
        proposal, "signerA", "sigA", current_time=150.0
    )

    # Quorum evaluation after expiry fails
    proposal.expiration_timestamp = 200.0
    coordinator.add_signature(proposal, "signerA", "sigA", current_time=150.0)
    assert not coordinator.evaluate_quorum(
        proposal, required_level="low", current_time=250.0
    )
