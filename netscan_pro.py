#!/usr/bin/env python3

import argparse
import socket
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_network, ip_address
from datetime import datetime

# Scapy imports - will require root/admin for some operations
try:
    from scapy.all import IP, TCP, ICMP, sr1, Ether, ARP, srp
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] Scapy is not installed. Some features (SYN scan, ICMP Ping, ARP scan) will be unavailable.")
    print("[!] Please install it with: pip install scapy")

# --- Configuration ---
DEFAULT_TIMEOUT = 1
DEFAULT_THREADS = 20
COMMON_TCP_PORTS = { # For simple reference, not fully used in --top-ports yet
    20: "FTP-Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPCBind", 135: "MS RPC",
    139: "NetBIOS-SSN", 143: "IMAP", 443: "HTTPS", 445: "Microsoft-DS (SMB)",
    993: "IMAPS", 995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP",
    5900: "VNC", 8080: "HTTP-Alt"
}

# --- Helper Functions ---

def resolve_target(target_str):
    """Resolves a hostname to an IP address."""
    try:
        return socket.gethostbyname(target_str)
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {target_str}")
        return None

def expand_targets(targets_str):
    """Expands target strings (single IP, CIDR, hostname) into a list of IP strings."""
    expanded = set()
    for t_str in targets_str.split(','):
        t_str = t_str.strip()
        if '/' in t_str: # CIDR
            try:
                network = ip_network(t_str, strict=False)
                for ip in network.hosts():
                    expanded.add(str(ip))
            except ValueError:
                print(f"[!] Invalid CIDR notation: {t_str}")
        else: # Single IP or hostname
            try:
                # Check if it's an IP address directly
                ip_addr_obj = ip_address(t_str)
                expanded.add(str(ip_addr_obj))
            except ValueError:
                # Not a direct IP, try to resolve as hostname
                resolved_ip = resolve_target(t_str)
                if resolved_ip:
                    expanded.add(resolved_ip)
    return list(expanded)

def parse_ports(ports_str, top_n=None):
    """Parses port strings (e.g., "22,80,443", "1-1024", "all")."""
    if not ports_str and top_n:
        return sorted(list(COMMON_TCP_PORTS.keys()))[:top_n]
    if ports_str.lower() == "all":
        return list(range(1, 65536))

    ports = set()
    parts = ports_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.update(range(start, end + 1))
        else:
            try:
                ports.add(int(part))
            except ValueError:
                print(f"[!] Invalid port specified: {part}")
    return sorted(list(ports))


# --- Scanning Functions ---

def icmp_ping(host, timeout):
    """Sends an ICMP Echo Request to a host. Requires Scapy and often root."""
    if not SCAPY_AVAILABLE:
        print(f"[-] ICMP Ping skipped for {host} (Scapy unavailable or not root).")
        return False # Cannot determine liveness without Scapy here
    try:
        # Using Scapy for ICMP ping
        pkt = IP(dst=host)/ICMP()
        resp = sr1(pkt, timeout=timeout, verbose=0)
        return resp is not None and resp.haslayer(ICMP) and resp[ICMP].type == 0 # Echo Reply
    except Exception as e:
        # print(f"[!] Error ICMP pinging {host}: {e}") # Can be very verbose
        return False

def arp_scan_local(network_cidr, timeout):
    """Performs an ARP scan on the local network. Requires Scapy and root."""
    if not SCAPY_AVAILABLE:
        print("[-] ARP Scan skipped (Scapy unavailable or not root).")
        return []

    live_hosts = []
    try:
        print(f"[*] Performing ARP scan on {network_cidr}...")
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network_cidr),
                         timeout=timeout, verbose=0, iface_hint=network_cidr) # iface_hint helps scapy pick interface
        for sent, received in ans:
            live_hosts.append(received.psrc)
            print(f"    [+] Host Found (ARP): {received.psrc} ({received.hwsrc})")
    except Exception as e:
        print(f"[!] Error during ARP scan: {e}")
    return live_hosts


