import socket
import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Tuple, Set

# Configure logging
# INFO level shows progress and results.
# DEBUG level (can be enabled if needed) can show details like "port closed/error".
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_ports(port_string: str) -> List[int]:
    """
    Parses a string defining port range(s) (e.g., '20-25,80,443,8080')
    and returns a sorted list of unique ports.

    Args:
        port_string: A string specifying ports or port ranges.

    Returns:
        A sorted list of unique integer port numbers.

    Raises:
        ValueError: If the port string format is invalid or ports are out of range.
    """
    ports: Set[int] = set()
    try:
        parts = port_string.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue

            if '-' in part:
                start_str, end_str = part.split('-')
                start_port = int(start_str.strip())
                end_port = int(end_str.strip())
                if not (1 <= start_port <= 65535) or not (1 <= end_port <= 65535):
                     raise ValueError("Port number out of valid range (1-65535)")
                if start_port > end_port:
                     raise ValueError("Start port cannot be greater than end port")
                ports.update(range(start_port, end_port + 1))
            else:
                port = int(part)
                if not (1 <= port <= 65535):
                     raise ValueError("Port number out of valid range (1-65535)")
                ports.add(port)
    except ValueError as e:
        raise ValueError(f"Invalid port format or range: {e}") from e
    except Exception as e:
         # Catch any other unexpected errors during parsing
         raise ValueError(f"An unexpected error occurred while parsing ports: {e}") from e

    return sorted(list(ports))


def scan_port(ip: str, port: int, timeout: float) -> Optional[int]:
    """
    Attempts to establish a TCP connection to the specified port on the IP address.
    Returns the port number if open, otherwise returns None.

    Args:
        ip: The target IP address or hostname.
        port: The port number to scan.
        timeout: The connection timeout in seconds.

    Returns:
        The port number if the connection is successful (port is open),
        otherwise None.
    """
    try:
        # socket.create_connection is a convenient function that combines socket creation,
        # setting timeout, and attempting to connect.
        with socket.create_connection((ip, port), timeout=timeout):
            # If connection is successful, the port is open
            logging.info(f"✅ Port Open: {port}")
            return port
    except (socket.timeout, ConnectionRefusedError):
        # These are the expected exceptions for a closed or unresponsive port
        # logging.debug(f"Port {port} closed/unresponsive") # Debug message if you want to see all ports
        return None
    except socket.gaierror:
        # Hostname resolution error - should ideally be caught before threading,
        # but handle here as well for robustness.
        # logging.error(f"Could not resolve hostname/IP in thread: {ip}")
        return None # Return None as this specific port couldn't be scanned
    except OSError as e:
         # Other socket errors like "Network is unreachable" or permission issues
         # logging.debug(f"Error scanning port {port}: {e}")
         return None
    except Exception as e:
        # Catch any other unexpected exceptions and log them
        logging.error(f"Unexpected error while scanning port {port}: {e}")
        return None

def scan_ports(ip: str, ports: List[int], timeout: float, max_workers: int) -> List[int]:
    """
    Scans a list of ports on the given IP address concurrently using a thread pool.
    Returns a list of open ports.

    Args:
        ip: The target IP address or hostname.
        ports: A list of port numbers to scan.
        timeout: The connection timeout for each port scan.
        max_workers: The maximum number of worker threads to use.

    Returns:
        A sorted list of open port numbers.
    """
    if not ports:
        logging.warning("Port list for scanning is empty.")
        return []

    # Pre-check IP resolution before starting threads
    try:
        resolved_ip = socket.gethostbyname(ip)
        logging.info(f"🔍 Starting scan on IP: {resolved_ip} (Hostname: {ip})")
        logging.info(f"Scanning ports: {ports[0]}-{ports[-1]} (total {len(ports)} ports) with {max_workers} workers and {timeout}s timeout.")
        ip = resolved_ip # Use the resolved IP for scanning
    except socket.gaierror:
        logging.error(f"Could not resolve hostname/IP: {ip}. Please check the address.")
        return [] # Return empty list as scanning is not possible

    open_ports = []

    # Use ThreadPoolExecutor for parallel execution of scan_port
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Dictionary to track which port corresponds to each 'future' task
        future_to_port = {executor.submit(scan_port, ip, port, timeout): port for port in ports}

        # Process results as they complete
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            try:
                result = future.result() # Get the result of the scan_port function
                if result is not None:
                    open_ports.append(result)
            except Exception as exc:
                # This branch catches exceptions that might have slipped through in scan_port
                logging.error(f"Port {port} generated an exception during execution: {exc}")

    logging.info(f"✨ Scan finished for IP: {ip}. Found open ports: {len(open_ports)}")
    return sorted(open_ports) # Return the sorted list of open ports

# --- Script Entry Point ---
if __name__ == "__main__":
    # Setup command-line argument parser
    parser = argparse.ArgumentParser(
        description="Simple TCP port scanner using multithreading."
    )
    parser.add_argument(
        "ip",
        help="Target IP address or hostname to scan."
    )
    parser.add_argument(
        "-p", "--ports",
        help="Ports to scan (e.g., '80,443,8080' or '20-1024' or '22'). "
             "Defaults to scanning ports 1 through 1024.",
        default="1-1024"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout in seconds (default: 1.0)."
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=100,
        help="Number of worker threads (default: 100). "
             "A very high value might cause issues on some systems."
    )

    args = parser.parse_args()

    # Parse the ports provided by the user
    try:
        ports_to_scan = parse_ports(args.ports)
        if not ports_to_scan:
            logging.error("Failed to get port list for scanning. Check the -p parameter.")
            sys.exit(1) # Exit with error
    except ValueError as e:
        logging.error(f"Error parsing ports: {e}")
        sys.exit(1) # Exit with error

    # Start the scan
    open_ports_list = scan_ports(
        args.ip,
        ports_to_scan,
        args.timeout,
        args.workers
    )

    # Print the final list of open ports
    if open_ports_list:
        logging.info(f"\n--- Final list of open ports on {args.ip} ---")
        for port in open_ports_list:
            print(f" - {port}/TCP") # Use print for clean list output
        print("------------------------------------------------------")
    else:
        logging.info(f"\nNo open ports found in the specified range on {args.ip}.")

# Example command-line usage after saving the code to a file (e.g., scanner.py):
# python scanner.py 192.168.1.1
# python scanner.py scanme.nmap.org -p 22,80,443,8080
# python scanner.py 10.0.0.1 -p 1-65535 -w 200 -t 0.5