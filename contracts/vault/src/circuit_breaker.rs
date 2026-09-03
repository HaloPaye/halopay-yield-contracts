#[derive(Debug, PartialEq, Eq)]
pub enum CircuitBreakerState {
    Active,
    Paused,
}

pub struct CircuitBreaker {
    pub state: CircuitBreakerState,
}

impl CircuitBreaker {
    pub fn new() -> Self {
        Self {
            state: CircuitBreakerState::Active,
        }
    }

    pub fn pause(&mut self) {
        self.state = CircuitBreakerState::Paused;
    }

    pub fn resume(&mut self) {
        self.state = CircuitBreakerState::Active;
    }

    pub fn is_active(&self) -> bool {
        self.state == CircuitBreakerState::Active
    }
}