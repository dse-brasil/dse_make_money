import json
import logging
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("CDI_Worker")

# BCB SGS API configuration
CDI_SERIES_CODE = 12  # Daily CDI rate from Banco Central (SGS)
BCB_API_URL = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CDI_SERIES_CODE}/dados/ultimos/1?formato=json"

def fetch_latest_cdi():
    """
    Queries the Banco Central do Brasil (BCB) SGS API to fetch the most recent
    daily CDI rate.
    """
    logger.info("Fetching latest CDI rate from Banco Central do Brasil SGS API...")
    logger.debug(f"API Endpoint: {BCB_API_URL}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    req = urllib.request.Request(BCB_API_URL, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                logger.error(f"HTTP Error: Received status code {response.status}")
                return None
            
            data_bytes = response.read()
            data_json = json.loads(data_bytes.decode("utf-8"))
            
            if not data_json or len(data_json) == 0:
                logger.warning("API returned empty dataset.")
                return None
                
            return data_json[0]

    except urllib.error.URLError as e:
        logger.error(f"Network error trying to connect to BCB API: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def calculate_annualized_rate(daily_rate_pct):
    """
    Calculates the annualized CDI rate (compounded over 252 business days).
    Formula: Annual_Rate = ((1 + Daily_Rate / 100) ^ 252 - 1) * 100
    """
    daily_rate_decimal = daily_rate_pct / 100.0
    annualized_decimal = (1.0 + daily_rate_decimal) ** 252 - 1.0
    return annualized_decimal * 100.0

def run_worker():
    """
    Runs the main worker logic.
    """
    logger.info("Starting CDI Ingestion Worker...")
    
    cdi_record = fetch_latest_cdi()
    
    if cdi_record:
        try:
            # Extract date and value from BCB response
            date_str = cdi_record.get("data")
            value_str = cdi_record.get("valor")
            
            if not date_str or not value_str:
                logger.error("Required fields 'data' or 'valor' missing in API payload.")
                sys.exit(1)
                
            daily_rate_pct = float(value_str)
            annualized_rate_pct = calculate_annualized_rate(daily_rate_pct)
            
            # Format and present findings
            print("\n" + "=" * 50)
            print("        CENTRAL BANK CDI INGESTION WORKER")
            print("=" * 50)
            print(f"Fetch Timestamp:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Reference Date:     {date_str}")
            print(f"Daily CDI Rate:     {daily_rate_pct:.6f}%")
            print(f"Annualized CDI:     {annualized_rate_pct:.4f}% p.a. (252 t.u.)")
            print("=" * 50 + "\n")
            
            logger.info("CDI ingestion task completed successfully.")
            
        except ValueError as e:
            logger.error(f"Error parsing CDI rate value to float: {e}")
            sys.exit(1)
    else:
        logger.error("Ingestion failed. Could not retrieve CDI data.")
        sys.exit(1)

if __name__ == "__main__":
    run_worker()
