#!/usr/bin/env python3
"""
📡 ADVANCED PACKET SNIFFER - Comprehensive Network Analysis Tool
Features:
- Real-time packet capture and analysis
- Protocol detection (TCP, UDP, ICMP, ARP, DNS, HTTP)
- Source/Destination IP and port extraction
- Payload inspection and data extraction
- Packet filtering by protocol/IP/port
- Save captures to PCAP file
- Statistics and traffic analysis
- Color-coded output for different protocols
- Live traffic monitoring with timestamps
"""

import os
import sys
import time
import threading
import signal
from datetime import datetime
from collections import defaultdict
import ipaddress

# Try importing Scapy with helpful error messages
try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    from scapy.layers.dns import DNS, DNSQR, DNSRR
    from scapy.layers.http import HTTPRequest, HTTPResponse
    SCAPY_AVAILABLE = True
    print("✅ Scapy module loaded successfully")
except ImportError as e:
    SCAPY_AVAILABLE = False
    print(f"❌ Scapy module not available: {e}")
    print("   Install with: pip install scapy")
    print("   On Windows, also install Npcap from: https://npcap.com")
    sys.exit(1)

# ANSI color codes for beautiful output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'  # Same as PURPLE
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Add PURPLE as alias for MAGENTA
    PURPLE = MAGENTA
    
    # Protocol-specific colors
    TCP_COLOR = '\033[94m'      # Blue
    UDP_COLOR = '\033[92m'       # Green
    ICMP_COLOR = '\033[93m'      # Yellow
    ARP_COLOR = '\033[95m'       # Magenta
    DNS_COLOR = '\033[96m'       # Cyan
    HTTP_COLOR = '\033[91m'      # Red
    OTHER_COLOR = '\033[97m'     # White


