#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE VULNERABILITY SCANNER
Analyzes all possible vulnerabilities an attacker could exploit
Features:
- Port scanning with service detection
- CVE lookup for discovered services
- Web vulnerability testing (SQLi, XSS, LFI, etc.)
- SSL/TLS analysis
- Security header checking
- Directory/file enumeration
- Detailed vulnerability reports
"""

import os
import sys
import socket
import ssl
import time
import json
import hashlib
import threading
import queue
import ipaddress
import subprocess
import re
import codecs
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from urllib.parse import urlparse, urljoin
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try importing optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
    print("✅ Requests module loaded")
except ImportError as e:
    REQUESTS_AVAILABLE = False
    print(f"❌ Requests module not available: {e}")
    print("   Install with: pip install requests")

try:
    from scapy.all import IP, TCP, sr1, conf
    SCAPY_AVAILABLE = True
    print("✅ Scapy module loaded")
except ImportError as e:
    SCAPY_AVAILABLE = False
    print(f"⚠️ Scapy module not available: {e}")
    print("   Install with: pip install scapy (optional)")

# ANSI color codes for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class VulnerabilityScanner:
    def __init__(self):
        self.target = None
        self.target_ip = None
        self.target_hostname = None
        self.ports = []
        self.open_ports = []
        self.vulnerabilities = []
        self.web_vulnerabilities = []
        self.ssl_info = {}
        self.security_headers = {}
        self.directories_found = []
        self.scan_start_time = None
        self.scan_end_time = None
        
        # Common ports to scan
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 
            995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9090, 9200, 27017
        ]
        
        # Common directories to check for web servers
        self.common_dirs = [
            "admin", "backup", "backups", "config", "css", "data", "db", 
            "database", "files", "images", "img", "includes", "js", "logs", 
            "old", "private", "restore", "sql", "src", "temp", "test", 
            "tests", "tmp", "uploads", "www", "wp-admin", "wp-content", 
            "wp-includes", ".git", ".svn", ".env", "phpinfo.php", "info.php", 
            "test.php", "php.ini", ".htaccess", "backup.zip", "backup.tar.gz",
            "dump.sql", "database.sql", "db.sql", "config.php", "config.bak"
        ]
        
        # SQL injection test payloads
        self.sqli_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' #",
            "admin' --",
            "admin' #",
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "1' AND '1'='1",
            "1' AND '1'='2",
            "1' ORDER BY 1--",
            "1' ORDER BY 100--"
        ]
        
        # XSS test payloads
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "\"><script>alert('XSS')</script>",
            "'><script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]
        
        # CVE database (simplified - in real tool, would query online APIs)
        self.cve_database = {
            "Apache httpd 2.4.49": ["CVE-2021-41773 (Path Traversal)", "CVE-2021-42013 (RCE)"],
            "Apache httpd 2.4.50": ["CVE-2021-42013 (RCE)"],
            "OpenSSH 7.2p2": ["CVE-2016-6210 (User Enumeration)", "CVE-2018-15473 (User Enumeration)"],
            "OpenSSH 7.4": ["CVE-2018-15919 (Remote Code Execution)"],
            "nginx 1.20.0": ["CVE-2021-23017 (Request Smuggling)"],
            "vsftpd 2.3.4": ["CVE-2011-2523 (Backdoor Command Execution)"],
            "ProFTPD 1.3.5": ["CVE-2015-3306 (File Copy Vulnerability)"],
            "MySQL 5.5.5": ["CVE-2012-2122 (Authentication Bypass)"],
            "Redis 2.8.13": ["CVE-2015-4335 (Unauthenticated Access)"],
            "PHP 5.6.40": ["CVE-2019-11043 (Remote Code Execution)"],
            "PHP 7.3.11": ["CVE-2019-11043 (Remote Code Execution)"],
            "WordPress 4.9.6": ["CVE-2018-6389 (Dos Vulnerability)"],
            "WordPress 5.0.3": ["CVE-2019-9787 (CSRF)"]
        }
        
    # ==================== UTILITY FUNCTIONS ====================
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Print tool banner"""
        banner = f"""
{Colors.RED}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║         COMPREHENSIVE VULNERABILITY SCANNER v2.0          ║
║     Analyzes all possible entry points for attackers      ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """
        print(banner)
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🔍 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    
    def print_success(self, message):
        """Print success message in green"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        """Print error message in red"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_warning(self, message):
        """Print warning message in yellow"""
        print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
    
    def print_info(self, message):
        """Print info message in blue"""
        print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
    
    def print_prompt(self, message):
        """Print prompt in purple"""
        print(f"{Colors.PURPLE}{message}{Colors.END}", end="")
    
    def print_vulnerability(self, message, severity="MEDIUM"):
        """Print vulnerability with severity color"""
        severity_colors = {
            "CRITICAL": Colors.RED + Colors.BOLD,
            "HIGH": Colors.RED,
            "MEDIUM": Colors.YELLOW,
            "LOW": Colors.BLUE,
            "INFO": Colors.GREEN
        }
        color = severity_colors.get(severity.upper(), Colors.YELLOW)
        print(f"{color}🔓 VULNERABILITY: {message}{Colors.END}")
    
    # ==================== TARGET RESOLUTION ====================
    
    def resolve_target(self, target: str) -> bool:
        """Resolve target to IP address"""
        try:
            # Remove http:// or https:// if present
            target = target.replace('http://', '').replace('https://', '').split('/')[0]
            
            # Check if it's an IP
            try:
                self.target_ip = str(ipaddress.ip_address(target))
                self.target_hostname = target
                self.target = target
                return True
            except:
                # Try to resolve hostname
                self.target_ip = socket.gethostbyname(target)
                self.target_hostname = target
                self.target = target
                return True
        except socket.gaierror as e:
            self.print_error(f"Could not resolve target: {e}")
            return False
        except Exception as e:
            self.print_error(f"Error resolving target: {e}")
            return False
    
    # ==================== PORT SCANNING ====================
    
    def scan_port(self, ip: str, port: int, timeout: float = 2.0) -> Tuple[bool, str]:
        """Scan a single TCP port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                # Get service banner
                banner = self.get_service_banner(ip, port)
                sock.close()
                return True, banner
            sock.close()
            return False, ""
        except Exception as e:
            return False, ""
    
    def get_service_banner(self, ip: str, port: int, timeout: float = 3.0) -> str:
        """Attempt to grab service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # Send probe based on port
            if port in [80, 8080, 443, 8443, 8888, 9090]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            elif port == 21:
                # FTP banner is sent immediately
                pass
            elif port == 22:
                # SSH banner is sent immediately
                pass
            elif port == 25:
                sock.send(b"EHLO test.com\r\n")
            elif port == 110:
                sock.send(b"USER test\r\n")
            elif port == 143:
                sock.send(b"a001 LOGIN\r\n")
            elif port == 3306:
                sock.send(b"\x00")
            else:
                sock.send(b"\r\n")
            
            try:
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            except:
                banner = ""
            
            sock.close()
            
            # Clean up banner
            banner = ' '.join(banner.split())
            if len(banner) > 100:
                banner = banner[:100] + "..."
            
            return banner if banner else "No banner"
        except Exception as e:
            return "No banner"
    
    def port_scan(self, ports: List[int] = None, threads: int = 50):
        """Scan multiple ports using threading"""
        if not ports:
            ports = self.common_ports
        
        self.print_info(f"Scanning {len(ports)} ports on {self.target_ip}...")
        
        port_queue = queue.Queue()
        results = []
        
        for port in ports:
            port_queue.put(port)
        
        def worker():
            while not port_queue.empty():
                try:
                    port = port_queue.get_nowait()
                    is_open, banner = self.scan_port(self.target_ip, port)
                    if is_open:
                        results.append({"port": port, "banner": banner})
                        self.print_success(f"Port {port}/TCP is open - {banner}")
                    port_queue.task_done()
                except queue.Empty:
                    break
                except Exception as e:
                    port_queue.task_done()
        
        # Create and start threads
        thread_list = []
        for _ in range(min(threads, len(ports))):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            thread_list.append(t)
        
        # Wait for completion
        for t in thread_list:
            t.join()
        
        self.open_ports = sorted(results, key=lambda x: x['port'])
        
        if self.open_ports:
            self.print_success(f"Found {len(self.open_ports)} open ports")
        else:
            self.print_warning("No open ports found")
        
        return self.open_ports
    
    # ==================== VULNERABILITY DETECTION ====================
    
    def check_cve_vulnerabilities(self):
        """Check for known CVEs based on service banners"""
        self.print_header("CVE VULNERABILITY CHECK")
        
        found_cves = False
        
        for port_info in self.open_ports:
            port = port_info['port']
            banner = port_info['banner']
            
            # Check against CVE database
            for service_pattern, cves in self.cve_database.items():
                if service_pattern.lower() in banner.lower():
                    found_cves = True
                    self.print_vulnerability(f"Port {port}: {banner}", "HIGH")
                    for cve in cves:
                        print(f"   • {cve}")
                    
                    self.vulnerabilities.append({
                        "type": "CVE",
                        "port": port,
                        "service": banner,
                        "cves": cves,
                        "severity": "HIGH"
                    })
        
        if not found_cves:
            self.print_info("No known CVEs detected from banners")
    
    def check_ssl_vulnerabilities(self):
        """Check SSL/TLS vulnerabilities for HTTPS ports"""
        https_ports = [443, 8443, 9443]
        
        for port_info in self.open_ports:
            if port_info['port'] in https_ports:
                self.check_ssl_certificate(port_info['port'])
    
    def check_ssl_certificate(self, port: int):
        """Analyze SSL certificate"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((self.target_ip, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.target_hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    if 'notAfter' in cert:
                        expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if expiry < datetime.now():
                            self.print_vulnerability(f"SSL Certificate EXPIRED on port {port}", "HIGH")
                            self.vulnerabilities.append({
                                "type": "SSL",
                                "port": port,
                                "issue": "Expired certificate",
                                "severity": "HIGH"
                            })
                        else:
                            days_left = (expiry - datetime.now()).days
                            if days_left < 30:
                                self.print_warning(f"SSL certificate expires in {days_left} days on port {port}")
                    
                    # Check cipher
                    cipher = ssock.cipher()
                    if cipher and any(weak in cipher[0].upper() for weak in ['RC4', 'DES', '3DES', 'MD5']):
                        self.print_vulnerability(f"Weak cipher {cipher[0]} on port {port}", "MEDIUM")
                        self.vulnerabilities.append({
                            "type": "SSL",
                            "port": port,
                            "issue": f"Weak cipher: {cipher[0]}",
                            "severity": "MEDIUM"
                        })
        except Exception as e:
            self.print_warning(f"Could not analyze SSL on port {port}: {e}")
    
    def check_anonymous_ftp(self):
        """Check for anonymous FTP access"""
        for port_info in self.open_ports:
            if port_info['port'] == 21:
                try:
                    ftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    ftp.settimeout(5)
                    ftp.connect((self.target_ip, 21))
                    banner = ftp.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Try anonymous login
                    ftp.send(b"USER anonymous\r\n")
                    resp = ftp.recv(1024).decode('utf-8', errors='ignore')
                    
                    if "331" in resp:  # Password required
                        ftp.send(b"PASS anonymous@example.com\r\n")
                        resp = ftp.recv(1024).decode('utf-8', errors='ignore')
                        
                        if "230" in resp:  # Login successful
                            self.print_vulnerability("Anonymous FTP login allowed", "HIGH")
                            self.vulnerabilities.append({
                                "type": "FTP",
                                "port": 21,
                                "issue": "Anonymous login allowed",
                                "severity": "HIGH"
                            })
                    ftp.close()
                except Exception as e:
                    pass
    
    def check_default_credentials(self):
        """Check for default credentials on common services"""
        default_creds = {
            22: [("root", "root"), ("admin", "admin")],  # SSH
            23: [("admin", "admin"), ("root", "1234")],  # Telnet
            3306: [("root", ""), ("root", "root")],      # MySQL
            5432: [("postgres", "postgres")],            # PostgreSQL
            6379: [("", "")],                             # Redis (no auth)
            27017: [("", "")],                            # MongoDB (no auth)
        }
        
        for port_info in self.open_ports:
            if port_info['port'] in default_creds:
                self.print_warning(f"Check default credentials on port {port_info['port']} manually")
                self.vulnerabilities.append({
                    "type": "Default Credentials",
                    "port": port_info['port'],
                    "issue": "May accept default credentials",
                    "severity": "MEDIUM"
                })
    
    # ==================== WEB VULNERABILITY SCANNING ====================
    
    def check_web_vulnerabilities(self):
        """Check for web vulnerabilities on HTTP/HTTPS ports"""
        if not REQUESTS_AVAILABLE:
            self.print_error("Requests module not available. Skipping web vulnerability checks.")
            return
        
        web_ports = [80, 443, 8080, 8443, 8888, 9090]
        
        for port_info in self.open_ports:
            if port_info['port'] in web_ports:
                protocol = "https" if port_info['port'] in [443, 8443] else "http"
                base_url = f"{protocol}://{self.target_hostname}:{port_info['port']}"
                self.scan_web_target(base_url, port_info['port'])
    
    def scan_web_target(self, base_url: str, port: int):
        """Scan a web target for vulnerabilities"""
        self.print_header(f"WEB SCAN: {base_url}")
        
        # Check if web server is responding
        try:
            response = requests.get(base_url, timeout=5, verify=False, allow_redirects=False)
            self.print_info(f"Web server responded with status: {response.status_code}")
            
            # Check security headers
            self.check_security_headers(response.headers, base_url)
            
            # Check for directory listing
            self.check_directory_listing(base_url)
            
            # Directory enumeration
            self.enumerate_directories(base_url)
            
            # Check for SQL injection (simplified)
            self.check_sql_injection(base_url)
            
            # Check for XSS (simplified)
            self.check_xss(base_url)
            
        except requests.exceptions.ConnectionError:
            self.print_warning(f"Could not connect to {base_url}")
        except Exception as e:
            self.print_warning(f"Error scanning {base_url}: {e}")
    
    def check_security_headers(self, headers: Dict, url: str):
        """Check for missing security headers"""
        security_headers = {
            "Strict-Transport-Security": "HSTS missing - allows protocol downgrade",
            "Content-Security-Policy": "CSP missing - allows XSS and data injection",
            "X-Content-Type-Options": "Missing - allows MIME type sniffing",
            "X-Frame-Options": "Missing - allows clickjacking",
            "X-XSS-Protection": "Missing - XSS protection disabled",
            "Referrer-Policy": "Missing - may leak information"
        }
        
        missing = []
        for header, description in security_headers.items():
            if header not in headers:
                missing.append(f"{header}: {description}")
        
        if missing:
            self.print_warning(f"Missing security headers on {url}")
            for issue in missing[:3]:  # Show first 3
                print(f"   • {issue}")
            
            self.vulnerabilities.append({
                "type": "Web",
                "url": url,
                "issue": "Missing security headers",
                "details": missing,
                "severity": "MEDIUM"
            })
    
    def check_directory_listing(self, base_url: str):
        """Check for directory listing vulnerabilities"""
        test_dirs = ["/images/", "/css/", "/js/", "/uploads/", "/backup/", "/admin/"]
        
        for directory in test_dirs:
            url = urljoin(base_url, directory)
            try:
                response = requests.get(url, timeout=3, verify=False)
                if response.status_code == 200:
                    # Check if it looks like a directory listing
                    if "Index of /" in response.text or "Parent Directory" in response.text:
                        self.print_vulnerability(f"Directory listing enabled: {url}", "MEDIUM")
                        self.vulnerabilities.append({
                            "type": "Web",
                            "url": url,
                            "issue": "Directory listing enabled",
                            "severity": "MEDIUM"
                        })
            except:
                pass
    
    def enumerate_directories(self, base_url: str):
        """Enumerate common directories and files"""
        self.print_info("Enumerating common directories...")
        
        found_dirs = []
        
        def check_dir(dir_name):
            url = urljoin(base_url, dir_name)
            try:
                response = requests.get(url, timeout=2, verify=False)
                if response.status_code == 200:
                    found_dirs.append(url)
                    self.print_warning(f"Found accessible path: {url}")
                elif response.status_code == 403:
                    self.print_warning(f"Path exists but forbidden: {url}")
                    found_dirs.append(f"{url} (403 Forbidden)")
                elif response.status_code == 401:
                    self.print_warning(f"Path requires authentication: {url}")
                    found_dirs.append(f"{url} (401 Unauthorized)")
            except:
                pass
        
        # Use threading for faster enumeration
        threads = []
        for directory in self.common_dirs:
            t = threading.Thread(target=check_dir, args=(directory,))
            t.start()
            threads.append(t)
            
            if len(threads) >= 10:
                for t in threads:
                    t.join(timeout=0.5)
                threads = []
        
        for t in threads:
            t.join(timeout=0.5)
        
        if found_dirs:
            self.directories_found = found_dirs
            self.vulnerabilities.append({
                "type": "Web",
                "url": base_url,
                "issue": "Sensitive directories exposed",
                "details": found_dirs,
                "severity": "MEDIUM"
            })
    
    def check_sql_injection(self, base_url: str):
        """Test for SQL injection vulnerabilities"""
        # This is a simplified check
        test_urls = [
            f"{base_url}/?id=1",
            f"{base_url}/index.php?id=1",
            f"{base_url}/page?id=1",
            f"{base_url}/product?id=1"
        ]
        
        for url in test_urls:
            try:
                # First request with normal parameter
                response_normal = requests.get(url, timeout=3, verify=False)
                
                # Test with SQL payload
                for payload in self.sqli_payloads[:3]:  # Test first few
                    test_url = url.replace("1", payload)
                    try:
                        response = requests.get(test_url, timeout=3, verify=False)
                        
                        # Check for SQL errors (simplified)
                        if any(error in response.text.lower() for error in [
                            "sql", "mysql", "syntax error", "unclosed quotation mark",
                            "odbc", "oracle", "postgresql", "warning: mysql"
                        ]):
                            self.print_vulnerability(f"Possible SQL injection at {url}", "CRITICAL")
                            self.vulnerabilities.append({
                                "type": "SQL Injection",
                                "url": url,
                                "payload": payload,
                                "severity": "CRITICAL"
                            })
                            break
                    except:
                        pass
            except:
                pass
    
    def check_xss(self, base_url: str):
        """Test for XSS vulnerabilities"""
        # Simplified XSS check
        test_params = ["q", "search", "s", "query", "id", "page"]
        
        for param in test_params:
            for payload in self.xss_payloads[:2]:  # Test first few
                try:
                    url = f"{base_url}/?{param}={payload}"
                    response = requests.get(url, timeout=3, verify=False)
                    
                    # Check if payload is reflected
                    if payload in response.text and "<script" in response.text.lower():
                        self.print_vulnerability(f"Possible XSS at {url}", "HIGH")
                        self.vulnerabilities.append({
                            "type": "XSS",
                            "url": url,
                            "payload": payload,
                            "severity": "HIGH"
                        })
                        break
                except:
                    pass
    
    # ==================== REPORT GENERATION ====================
    
    def generate_report(self) -> str:
        """Generate comprehensive vulnerability report"""
        report = []
        
        report.append(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        report.append(f"{Colors.BOLD}{Colors.RED}🔍 VULNERABILITY ASSESSMENT REPORT{Colors.END}")
        report.append(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
        
        # Target info
        report.append(f"{Colors.BOLD}Target:{Colors.END} {self.target}")
        report.append(f"{Colors.BOLD}IP Address:{Colors.END} {self.target_ip}")
        report.append(f"{Colors.BOLD}Scan Start:{Colors.END} {self.scan_start_time}")
        report.append(f"{Colors.BOLD}Scan End:{Colors.END} {self.scan_end_time}\n")
        
        # Summary
        report.append(f"{Colors.BOLD}📊 SCAN SUMMARY:{Colors.END}")
        report.append(f"   Open ports: {len(self.open_ports)}")
        report.append(f"   Vulnerabilities found: {len(self.vulnerabilities)}")
        report.append(f"   Web directories discovered: {len(self.directories_found)}\n")
        
        # Open ports
        if self.open_ports:
            report.append(f"{Colors.BOLD}🔓 OPEN PORTS:{Colors.END}")
            for port_info in self.open_ports:
                report.append(f"   • Port {port_info['port']}/TCP - {port_info['banner']}")
            report.append("")
        
        # Vulnerabilities by severity
        if self.vulnerabilities:
            report.append(f"{Colors.BOLD}{Colors.RED}⚠️  VULNERABILITIES DETECTED:{Colors.END}")
            
            # Group by severity
            critical = [v for v in self.vulnerabilities if v.get('severity') == 'CRITICAL']
            high = [v for v in self.vulnerabilities if v.get('severity') == 'HIGH']
            medium = [v for v in self.vulnerabilities if v.get('severity') == 'MEDIUM']
            low = [v for v in self.vulnerabilities if v.get('severity') == 'LOW']
            
            if critical:
                report.append(f"\n{Colors.RED}{Colors.BOLD}🔴 CRITICAL:{Colors.END}")
                for v in critical:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if high:
                report.append(f"\n{Colors.RED}🟠 HIGH:{Colors.END}")
                for v in high:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if medium:
                report.append(f"\n{Colors.YELLOW}🟡 MEDIUM:{Colors.END}")
                for v in medium:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if low:
                report.append(f"\n{Colors.BLUE}🔵 LOW:{Colors.END}")
                for v in low:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            report.append("")
        
        # Web directories found
        if self.directories_found:
            report.append(f"{Colors.BOLD}📁 SENSITIVE DIRECTORIES FOUND:{Colors.END}")
            for dir_path in self.directories_found[:10]:  # Show first 10
                report.append(f"   • {dir_path}")
            if len(self.directories_found) > 10:
                report.append(f"   • ... and {len(self.directories_found) - 10} more")
            report.append("")
        
        # Remediation recommendations
        report.append(f"{Colors.BOLD}🛡️  REMEDIATION RECOMMENDATIONS:{Colors.END}")
        
        if critical or high:
            report.append(f"   • {Colors.RED}PATCH CRITICAL/HIGH VULNERABILITIES IMMEDIATELY{Colors.END}")
        
        if any(v['type'] == 'SQL Injection' for v in self.vulnerabilities):
            report.append("   • Use parameterized queries to prevent SQL injection")
            report.append("   • Implement input validation and sanitization")
        
        if any(v['type'] == 'XSS' for v in self.vulnerabilities):
            report.append("   • Implement Content Security Policy (CSP)")
            report.append("   • Encode output and validate input")
        
        if any(v.get('issue') == 'Missing security headers' for v in self.vulnerabilities):
            report.append("   • Add recommended security headers (HSTS, CSP, X-Frame-Options, etc.)")
        
        if any(v.get('issue') == 'Directory listing enabled' for v in self.vulnerabilities):
            report.append("   • Disable directory listing in web server configuration")
        
        if any(v['type'] == 'FTP' for v in self.vulnerabilities):
            report.append("   • Disable anonymous FTP access")
            report.append("   • Use SFTP/FTPS instead of plain FTP")
        
        if any(v['type'] == 'SSL' for v in self.vulnerabilities):
            report.append("   • Update SSL/TLS certificates before expiration")
            report.append("   • Disable weak ciphers and protocols")
        
        if any(v['type'] == 'Default Credentials' for v in self.vulnerabilities):
            report.append("   • Change all default passwords on network devices")
            report.append("   • Use strong, unique passwords for each service")
        
        if any(v['type'] == 'CVE' for v in self.vulnerabilities):
            report.append("   • Update all software to latest patched versions")
            report.append("   • Subscribe to security advisories for your software")
        
        report.append(f"\n{Colors.CYAN}{'='*80}{Colors.END}")
        report.append(f"{Colors.BOLD}⚠️  DISCLAIMER: This tool is for authorized testing only{Colors.END}")
        report.append(f"{Colors.CYAN}{'='*80}{Colors.END}")
        
        return '\n'.join(report)
    
    def save_report(self, filename: str = None):
        """Save report to file with proper Unicode handling"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vuln_scan_{self.target_hostname}_{timestamp}.txt"
        
        # Generate report with colors (for terminal)
        report_with_colors = self.generate_report()
        
        # Generate report without colors (for file)
        report_without_colors = self.generate_report_for_file()
        
        # Save to file using UTF-8 encoding
        try:
            with codecs.open(filename, 'w', encoding='utf-8') as f:
                f.write(report_without_colors)
            self.print_success(f"Report saved to: {filename}")
        except Exception as e:
            self.print_error(f"Error saving report: {e}")
            # Try with different encoding as fallback
            try:
                with open(filename, 'w', encoding='cp1252', errors='ignore') as f:
                    f.write(report_without_colors)
                self.print_success(f"Report saved with alternate encoding to: {filename}")
            except:
                self.print_error("Could not save report")
    
    def generate_report_for_file(self) -> str:
        """Generate report without ANSI color codes for file saving"""
        report = []
        
        report.append(f"\n{'='*80}")
        report.append(f"🔍 VULNERABILITY ASSESSMENT REPORT")
        report.append(f"{'='*80}\n")
        
        # Target info
        report.append(f"Target: {self.target}")
        report.append(f"IP Address: {self.target_ip}")
        report.append(f"Scan Start: {self.scan_start_time}")
        report.append(f"Scan End: {self.scan_end_time}\n")
        
        # Summary
        report.append(f"📊 SCAN SUMMARY:")
        report.append(f"   Open ports: {len(self.open_ports)}")
        report.append(f"   Vulnerabilities found: {len(self.vulnerabilities)}")
        report.append(f"   Web directories discovered: {len(self.directories_found)}\n")
        
        # Open ports
        if self.open_ports:
            report.append(f"🔓 OPEN PORTS:")
            for port_info in self.open_ports:
                report.append(f"   • Port {port_info['port']}/TCP - {port_info['banner']}")
            report.append("")
        
        # Vulnerabilities by severity
        if self.vulnerabilities:
            report.append(f"⚠️  VULNERABILITIES DETECTED:")
            
            # Group by severity
            critical = [v for v in self.vulnerabilities if v.get('severity') == 'CRITICAL']
            high = [v for v in self.vulnerabilities if v.get('severity') == 'HIGH']
            medium = [v for v in self.vulnerabilities if v.get('severity') == 'MEDIUM']
            low = [v for v in self.vulnerabilities if v.get('severity') == 'LOW']
            
            if critical:
                report.append(f"\n🔴 CRITICAL:")
                for v in critical:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if high:
                report.append(f"\n🟠 HIGH:")
                for v in high:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if medium:
                report.append(f"\n🟡 MEDIUM:")
                for v in medium:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            
            if low:
                report.append(f"\n🔵 LOW:")
                for v in low:
                    url = v.get('url', '')
                    issue = v.get('issue', '')
                    if url:
                        report.append(f"   • {v.get('type')}: {url} - {issue}")
                    else:
                        report.append(f"   • {v.get('type')}: {issue}")
            report.append("")
        
        # Web directories found
        if self.directories_found:
            report.append(f"📁 SENSITIVE DIRECTORIES FOUND:")
            for dir_path in self.directories_found[:10]:
                report.append(f"   • {dir_path}")
            if len(self.directories_found) > 10:
                report.append(f"   • ... and {len(self.directories_found) - 10} more")
            report.append("")
        
        # Remediation recommendations
        report.append(f"🛡️  REMEDIATION RECOMMENDATIONS:")
        
        if critical or high:
            report.append(f"   • PATCH CRITICAL/HIGH VULNERABILITIES IMMEDIATELY")
        
        if any(v['type'] == 'SQL Injection' for v in self.vulnerabilities):
            report.append("   • Use parameterized queries to prevent SQL injection")
            report.append("   • Implement input validation and sanitization")
        
        if any(v['type'] == 'XSS' for v in self.vulnerabilities):
            report.append("   • Implement Content Security Policy (CSP)")
            report.append("   • Encode output and validate input")
        
        if any(v.get('issue') == 'Missing security headers' for v in self.vulnerabilities):
            report.append("   • Add recommended security headers (HSTS, CSP, X-Frame-Options, etc.)")
        
        if any(v.get('issue') == 'Directory listing enabled' for v in self.vulnerabilities):
            report.append("   • Disable directory listing in web server configuration")
        
        if any(v['type'] == 'FTP' for v in self.vulnerabilities):
            report.append("   • Disable anonymous FTP access")
            report.append("   • Use SFTP/FTPS instead of plain FTP")
        
        if any(v['type'] == 'SSL' for v in self.vulnerabilities):
            report.append("   • Update SSL/TLS certificates before expiration")
            report.append("   • Disable weak ciphers and protocols")
        
        if any(v['type'] == 'Default Credentials' for v in self.vulnerabilities):
            report.append("   • Change all default passwords on network devices")
            report.append("   • Use strong, unique passwords for each service")
        
        if any(v['type'] == 'CVE' for v in self.vulnerabilities):
            report.append("   • Update all software to latest patched versions")
            report.append("   • Subscribe to security advisories for your software")
        
        report.append(f"\n{'='*80}")
        report.append(f"⚠️  DISCLAIMER: This tool is for authorized testing only")
        report.append(f"{'='*80}")
        
        return '\n'.join(report)
    
    # ==================== MAIN SCAN FUNCTION ====================
    
    def scan(self, target: str):
        """Perform complete vulnerability scan"""
        self.scan_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.clear_screen()
        self.print_banner()
        self.print_header(f"SCANNING TARGET: {target}")
        
        # Resolve target
        self.print_info(f"Resolving target: {target}")
        if not self.resolve_target(target):
            self.print_error(f"Could not resolve target: {target}")
            return False
        
        self.print_success(f"Target resolved: {self.target_ip} ({self.target_hostname})")
        
        # Port scan
        self.port_scan()
        
        if not self.open_ports:
            self.print_warning("No open ports found. Target may be down or heavily firewalled.")
        
        # Check for vulnerabilities on open ports
        if self.open_ports:
            self.check_cve_vulnerabilities()
            self.check_anonymous_ftp()
            self.check_default_credentials()
            self.check_ssl_vulnerabilities()
            self.check_web_vulnerabilities()
        
        self.scan_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate report
        print()
        print(self.generate_report())
        
        # Save report
        save = input(f"\n{Colors.PURPLE}Save report to file? (y/n): {Colors.END}").lower()
        if save == 'y':
            self.save_report()
        
        return True


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}🔍 COMPREHENSIVE VULNERABILITY SCANNER{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    print(f"\n{Colors.BOLD}⚠️  LEGAL DISCLAIMER:{Colors.END}")
    print("This tool is for authorized security testing ONLY.")
    print("Scanning systems you don't own or have permission to test is ILLEGAL.\n")
    
    accept = input(f"{Colors.PURPLE}Do you accept responsibility for lawful use? (yes/no): {Colors.END}").lower()
    if accept not in ['yes', 'y']:
        print(f"{Colors.RED}Exiting...{Colors.END}")
        sys.exit(0)
    
    scanner = VulnerabilityScanner()
    
    while True:
        scanner.clear_screen()
        scanner.print_banner()
        
        print(f"\n{Colors.BOLD}Enter target website/IP to scan:{Colors.END}")
        print(f"Examples: example.com, 192.168.1.1, https://example.com")
        
        target = input(f"\n{Colors.PURPLE}Target: {Colors.END}").strip()
        
        if target.lower() == 'quit' or target.lower() == 'exit':
            print(f"{Colors.GREEN}Goodbye! Stay secure!{Colors.END}")
            break
        
        if not target:
            print(f"{Colors.RED}Please enter a target{Colors.END}")
            continue
        
        # Perform scan
        scanner.scan(target)
        
        input(f"\n{Colors.PURPLE}Press Enter to scan another target...{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Scan interrupted by user{Colors.END}")
        print(f"{Colors.GREEN}Goodbye!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)