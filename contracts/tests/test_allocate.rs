#![cfg(test)]

use soroban_sdk::{testutils::Address as _, Address, Env};
use halopay_treasury::{YieldTreasuryContract, YieldTreasuryContractClient};


fn setup() -> (Env, YieldTreasuryContractClient<'static>, Address, Address) {
    let env = Env::default();
    env.mock_all_auths();
    let contract_id = env.register_contract(None, YieldTreasuryContract);
    let client = YieldTreasuryContractClient::new(&env, &contract_id);
    let admin = Address::generate(&env);
    let agent = Address::generate(&env);
    client.init(&admin, &agent);
    (env, client, admin, agent)
}



#[test]
fn test_allocate_success() {
    let (env, client, _admin, _agent) = setup();
    let dest = Address::generate(&env);
    client.add_allowlist(&dest);
    client.deposit(&1000);
    client.allocate(&dest, &500);
    let (_deposits, allocated) = client.get_position();
    assert_eq!(allocated, 500);
}
