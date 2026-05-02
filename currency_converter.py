import requests
import re

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class CurrencyConverter:
    def __init__(self):
        # Complete dictionary of world currencies
        self.currencies = {
            'USD': 'US Dollar',
            'EUR': 'Euro',
            'GBP': 'British Pound',
            'JPY': 'Japanese Yen',
            'KES': 'Kenyan Shilling',
            'CNY': 'Chinese Yuan',
            'INR': 'Indian Rupee',
            'CAD': 'Canadian Dollar',
            'AUD': 'Australian Dollar',
            'CHF': 'Swiss Franc',
            'ZAR': 'South African Rand',
            'NGN': 'Nigerian Naira',
            'GHS': 'Ghanaian Cedi',
            'UGX': 'Ugandan Shilling',
            'TZS': 'Tanzanian Shilling',
            'RWF': 'Rwandan Franc',
            'ETB': 'Ethiopian Birr',
            'MAD': 'Moroccan Dirham',
            'EGP': 'Egyptian Pound',
            'BRL': 'Brazilian Real',
            'RUB': 'Russian Ruble',
            'KRW': 'South Korean Won',
            'SGD': 'Singapore Dollar',
            'HKD': 'Hong Kong Dollar',
            'NZD': 'New Zealand Dollar',
            'MXN': 'Mexican Peso',
            'TRY': 'Turkish Lira',
            'SEK': 'Swedish Krona',
            'NOK': 'Norwegian Krone',
            'DKK': 'Danish Krone',
            'PLN': 'Polish Złoty',
            'CZK': 'Czech Koruna',
            'HUF': 'Hungarian Forint',
            'ILS': 'Israeli Shekel',
            'SAR': 'Saudi Riyal',
            'AED': 'UAE Dirham',
            'THB': 'Thai Baht',
            'MYR': 'Malaysian Ringgit',
            'IDR': 'Indonesian Rupiah',
            'PHP': 'Philippine Peso',
            'VND': 'Vietnamese Dong',
            'PKR': 'Pakistani Rupee',
            'BDT': 'Bangladeshi Taka',
            'LKR': 'Sri Lankan Rupee',
            'NPR': 'Nepalese Rupee',
        }
        
        # Common variations/aliases
        self.aliases = {
            'ksh': 'KES',
            'shilling': 'KES',
            'kenya': 'KES',
            'usd': 'USD',
            'dollar': 'USD',
            'us': 'USD',
            'eur': 'EUR',
            'euro': 'EUR',
            'gbp': 'GBP',
            'pound': 'GBP',
            'yen': 'JPY',
            'japan': 'JPY',
            'rupee': 'INR',
            'india': 'INR',
            'yuan': 'CNY',
            'china': 'CNY',
            'rand': 'ZAR',
            'south africa': 'ZAR',
            'naira': 'NGN',
            'nigeria': 'NGN',
            'cedi': 'GHS',
            'ghana': 'GHS',
        }
    
    def print_color(self, text, color=Colors.RESET, bold=False, end='\n'):
        if bold:
            print(f"{Colors.BOLD}{color}{text}{Colors.RESET}", end=end)
        else:
            print(f"{color}{text}{Colors.RESET}", end=end)
    
    def print_header(self, text):
        print(f"\n{Colors.BLUE}{Colors.BOLD}╔{'═'*60}╗{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}║{text.center(60)}║{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}╚{'═'*60}╝{Colors.RESET}")
    
    def normalize_currency(self, input_text):
        """Convert user input to standard currency code"""
        if not input_text:
            return None
        
        # Convert to uppercase for standard codes
        upper_input = input_text.upper().strip()
        
        # Check if it's already a valid code
        if upper_input in self.currencies:
            return upper_input
        
        # Check aliases (case-insensitive)
        lower_input = input_text.lower().strip()
        if lower_input in self.aliases:
            return self.aliases[lower_input]
        
        # Try partial matches
        for code, name in self.currencies.items():
            if lower_input in name.lower() or lower_input in code.lower():
                return code
        
        return None
    
    def list_currencies(self):
        """Display all available currencies"""
        self.print_header("💰 AVAILABLE CURRENCIES")
        
        # Sort currencies by code
        sorted_currencies = sorted(self.currencies.items())
        
        # Display in columns
        count = 0
        for code, name in sorted_currencies:
            print(f"{Colors.CYAN}{code}{Colors.RESET}: {name:<25}", end='')
            count += 1
            if count % 3 == 0:
                print()
        
        print(f"\n\n{Colors.GREEN}✓ Total: {len(self.currencies)} currencies{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Examples: KES (Kenyan Shilling), USD (US Dollar), EUR (Euro){Colors.RESET}")
    
    def get_exchange_rate(self, from_curr, to_curr):
        """Fetch exchange rate from API"""
        try:
            # Using a reliable free API
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if to_curr in data['rates']:
                    return {
                        'success': True,
                        'rate': data['rates'][to_curr],
                        'date': data['date']
                    }
            
            # Fallback to another API
            url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_curr.lower()}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if to_curr.lower() in data[from_curr.lower()]:
                    return {
                        'success': True,
                        'rate': data[from_curr.lower()][to_curr.lower()],
                        'date': 'latest'
                    }
            
            return {'success': False}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def convert(self):
        """Main conversion function"""
        self.print_header("💱 CURRENCY CONVERTER")
        
        # Get amount
        while True:
            try:
                amount_str = input(f"{Colors.YELLOW}Enter amount: {Colors.RESET}").strip()
                # Extract number from input (handles "1ksh", "100 USD", etc.)
                numbers = re.findall(r"[-+]?\d*\.?\d+", amount_str)
                if numbers:
                    amount = float(numbers[0])
                    if amount > 0:
                        break
                    else:
                        self.print_color("❌ Amount must be positive!", Colors.RED)
                else:
                    self.print_color("❌ Please enter a valid number!", Colors.RED)
            except:
                self.print_color("❌ Invalid input!", Colors.RED)
        
        # Get source currency
        while True:
            from_input = input(f"{Colors.YELLOW}From currency (e.g., USD, KES, Euro): {Colors.RESET}").strip()
            if from_input.lower() == 'list':
                self.list_currencies()
                continue
            
            from_curr = self.normalize_currency(from_input)
            if from_curr:
                break
            else:
                self.print_color(f"❌ '{from_input}' is not a valid currency!", Colors.RED)
                self.print_color("💡 Try: USD, KES, EUR, or 'dollar', 'shilling', 'euro'", Colors.YELLOW)
        
        # Get target currency
        while True:
            to_input = input(f"{Colors.YELLOW}To currency (e.g., USD, KES, Euro): {Colors.RESET}").strip()
            if to_input.lower() == 'list':
                self.list_currencies()
                continue
            
            to_curr = self.normalize_currency(to_input)
            if to_curr:
                break
            else:
                self.print_color(f"❌ '{to_input}' is not a valid currency!", Colors.RED)
                self.print_color("💡 Try: USD, KES, EUR, or 'dollar', 'shilling', 'euro'", Colors.YELLOW)
        
        # Show what we're converting
        self.print_color(f"\n🔄 Converting {amount} {from_curr} to {to_curr}...", Colors.CYAN)
        
        # Get rate
        result = self.get_exchange_rate(from_curr, to_curr)
        
        if result['success']:
            converted = amount * result['rate']
            
            # Choose color based on rate
            rate_color = Colors.GREEN if result['rate'] > 1 else Colors.RED if result['rate'] < 1 else Colors.YELLOW
            
            print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
            print(f"{Colors.BLUE}Date:{Colors.RESET} {result['date']}")
            print(f"{Colors.BLUE}Rate:{Colors.RESET} 1 {from_curr} = ", end="")
            self.print_color(f"{result['rate']:.4f} {to_curr}", rate_color, bold=True)
            
            print(f"\n{Colors.BOLD}RESULT:{Colors.RESET} ", end="")
            self.print_color(f"{amount:,.2f} {from_curr}", Colors.CYAN, bold=True)
            print(f" = ", end="")
            
            # Color the result
            result_color = Colors.GREEN if converted > amount else Colors.RED
            self.print_color(f"{converted:,.2f} {to_curr}", result_color, bold=True)
            print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}\n")
            
            # Show full names
            print(f"{Colors.PINK}{self.currencies[from_curr]} → {self.currencies[to_curr]}{Colors.RESET}")
            
        else:
            self.print_color(f"\n❌ Could not fetch exchange rate. Please try again.", Colors.RED)
            self.print_color("💡 Make sure you have an internet connection", Colors.YELLOW)

def main():
    converter = CurrencyConverter()
    
    print(f"{Colors.BOLD}{Colors.CYAN}Loading currency converter...{Colors.RESET}")
    
    while True:
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.PINK}🌍 GLOBAL CURRENCY CONVERTER 🌍{Colors.RESET}".center(68))
        print(f"{Colors.BOLD}{Colors.YELLOW}Supported: {len(converter.currencies)}+ currencies including KES, NGN, GHS{Colors.RESET}".center(68))
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
        print(f"  {Colors.GREEN}1.{Colors.RESET} 💱 Convert Currency")
        print(f"  {Colors.CYAN}2.{Colors.RESET} 📋 List Available Currencies")
        print(f"  {Colors.RED}3.{Colors.RESET} 🚪 Exit")
        
        choice = input(f"\n{Colors.BOLD}Enter your choice (1-3): {Colors.RESET}").strip()
        
        if choice == "1":
            converter.convert()
        elif choice == "2":
            converter.list_currencies()
        elif choice == "3":
            print(f"\n{Colors.PINK}{Colors.BOLD}Thank you for using Currency Converter! 👋{Colors.RESET}")
            break
        else:
            print(f"\n{Colors.RED}❌ Invalid choice. Please enter 1-3.{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.RESET}")