use soroban_sdk::contracterror;

#[contracterror]
#[derive(Copy, Clone, Debug, Eq, PartialEq, PartialOrd, Ord)]
#[repr(u32)]
pub enum TreasuryError {
    NotAuthorized = 1,
    ExceedsTransactionCap = 2,
    ExceedsGlobalCap = 3,
    BreachesMinimumFloor = 4,
    DestinationNotAllowed = 5,
    InsufficientBalance = 6,
}
