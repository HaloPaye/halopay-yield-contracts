pub struct TimelockQueue {
    pub execution_delay_seconds: u64,
}

impl TimelockQueue {
    pub fn new(execution_delay_seconds: u64) -> Self {
        Self {
            execution_delay_seconds,
        }
    }

    pub fn is_ready(&self, scheduled_timestamp: u64, current_timestamp: u64) -> bool {
        current_timestamp >= scheduled_timestamp + self.execution_delay_seconds
    }
}