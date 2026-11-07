---
name: webscan
description: Professional network reconnaissance and port scanning. Use when the user needs to scan a certain IP or DNS for open ports, service versions, OS fingerprints, networks among other details on a target IP or hostname. Or when the user explicitly asks for it. Scans can use IPv4 or IPv6. Aditionally, curl requests can be made to a specific URL with optional flags. The skill is designed to be used in a controlled and ethical manner, ensuring that scans are performed only on authorized targets.
---

# Nmap Operational Workflow

## PHASE 0: ENVIRONMENT CHECK (PAUSE AFTER THIS)

- **Action:** Immediately run `local_ip` to identify the LAN IP/Subnet the container is running on.
- **Action:** Proceed to show current IP to the user.
- **Action:** Ask the user how to proceed, given the identified IP and the fact that on Mac or Windows the container runs inside a VM, not the actual host's ip, so scanning the LAN might not work as expected. If they want to scan their actual LAN, they should provide the correct IP/Subnet to scan.

## PHASE 1: DISCOVERY (PAUSE AFTER THIS)

- Use `ping_scan` or `ping6_scan` on the identified LAN subnet (e.g., `nmap -sn 192.168.1.0/24`).
  - If the host OS/container setup is unknown, ask whether the MCP server is running in Docker on Mac before starting IPv4 discovery.
  - For IPv4 discovery from a Mac-hosted container, call `ping_scan(target, disable_arp_ping=True)` because ARP ping may not work correctly from inside the container.
  - For Linux/native host networking, call `ping_scan(target)` and leave `disable_arp_ping` unset unless the user explicitly requests otherwise; ARP ping is usually the most reliable local-network discovery method there.
  - For IPv6 discovery, use `ping6_scan`; ARP is IPv4-only, so do not try to apply `disable_arp_ping` to IPv6 scans.
- **CRITICAL:** Once discovery is complete, you MUST stop and report:
  1. The local IP and subnet detected. Remember, nmap runs on a Docker container, so the local IP may not be the actual host's LAN IP.
  2. Number of live hosts found.
  3. A list of those IP addresses.
- **STOP:** Do not proceed. You must explicitly ask: _"I have found [X] live hosts. Which specific IPs should I proceed to scan for ports and services?"_

## PHASE 2: TARGETED SCANNING (REQUIRES PERMISSION)

- Only scan targets explicitly selected by the user in Phase 1.
- **Tool:** Use `nmap_scan`, which allows for custom flags and options.
- **Tool:** Use `curl_request` for specific HTTP requests to a URL with optional flags.
- **Default Flags:** `-sS -sV -T3 --open`.
- **Aggressive Flags:** If you intend to use `-A`, `-T4`, or `--script vuln`

# Operational Guardrails

- **Host Networking:** Since running in `--network host`, be aware that scans originate directly from the host's IP.
- **No Chaining:** Never "auto-start" Phase 2 after Phase 1. The transition requires human approval.
- **Results Analysis:** After `nmap_scan`, `curl_request` or `whatweb_scan` finishes, summarize the open ports and ask: _"How do you want to proceed?"_
- **CRITICAL:** `local_ip`, only works on Linux hosts. If the user is on Mac or Windows, the container runs inside a VM and `local_ip` will return the VM's IP, not the host's actual LAN IP. In this case, you must ask the user to provide the correct IP/Subnet to scan their LAN.
