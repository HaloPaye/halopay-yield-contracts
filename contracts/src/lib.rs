#![no_std]
use soroban_sdk::{contract, contractimpl, Env};

#[contract]
pub struct YieldTreasuryContract;

#[contractimpl]
impl YieldTreasuryContract {
    pub fn deposit(env: Env, amount: u32) -> u32 {
        amount
    }
}
