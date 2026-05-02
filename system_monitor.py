import psutil
import platform
import time
import os
from datetime import datetime
import socket

# ANSI color codes
class Colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bar(percent, width=20, color=Colors.GREEN):
    """Create a colored progress bar"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"{color}{bar}{Colors.END}"

def format_bytes(bytes):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

def get_color_for_percent(percent):
    """Return color based on percentage"""
    if percent < 50:
        return Colors.GREEN
    elif percent < 75:
        return Colors.YELLOW
    elif percent < 90:
        return Colors.PINK
    else:
        return Colors.RED

def display_system_info():
    """Display all system information with colors"""
    while True:
        clear_screen()
        
        # Header
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}🔧 SYSTEM MONITOR 🔧{Colors.END}".center(60))
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        # System Info
        print(f"{Colors.BOLD}{Colors.YELLOW}📌 SYSTEM INFORMATION:{Colors.END}")
        print(f"{Colors.WHITE}  System: {platform.system()} {platform.release()}{Colors.END}")
        print(f"{Colors.WHITE}  Hostname: {socket.gethostname()}{Colors.END}")
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        print(f"{Colors.WHITE}  Uptime: {days}d {hours}h {minutes}m{Colors.END}\n")
        
        # CPU Info
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_color = get_color_for_percent(cpu_percent)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        print(f"{Colors.BOLD}{Colors.GREEN}🎮 CPU USAGE:{Colors.END}")
        bar = get_bar(cpu_percent, color=cpu_color)
        print(f"  {bar} {cpu_color}{cpu_percent}%{Colors.END}")
        if cpu_freq:
            print(f"{Colors.WHITE}  Frequency: {cpu_freq.current:.0f} MHz{Colors.END}")
        print(f"{Colors.WHITE}  Cores: {cpu_count} ({psutil.cpu_count(logical=False)} physical){Colors.END}\n")
        
        # Memory Info
        memory = psutil.virtual_memory()
        mem_color = get_color_for_percent(memory.percent)
        
        print(f"{Colors.BOLD}{Colors.PINK}📊 MEMORY USAGE:{Colors.END}")
        bar = get_bar(memory.percent, color=mem_color)
        print(f"  {bar} {mem_color}{memory.percent}%{Colors.END}")
        print(f"{Colors.WHITE}  Total: {format_bytes(memory.total)}{Colors.END}")
        print(f"{Colors.WHITE}  Used: {format_bytes(memory.used)}{Colors.END}")
        print(f"{Colors.WHITE}  Available: {format_bytes(memory.available)}{Colors.END}\n")
        
        # Swap Memory
        swap = psutil.swap_memory()
        if swap.total > 0:
            swap_color = get_color_for_percent(swap.percent)
            print(f"{Colors.BOLD}{Colors.PINK}💾 SWAP USAGE:{Colors.END}")
            bar = get_bar(swap.percent, color=swap_color)
            print(f"  {bar} {swap_color}{swap.percent}%{Colors.END}")
            print(f"{Colors.WHITE}  Total: {format_bytes(swap.total)}{Colors.END}")
            print(f"{Colors.WHITE}  Used: {format_bytes(swap.used)}{Colors.END}\n")
        
        # Disk Usage
        print(f"{Colors.BOLD}{Colors.YELLOW}💽 DISK USAGE:{Colors.END}")
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_color = get_color_for_percent(usage.percent)
                bar = get_bar(usage.percent, color=disk_color)
                print(f"  {Colors.CYAN}{partition.device}{Colors.END} - {partition.mountpoint}")
                print(f"    {bar} {disk_color}{usage.percent}%{Colors.END}")
                print(f"    {Colors.WHITE}Total: {format_bytes(usage.total)} | "
                      f"Used: {format_bytes(usage.used)} | "
                      f"Free: {format_bytes(usage.free)}{Colors.END}")
            except:
                pass
        print()
        
        # Network Info
        net_io = psutil.net_io_counters()
        print(f"{Colors.BOLD}{Colors.BLUE}🌐 NETWORK:{Colors.END}")
        print(f"{Colors.WHITE}  📤 Sent: {format_bytes(net_io.bytes_sent)}{Colors.END}")
        print(f"{Colors.WHITE}  📥 Received: {format_bytes(net_io.bytes_recv)}{Colors.END}")
        
        # Network speed (calculate over 1 second)
        time.sleep(1)
        new_net_io = psutil.net_io_counters()
        download_speed = (new_net_io.bytes_recv - net_io.bytes_recv) / 1024  # KB/s
        upload_speed = (new_net_io.bytes_sent - net_io.bytes_sent) / 1024    # KB/s
        
        download_color = Colors.GREEN if download_speed < 100 else Colors.YELLOW if download_speed < 500 else Colors.RED
        upload_color = Colors.GREEN if upload_speed < 50 else Colors.YELLOW if upload_speed < 200 else Colors.RED
        
        print(f"{Colors.WHITE}  Speed: {download_color}⬇️ {download_speed:.1f} KB/s{Colors.END} "
              f"{upload_color}⬆️ {upload_speed:.1f} KB/s{Colors.END}\n")
        
        # Top Processes
        print(f"{Colors.BOLD}{Colors.RED}⚡ TOP PROCESSES (by CPU):{Colors.END}")
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'pid']):
            try:
                processes.append((
                    proc.info['name'],
                    proc.info['cpu_percent'],
                    proc.info['memory_percent'],
                    proc.info['pid']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x[1], reverse=True)
        
        print(f"{Colors.CYAN}{'PID':<8} {'NAME':<20} {'CPU%':<8} {'MEM%':<8}{Colors.END}")
        print(f"{Colors.WHITE}{'-'*45}{Colors.END}")
        
        for name, cpu, mem, pid in processes[:10]:
            if cpu is None: cpu = 0
            if mem is None: mem = 0
            
            cpu_color = Colors.GREEN if cpu < 10 else Colors.YELLOW if cpu < 30 else Colors.RED
            mem_color = Colors.GREEN if mem < 10 else Colors.YELLOW if mem < 30 else Colors.RED
            
            name_short = name[:18] if name else "Unknown"
            print(f"{Colors.WHITE}{pid:<8} {name_short:<20} {cpu_color}{cpu:>6.1f}%{Colors.END} "
                  f"{mem_color}{mem:>6.1f}%{Colors.END}")
        
        # Battery Info (if available)
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                batt_color = Colors.GREEN if battery.percent > 50 else Colors.YELLOW if battery.percent > 20 else Colors.RED
                print(f"\n{Colors.BOLD}{Colors.PINK}🔋 BATTERY:{Colors.END}")
                bar = get_bar(battery.percent, color=batt_color)
                print(f"  {bar} {batt_color}{battery.percent}%{Colors.END}")
                status = "🔌 Charging" if battery.power_plugged else "🔋 Discharging"
                print(f"  {Colors.WHITE}{status}{Colors.END}")
        
        # Footer
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.YELLOW}Press Ctrl+C to exit{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
        
        time.sleep(2)  # Update every 2 seconds

def main():
    try:
        # Check if psutil is installed
        try:
            import psutil
        except ImportError:
            print(f"{Colors.RED}Error: psutil is not installed!{Colors.END}")
            print(f"{Colors.YELLOW}Install with: pip install psutil{Colors.END}")
            return
        
        display_system_info()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}👋 Goodbye!{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")

if __name__ == "__main__":
    main()