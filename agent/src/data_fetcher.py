import requests
from src.logger import log_event

HORIZON_URL = "https://horizon-testnet.stellar.org"

def fetch_liquidity_pools():
    try:
        url = f"{HORIZON_URL}/liquidity_pools"
        response = requests.get(url, timeout=10)
        
        if response.status_code in [429, 500]:
            log_event("SYSTEM", "ERROR", "NETWORK_ERROR", action="SLEEP_AND_RETRY", status=response.status_code)
            return None
            
        response.raise_for_status()
        data = response.json()
        
        pools = data.get("_embedded", {}).get("records", [])
        return pools
    except requests.exceptions.RequestException as e:
        log_event("SYSTEM", "ERROR", "NETWORK_ERROR", action="SLEEP_AND_RETRY", error=str(e))
        return None
    except ValueError as e:
        log_event("SYSTEM", "ERROR", "PARSE_ERROR", action="DISCARD_POOL", error=str(e))
        return None
