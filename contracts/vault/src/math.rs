pub const PRECISION: i128 = 10_000_000; // 7 decimals for XLM

pub fn compute_shares(deposit_amount: i128, total_assets: i128, total_shares: i128) -> i128 {
    if total_shares == 0 || total_assets == 0 {
        deposit_amount
    } else {
        (deposit_amount * total_shares) / total_assets
    }
}