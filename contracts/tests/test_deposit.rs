#![cfg(test)]

use soroban_sdk::Env;
use halopay_treasury::{YieldTreasuryContract, YieldTreasuryContractClient};

#[test]
fn test_deposit_and_get_position() {
    let env = Env::default();
    let contract_id = env.register_contract(None, YieldTreasuryContract);
    let client = YieldTreasuryContractClient::new(&env, &contract_id);

    client.deposit(&500);
    client.deposit(&200);

    let (deposits, allocated) = client.get_position();
    assert_eq!(deposits, 700);
    assert_eq!(allocated, 0);
}
