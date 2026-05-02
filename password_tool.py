#!/usr/bin/env python3
"""
🔐 PASSWORD GENERATOR & MANAGER - All-in-One Tool
Run with: python password_tool.py
"""

import os
import json
import base64
import random
import string
import getpass
import sys
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # Fixed typo here

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
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class PasswordTool:
    def __init__(self):
        self.data_file = "vault.enc"
        self.salt_file = "vault.salt"
        self.cipher = None
        self.vault = {}
        
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
    
    def print_warning(self, message):
        """Print warning message in yellow"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def print_password(self, password):
        """Print password in green"""
        print(f"{Colors.GREEN}{Colors.BOLD}{password}{Colors.END}")
    
    def print_prompt(self, message):
        """Print prompt in purple"""
        print(f"{Colors.PURPLE}{message}{Colors.END}", end="")
    
    def generate_key_from_password(self, password, salt):
        """Generate encryption key from master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def first_time_setup(self):
        """First time setup - create master password"""
        self.clear_screen()
        self.print_header("FIRST TIME SETUP")
        print(f"\n{Colors.BOLD}📝 Let's create your Master Password{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print("This password will be used to:")
        print("  • Generate new passwords")
        print("  • View saved passwords")
        print("  • Edit existing passwords")
        print("  • Manage your vault")
        print(f"\n{Colors.YELLOW}⚠️  WARNING: This password CANNOT be recovered if forgotten!{Colors.END}\n")
        
        while True:
            master_pass = getpass.getpass(f"{Colors.PURPLE}🔑 Create Master Password: {Colors.END}")
            if len(master_pass) < 8:
                self.print_error("Password must be at least 8 characters long!\n")
                continue
                
            confirm_pass = getpass.getpass(f"{Colors.PURPLE}🔑 Confirm Master Password: {Colors.END}")
            
            if master_pass != confirm_pass:
                self.print_error("Passwords don't match! Try again.\n")
                continue
            
            break
        
        # Generate and save salt
        salt = os.urandom(16)
        with open(self.salt_file, 'wb') as f:
            f.write(salt)
        
        # Generate key and create empty vault
        key = self.generate_key_from_password(master_pass, salt)
        self.cipher = Fernet(key)
        empty_vault = {}
        encrypted_vault = self.cipher.encrypt(json.dumps(empty_vault).encode())
        
        with open(self.data_file, 'wb') as f:
            f.write(encrypted_vault)
        
        self.print_success("Master Password created successfully!")
        print(f"\n{Colors.GREEN}🎉 Your password vault is ready to use!{Colors.END}")
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
        return True
    
    def login(self):
        """Login with master password"""
        self.clear_screen()
        self.print_header("WELCOME BACK")
        
        # Check if first time setup is needed
        if not os.path.exists(self.salt_file):
            print(f"{Colors.CYAN}👋 First time using Password Tool!{Colors.END}")
            self.first_time_setup()
            return True
        
        print(f"\n{Colors.BOLD}🔑 Please enter your Master Password to continue{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        
        # Load salt
        with open(self.salt_file, 'rb') as f:
            salt = f.read()
        
        # Try to login (3 attempts)
        attempts = 3
        while attempts > 0:
            master_pass = getpass.getpass(f"\n{Colors.PURPLE}🔑 Master Password: {Colors.END}")
            
            # Generate key and try to decrypt
            key = self.generate_key_from_password(master_pass, salt)
            self.cipher = Fernet(key)
            
            try:
                with open(self.data_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self.vault = json.loads(decrypted_data.decode())
                self.print_success("Login successful!")
                return True
                
            except:
                attempts -= 1
                if attempts > 0:
                    self.print_error(f"Wrong password! {attempts} attempts remaining.")
                else:
                    self.print_error("Too many failed attempts. Exiting...")
                    sys.exit(1)
    
    def save_vault(self):
        """Save the vault to encrypted file"""
        encrypted_data = self.cipher.encrypt(json.dumps(self.vault).encode())
        with open(self.data_file, 'wb') as f:
            f.write(encrypted_data)
    
    def generate_specific_password(self):
        """
        Generate password with specific format:
        - First letter Uppercase
        - Then 5 lowercase letters
        - Then 4 digits
        - Then 1 symbol
        """
        # Uppercase first letter
        first = random.choice(string.ascii_uppercase)
        
        # 5 lowercase letters
        middle = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        
        # 4 digits
        numbers = ''.join(random.choice(string.digits) for _ in range(4))
        
        # 1 symbol
        symbols = "!@#$%^&*"
        symbol = random.choice(symbols)
        
        # Combine all parts
        password = first + middle + numbers + symbol
        
        return password
    
    def password_generator_mode(self):
        """Password Generator Mode - Generate and optionally save passwords"""
        while True:
            self.clear_screen()
            self.print_header("PASSWORD GENERATOR MODE")
            
            print(f"\n{Colors.BOLD}📋 MENU:{Colors.END}")
            print("1. 🎲 Generate new password (format: Xxxxxx1234@)")
            print("2. 🔙 Back to main menu")
            
            choice = input(f"\n{Colors.PURPLE}Choose (1-2): {Colors.END}").strip()
            
            if choice == "1":
                self.generate_and_save()
            elif choice == "2":
                break
            else:
                self.print_error("Invalid choice!")
                input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def generate_and_save(self):
        """Generate password and optionally save it"""
        self.clear_screen()
        self.print_header("GENERATE NEW PASSWORD")
        
        # Generate password with specific format
        password = self.generate_specific_password()
        
        print(f"\n{Colors.BOLD}🔐 Your Generated Password:{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        print(f"\n   ", end="")
        self.print_password(password)
        print(f"\n{Colors.CYAN}{'-'*40}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Format: Uppercase + 5 lowercase + 4 digits + 1 symbol{Colors.END}")
        print(f"Example: {Colors.GREEN}Bhello1234@{Colors.END}\n")
        
        # Ask if they want to save it
        save = input(f"{Colors.PURPLE}💾 Do you want to save this password? (yes/no): {Colors.END}").lower()
        if save in ['yes', 'y']:
            self.save_generated_password(password)
        else:
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def save_generated_password(self, password):
        """Save a generated password to the vault"""
        print(f"\n{Colors.BOLD}📝 Let's save this password:{Colors.END}")
        
        website = input(f"{Colors.PURPLE}🌐 Website/Service name: {Colors.END}").strip()
        if not website:
            self.print_error("Website name is required!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        username = input(f"{Colors.PURPLE}👤 Username/Email: {Colors.END}").strip()
        if not username:
            self.print_error("Username is required!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        notes = input(f"{Colors.PURPLE}📝 Notes (optional): {Colors.END}").strip()
        
        # Create entry
        entry = {
            "username": username,
            "password": password,
            "notes": notes,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "generated": True
        }
        
        # Save to vault
        if website not in self.vault:
            self.vault[website] = []
        
        self.vault[website].append(entry)
        self.save_vault()
        
        self.print_success(f"Password saved for {website}!")
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def password_manager_mode(self):
        """Password Manager Mode - Search and manage passwords"""
        while True:
            self.clear_screen()
            self.print_header("PASSWORD MANAGER MODE")
            
            # Count total passwords
            total = sum(len(entries) for entries in self.vault.values())
            websites = len(self.vault)
            
            print(f"\n{Colors.BOLD}📊 VAULT SUMMARY:{Colors.END}")
            print(f"   • {total} password(s) saved")
            print(f"   • {websites} website(s)")
            
            print(f"\n{Colors.BOLD}📋 MENU:{Colors.END}")
            print("1. 🔍 Search for a website password")
            print("2. ✏️  Edit an existing password")
            print("3. 🗑️  Delete a password")
            print("4. 🔙 Back to main menu")
            
            choice = input(f"\n{Colors.PURPLE}Choose (1-4): {Colors.END}").strip()
            
            if choice == "1":
                self.search_password_fuzzy()
            elif choice == "2":
                self.edit_password()
            elif choice == "3":
                self.delete_password()
            elif choice == "4":
                break
            else:
                self.print_error("Invalid choice!")
                input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def calculate_similarity(self, s1, s2):
        """
        Calculate similarity between two strings using Levenshtein distance
        Returns a score between 0 and 1 (higher = more similar)
        """
        # Convert both to lowercase for comparison
        s1 = s1.lower()
        s2 = s2.lower()
        
        # If one string contains the other, give high similarity
        if s1 in s2 or s2 in s1:
            return 0.9
        
        # Calculate Levenshtein distance
        if len(s1) < len(s2):
            return self.calculate_similarity(s2, s1)
        
        if len(s2) == 0:
            return 0.0
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distance = previous_row[-1]
        max_len = max(len(s1), len(s2))
        similarity = 1 - (distance / max_len)
        
        return similarity
    
    def find_similar_websites(self, search_term, threshold=0.4):
        """
        Find websites similar to the search term
        Returns list of (website, similarity_score) tuples sorted by score
        """
        matches = []
        search_term = search_term.lower()
        
        for website in self.vault.keys():
            # Direct contains check (case insensitive)
            if search_term in website.lower():
                matches.append((website, 1.0))
                continue
            
            # Calculate similarity
            similarity = self.calculate_similarity(search_term, website)
            if similarity >= threshold:
                matches.append((website, similarity))
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def search_password_fuzzy(self):
        """Enhanced search with fuzzy matching and suggestions"""
        self.clear_screen()
        self.print_header("SEARCH PASSWORD")
        
        if not self.vault:
            self.print_error("No passwords saved yet!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}🔍 Fuzzy Search - I'll find it even if you type it wrong!{Colors.END}")
        print(f"{Colors.CYAN}{'-'*60}{Colors.END}")
        print(f"{Colors.YELLOW}Tips:{Colors.END}")
        print("  • Type in lowercase or uppercase - I don't mind")
        print("  • Make typos - I'll find close matches")
        print("  • Type part of the name - I'll find it")
        print(f"{Colors.CYAN}{'-'*60}{Colors.END}\n")
        
        # Ask for website
        search = input(f"{Colors.PURPLE}🌐 Website name (or part of it): {Colors.END}").strip()
        
        if not search:
            self.print_error("Please enter a website name!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        # Find similar websites
        matches = self.find_similar_websites(search)
        
        if not matches:
            print(f"\n{Colors.YELLOW}No exact or similar matches found for '{search}'{Colors.END}")
            
            # Show all websites as last resort
            print(f"\n{Colors.BOLD}Here are all your saved websites:{Colors.END}")
            for i, website in enumerate(sorted(self.vault.keys()), 1):
                count = len(self.vault[website])
                print(f"  {i}. {website} ({count} password{'s' if count > 1 else ''})")
            
            # Ask if they want to try again
            retry = input(f"\n{Colors.PURPLE}Try another search? (yes/no): {Colors.END}").lower()
            if retry in ['yes', 'y']:
                self.search_password_fuzzy()
                return
        else:
            # Show matches
            print(f"\n{Colors.GREEN}Found {len(matches)} matching website(s):{Colors.END}")
            print(f"{Colors.CYAN}{'-'*60}{Colors.END}")
            
            for idx, (website, score) in enumerate(matches, 1):
                # Show similarity score as stars
                stars = "⭐" * int(score * 5) + "☆" * (5 - int(score * 5))
                
                if score == 1.0:
                    match_type = "EXACT MATCH"
                    color = Colors.GREEN
                elif score >= 0.8:
                    match_type = "VERY CLOSE"
                    color = Colors.CYAN
                elif score >= 0.6:
                    match_type = "CLOSE"
                    color = Colors.YELLOW
                else:
                    match_type = "SIMILAR"
                    color = Colors.PURPLE
                
                print(f"\n{color}{idx}. {website}{Colors.END}")
                print(f"   {color}Match: {match_type} {stars} ({score:.1%}){Colors.END}")
            
            print(f"\n{Colors.CYAN}{'-'*60}{Colors.END}")
            
            # Let user choose which one to view
            print(f"\n{Colors.BOLD}Enter the number to view details, or press Enter to see all:{Colors.END}")
            choice = input(f"{Colors.PURPLE}Choice: {Colors.END}").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matches):
                    website = matches[idx][0]
                    self.display_website_passwords(website)
                else:
                    self.print_error("Invalid number!")
            else:
                # Show all matches
                for website, _ in matches:
                    self.display_website_passwords(website, show_header=False)
        
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def display_website_passwords(self, website, show_header=True):
        """Display passwords for a specific website"""
        if show_header:
            print(f"\n{Colors.BOLD}{Colors.CYAN}📌 {website.upper()}{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        
        entries = self.vault[website]
        for i, entry in enumerate(entries, 1):
            print(f"\n  {i}. Username: {Colors.BOLD}{entry['username']}{Colors.END}")
            print(f"     Password: ", end="")
            self.print_password(entry['password'])
            if entry.get('notes'):
                print(f"     Notes: {entry['notes']}")
            print(f"     Saved: {entry['created']}")
            if entry.get('last_modified') and entry['last_modified'] != entry['created']:
                print(f"     Modified: {entry['last_modified']}")
    
    def edit_password(self):
        """Edit an existing password"""
        self.clear_screen()
        self.print_header("EDIT PASSWORD")
        
        if not self.vault:
            self.print_error("No passwords saved yet!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        # Ask for website with fuzzy search
        print(f"\n{Colors.BOLD}Enter the website name to edit (I'll help you find it):{Colors.END}")
        search = input(f"{Colors.PURPLE}🌐 Website: {Colors.END}").strip()
        
        # Find matches
        matches = self.find_similar_websites(search)
        
        if not matches:
            self.print_error(f"No websites found matching '{search}'")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        elif len(matches) == 1:
            website = matches[0][0]
        else:
            # Show multiple matches
            print(f"\n{Colors.GREEN}Multiple matches found:{Colors.END}")
            for idx, (site, score) in enumerate(matches, 1):
                print(f"{idx}. {site} ({score:.1%} match)")
            
            choice = input(f"\n{Colors.PURPLE}Choose number: {Colors.END}").strip()
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(matches):
                self.print_error("Invalid choice!")
                return
            website = matches[int(choice)-1][0]
        
        entries = self.vault[website]
        
        if len(entries) == 1:
            # Only one entry, edit it directly
            self.edit_entry(website, entries[0], 0)
        else:
            # Multiple entries, ask which one
            print(f"\n{Colors.BOLD}Passwords for {website}:{Colors.END}")
            for i, entry in enumerate(entries, 1):
                print(f"{i}. {entry['username']}")
            
            try:
                choice = int(input(f"\n{Colors.PURPLE}Enter number to edit: {Colors.END}")) - 1
                if 0 <= choice < len(entries):
                    self.edit_entry(website, entries[choice], choice)
                else:
                    self.print_error("Invalid number!")
            except ValueError:
                self.print_error("Invalid input!")
        
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def edit_entry(self, website, entry, index):
        """Edit a specific password entry"""
        print(f"\n{Colors.BOLD}Editing password for {website}{Colors.END}")
        print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
        
        print(f"\nCurrent username: {entry['username']}")
        new_username = input(f"{Colors.PURPLE}New username (press Enter to keep current): {Colors.END}").strip()
        if new_username:
            entry['username'] = new_username
        
        print(f"\nCurrent password: ", end="")
        self.print_password(entry['password'])
        
        print(f"\n{Colors.BOLD}Password options:{Colors.END}")
        print("1. Keep current password")
        print("2. Generate new password (format: Xxxxxx1234@)")
        print("3. Enter custom password")
        
        choice = input(f"\n{Colors.PURPLE}Choose (1-3): {Colors.END}").strip()
        
        if choice == "2":
            new_password = self.generate_specific_password()
            print(f"\nNew generated password: ", end="")
            self.print_password(new_password)
            entry['password'] = new_password
        elif choice == "3":
            new_password = getpass.getpass(f"{Colors.PURPLE}Enter new password: {Colors.END}")
            if new_password:
                entry['password'] = new_password
        
        new_notes = input(f"\n{Colors.PURPLE}New notes (press Enter to keep current): {Colors.END}").strip()
        if new_notes:
            entry['notes'] = new_notes
        elif not new_notes and entry.get('notes'):
            keep = input(f"{Colors.PURPLE}Keep current notes? (yes/no): {Colors.END}").lower()
            if keep not in ['yes', 'y']:
                entry['notes'] = ""
        
        # Update modification time
        entry['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save changes
        self.vault[website][index] = entry
        self.save_vault()
        
        self.print_success("Password updated successfully!")
    
    def delete_password(self):
        """Delete a password entry"""
        self.clear_screen()
        self.print_header("DELETE PASSWORD")
        
        if not self.vault:
            self.print_error("No passwords to delete!")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        
        # Ask for website with fuzzy search
        print(f"\n{Colors.BOLD}Enter the website name to delete from:{Colors.END}")
        search = input(f"{Colors.PURPLE}🌐 Website: {Colors.END}").strip()
        
        # Find matches
        matches = self.find_similar_websites(search)
        
        if not matches:
            self.print_error(f"No websites found matching '{search}'")
            input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
            return
        elif len(matches) == 1:
            website = matches[0][0]
        else:
            # Show multiple matches
            print(f"\n{Colors.GREEN}Multiple matches found:{Colors.END}")
            for idx, (site, score) in enumerate(matches, 1):
                print(f"{idx}. {site} ({score:.1%} match)")
            
            choice = input(f"\n{Colors.PURPLE}Choose number: {Colors.END}").strip()
            if not choice.isdigit() or int(choice) < 1 or int(choice) > len(matches):
                self.print_error("Invalid choice!")
                return
            website = matches[int(choice)-1][0]
        
        entries = self.vault[website]
        
        if len(entries) == 1:
            # Single entry
            print(f"\nUsername: {entries[0]['username']}")
            print(f"Password: ", end="")
            self.print_password(entries[0]['password'])
            
            confirm = input(f"\n{Colors.PURPLE}⚠️  Delete this password? (yes/no): {Colors.END}").lower()
            if confirm in ['yes', 'y']:
                del self.vault[website]
                self.print_success("Password deleted!")
            else:
                self.print_warning("Deletion cancelled")
        else:
            # Multiple entries
            print(f"\n{Colors.BOLD}Passwords for {website}:{Colors.END}")
            for i, entry in enumerate(entries, 1):
                print(f"{i}. {entry['username']}")
            
            try:
                choice = int(input(f"\n{Colors.PURPLE}Enter number to delete: {Colors.END}")) - 1
                if 0 <= choice < len(entries):
                    confirm = input(f"{Colors.PURPLE}Delete password for {entries[choice]['username']}? (yes/no): {Colors.END}").lower()
                    if confirm in ['yes', 'y']:
                        self.vault[website].pop(choice)
                        if not self.vault[website]:
                            del self.vault[website]
                        self.print_success("Password deleted!")
                    else:
                        self.print_warning("Deletion cancelled")
                else:
                    self.print_error("Invalid number!")
            except ValueError:
                self.print_error("Invalid input!")
        
        # Save changes
        self.save_vault()
        input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")
    
    def main_menu(self):
        """Main menu - Choose between Generator and Manager"""
        while True:
            self.clear_screen()
            self.print_header("PASSWORD TOOL")
            
            print(f"\n{Colors.BOLD}🎯 WHAT WOULD YOU LIKE TO DO?{Colors.END}")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            print("1. 🎲 Password Generator")
            print("   → Generate new passwords (format: Xxxxxx1234@)")
            print("\n2. 🔐 Password Manager")
            print("   → Search, edit, and manage saved passwords")
            print("\n3. 🚪 Exit")
            print(f"{Colors.CYAN}{'-'*40}{Colors.END}")
            
            choice = input(f"\n{Colors.PURPLE}Choose (1, 2, or 3): {Colors.END}").strip()
            
            if choice == "1":
                self.password_generator_mode()
            elif choice == "2":
                self.password_manager_mode()
            elif choice == "3":
                self.clear_screen()
                print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.GREEN}👋 Thank you for using Password Tool!{Colors.END}")
                print(f"{Colors.BOLD}{Colors.YELLOW}🔒 Remember to keep your master password safe!{Colors.END}")
                print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")
                sys.exit(0)
            else:
                self.print_error("Invalid choice! Please choose 1, 2, or 3.")
                input(f"\n{Colors.PURPLE}Press Enter to continue...{Colors.END}")

def main():
    """Main entry point"""
    try:
        # Check for required package
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            print(f"\n{Colors.RED}❌ Required package 'cryptography' not found!{Colors.END}")
            print(f"\n{Colors.YELLOW}📦 Install it with:{Colors.END}")
            print(f"   {Colors.GREEN}pip install cryptography{Colors.END}")
            sys.exit(1)
        
        # Create and run tool
        tool = PasswordTool()
        
        # Login or setup
        if tool.login():
            tool.main_menu()
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.GREEN}👋 Goodbye! Stay secure! 🔒{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()