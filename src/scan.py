import subprocess
import random 
from typing import List, Dict, Any  
from conf import TIMEOUT, USER_AGENTS 

class CmdExec: 
    def __init__(self, cmd, timeout=TIMEOUT): 
        self.cmd = cmd
        self.timeout = timeout
        self.process = None
    
    def execute(self): 
        try:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, text=True)
            stdout, stderr = self.process.communicate(timeout=self.timeout)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": self.process.returncode
            }
        except subprocess.TimeoutExpired:
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    if self.process:
                        self.process.kill()
            return {
                "stdout": "",
                "stderr": f"Error: timed out after {self.timeout} seconds",
                "returncode": -1
            }

def nmap_execute(args: List[str]) -> Dict[str, Any]:
    nmap_cmd = ["nmap"] + args
    if not args or args[-1].strip() == "":
        return {"error": "No target specified for Nmap scan"} 
    try:
        cmd_exec = CmdExec(nmap_cmd)
        return cmd_exec.execute()
    except Exception as e:
        return {"error": f"Error executing Nmap: {e}"}
    
def validate_ports(ports: str) -> bool:
    if not ports:
        return True
    try:
        for part in ports.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                if start < 1 or end > 65535 or start > end:
                    return False 
            else:
                port = int(part)
                if port < 1 or port > 65535:
                    return False
        return True
    except ValueError:
        return False


def curl_execute(args: List[str]) -> Dict[str, Any]:
    curl_cmd = ["curl", "-A", random.choice(USER_AGENTS), *args]  
    try:
        cmd_exec = CmdExec(curl_cmd)
        return cmd_exec.execute()
    except Exception as e:
        return {"error": f"Error executing curl: {e}"}

def whatweb_execute(args: List[str]) -> Dict[str, Any]:
    whatweb_cmd = ["whatweb"] + args
    if not args or args[-1].strip() == "":
        return {"error": "No target specified for WhatWeb scan"}
    try:
        cmd_exec = CmdExec(whatweb_cmd)
        return cmd_exec.execute()
    except Exception as e:
        return {"error": f"Error executing WhatWeb: {e}"}
