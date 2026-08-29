use soroban_sdk::{contracttype, Address, Env};

#[contracttype]
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum DataKey {
    Admin,
    Agent,
    Allowlist(Address),
    TotalDeposits,
    TotalAllocated,
}

pub fn get_admin(env: &Env) -> Option<Address> {
    env.storage().instance().get(&DataKey::Admin)
}

pub fn set_admin(env: &Env, admin: &Address) {
    env.storage().instance().set(&DataKey::Admin, admin);
}

pub fn get_agent(env: &Env) -> Option<Address> {
    env.storage().instance().get(&DataKey::Agent)
}

pub fn set_agent(env: &Env, agent: &Address) {
    env.storage().instance().set(&DataKey::Agent, agent);
}

pub fn is_allowed(env: &Env, target: &Address) -> bool {
    env.storage()
        .persistent()
        .get(&DataKey::Allowlist(target.clone()))
        .unwrap_or(false)
}

pub fn set_allowed(env: &Env, target: &Address) {
    env.storage()
        .persistent()
        .set(&DataKey::Allowlist(target.clone()), &true);
}

pub fn get_total_deposits(env: &Env) -> u128 {
    env.storage()
        .persistent()
        .get(&DataKey::TotalDeposits)
        .unwrap_or(0)
}

pub fn set_total_deposits(env: &Env, amount: u128) {
    env.storage()
        .persistent()
        .set(&DataKey::TotalDeposits, &amount);
}

pub fn get_total_allocated(env: &Env) -> u128 {
    env.storage()
        .persistent()
        .get(&DataKey::TotalAllocated)
        .unwrap_or(0)
}

pub fn set_total_allocated(env: &Env, amount: u128) {
    env.storage()
        .persistent()
        .set(&DataKey::TotalAllocated, &amount);
}
