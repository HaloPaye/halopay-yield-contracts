use soroban_sdk::{Env, Address, symbol_short};

pub fn emit_funds_allocated(env: &Env, agent: Address, destination: Address, amount: u128) {
    let topics = (symbol_short!("allocate"),);
    env.events().publish(topics, (agent, destination, amount));
}

pub fn emit_funds_withdrawn(env: &Env, admin: Address, amount: u128) {
    let topics = (symbol_short!("withdraw"),);
    env.events().publish(topics, (admin, amount));
}
