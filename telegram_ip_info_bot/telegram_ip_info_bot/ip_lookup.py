# ip_lookup.py
# This module contains the function to query IP information from ip-api.com

import requests
import json
import logging
from typing import Optional, Dict, Any

# Configure logging - the bot's main logging configuration will be used
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_ip_info_from_api(ip_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Queries the ip-api.com service for information about an IP address.

    Args:
        ip_address: The IP address to look up. If None, the API will return
                    information for the IP address of the calling machine (the bot server).

    Returns:
        A dictionary containing the API response data and status.
        Returns {'status': 'success', 'data': {...}} on success.
        Returns {'status': 'error', 'message': 'Error description'} on failure.
    """
    base_url = "http://ip-api.com/json/"
    url = f"{base_url}{ip_address}" if ip_address else base_url

    headers = {
        'User-Agent': 'TelegramIPLookupBot/1.0 (Python)' # Identify your bot script
    }

    logging.debug(f"Querying API: {url} for IP: {ip_address if ip_address else 'caller IP'}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Check the 'status' field within the API response itself
        if data.get('status') == 'success':
            return {'status': 'success', 'data': data}
        else:
            # API returned an error status
            message = data.get('message', 'Unknown error from API')
            logging.warning(f"API returned error status for {ip_address}: {message}")
            return {'status': 'error', 'message': f"API error: {message}"}

    except requests.exceptions.Timeout:
        logging.error(f"API request timed out for {ip_address}")
        return {'status': 'error', 'message': "API request timed out."}
    except requests.exceptions.RequestException as e:
        logging.error(f"Network or HTTP error during API call for {ip_address}: {e}")
        return {'status': 'error', 'message': f"Network or HTTP error: {e}"}
    except json.JSONDecodeError:
         logging.error(f"API response was not valid JSON for {ip_address}")
         return {'status': 'error', 'message': "Invalid response from API."}
    except Exception as e:
         logging.error(f"An unexpected error occurred during API call for {ip_address}: {e}")
         return {'status': 'error', 'message': f"An unexpected error occurred: {e}"}
