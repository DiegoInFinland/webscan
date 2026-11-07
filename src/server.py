from mcp.server.fastmcp import FastMCP 
import logging
import sys
from scan import curl_execute, nmap_execute, validate_ports, whatweb_execute
from typing import Dict, Any, List 

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
logging.getLogger("mcp").setLevel(logging.WARNING)
mcp = FastMCP('nmap-scanner')

# Deny list of file output flags (not needed since results are returned as JSON)
DENY_FLAGS = {
    "-oN", "-oX", "-oG", "-oS", "-oA", "--output-xml"
}


@mcp.tool()
def local_ip() -> Dict[str, Any]:
    """Checks local IP in the current container.  
    Returning the results as a JSON object of the current network interfaces and routing table. 
    Ultimately showing the local IP addresses and network configuration.
    
    Returns:
        Dict[str, Any]: A dictionary containing the results of the local IP check.

    """ 
    return nmap_execute(["--iflist"])

@mcp.tool()
def ping_scan(target: str, disable_arp_ping: bool = False) -> Dict[str, Any]:
    """Performs a ping scan on the specified target, returning the results as a JSON object. 

    Args:
        target (str): The target to ping (e.g., IP address or hostname).
        disable_arp_ping (bool): Disable ARP ping for containerized Mac environments. Defaults to False.
    Returns:
        Dict[str, Any]: A dictionary containing the results of the ping scan.
    """
    args = ["-sn"]
    if disable_arp_ping:
        args.append("--disable-arp-ping")
    args.extend(["-R", "-PE", target])
    return nmap_execute(args)

@mcp.tool()
def ping6_scan(target: str) -> Dict[str, Any]:
    """Performs a ping scan on the specified IPv6 target, returning the results as a JSON object.
    Please, be aware that ipv6 networks are significantly larger than ipv4.
    It is always preferable to specify a single target or a small range of addresses to avoid long scan times.
    Avoid scanning large ipv6 subnets (e.g., /64 or larger) as it may lead to extremely long scan times and potential performance issues.

    Args:
        target (str): The IPv6 target to ping (e.g., IPv6 address or hostname).
    Returns:
        Dict[str, Any]: A dictionary containing the results of the ping scan.
    """
    return nmap_execute(["-6", "-sn", "-R", target])

@mcp.tool()
def nmap_scan(target: str, flags: str="", ports: str="") -> Dict[str, Any]:
    """Executes an Nmap scan on the specified target with optional flags and ports, returning the results as a JSON object.

    Args:
        target (str): The target to scan (e.g., IP address or hostname).
        flags (str, optional): Additional Nmap flags to include in the scan. Defaults to "".
        ports (str, optional): Specific ports to scan (e.g., "80,443"). Defaults to "".

    Returns:
        Dict[str, Any]: A dictionary containing the results of the Nmap scan.
    """
    args = []
    if flags:
        flag_list = flags.split()
        # Check for dangerous flags
        for flag in flag_list:
            if flag in DENY_FLAGS:
                return {"error": f"Dangerous flag '{flag}' is not allowed"}
        args.extend(flag_list)
    if ports:
        if not validate_ports(ports):
            return {"error": "Invalid ports specified"}
        args.extend(["-p", ports])
    args.append(target)
    return nmap_execute(args) 

@mcp.tool()
def curl_request(flags: List[str], url: str) -> Dict[str, Any]:
    """Executes a curl request to the specified URL, returning the results as a JSON object.

    Args:
        flags (List[str]): Additional curl flags to include in the request.
        url (str): The URL to send the curl request to.
    Returns:
        Dict[str, Any]: A dictionary containing the results of the curl request.
    """
    return curl_execute(flags + [url])

@mcp.tool()
def whatweb_scan(flags: List[str], url: str) -> Dict[str, Any]:
    """Executes WhatWeb against the specified URL, returning the results as a JSON object.

    Args:
        flags (List[str]): Additional WhatWeb flags to include in the request.
        url (str): The URL or target to fingerprint.
    Returns:
        Dict[str, Any]: A dictionary containing the results of the WhatWeb scan.
    """
    return whatweb_execute(flags + [url])

if __name__ == "__main__": 
    mcp.run(transport="stdio")  

    
