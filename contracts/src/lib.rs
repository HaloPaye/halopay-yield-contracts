#![no_std]

#[path = "core/mod.rs"]
pub mod core_domain;
pub mod interfaces;
pub mod state;
pub mod security;

use soroban_sdk::{contract, contractimpl, Address, Env};
use core_domain::errors::TreasuryError;
use core_domain::events;
use state::storage;
use security::auth;

#[contract]
pub struct YieldTreasuryContract;

#[contractimpl]
impl YieldTreasuryContract {
    pub fn init(env: Env, admin: Address, agent: Address) {
        if storage::get_admin(&env).is_some() {
            panic!("already initialized");
        }
        storage::set_admin(&env, &admin);
        storage::set_agent(&env, &agent);
    }

    pub fn add_allowlist(env: Env, target: Address) -> Result<(), TreasuryError> {
        auth::add_allowlist(&env, target)
    }

    pub fn deposit(env: Env, amount: u128) {
        // No auth required
        let total = storage::get_total_deposits(&env);
        storage::set_total_deposits(&env, total + amount);
    }

    pub fn allocate(env: Env, destination: Address, amount: u128) -> Result<(), TreasuryError> {
        let agent = storage::get_agent(&env).ok_or(TreasuryError::NotAuthorized)?;
        agent.require_auth();

        if !storage::is_allowed(&env, &destination) {
            return Err(TreasuryError::DestinationNotAllowed);
        }
        if amount > 1000 {
            return Err(TreasuryError::ExceedsTransactionCap);
        }

        let total_deposits = storage::get_total_deposits(&env);
        let total_allocated = storage::get_total_allocated(&env);

        if total_allocated + amount > (total_deposits * 8) / 10 {
            return Err(TreasuryError::ExceedsGlobalCap);
        }

        let remaining = total_deposits - total_allocated;
        if remaining < amount {
            return Err(TreasuryError::InsufficientBalance);
        }
        
        if remaining - amount < 100 {
            return Err(TreasuryError::BreachesMinimumFloor);
        }

        // Action: Invokes destination cross-contract to deposit amount. 
        // For the sake of this mock hackathon implementation, we just update state and emit event.
        storage::set_total_allocated(&env, total_allocated + amount);
        events::emit_funds_allocated(&env, agent, destination, amount);
        Ok(())
    }

    pub fn withdraw(env: Env, amount: u128, _to: Address) -> Result<(), TreasuryError> {
        let admin = storage::get_admin(&env).ok_or(TreasuryError::NotAuthorized)?;
        admin.require_auth();
        
        // Mock transfer for now
        events::emit_funds_withdrawn(&env, admin, amount);
        Ok(())
    }

    pub fn get_position(env: Env) -> (u128, u128) {
        (storage::get_total_deposits(&env), storage::get_total_allocated(&env))
    }
}
