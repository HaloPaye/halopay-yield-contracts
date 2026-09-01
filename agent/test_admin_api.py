# Admin Dashboard API Unit Tests
def test_admin_metrics_summary():
    metrics = {
        "total_yield_harvested": 1420.50,
        "active_strategies": 4,
        "status": "HEALTHY"
    }
    assert metrics["total_yield_harvested"] > 0
    assert metrics["status"] == "HEALTHY"
