from unittest.mock import patch, MagicMock
import subprocess
from scan import nmap_execute, CmdExec, validate_ports, whatweb_execute
from server import nmap_scan, ping_scan, ping6_scan, whatweb_scan

def test_nmap_execute_returns_stdout_stderr_returncode():
    with patch("scan.subprocess.Popen") as mock_popen:
        proc = MagicMock()
        proc.communicate.return_value = ("nmap output", "")
        proc.returncode = 0
        mock_popen.return_value = proc

        result = nmap_execute(["127.0.0.1"])

        assert result == {"stdout": "nmap output", "stderr": "", "returncode": 0}
        mock_popen.assert_called_once_with(
            ["nmap", "127.0.0.1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
        )


def test_nmap_execute_empty_target():
    result = nmap_execute([""])
    assert result == {"error": "No target specified for Nmap scan"}


def test_nmap_execute_empty_list():
    result = nmap_execute([])
    assert result == {"error": "No target specified for Nmap scan"}


def test_nmap_execute_timeout():
    with patch("scan.subprocess.Popen") as mock_popen:
        proc = MagicMock()
        proc.communicate.side_effect = subprocess.TimeoutExpired(cmd="nmap", timeout=300)
        mock_popen.return_value = proc

        result = nmap_execute(["scanme.nmap.org"])

        assert result == {"stdout": "", "stderr": "Error: timed out after 300 seconds", "returncode": -1}


def test_nmap_execute_unexpected_error():
    with patch("scan.subprocess.Popen") as mock_popen:
        mock_popen.side_effect = Exception("nmap not found")

        result = nmap_execute(["scanme.nmap.org"])

        assert result == {"error": "Error executing Nmap: nmap not found"}


def test_whatweb_execute_returns_stdout_stderr_returncode():
    with patch("scan.subprocess.Popen") as mock_popen:
        proc = MagicMock()
        proc.communicate.return_value = ("whatweb output", "")
        proc.returncode = 0
        mock_popen.return_value = proc

        result = whatweb_execute(["https://example.com"])

        assert result == {"stdout": "whatweb output", "stderr": "", "returncode": 0}
        mock_popen.assert_called_once_with(
            ["whatweb", "https://example.com"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
        )


def test_whatweb_execute_empty_target():
    result = whatweb_execute([""])
    assert result == {"error": "No target specified for WhatWeb scan"}


def test_whatweb_scan_with_flags():
    with patch("server.whatweb_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = whatweb_scan(flags=["--no-errors"], url="https://example.com")

        mock_exec.assert_called_once_with(["--no-errors", "https://example.com"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_nmap_scan_bare_target():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = nmap_scan(target="127.0.0.1")

        mock_exec.assert_called_once_with(["127.0.0.1"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_nmap_scan_with_flags():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = nmap_scan(target="scanme.nmap.org", flags="-sV -O")

        mock_exec.assert_called_once_with(["-sV", "-O", "scanme.nmap.org"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_nmap_scan_with_ports():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = nmap_scan(target="192.168.1.1", ports="80,443")

        mock_exec.assert_called_once_with(["-p", "80,443", "192.168.1.1"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_nmap_scan_with_flags_and_ports():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = nmap_scan(target="10.0.0.1", flags="-A -T4", ports="22,80,443")

        mock_exec.assert_called_once_with(["-A", "-T4", "-p", "22,80,443", "10.0.0.1"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_ping_scan():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = ping_scan(target="192.168.1.0/24")
        mock_exec.assert_called_once_with(["-sn", "-R", "-PE", "192.168.1.0/24"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_ping_scan_with_disable_arp_ping():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = ping_scan(target="192.168.1.0/24", disable_arp_ping=True)

        mock_exec.assert_called_once_with(["-sn", "--disable-arp-ping", "-R", "-PE", "192.168.1.0/24"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_ping6_scan():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = ping6_scan(target="2001:db8::1")

        mock_exec.assert_called_once_with(["-6", "-sn", "-R", "2001:db8::1"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_validate_ports_single():
    assert validate_ports("80") is True


def test_validate_ports_list():
    assert validate_ports("80,443,8080") is True


def test_validate_ports_range():
    assert validate_ports("1-1000") is True


def test_validate_ports_mixed():
    assert validate_ports("80,443,8000-9000") is True


def test_validate_ports_empty():
    assert validate_ports("") is True


def test_validate_ports_invalid_string():
    assert validate_ports("abc") is False


def test_validate_ports_zero():
    assert validate_ports("0") is False


def test_validate_ports_too_high():
    assert validate_ports("65536") is False


def test_validate_ports_range_invalid_start():
    assert validate_ports("0-100") is False


def test_validate_ports_range_invalid_end():
    assert validate_ports("1-65536") is False


def test_validate_ports_range_reversed():
    assert validate_ports("100-50") is False


def test_nmap_scan_with_port_range():
    with patch("server.nmap_execute") as mock_exec:
        mock_exec.return_value = {"stdout": "", "stderr": "", "returncode": 0}

        result = nmap_scan(target="10.0.0.1", ports="1-1000")

        mock_exec.assert_called_once_with(["-p", "1-1000", "10.0.0.1"])
        assert result == {"stdout": "", "stderr": "", "returncode": 0}


def test_nmap_scan_invalid_ports_rejected():
    with patch("server.nmap_execute") as mock_exec:
        result = nmap_scan(target="10.0.0.1", ports="abc")
        assert result == {"error": "Invalid ports specified"}
        mock_exec.assert_not_called()


def test_cmdexec_execute_returns_dict():
    with patch("scan.subprocess.Popen") as mock_popen:
        proc = MagicMock()
        proc.communicate.return_value = ("output", "error")
        proc.returncode = 1
        mock_popen.return_value = proc

        cmd = CmdExec(["nmap", "127.0.0.1"])
        result = cmd.execute()

        assert result == {"stdout": "output", "stderr": "error", "returncode": 1}