class PacketSniffer:
    def __init__(self):
        self.packets = []
        self.capturing = False
        self.packet_count = 0
        self.start_time = None
        self.end_time = None
        self.stats = {
            'total': 0,
            'tcp': 0,
            'udp': 0,
            'icmp': 0,
            'arp': 0,
            'dns': 0,
            'http': 0,
            'other': 0,
            'bytes': 0,
            'ip_src': defaultdict(int),
            'ip_dst': defaultdict(int),
            'ports': defaultdict(int)
        }
        self.interface = self.get_default_interface()
        self.filter_str = ""
        self.output_file = None
        
    # ==================== UTILITY FUNCTIONS ====================
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Print tool banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║              ADVANCED PACKET SNIFFER v2.0                  ║
║         Real-time Network Traffic Analysis Tool             ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """
        print(banner)
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}📡 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    
    def print_success(self, message):
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_warning(self, message):
        print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
    
    def print_info(self, message):
        print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
    
    def print_prompt(self, message):
        """Print prompt in purple"""
        print(f"{Colors.PURPLE}{message}{Colors.END}", end="")
    
    def get_default_interface(self) -> str:
        """Get default network interface"""
        try:
            interfaces = get_if_list()
            for iface in interfaces:
                if iface not in ['lo', 'loopback', 'docker0', 'vboxnet0']:
                    return iface
        except:
            pass
        return 'eth0'  # Default fallback
    
    def list_interfaces(self):
        """List all available network interfaces"""
        try:
            interfaces = get_if_list()
            print(f"\n{Colors.BOLD}Available interfaces:{Colors.END}")
            for i, iface in enumerate(interfaces, 1):
                print(f"  {i}. {iface}")
            return interfaces
        except:
            self.print_error("Could not list interfaces")
            return []
    
    def check_admin_privileges(self):
        """Check if running with admin/root privileges"""
        if os.name == 'nt':
            # Windows - check if admin (simplified)
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            # Linux/Mac - check if root
            return os.geteuid() == 0
    
    # ==================== PACKET HANDLING ====================
    
    def packet_callback(self, packet):
        """
        Main callback function for each captured packet
        """
        self.packet_count += 1
        self.stats['total'] += 1
        self.stats['bytes'] += len(packet)
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Determine packet type and extract information
        if IP in packet:
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            proto = ip_layer.proto
            
            # TCP Packets
            if TCP in packet:
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                flags = tcp_layer.flags
                
                self.stats['tcp'] += 1
                self.stats['ports'][src_port] += 1
                self.stats['ports'][dst_port] += 1
                
                # Check for HTTP (port 80) or HTTPS (port 443)
                if dst_port == 80 or src_port == 80:
                    self.stats['http'] += 1
                    self.display_packet(timestamp, "HTTP", src_ip, src_port, dst_ip, dst_port, packet)
                else:
                    self.display_packet(timestamp, "TCP", src_ip, src_port, dst_ip, dst_port, packet, flags)
            
            # UDP Packets
            elif UDP in packet:
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                
                self.stats['udp'] += 1
                self.stats['ports'][src_port] += 1
                self.stats['ports'][dst_port] += 1
                
                # Check for DNS (port 53)
                if dst_port == 53 or src_port == 53:
                    self.stats['dns'] += 1
                    self.display_packet(timestamp, "DNS", src_ip, src_port, dst_ip, dst_port, packet)
                else:
                    self.display_packet(timestamp, "UDP", src_ip, src_port, dst_ip, dst_port, packet)
            
            # ICMP Packets
            elif ICMP in packet:
                self.stats['icmp'] += 1
                self.display_packet(timestamp, "ICMP", src_ip, None, dst_ip, None, packet)
            
            else:
                self.stats['other'] += 1
                self.display_packet(timestamp, "OTHER", src_ip, None, dst_ip, None, packet)
            
            # Update IP statistics
            self.stats['ip_src'][src_ip] += 1
            self.stats['ip_dst'][dst_ip] += 1
            
        elif ARP in packet:
            # ARP Packets
            self.stats['arp'] += 1
            self.stats['other'] += 1
            self.display_arp_packet(timestamp, packet)
        
        else:
            self.stats['other'] += 1
            self.display_raw_packet(timestamp, packet)
        
        # Save to file if enabled
        if self.output_file:
            self.packets.append(packet)
    
    def display_packet(self, timestamp, protocol, src_ip, src_port, dst_ip, dst_port, packet, flags=None):
        """
        Display packet information with colors
        """
        # Choose color based on protocol
        if protocol == "TCP":
            color = Colors.TCP_COLOR
        elif protocol == "UDP":
            color = Colors.UDP_COLOR
        elif protocol == "ICMP":
            color = Colors.ICMP_COLOR
        elif protocol == "DNS":
            color = Colors.DNS_COLOR
        elif protocol == "HTTP":
            color = Colors.HTTP_COLOR
        else:
            color = Colors.OTHER_COLOR
        
        # Format the output
        if src_port and dst_port:
            # TCP/UDP with ports
            flag_info = f" [Flags: {flags}]" if flags else ""
            print(f"{color}[{timestamp}] {protocol:5} {src_ip}:{src_port} → {dst_ip}:{dst_port}{flag_info}{Colors.END}")
        else:
            # ICMP or other protocols without ports
            print(f"{color}[{timestamp}] {protocol:5} {src_ip} → {dst_ip}{Colors.END}")
        
        # Show payload summary for interesting packets
        if protocol in ["HTTP", "DNS"] and Raw in packet:
            payload = packet[Raw].load[:100]  # First 100 bytes
            try:
                payload_str = payload.decode('utf-8', errors='ignore').strip()
                if payload_str:
                    # Clean up the payload for display
                    payload_str = ' '.join(payload_str.split())
                    if len(payload_str) > 80:
                        payload_str = payload_str[:80] + "..."
                    print(f"      Payload: {payload_str}")
            except:
                pass
    
    def display_arp_packet(self, timestamp, packet):
        """
        Display ARP packet information
        """
        arp = packet[ARP]
        op = "Request" if arp.op == 1 else "Reply" if arp.op == 2 else f"Op:{arp.op}"
        
        print(f"{Colors.ARP_COLOR}[{timestamp}] ARP     {op}: {arp.psrc} ({arp.hwsrc}) → {arp.pdst} ({arp.hwdst}){Colors.END}")
    
    def display_raw_packet(self, timestamp, packet):
        """
        Display raw packet summary
        """
        print(f"{Colors.OTHER_COLOR}[{timestamp}] OTHER   {packet.summary()[:80]}{Colors.END}")
    
    # ==================== CAPTURE CONTROL ====================
    
    def start_capture(self, interface=None, packet_count=0, filter_str="", output_file=None):
        """
        Start packet capture
        """
        if not self.check_admin_privileges():
            self.print_warning("⚠️ Administrator/root privileges required for packet capture!")
            self.print_info("Please run as Administrator (Windows) or with sudo (Linux/Mac)")
            return False
        
        if interface:
            self.interface = interface
        
        self.filter_str = filter_str
        self.output_file = output_file
        self.capturing = True
        self.packet_count = 0
        self.start_time = datetime.now()
        
        self.print_header(f"STARTING CAPTURE ON {self.interface}")
        print(f"Interface: {self.interface}")
        if filter_str:
            print(f"Filter: {filter_str}")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop capture{Colors.END}\n")
        
        try:
            # Start sniffing
            sniff_kwargs = {
                'iface': self.interface,
                'prn': self.packet_callback,
                'store': bool(self.output_file)
            }
            
            if filter_str:
                sniff_kwargs['filter'] = filter_str
            
            if packet_count > 0:
                sniff_kwargs['count'] = packet_count
            
            sniff(**sniff_kwargs)
            
        except PermissionError:
            self.print_error("Permission denied! Need admin/root privileges.")
            return False
        except Exception as e:
            self.print_error(f"Capture error: {e}")
            return False
        
        self.stop_capture()
        return True
    
    def stop_capture(self):
        """Stop packet capture"""
        self.capturing = False
        self.end_time = datetime.now()
        
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.print_header("CAPTURE COMPLETE")
        print(f"Stopped at: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Total packets: {self.packet_count}")
        if duration > 0:
            print(f"Average rate: {self.packet_count/duration:.2f} packets/sec\n")
        
        # Save packets if output file was specified
        if self.output_file and self.packets:
            self.save_packets()
        
        # Display statistics
        self.display_statistics()
    
    # ==================== FILE OPERATIONS ====================
    
    def save_packets(self, filename=None):
        """
        Save captured packets to PCAP file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.pcap"
        
        try:
            wrpcap(filename, self.packets)
            self.print_success(f"Saved {len(self.packets)} packets to {filename}")
        except Exception as e:
            self.print_error(f"Failed to save packets: {e}")
    
    def load_packets(self, filename):
        """
        Load packets from PCAP file for analysis
        """
        try:
            packets = rdpcap(filename)
            self.print_success(f"Loaded {len(packets)} packets from {filename}")
            return packets
        except Exception as e:
            self.print_error(f"Failed to load packets: {e}")
            return []
    
    # ==================== STATISTICS ====================
    
    def display_statistics(self):
        """
        Display comprehensive capture statistics
        """
        self.print_header("CAPTURE STATISTICS")
        
        # Protocol distribution
        total = self.stats['total'] or 1  # Avoid division by zero
        print(f"\n{Colors.BOLD}📊 Protocol Distribution:{Colors.END}")
        print(f"  TCP:   {self.stats['tcp']:6} ({self.stats['tcp']*100/total:.1f}%)")
        print(f"  UDP:   {self.stats['udp']:6} ({self.stats['udp']*100/total:.1f}%)")
        print(f"  ICMP:  {self.stats['icmp']:6} ({self.stats['icmp']*100/total:.1f}%)")
        print(f"  ARP:   {self.stats['arp']:6} ({self.stats['arp']*100/total:.1f}%)")
        print(f"  DNS:   {self.stats['dns']:6} ({self.stats['dns']*100/total:.1f}%)")
        print(f"  HTTP:  {self.stats['http']:6} ({self.stats['http']*100/total:.1f}%)")
        print(f"  Other: {self.stats['other']:6} ({self.stats['other']*100/total:.1f}%)")
        
        # Top source IPs
        if self.stats['ip_src']:
            print(f"\n{Colors.BOLD}📊 Top Source IPs:{Colors.END}")
            for ip, count in sorted(self.stats['ip_src'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {ip:15} : {count:5} packets ({count*100/total:.1f}%)")
        
        # Top destination IPs
        if self.stats['ip_dst']:
            print(f"\n{Colors.BOLD}📊 Top Destination IPs:{Colors.END}")
            for ip, count in sorted(self.stats['ip_dst'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {ip:15} : {count:5} packets ({count*100/total:.1f}%)")
        
        # Top ports
        if self.stats['ports']:
            print(f"\n{Colors.BOLD}📊 Top Ports:{Colors.END}")
            for port, count in sorted(self.stats['ports'].items(), key=lambda x: x[1], reverse=True)[:5]:
                service = self.get_port_service(port)
                print(f"  Port {port:5} ({service}): {count:5} packets")
        
        # Traffic volume
        bytes_mb = self.stats['bytes'] / (1024 * 1024)
        print(f"\n{Colors.BOLD}📊 Traffic Volume:{Colors.END}")
        print(f"  Total bytes: {self.stats['bytes']} ({bytes_mb:.2f} MB)")
        print(f"  Average packet size: {self.stats['bytes']/total:.1f} bytes")
    
    def get_port_service(self, port):
        """Get service name for common ports"""
        services = {
            20: "FTP-data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC", 135: "MSRPC",
            139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
            995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
            5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
            27017: "MongoDB", 5060: "SIP", 5061: "SIPS"
        }
        return services.get(port, "unknown")
    
    # ==================== ADVANCED ANALYSIS ====================
    
    def analyze_http_traffic(self, packets=None):
        """
        Extract and analyze HTTP traffic
        """
        if packets is None:
            packets = self.packets
        
        http_requests = []
        http_responses = []
        
        for pkt in packets:
            if TCP in pkt and (pkt[TCP].sport == 80 or pkt[TCP].dport == 80):
                if Raw in pkt:
                    try:
                        payload = pkt[Raw].load.decode('utf-8', errors='ignore')
                        
                        if payload.startswith(('GET', 'POST', 'HEAD', 'PUT', 'DELETE')):
                            # HTTP Request
                            lines = payload.split('\n')
                            request_line = lines[0] if lines else ""
                            http_requests.append({
                                'time': datetime.fromtimestamp(float(pkt.time)),
                                'src': pkt[IP].src,
                                'dst': pkt[IP].dst,
                                'request': request_line,
                                'full': payload[:200]
                            })
                        elif payload.startswith(('HTTP/')):
                            # HTTP Response
                            lines = payload.split('\n')
                            status_line = lines[0] if lines else ""
                            http_responses.append({
                                'time': datetime.fromtimestamp(float(pkt.time)),
                                'src': pkt[IP].src,
                                'dst': pkt[IP].dst,
                                'status': status_line,
                                'full': payload[:200]
                            })
                    except:
                        pass
        
        if http_requests:
            self.print_header("HTTP REQUESTS")
            for req in http_requests[:10]:  # Show first 10
                print(f"{Colors.HTTP_COLOR}[{req['time'].strftime('%H:%M:%S')}] {req['src']} → {req['dst']}: {req['request']}{Colors.END}")
        
        return http_requests, http_responses
    
    def analyze_dns_queries(self, packets=None):
        """
        Extract and analyze DNS queries
        """
        if packets is None:
            packets = self.packets
        
        dns_queries = []
        
        for pkt in packets:
            if DNS in pkt and pkt[DNS].qr == 0:  # DNS Query
                if DNSQR in pkt:
                    try:
                        qname = pkt[DNSQR].qname.decode('utf-8', errors='ignore')
                        dns_queries.append({
                            'time': datetime.fromtimestamp(float(pkt.time)),
                            'src': pkt[IP].src,
                            'dst': pkt[IP].dst,
                            'query': qname,
                            'type': pkt[DNSQR].qtype
                        })
                    except:
                        pass
        
        if dns_queries:
            self.print_header("DNS QUERIES")
            for query in dns_queries[:10]:  # Show first 10
                print(f"{Colors.DNS_COLOR}[{query['time'].strftime('%H:%M:%S')}] {query['src']} → {query['dst']}: {query['query']}{Colors.END}")
        
        return dns_queries
    
    # ==================== INTERACTIVE MENU ====================
    
    def interactive_menu(self):
        """Interactive menu for packet sniffing"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            # Check privileges
            if not self.check_admin_privileges():
                self.print_warning("⚠️  Administrator/root privileges recommended for packet capture")
            
            print(f"\n{Colors.BOLD}📋 MAIN MENU:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
            print("1. 🎯 Start live packet capture")
            print("2. ⚙️  Configure capture settings")
            print("3. 📊 Analyze saved capture file")
            print("4. 📈 View statistics (last capture)")
            print("5. ℹ️  Help & Information")
            print("6. 🚪 Exit")
            
            choice = input(f"\n{Colors.PURPLE}Choose (1-6): {Colors.END}").strip()
            
            if choice == "1":
                self.live_capture_menu()
            elif choice == "2":
                self.settings_menu()
            elif choice == "3":
                self.analyze_file_menu()
            elif choice == "4":
                if self.packets:
                    self.display_statistics()
                else:
                    self.print_warning("No capture data available")
                input(f"\n{Colors.PURPLE}Press Enter...{Colors.END}")
            elif choice == "5":
                self.help_menu()
            elif choice == "6":
                self.print_success("Goodbye! Stay secure!")
                break
    
    def live_capture_menu(self):
        """Menu for live capture options"""
        self.clear_screen()
        self.print_header("LIVE CAPTURE OPTIONS")
        
        print(f"\n{Colors.BOLD}Select capture type:{Colors.END}")
        print("1. 🔍 Basic capture (all traffic)")
        print("2. 🌐 HTTP traffic only")
        print("3. 📧 DNS queries only")
        print("4. 🖧 TCP traffic only")
        print("5. 📦 UDP traffic only")
        print("6. 🎯 Custom BPF filter")
        print("7. ⏱️  Capture limited packets")
        print("8. 🔙 Back to main menu")
        
        choice = input(f"\n{Colors.PURPLE}Choose (1-8): {Colors.END}").strip()
        
        filter_str = ""
        packet_count = 0
        
        if choice == "1":
            filter_str = ""
        elif choice == "2":
            filter_str = "tcp port 80"
        elif choice == "3":
            filter_str = "udp port 53"
        elif choice == "4":
            filter_str = "tcp"
        elif choice == "5":
            filter_str = "udp"
        elif choice == "6":
            filter_str = input(f"{Colors.PURPLE}Enter BPF filter (e.g., 'host 192.168.1.1'): {Colors.END}").strip()
        elif choice == "7":
            try:
                packet_count = int(input(f"{Colors.PURPLE}Number of packets to capture: {Colors.END}"))
            except:
                self.print_error("Invalid number")
                return
        elif choice == "8":
            return
        else:
            self.print_error("Invalid choice")
            return
        
        # Ask for output file
        save = input(f"{Colors.PURPLE}Save to file? (y/n): {Colors.END}").lower()
        output_file = None
        if save in ['y', 'yes']:
            filename = input(f"{Colors.PURPLE}Filename (default: auto): {Colors.END}").strip()
            output_file = filename if filename else None
        
        # Start capture
        self.start_capture(
            interface=self.interface,
            packet_count=packet_count,
            filter_str=filter_str,
            output_file=output_file
        )
        
        input(f"\n{Colors.PURPLE}Press Enter...{Colors.END}")
    
    def settings_menu(self):
        """Menu for configuring capture settings"""
        self.clear_screen()
        self.print_header("CAPTURE SETTINGS")
        
        # List and select interface
        interfaces = self.list_interfaces()
        if interfaces:
            try:
                idx = int(input(f"\n{Colors.PURPLE}Select interface number: {Colors.END}")) - 1
                if 0 <= idx < len(interfaces):
                    self.interface = interfaces[idx]
                    self.print_success(f"Interface set to: {self.interface}")
                else:
                    self.print_error("Invalid selection")
            except:
                self.print_error("Invalid input")
        
        input(f"\n{Colors.PURPLE}Press Enter...{Colors.END}")
    
    def analyze_file_menu(self):
        """Menu for analyzing saved capture files"""
        self.clear_screen()
        self.print_header("ANALYZE CAPTURE FILE")
        
        filename = input(f"{Colors.PURPLE}Enter PCAP filename: {Colors.END}").strip()
        if not filename:
            return
        
        packets = self.load_packets(filename)
        if packets:
            self.packets = packets
            self.stats = self.calculate_stats(packets)
            self.display_statistics()
            
            # Ask for deeper analysis
            print(f"\n{Colors.BOLD}Additional Analysis:{Colors.END}")
            print("1. Show HTTP requests")
            print("2. Show DNS queries")
            print("3. Back")
            
            subchoice = input(f"{Colors.PURPLE}Choose: {Colors.END}").strip()
            if subchoice == "1":
                self.analyze_http_traffic(packets)
            elif subchoice == "2":
                self.analyze_dns_queries(packets)
        
        input(f"\n{Colors.PURPLE}Press Enter...{Colors.END}")
    
    def calculate_stats(self, packets):
        """Calculate statistics from loaded packets"""
        stats = {
            'total': len(packets),
            'tcp': 0, 'udp': 0, 'icmp': 0, 'arp': 0, 'dns': 0, 'http': 0, 'other': 0,
            'bytes': 0, 'ip_src': defaultdict(int), 'ip_dst': defaultdict(int),
            'ports': defaultdict(int)
        }
        
        for pkt in packets:
            stats['bytes'] += len(pkt)
            
            if IP in pkt:
                stats['ip_src'][pkt[IP].src] += 1
                stats['ip_dst'][pkt[IP].dst] += 1
                
                if TCP in pkt:
                    stats['tcp'] += 1
                    stats['ports'][pkt[TCP].sport] += 1
                    stats['ports'][pkt[TCP].dport] += 1
                    if pkt[TCP].dport == 80 or pkt[TCP].sport == 80:
                        stats['http'] += 1
                elif UDP in pkt:
                    stats['udp'] += 1
                    stats['ports'][pkt[UDP].sport] += 1
                    stats['ports'][pkt[UDP].dport] += 1
                    if pkt[UDP].dport == 53 or pkt[UDP].sport == 53:
                        stats['dns'] += 1
                elif ICMP in pkt:
                    stats['icmp'] += 1
                else:
                    stats['other'] += 1
            elif ARP in pkt:
                stats['arp'] += 1
                stats['other'] += 1
            else:
                stats['other'] += 1
        
        return stats
    
    def help_menu(self):
        """Display help information"""
        self.clear_screen()
        self.print_header("HELP & INFORMATION")
        
        print(f"""
{Colors.BOLD}📡 About this Tool:{Colors.END}
  This advanced packet sniffer captures and analyzes network traffic in real-time.
  It can detect multiple protocols and provide detailed statistics.

{Colors.BOLD}🎯 Features:{Colors.END}
  • Real-time packet capture and analysis
  • Protocol detection (TCP, UDP, ICMP, ARP, DNS, HTTP)
  • Source/Destination IP and port extraction
  • Packet filtering using BPF syntax
  • Save captures to PCAP files
  • Comprehensive statistics and traffic analysis
  • Color-coded output for easy reading

{Colors.BOLD}🔧 Requirements:{Colors.END}
  • Python 3.6+ with Scapy library
  • Npcap (Windows) or libpcap (Linux/Mac)
  • Administrator/root privileges

{Colors.BOLD}📝 BPF Filter Examples:{Colors.END}
  • host 192.168.1.1        - Traffic to/from specific IP
  • tcp port 80              - HTTP traffic only
  • udp port 53              - DNS queries only
  • not arp                  - Exclude ARP traffic
  • src net 192.168.1.0/24   - Traffic from local network

{Colors.BOLD}⚠️  Legal Disclaimer:{Colors.END}
  This tool is for educational and authorized testing purposes only.
  Capturing traffic on networks you don't own may be illegal.
  Always obtain proper authorization before use.

{Colors.BOLD}📚 Resources:{Colors.END}
  • Scapy Documentation: https://scapy.readthedocs.io/
  • BPF Filter Syntax: https://biot.com/capstats/bpf.html
        """)
        
        input(f"\n{Colors.PURPLE}Press Enter...{Colors.END}")


def main():
    """Main entry point"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}📡 PACKET SNIFFER - Network Analysis Tool{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    if not SCAPY_AVAILABLE:
        sys.exit(1)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run sniffer
    sniffer = PacketSniffer()
    
    try:
        sniffer.interactive_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()