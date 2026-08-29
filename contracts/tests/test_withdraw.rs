#![cfg(test)]

use halopay_treasury::{YieldTreasuryContract, YieldTreasuryContractClient};
use soroban_sdk::{testutils::Address as _, Address, Env};

#[test]
fn test_withdraw() {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, YieldTreasuryContract);
    let client = YieldTreasuryContractClient::new(&env, &contract_id);

    let admin = Address::generate(&env);
    let agent = Address::generate(&env);
    client.init(&admin, &agent);

    client.deposit(&1000);

    let to = Address::generate(&env);
    client.withdraw(&200, &to);
}
