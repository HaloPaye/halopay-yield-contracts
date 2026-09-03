#[derive(Debug, PartialEq, Eq)]
pub struct OptimizedStorageKey {
    pub key_id: u32,
}

impl OptimizedStorageKey {
    pub fn new(key_id: u32) -> Self {
        Self { key_id }
    }
}