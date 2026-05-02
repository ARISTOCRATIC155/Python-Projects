#!/usr/bin/env python3
"""
🔐 PASSWORD BRUTE FORCE SIMULATOR
A tool to test password strength by simulating different attack methods
"""

import itertools
import random
import string
import time
import hashlib
import sys
import os
from datetime import datetime, timedelta

# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class BruteForceSimulator:
    def __init__(self):
        self.common_passwords = self.load_common_passwords()
        self.attempts = 0
        self.start_time = None
        self.end_time = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🔐 {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    
    def print_success(self, message):
        """Print success message in green"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        """Print error message in red"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_info(self, message):
        """Print info message in blue"""
        print(f"{Colors.BLUE}ℹ️ {message}{Colors.END}")
    
    def print_warning(self, message):
        """Print warning message in yellow"""
        print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")
    
    def print_prompt(self, message):
        """Print prompt in purple"""
        print(f"{Colors.PURPLE}{message}{Colors.END}", end="")
    
    def load_common_passwords(self):
        """Load a list of common passwords"""
        return [
            "password", "123456", "12345678", "1234", "qwerty", "12345", 
            "dragon", "pussy", "baseball", "football", "letmein", "monkey",
            "abc123", "mustang", "access", "shadow", "master", "michael",
            "superman", "696969", "123123", "batman", "trustno1", "admin",
            "hello", "secret", "love", "computer", "password1", "password123",
            "admin123", "root", "toor", "qwerty123", "welcome", "passw0rd",
            "iloveyou", "princess", "sunshine", "whatever", "donald", "ashley",
            "maggie", "tigger", "charlie", "summer", "hockey", "jackson",
            "camaro", "fuckyou", "fucker", "asdfgh", "zxcvbn", "1234567",
            "123456789", "1234567890", "987654321", "qwertyuiop", "q1w2e3r4",
            "pass", "password1234", "password12345", "pass123", "pass1234",
            "p@ssw0rd", "P@ssw0rd", "P@ssword", "Password1", "Password123",
            "adminadmin", "administrator", "root123", "toor123", "test",
            "test123", "guest", "guest123", "user", "user123", "login",
            "login123", "welcome123", "letmein123", "hello123", "hi123",
            "nopass", "nopassword", "blank", "empty", "null", "none",
            "god", "god123", "jesus", "jesus123", "christ", "christ123",
            "money", "money123", "cash", "cash123", "dollar", "dollar123",
            "freedom", "freedom123", "america", "america123", "usa", "usa123",
            "qwerty123456", "qazwsx", "qazwsxedc", "zaq12wsx", "1qaz2wsx",
            "1q2w3e4r", "1q2w3e4r5t", "1qazxsw2", "q1w2e3r4t5", "qwer1234"
        ]
    
    def get_password_strength(self, password):
        """Analyze password strength"""
        score = 0
        feedback = []
        
        # Check length
        length = len(password)
        if length >= 12:
            score += 3
        elif length >= 8:
            score += 2
        elif length >= 6:
            score += 1
        else:
            feedback.append("Password is too short")
        
        # Check character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if has_upper:
            score += 1
        if has_lower:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 2
        
        # Check for common patterns
        if password.lower() in self.common_passwords:
            score -= 2
            feedback.append("Password is too common")
        
        if password.isdigit():
            score -= 1
            feedback.append("Only numbers - very weak")
        
        if password.isalpha():
            score -= 1
            feedback.append("Only letters - could be stronger")
        
        # Determine strength level
        if score >= 8:
            strength = "VERY STRONG 💪"
            color = Colors.GREEN
        elif score >= 6:
            strength = "STRONG 👍"
            color = Colors.GREEN
        elif score >= 4:
            strength = "MEDIUM ⚠️"
            color = Colors.YELLOW
        elif score >= 2:
            strength = "WEAK ❌"
            color = Colors.RED
        else:
            strength = "VERY WEAK 💀"
            color = Colors.RED
        
        return strength, color, score, feedback
    
    def estimate_crack_time(self, password, attempts_per_second=1000000):
        """Estimate time to crack password based on complexity"""
        char_sets = []
        
        if any(c.islower() for c in password):
            char_sets.append(26)  # lowercase
        if any(c.isupper() for c in password):
            char_sets.append(26)  # uppercase
        if any(c.isdigit() for c in password):
            char_sets.append(10)  # digits
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            char_sets.append(32)  # special characters
        
        if not char_sets:
            return "Instant"
        
        # Calculate total possible combinations
        char_space = sum(char_sets)
        length = len(password)
        combinations = char_space ** length
        
        # Calculate time
        seconds = combinations / attempts_per_second
        
        if seconds < 1:
            return "Less than 1 second"
        elif seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.1f} days"
        elif seconds < 315360000:
            return f"{seconds/31536000:.1f} years"
        else:
            centuries = seconds / 31536000 / 100
            if centuries > 1000:
                return "Centuries (practically uncrackable)"
            else:
                return f"{centuries:.1f} centuries"
    
    def dictionary_attack(self, target_password):
        """Simulate a dictionary attack using common passwords"""
        self.print_info("Starting dictionary attack...")
        time.sleep(0.5)
        
        self.attempts = 0
        self.start_time = time.time()
        
        # Try common passwords first
        for password in self.common_passwords:
            self.attempts += 1
            if password == target_password:
                self.end_time = time.time()
                return True
            
            # Add common variations
            variations = [
                password + "123",
                password + "1234",
                password + "!",
                password.capitalize(),
                password.upper(),
                password + str(random.randint(10, 99))
            ]
            
            for var in variations:
                self.attempts += 1
                if var == target_password:
                    self.end_time = time.time()
                    return True
        
        self.end_time = time.time()
        return False
    
    def brute_force_attack(self, target_password, max_length=4):
        """Simulate a brute force attack up to a certain length"""
        self.print_info(f"Starting brute force attack (up to {max_length} characters)...")
        time.sleep(0.5)
        
        chars = string.ascii_lowercase + string.digits
        self.attempts = 0
        self.start_time = time.time()
        
        for length in range(1, max_length + 1):
            for attempt in itertools.product(chars, repeat=length):
                self.attempts += 1
                test_pass = ''.join(attempt)
                
                # Show progress occasionally
                if self.attempts % 100000 == 0:
                    print(f"\r{Colors.YELLOW}Attempts: {self.attempts:,} - Current: {test_pass}{Colors.END}", end="")
                
                if test_pass == target_password:
                    print()  # New line after progress
                    self.end_time = time.time()
                    return True
                
                # Limit for demo purposes
                if self.attempts > 1000000:
                    print()  # New line after progress
                    self.end_time = time.time()
                    return False
        
        print()  # New line after progress
        self.end_time = time.time()
        return False
    
    def mixed_attack(self, target_password):
        """Combination of dictionary and smart brute force"""
        self.print_info("Starting intelligent attack (dictionary + variations)...")
        time.sleep(0.5)
        
        self.attempts = 0
        self.start_time = time.time()
        
        # First try dictionary
        for password in self.common_passwords:
            self.attempts += 1
            
            # Try the password itself
            if password == target_password:
                self.end_time = time.time()
                return True
            
            # Try common leet speak substitutions
            leet_map = {
                'a': ['4', '@'],
                'e': ['3'],
                'i': ['1', '!'],
                'o': ['0'],
                's': ['5', '$'],
                't': ['7'],
                'b': ['8'],
                'g': ['9']
            }
            
            # Generate leet variations
            for char, replacements in leet_map.items():
                for rep in replacements:
                    leet_pass = password.replace(char, rep)
                    self.attempts += 1
                    if leet_pass == target_password:
                        self.end_time = time.time()
                        return True
            
            # Try with numbers at the end
            for num in range(0, 100):
                self.attempts += 1
                if f"{password}{num}" == target_password:
                    self.end_time = time.time()
                    return True
                
                self.attempts += 1
                if f"{password}{num:02d}" == target_password:
                    self.end_time = time.time()
                    return True
        
        # Try common patterns
        patterns = [
            "123456", "password", "qwerty", "abc123", "admin",
            "letmein", "welcome", "monkey", "sunshine", "master"
        ]
        
        for pattern in patterns:
            for year in range(1990, 2025):
                self.attempts += 1
                if f"{pattern}{year}" == target_password:
                    self.end_time = time.time()
                    return True
        
        self.end_time = time.time()
        return False
    
    def show_results(self, cracked, method):
        """Display the results of the attack"""
        time_taken = self.end_time - self.start_time
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        if cracked:
            self.print_success(f"Password CRACKED using {method}!")
        else:
            self.print_error(f"Password NOT cracked using {method}")
        
        print(f"\n{Colors.BOLD}📊 Attack Statistics:{Colors.END}")
        print(f"   • Attempts made: {Colors.GREEN}{self.attempts:,}{Colors.END}")
        print(f"   • Time taken: {Colors.YELLOW}{time_taken:.2f} seconds{Colors.END}")
        print(f"   • Attempts per second: {Colors.BLUE}{self.attempts/time_taken:.0f}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    def run(self):
        """Main program loop"""
        while True:
            self.clear_screen()
            self.print_header("PASSWORD BRUTE FORCE SIMULATOR")
            
            print(f"\n{Colors.BOLD}📋 MENU:{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            print("1. 🔍 Test a specific password")
            print("2. 🎲 Generate random password and test it")
            print("3. 📊 View common passwords list")
            print("4. ❓ Learn about password security")
            print("5. 🚪 Exit")
            
            choice = input(f"\n{Colors.PURPLE}Choose (1-5): {Colors.END}").strip()
            
            if choice == "1":
                self.test_specific_password()
            elif choice == "2":
                self.test_random_password()
            elif choice == "3":
                self.show_common_passwords()
            elif choice == "4":
                self.show_security_tips()
            elif choice == "5":
                self.print_success("Stay secure! Goodbye!")
                break
    
    def test_specific_password(self):
        """Test a user-provided password"""
        self.clear_screen()
        self.print_header("TEST SPECIFIC PASSWORD")
        
        self.print_prompt("🔑 Enter password to test: ")
        password = input().strip()
        
        if not password:
            self.print_error("No password entered!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        # Show password strength
        strength, color, score, feedback = self.get_password_strength(password)
        crack_time = self.estimate_crack_time(password)
        
        print(f"\n{Colors.BOLD}📊 PASSWORD ANALYSIS:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print(f"Password: {Colors.BOLD}{password}{Colors.END}")
        print(f"Length: {len(password)} characters")
        print(f"Strength: {color}{strength}{Colors.END} (Score: {score}/10)")
        print(f"Est. crack time: {Colors.YELLOW}{crack_time}{Colors.END}")
        
        if feedback:
            print(f"\n{Colors.BOLD}Suggestions:{Colors.END}")
            for tip in feedback:
                print(f"  {Colors.YELLOW}•{Colors.END} {tip}")
        
        print(f"\n{Colors.BOLD}⚔️  Select attack method to simulate:{Colors.END}")
        print("1. 📚 Dictionary attack (common passwords)")
        print("2. 🔢 Brute force (up to 4 chars, letters+numbers)")
        print("3. 🧠 Intelligent attack (dictionary + variations)")
        
        attack_choice = input(f"\n{Colors.PURPLE}Choose (1-3): {Colors.END}").strip()
        
        if attack_choice == "1":
            cracked = self.dictionary_attack(password)
            self.show_results(cracked, "Dictionary Attack")
        elif attack_choice == "2":
            cracked = self.brute_force_attack(password)
            self.show_results(cracked, "Brute Force Attack")
        elif attack_choice == "3":
            cracked = self.mixed_attack(password)
            self.show_results(cracked, "Intelligent Attack")
        
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def test_random_password(self):
        """Generate and test a random password"""
        self.clear_screen()
        self.print_header("RANDOM PASSWORD TEST")
        
        print(f"\n{Colors.BOLD}Select password type:{Colors.END}")
        print("1. 🔢 Weak (6 chars, lowercase only)")
        print("2. 🔐 Medium (8 chars, letters+numbers)")
        print("3. 💪 Strong (12 chars, all types)")
        print("4. 🏆 Very Strong (16 chars, all types + special)")
        
        choice = input(f"\n{Colors.PURPLE}Choose (1-4): {Colors.END}").strip()
        
        if choice == "1":
            chars = string.ascii_lowercase
            length = 6
            pwd_type = "WEAK"
        elif choice == "2":
            chars = string.ascii_letters + string.digits
            length = 8
            pwd_type = "MEDIUM"
        elif choice == "3":
            chars = string.ascii_letters + string.digits
            length = 12
            pwd_type = "STRONG"
        else:
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            length = 16
            pwd_type = "VERY STRONG"
        
        password = ''.join(random.choice(chars) for _ in range(length))
        
        print(f"\n{Colors.GREEN}Generated {pwd_type} password:{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{password}{Colors.END}")
        
        # Analyze the password
        strength, color, score, feedback = self.get_password_strength(password)
        crack_time = self.estimate_crack_time(password)
        
        print(f"\n{Colors.BOLD}📊 ANALYSIS:{Colors.END}")
        print(f"Strength: {color}{strength}{Colors.END}")
        print(f"Est. crack time: {Colors.YELLOW}{crack_time}{Colors.END}")
        
        print(f"\n{Colors.BOLD}⚔️  Run attack simulation?{Colors.END}")
        simulate = input(f"{Colors.PURPLE}Run intelligent attack? (yes/no): {Colors.END}").lower()
        
        if simulate in ['yes', 'y']:
            cracked = self.mixed_attack(password)
            self.show_results(cracked, "Intelligent Attack")
        
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def show_common_passwords(self):
        """Display list of common passwords"""
        self.clear_screen()
        self.print_header("TOP 50 COMMON PASSWORDS")
        
        print(f"\n{Colors.RED}⚠️  NEVER use these passwords!{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        
        for i, pwd in enumerate(self.common_passwords[:50], 1):
            print(f"{i:2d}. {Colors.YELLOW}{pwd}{Colors.END}")
            
            if i % 10 == 0:
                print()
        
        print(f"\n{Colors.BOLD}Total common passwords in database: {len(self.common_passwords)}{Colors.END}")
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def show_security_tips(self):
        """Display password security tips"""
        self.clear_screen()
        self.print_header("PASSWORD SECURITY TIPS")
        
        tips = [
            ("Length matters", "Use at least 12 characters"),
            ("Mix it up", "Combine uppercase, lowercase, numbers, and symbols"),
            ("Avoid common words", "Don't use dictionary words or common patterns"),
            ("No personal info", "Avoid names, birthdays, or personal details"),
            ("Unique passwords", "Use different passwords for different accounts"),
            ("Password manager", "Consider using a password manager"),
            ("Two-factor authentication", "Enable 2FA whenever possible"),
            ("Regular changes", "Change important passwords periodically"),
            ("Beware of leaks", "Check if your passwords have been compromised"),
            ("Longer is better", "A 16-character password is exponentially stronger than 8")
        ]
        
        print(f"\n{Colors.GREEN}📌 Top 10 Password Security Tips:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*50}{Colors.END}")
        
        for i, (title, tip) in enumerate(tips, 1):
            print(f"{Colors.YELLOW}{i}. {title}:{Colors.END}")
            print(f"   {tip}\n")
        
        print(f"\n{Colors.BOLD}⏱️  Estimated crack times:{Colors.END}")
        print(f"   6 chars (lowercase): {Colors.YELLOW}Seconds{Colors.END}")
        print(f"   8 chars (mixed): {Colors.YELLOW}Hours to days{Colors.END}")
        print(f"   12 chars (mixed): {Colors.YELLOW}Years{Colors.END}")
        print(f"   16 chars (all types): {Colors.GREEN}Centuries{Colors.END}")
        
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")

def main():
    """Main entry point"""
    try:
        simulator = BruteForceSimulator()
        simulator.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Goodbye! Stay secure!{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()