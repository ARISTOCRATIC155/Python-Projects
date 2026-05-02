#!/usr/bin/env python3
"""
📶 WiFi Password Retriever - Extract all saved WiFi passwords from Windows
This tool displays all WiFi networks your computer has connected to and their passwords.
For Windows only - uses netsh commands.
"""

import subprocess
import re
import sys
import os
from typing import List, Dict, Tuple

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


class WiFiPasswordRetriever:
    def __init__(self):
        self.profiles = []
        self.passwords = {}
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Print tool banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║              WiFi PASSWORD RETRIEVER v1.0                 ║
║         Extract all saved WiFi passwords from Windows      ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """
        print(banner)
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}📶 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    def print_success(self, message):
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_warning(self, message):
        print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
    
    def print_info(self, message):
        print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
    
    def check_windows(self) -> bool:
        """Verify the script is running on Windows"""
        if os.name != 'nt':
            self.print_error("This tool only works on Windows operating system!")
            self.print_info("The script uses Windows 'netsh' commands which are not available on other OS.")
            return False
        return True
    
    def get_all_profiles(self) -> List[str]:
        """
        Retrieve all WiFi profile names from the system
        Uses: netsh wlan show profiles
        """
        try:
            # Execute netsh command to get all profiles
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'], 
                capture_output=True, 
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                self.print_error("Failed to retrieve WiFi profiles")
                return []
            
            # Parse the output to extract profile names [citation:5]
            profiles = []
            for line in result.stdout.split('\n'):
                if "All User Profile" in line:
                    # Extract profile name (after the colon)
                    profile = line.split(':')[1].strip()
                    profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            self.print_error(f"Error retrieving profiles: {e}")
            return []
    
    def get_profile_password(self, profile: str) -> str:
        """
        Get password for a specific WiFi profile
        Uses: netsh wlan show profile name=<profile> key=clear
        """
        try:
            # Execute netsh command with key=clear to show password [citation:5]
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', 'name=' + profile, 'key=clear'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                return "Error retrieving"
            
            # Parse the output to find the password [citation:5]
            for line in result.stdout.split('\n'):
                if "Key Content" in line:
                    password = line.split(':')[1].strip()
                    return password
            
            return "No password found"
            
        except Exception as e:
            return f"Error: {e}"
    
    def retrieve_all_passwords(self) -> Dict[str, str]:
        """
        Retrieve passwords for all WiFi profiles
        """
        self.print_info("Scanning for saved WiFi profiles...")
        
        # Get all profiles [citation:5]
        profiles = self.get_all_profiles()
        
        if not profiles:
            self.print_warning("No WiFi profiles found on this system")
            return {}
        
        self.print_success(f"Found {len(profiles)} WiFi profile(s)")
        
        # Get password for each profile
        passwords = {}
        for i, profile in enumerate(profiles, 1):
            print(f"   [{i}/{len(profiles)}] Retrieving password for: {profile}...")
            password = self.get_profile_password(profile)
            passwords[profile] = password
        
        return passwords
    
    def display_passwords_table(self, passwords: Dict[str, str]):
        """
        Display passwords in a formatted table
        """
        if not passwords:
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 SAVED WIFI NETWORKS:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
        print(f"{'#':<3} {'WiFi Network (SSID)':<35} {'Password':<25}")
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
        
        for i, (profile, password) in enumerate(sorted(passwords.items()), 1):
            # Truncate long names
            display_profile = profile[:34] + "..." if len(profile) > 34 else profile
            
            # Color code based on password
            if password and password not in ["No password found", "Error retrieving"]:
                password_display = f"{Colors.GREEN}{password}{Colors.END}"
            elif password == "No password found":
                password_display = f"{Colors.YELLOW}No password (Open network?){Colors.END}"
            else:
                password_display = f"{Colors.RED}{password}{Colors.END}"
            
            print(f"{i:<3} {display_profile:<35} {password_display}")
        
        print(f"{Colors.CYAN}{'-'*70}{Colors.END}")
    
    def export_to_file(self, passwords: Dict[str, str], filename: str = "wifi_passwords.txt"):
        """
        Export passwords to a text file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("WIFI PASSWORDS EXPORT\n")
                f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*60 + "\n\n")
                
                for profile, password in sorted(passwords.items()):
                    f.write(f"Network: {profile}\n")
                    f.write(f"Password: {password}\n")
                    f.write("-"*40 + "\n")
            
            self.print_success(f"Passwords exported to: {filename}")
            return True
        except Exception as e:
            self.print_error(f"Failed to export: {e}")
            return False
    
    def show_system_info(self):
        """Display system information"""
        try:
            # Get Windows version
            ver_result = subprocess.run(['ver'], capture_output=True, text=True, shell=True)
            
            # Get network interfaces
            ip_result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            
            print(f"\n{Colors.BOLD}System Information:{Colors.END}")
            print(f"   OS: Windows")
            print(f"   User: {os.getenv('USERNAME', 'Unknown')}")
            print(f"   Computer: {os.getenv('COMPUTERNAME', 'Unknown')}")
            
        except:
            pass
    
    def run(self):
        """Main execution function"""
        self.clear_screen()
        self.print_banner()
        
        # Check if running on Windows [citation:5]
        if not self.check_windows():
            input(f"\n{Colors.PURPLE}Press Enter to exit...{Colors.END}")
            return
        
        # Legal disclaimer [citation:5]
        print(f"\n{Colors.BOLD}⚠️  LEGAL DISCLAIMER:{Colors.END}")
        print("This tool is for recovering YOUR OWN saved WiFi passwords.")
        print("Only use on systems you own or have explicit permission to access.")
        print("Unauthorized access to others' passwords may violate privacy laws.\n")
        
        accept = input(f"{Colors.PURPLE}Do you accept and wish to continue? (yes/no): {Colors.END}").lower()
        if accept not in ['yes', 'y']:
            self.print_info("Exiting...")
            return
        
        # Show system info
        self.show_system_info()
        
        # Retrieve all passwords [citation:5]
        print()
        passwords = self.retrieve_all_passwords()
        
        if passwords:
            # Display results
            self.display_passwords_table(passwords)
            
            # Summary
            open_networks = sum(1 for p in passwords.values() if p == "No password found")
            secured = len(passwords) - open_networks
            
            print(f"\n{Colors.BOLD}Summary:{Colors.END}")
            print(f"   Total networks: {len(passwords)}")
            print(f"   Secured networks (with passwords): {secured}")
            print(f"   Open networks: {open_networks}")
            
            # Ask to export
            export = input(f"\n{Colors.PURPLE}Export passwords to file? (yes/no): {Colors.END}").lower()
            if export in ['yes', 'y']:
                filename = input(f"{Colors.PURPLE}Filename (default: wifi_passwords.txt): {Colors.END}").strip()
                if not filename:
                    filename = "wifi_passwords.txt"
                self.export_to_file(passwords, filename)
        else:
            self.print_warning("No WiFi profiles found to display")
        
        input(f"\n{Colors.PURPLE}Press Enter to exit...{Colors.END}")


def main():
    """Main entry point"""
    try:
        retriever = WiFiPasswordRetriever()
        retriever.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Operation cancelled by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()