use soroban_sdk::{Env, Address};
use crate::{storage, errors::TreasuryError};

pub fn add_allowlist(env: &Env, target: Address) -> Result<(), TreasuryError> {
    let admin = storage::get_admin(env).ok_or(TreasuryError::NotAuthorized)?;
    admin.require_auth();
    storage::set_allowed(env, &target);
    Ok(())
}
