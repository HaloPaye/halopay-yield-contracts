use crate::{core_domain::errors::TreasuryError, state::storage};
use soroban_sdk::{Address, Env};

pub fn add_allowlist(env: &Env, target: Address) -> Result<(), TreasuryError> {
    let admin = storage::get_admin(env).ok_or(TreasuryError::NotAuthorized)?;
    admin.require_auth();
    storage::set_allowed(env, &target);
    Ok(())
}