def scan_tcp_connect(host, port, timeout):
    """Attempts a TCP Connect scan on a single port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result == 0:
                return "open"
    except socket.timeout:
        return "filtered (timeout)" # Or just closed, hard to distinguish simply
    except socket.error:
        return "closed" # Connection refused, host down etc.
    return "closed"

def scan_tcp_syn(host, port, timeout):
    """Performs a TCP SYN scan on a single port. Requires Scapy and root."""
    if not SCAPY_AVAILABLE:
        # Fallback or error if scapy is not available/usable
        # print(f"[-] SYN Scan for {host}:{port} skipped (Scapy unavailable or not root). Falling back to Connect Scan.")
        # For this example, we'll just indicate it couldn't run.
        # In a more robust tool, you might fall back to TCP Connect.
        return "error (scapy unavailable)"

    try:
        src_port = socket.htons(1500 + port % 1000) # Some randomness, or use RandShort() from scapy
        ip_layer = IP(dst=host)
        tcp_layer = TCP(sport=src_port, dport=port, flags="S") # SYN flag
        
        response = sr1(ip_layer/tcp_layer, timeout=timeout, verbose=0)

        if response is None:
            return "filtered" # No response
        elif response.haslayer(TCP):
            if response[TCP].flags == 0x12: # SYN-ACK
                # Send RST to close the connection gracefully (optional, good practice)
                # rst_pkt = IP(dst=host)/TCP(sport=src_port, dport=port, flags="R")
                # send(rst_pkt, verbose=0)
                return "open"
            elif response[TCP].flags == 0x14 or response[TCP].flags == 0x04: # RST-ACK or RST
                return "closed"
            else: # Other flags
                return f"filtered (flags: {response[TCP].flags:#04x})"
        elif response.haslayer(ICMP):
            # ICMP unreachable (type 3, code 1, 2, 3, 9, 10, or 13)
            if int(response[ICMP].type) == 3 and int(response[ICMP].code) in [1, 2, 3, 9, 10, 13]:
                return "filtered (ICMP)"
            else:
                return "filtered (ICMP other)"
        else:
            return "filtered (unknown response)"
            
    except PermissionError:
        # This will likely be caught earlier by SCAPY_AVAILABLE check if run as non-root
        print(f"[!] Permission denied for SYN scan on {host}:{port}. Try running as root/administrator.")
        return "error (permission)"
    except Exception as e:
        # print(f"[!] Error SYN scanning {host}:{port}: {e}") # Can be verbose
        return "error"


def get_service_banner(host, port, timeout=2):
    """Tries to grab a service banner from an open TCP port."""
    banner = "unknown"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            # For HTTP, send a basic request. For others, just try to receive.
            if port == 80 or port == 8080:
                s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            elif port == 443: # Basic SSL/TLS handshake often reveals server type
                 s.sendall(b"\x16\x03\x01\x00\x88\x01\x00\x00\x84\x03\x03") # ClientHello start
            
            # Try to receive a small amount of data
            # Be careful with large banners or services that wait for client input
            banner_data = s.recv(1024)
            try:
                banner = banner_data.decode('utf-8', errors='ignore').strip().split('\n')[0]
                banner = ''.join(c for c in banner if c.isprintable()) # Clean non-printable
                if not banner: banner = "(empty response)"
            except:
                banner = "(binary data)"

    except socket.timeout:
        banner = "(banner grab timeout)"
    except ConnectionRefusedError:
        banner = "(connection refused for banner)" # Should not happen if port reported open
    except Exception:
        banner = "(banner grab error)"
    return banner

# --- Main Logic ---

def main():
    parser = argparse.ArgumentParser(
        description="NetScan Pro - Python-Based Network Scanner",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Example Usage:
  python netscan_pro.py -t 192.168.1.1 -p 22,80,443 -sT -sV
  python netscan_pro.py -t 192.168.1.0/24 -sn  (ICMP Ping Sweep)
  python netscan_pro.py -t 192.168.1.1-192.168.1.10 --top-ports 10 -sS (SYN Scan, requires root)
  python netscan_pro.py --arp-scan 192.168.1.0/24 (ARP Scan for local net, requires root)
  python netscan_pro.py -t scanme.nmap.org -p 1-100 -sT -oJ results.json

Disclaimer:
  This tool is for educational purposes and authorized scanning only.
  Unauthorized scanning is illegal and unethical. Use responsibly.
"""
    )
    # Target Specification
    parser.add_argument("-t", "--targets", required=False, help="Target IP, hostname, CIDR, or comma-separated list (e.g., 192.168.1.1,192.168.1.0/24,example.com)")
    parser.add_argument("--target-file", help="File containing a list of targets, one per line.")

    # Scan Type
    scan_type_group = parser.add_argument_group('Scan Types')
    scan_type_group.add_argument("-sn", "--ping-scan", action="store_true", help="Host discovery only (ICMP Ping). No port scan.")
    scan_type_group.add_argument("--arp-scan", metavar="NETWORK_CIDR", help="ARP scan for live hosts on the local network (e.g., 192.168.1.0/24). Requires root. Overrides -t for host discovery if local.")
    scan_type_group.add_argument("-sT", "--tcp-connect-scan", action="store_true", help="TCP Connect Scan (default if no scan type specified and not -sn)")
    scan_type_group.add_argument("-sS", "--tcp-syn-scan", action="store_true", help="TCP SYN (Stealth) Scan (requires root/admin & Scapy)")
    # parser.add_argument("-sU", "--udp-scan", action="store_true", help="UDP Scan (can be slow and less reliable)") # Not implemented yet

    # Port Specification
    port_group = parser.add_argument_group('Port Specification')
    port_group.add_argument("-p", "--ports", default="1-1024", help="Ports to scan (e.g., 22,80,443 or 1-1024 or 'all'). Default: 1-1024.")
    port_group.add_argument("--top-ports", type=int, metavar="N", help="Scan the top N most common TCP ports.")


    # Service and Version
    parser.add_argument("-sV", "--service-version", action="store_true", help="Attempt service and version detection (basic banner grabbing).")

    # Performance
    performance_group = parser.add_argument_group('Performance')
    performance_group.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Timeout for probes in seconds (default: {DEFAULT_TIMEOUT})")
    performance_group.add_argument("--threads", type=int, default=DEFAULT_THREADS, help=f"Number of concurrent threads (default: {DEFAULT_THREADS})")

    # Output
    output_group = parser.add_argument_group('Output')
    output_group.add_argument("-oJ", "--output-json", metavar="FILENAME", help="Output results in JSON format to a file.")
    # output_group.add_argument("-oN", "--output-normal", metavar="FILENAME", help="Output results in Normal format to a file.") # For text file
    # output_group.add_argument("-oX", "--output-xml", metavar="FILENAME", help="Output results in XML format to a file.") # More complex
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output (show closed/filtered ports).")

    args = parser.parse_args()

    # --- Argument Validation and Processing ---
    if not args.targets and not args.target_file and not args.arp_scan:
        parser.error("No targets specified. Use -t, --target-file, or --arp-scan.")

    # Default to TCP Connect scan if no scan type is given and not a ping scan
    if not args.ping_scan and not args.tcp_connect_scan and not args.tcp_syn_scan and not args.arp_scan:
        args.tcp_connect_scan = True # Make TCP Connect the default port scan

    if args.tcp_syn_scan and not SCAPY_AVAILABLE:
        print("[!] TCP SYN Scan (-sS) requires Scapy. Please install it or choose another scan type.")
        sys.exit(1)
    if args.ping_scan and not SCAPY_AVAILABLE and not args.arp_scan: # ARP scan can discover without ICMP
        print("[!] ICMP Ping Scan (-sn) requires Scapy for best results. Please install it.")
        # Could allow it to proceed with a warning if we had a TCP-ping alternative for -sn
        # sys.exit(1)

    all_targets = []
    if args.targets:
        all_targets.extend(expand_targets(args.targets))
    if args.target_file:
        try:
            with open(args.target_file, 'r') as f:
                file_targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                all_targets.extend(expand_targets(",".join(file_targets))) # Process through expand_targets for consistency
        except FileNotFoundError:
            print(f"[!] Target file not found: {args.target_file}")
            sys.exit(1)
    
    # Remove duplicates
    all_targets = sorted(list(set(all_targets)))


    if not all_targets and not args.arp_scan:
        print("[!] No valid targets to scan after processing inputs.")
        sys.exit(0)

    ports_to_scan = []
    if not args.ping_scan and not args.arp_scan: # Only parse ports if we're doing a port scan
         ports_to_scan = parse_ports(args.ports if args.ports else "", args.top_ports)
         if not ports_to_scan:
             print("[!] No ports specified or parsed correctly for scanning.")
             sys.exit(1)

    scan_results = {} # Store results: { "host": { "status": "up/down", "ports": [ {port, state, service} ] } }
    start_time = datetime.now()
    print(f"[*] NetScan Pro starting at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")


    # --- Host Discovery Phase ---
    live_hosts = []
    if args.arp_scan:
        if not SCAPY_AVAILABLE:
            print("[!] ARP Scan requires Scapy and usually root privileges. Aborting ARP scan.")
        else:
            try:
                # Check if current user is root (simplistic check for Linux/macOS)
                import os
                if os.geteuid() != 0 and sys.platform != "win32": # Not root and not Windows
                     print("[!] ARP Scan (-arp-scan) typically requires root/administrator privileges.")
                     # Optionally exit or just warn
            except AttributeError: # os.geteuid() not available on Windows
                pass
            except ImportError: # os module not available (highly unlikely)
                pass

            print(f"[*] Initiating ARP scan for {args.arp_scan}...")
            live_hosts = arp_scan_local(args.arp_scan, args.timeout)
            # If ARP scan is primary, other targets might be ignored or handled separately
            # For now, we'll use ARP discovered hosts if any, otherwise proceed with -t targets
            if not live_hosts and all_targets:
                print("[i] ARP scan found no hosts. Proceeding with ICMP ping for specified targets (if any).")
            elif live_hosts:
                print(f"[*] ARP Scan complete. Found {len(live_hosts)} live host(s).")
                # If ARP scan is done, we might not need to ICMP ping these.
                # For simplicity now, if ARP scan is specified, its results are the primary live_hosts.
                # If -t was also given, those will be ICMP pinged unless they were found by ARP.
                discovered_by_arp = set(live_hosts)
                remaining_targets_for_ping = [t for t in all_targets if t not in discovered_by_arp]
                
                # Add ARP discovered hosts to scan_results
                for host_ip in live_hosts:
                    scan_results[host_ip] = {"status": "up (ARP)", "ports": []}

                if remaining_targets_for_ping:
                    print(f"[*] Performing ICMP Ping for remaining {len(remaining_targets_for_ping)} target(s) specified with -t...")
                    with ThreadPoolExecutor(max_workers=args.threads) as executor:
                        future_to_host = {executor.submit(icmp_ping, target, args.timeout): target for target in remaining_targets_for_ping}
                        for future in as_completed(future_to_host):
                            host = future_to_host[future]
                            try:
                                if future.result():
                                    print(f"    [+] Host Found (ICMP): {host}")
                                    live_hosts.append(host)
                                    scan_results[host] = {"status": "up (ICMP)", "ports": []}
                                else:
                                    scan_results[host] = {"status": "down (ICMP)", "ports": []}
                            except Exception as e:
                                print(f"[!] Error pinging {host}: {e}")
                                scan_results[host] = {"status": f"error pinging ({e})", "ports": []}
                all_targets = list(set(live_hosts + remaining_targets_for_ping)) # Update all_targets for port scanning phase
            else: # No ARP specified, or ARP found nothing and no -t targets
                 pass # Continue to normal ICMP ping if all_targets exist
        
    if not args.arp_scan or (args.arp_scan and not live_hosts and all_targets): # If no ARP scan, or ARP failed and we have -t targets
        if all_targets:
            print(f"[*] Initiating ICMP Ping scan for {len(all_targets)} target(s)...")
            ping_targets_to_scan = [t for t in all_targets if t not in live_hosts] # Avoid re-pinging ARP found hosts

            if ping_targets_to_scan:
                with ThreadPoolExecutor(max_workers=args.threads) as executor:
                    future_to_host = {executor.submit(icmp_ping, target, args.timeout): target for target in ping_targets_to_scan}
                    for future in as_completed(future_to_host):
                        host = future_to_host[future]
                        try:
                            if future.result():
                                print(f"    [+] Host Found (ICMP): {host}")
                                live_hosts.append(host)
                                scan_results[host] = {"status": "up (ICMP)", "ports": []}
                            else:
                                if args.verbose: print(f"    [-] Host Appears Down (ICMP): {host}")
                                scan_results[host] = {"status": "down (ICMP)", "ports": []}
                        except Exception as e:
                            print(f"[!] Error pinging {host}: {e}")
                            scan_results[host] = {"status": f"error pinging ({e})", "ports": []}
            live_hosts = sorted(list(set(live_hosts))) # Ensure unique and sorted
            print(f"[*] ICMP Ping scan complete. Found {len(live_hosts)} live host(s).")


    if args.ping_scan: # If it's just a host discovery scan
        print("\n[*] Host Discovery Results:")
        for host, data in scan_results.items():
            if "up" in data["status"]: # Check if status contains "up"
                 print(f"    {host} is {data['status']}")
        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(scan_results, f, indent=4)
            print(f"\n[+] Results saved to {args.output_json}")
        end_time = datetime.now()
        print(f"\n[*] NetScan Pro finished in {end_time - start_time}")
        sys.exit(0)

    if not live_hosts:
        print("\n[!] No live hosts found. Aborting port scan.")
        sys.exit(0)

    # --- Port Scanning Phase ---
    print(f"\n[*] Initiating port scan on {len(live_hosts)} live host(s) for {len(ports_to_scan)} port(s) per host.")
    
    # Determine scan function
    scan_function = None
    scan_type_str = ""
    if args.tcp_syn_scan:
        scan_function = scan_tcp_syn
        scan_type_str = "TCP SYN"
        if not SCAPY_AVAILABLE: # Should have been caught earlier, but double check
            print("[!] Cannot perform SYN scan without Scapy. Exiting.")
            sys.exit(1)
        try: # Check for root/admin for SYN scan
            import os
            if os.geteuid() != 0 and sys.platform != "win32":
                 print("[!] TCP SYN Scan (-sS) typically requires root/administrator privileges.")
                 # continue or exit
        except AttributeError: pass # Windows
        except ImportError: pass


    elif args.tcp_connect_scan:
        scan_function = scan_tcp_connect
        scan_type_str = "TCP Connect"
    else:
        print("[!] No valid port scan type specified. Defaulting to TCP Connect Scan.")
        scan_function = scan_tcp_connect # Fallback
        scan_type_str = "TCP Connect (Fallback)"

    print(f"[*] Using {scan_type_str} scan type.")

    total_ports_to_scan_overall = len(live_hosts) * len(ports_to_scan)
    scanned_count = 0

    for host in live_hosts: # Iterate through hosts sequentially for clarity, ports concurrently
        if scan_results.get(host, {}).get("status", "down").startswith("down"): # Skip hosts marked as down
            if args.verbose: print(f"[-] Skipping port scan for {host} (marked as down).")
            continue

        print(f"\n[*] Scanning {host}...")
        open_ports_on_host = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_port = {
                executor.submit(scan_function, host, port, args.timeout): port for port in ports_to_scan
            }
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                scanned_count += 1
                progress = (scanned_count / total_ports_to_scan_overall) * 100
                sys.stdout.write(f"\r    Progress: {progress:.2f}% ({scanned_count}/{total_ports_to_scan_overall} host-port pairs) ")
                sys.stdout.flush()
                try:
                    status = future.result()
                    if status == "open":
                        service_info = {"port": port, "status": status, "service": "unknown", "banner": ""}
                        if args.service_version:
                            banner = get_service_banner(host, port, args.timeout)
                            service_info["banner"] = banner
                            # Basic service name from common ports
                            service_info["service"] = COMMON_TCP_PORTS.get(port, "unknown")
                        open_ports_on_host.append(service_info)
                        print(f"\r    [+] {host}:{port}/tcp {status.ljust(10)} {service_info['service']} {service_info['banner'][:50]}{'...' if len(service_info['banner']) > 50 else ''}")
                    elif args.verbose and status not in ["error (scapy unavailable)", "error (permission)"]: # Don't flood with scapy errors
                        print(f"\r    [-] {host}:{port}/tcp {status.ljust(10)}")

                except Exception as e:
                    if args.verbose: print(f"\r    [!] Error scanning {host}:{port}: {e}")
        
        if host in scan_results:
             scan_results[host]["ports"] = sorted(open_ports_on_host, key=lambda x: x['port'])
        else: # Should not happen if host discovery ran correctly
             scan_results[host] = {"status": "unknown", "ports": sorted(open_ports_on_host, key=lambda x: x['port'])}
        
        # Ensure a newline after progress bar and port results for this host
        sys.stdout.write("\r" + " " * 80 + "\r") # Clear the progress line
        sys.stdout.flush()
        if not open_ports_on_host and not args.verbose:
            print(f"    No open ports found on {host} (or not verbose enough to show others).")


    # --- Output Results ---
    print("\n\n--- Scan Summary ---")
    for host, data in scan_results.items():
        if "up" not in data.get("status", "down"): # Skip hosts that were down or error
            if args.verbose: print(f"{host}: Status {data.get('status', 'unknown')}")
            continue

        print(f"\nHost: {host} ({data.get('status', 'unknown')})")
        if data.get("ports"):
            print("  PORT     STATE   SERVICE    BANNER")
            for p_info in data["ports"]:
                banner_snip = p_info.get('banner', '')[:40]
                if len(p_info.get('banner', '')) > 40: banner_snip += "..."
                print(f"  {str(p_info['port']).ljust(7)} {p_info['status'].ljust(7)} {p_info.get('service', 'unknown').ljust(10)} {banner_snip}")
        else:
            if data.get("status", "").startswith("up"): # Only say "no open ports" if host was up
                print("  No open ports found (or service detection disabled for closed ports).")

    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(scan_results, f, indent=4)
        print(f"\n[+] Full results saved to {args.output_json}")

    end_time = datetime.now()
    print(f"\n[*] NetScan Pro finished in {end_time - start_time}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user. Exiting.")
        sys.exit(1)
    except PermissionError as e:
        # This might catch if Scapy's raw socket operations are attempted without root
        # outside of the specific Scapy functions where it's handled.
        print(f"\n[!] A PermissionError occurred: {e}")
        print("[!] Some operations (like SYN scans or raw pings) require root/administrator privileges.")
        print("[!] Try running the script with 'sudo' (on Linux/macOS) or as Administrator (on Windows).")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)