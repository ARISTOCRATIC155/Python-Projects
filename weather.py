import requests

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def get_temperature_color(temp_c):
    """Return color based on temperature"""
    try:
        temp = float(temp_c)
        if temp > 35:
            return Colors.RED
        elif temp > 25:
            return Colors.YELLOW
        elif temp > 15:
            return Colors.GREEN
        else:
            return Colors.PINK
    except:
        return Colors.RESET

def print_colored(text, color=Colors.RESET, bold=False):
    """Print text with specified color"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.RESET}")
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """Print a colored header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}╔{'═'*50}╗{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}║{text.center(50)}║{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}╚{'═'*50}╝{Colors.RESET}")

# Dictionary of common Kenyan cities with their proper formats
KENYAN_CITIES = {
    "nairobi": "Nairobi",
    "mombasa": "Mombasa",
    "kisumu": "Kisumu",
    "nakuru": "Nakuru",
    "eldoret": "Eldoret",
    "thika": "Thika",
    "kitale": "Kitale",
    "malindi": "Malindi",
    "lamu": "Lamu",
    "kakamega": "Kakamega",
    "kisii": "Kisii",
    "garissa": "Garissa",
    "wajir": "Wajir",
    "mandera": "Mandera",
    "machakos": "Machakos",
    "naivasha": "Naivasha",
    "nyeri": "Nyeri",
    "meru": "Meru",
    "embu": "Embu",
    "busia": "Busia",
    "bungoma": "Bungoma",
    "vihiga": "Vihiga",
    "siaya": "Siaya",
    "homa bay": "Homa Bay",
    "migori": "Migori",
    "nyamira": "Nyamira",
    "kericho": "Kericho",
    "bomet": "Bomet",
    "narok": "Narok",
    "kajiado": "Kajiado",
    "turkana": "Turkana",
    "marsabit": "Marsabit",
    "isiolo": "Isiolo",
    "laikipia": "Laikipia",
    "samburu": "Samburu",
    "trans nzoia": "Trans Nzoia",
    "uasin gishu": "Uasin Gishu",
    "elgeyo marakwet": "Elgeyo Marakwet",
    "nandi": "Nandi",
    "baringo": "Baringo",
    "pokot": "Pokot",
}

def format_city_name(city):
    """Format city name properly for the API"""
    city_lower = city.lower().strip()
    
    # Check if it's a Kenyan city
    if city_lower in KENYAN_CITIES:
        return KENYAN_CITIES[city_lower]
    
    # For other cities, just return with first letter capitalized
    return city.strip().title()

def get_weather_direct(city):
    """
    Direct approach - try multiple formats until one works
    This is the most reliable method
    """
    
    # List of formats to try in order
    formats_to_try = [
        city,  # Original input
        format_city_name(city),  # Properly formatted
        f"{city}, Kenya",  # With country
        f"{city},KE",  # With country code
        f"~{city}",  # wttr.in's fuzzy search
    ]
    
    for attempt in formats_to_try:
        try:
            url = f"https://wttr.in/{attempt}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "current_condition" in data and data["current_condition"]:
                    # Found working format!
                    return attempt, data
        except:
            continue
    
    return None, None

def get_weather(city):
    """Fetch and display weather with colors - works for ALL cities"""
    
    print_colored(f"🔍 Searching for weather in: {city}", Colors.CYAN)
    
    # Try to get weather data using multiple formats
    working_format, data = get_weather_direct(city)
    
    if not working_format:
        print_colored(f"\n❌ Could not find weather data for '{city}'", Colors.RED)
        print_colored("\n💡 Try one of these formats:", Colors.YELLOW)
        print_colored("   • Add country: 'Kisumu, Kenya'", Colors.CYAN)
        print_colored("   • Use airport code: 'KIS'", Colors.CYAN)
        print_colored("   • Be more specific: 'Kisumu, KE'", Colors.CYAN)
        
        # Show Kenyan city examples
        print_colored("\n🇰🇪 Kenyan cities that work:", Colors.GREEN)
        kenyan_examples = list(KENYAN_CITIES.keys())[:10]
        for i, kcity in enumerate(kenyan_examples, 1):
            if i % 5 == 0:
                print()
            print_colored(f"   • {kcity.title()}", Colors.CYAN, end="")
        print()
        return
    
    # If the working format is different from input, show what worked
    if working_format != city:
        print_colored(f"📌 Found weather for: {working_format}", Colors.GREEN)
    
    try:
        current = data["current_condition"][0]

        temperature = current["temp_C"]
        description = current["weatherDesc"][0]["value"]
        humidity = current["humidity"]
        wind = current["windspeedKmph"]
        feels_like = current["FeelsLikeC"]
        uv_index = current["uvIndex"]
        pressure = current["pressure"]
        visibility = current["visibility"]

        # Get color based on temperature
        temp_color = get_temperature_color(temperature)
        feels_like_color = get_temperature_color(feels_like)

        # Print beautiful colored output
        print_header(f"📍 WEATHER REPORT: {working_format.upper()}")

        # Temperature with color
        print(f"{Colors.CYAN}🌡️  Temperature:{Colors.RESET} ", end="")
        print_colored(f"{temperature}°C", temp_color, bold=True)
        
        # Feels like temperature
        print(f"{Colors.CYAN}🤔 Feels Like:{Colors.RESET} ", end="")
        print_colored(f"{feels_like}°C", feels_like_color)

        # Weather condition with emoji
        if "sun" in description.lower():
            emoji = "☀️"
        elif "cloud" in description.lower():
            emoji = "☁️"
        elif "rain" in description.lower():
            emoji = "🌧️"
        elif "snow" in description.lower():
            emoji = "❄️"
        elif "thunder" in description.lower():
            emoji = "⛈️"
        else:
            emoji = "⛅"
            
        print(f"{Colors.CYAN}{emoji} Condition:{Colors.RESET} ", end="")
        print_colored(description, Colors.GREEN if "sun" in description.lower() else Colors.RESET)

        # Other weather data
        print(f"{Colors.CYAN}💧 Humidity:{Colors.RESET} ", end="")
        print_colored(f"{humidity}%", Colors.BLUE)

        print(f"{Colors.CYAN}💨 Wind Speed:{Colors.RESET} ", end="")
        wind_speed = int(wind)
        if wind_speed > 30:
            wind_color = Colors.RED
        elif wind_speed > 15:
            wind_color = Colors.YELLOW
        else:
            wind_color = Colors.GREEN
        print_colored(f"{wind} km/h", wind_color)

        print(f"{Colors.CYAN}📊 Pressure:{Colors.RESET} ", end="")
        print_colored(f"{pressure} hPa", Colors.PINK)

        print(f"{Colors.CYAN}👁️  Visibility:{Colors.RESET} ", end="")
        print_colored(f"{visibility} km", Colors.CYAN)

        print(f"{Colors.CYAN}☀️ UV Index:{Colors.RESET} ", end="")
        uv = int(uv_index)
        if uv > 7:
            uv_color = Colors.RED
        elif uv > 3:
            uv_color = Colors.YELLOW
        else:
            uv_color = Colors.GREEN
        print_colored(uv_index, uv_color)

        # Weather tip based on conditions
        print(f"\n{Colors.BOLD}{Colors.BLUE}💡 WEATHER TIP:{Colors.RESET} ", end="")
        temp_int = int(temperature)
        if temp_int > 35:
            print_colored("Extreme heat! Stay hydrated and avoid sun exposure.", Colors.RED)
        elif temp_int > 25:
            print_colored("Warm weather! Wear light clothes and sunscreen.", Colors.YELLOW)
        elif temp_int > 15:
            print_colored("Pleasant weather! Great day for outdoor activities.", Colors.GREEN)
        elif temp_int > 5:
            print_colored("Cool weather! Bring a light jacket.", Colors.PINK)
        else:
            print_colored("Cold weather! Bundle up and stay warm.", Colors.BLUE)

        # Decorative footer
        print(f"{Colors.BLUE}{'─'*52}{Colors.RESET}\n")

    except Exception as e:
        print_colored(f"\n❌ Error parsing weather data: {e}", Colors.RED)

def main():
    """Main function with Kenyan city focus"""
    print_colored("╔══════════════════════════════════════════╗", Colors.BLUE, bold=True)
    print_colored("║     🌤️  KENYAN WEATHER CHECKER          ║", Colors.CYAN, bold=True)
    print_colored("║   ✓ Nairobi, Mombasa, Kisumu & MORE!    ║", Colors.GREEN, bold=True)
    print_colored("╚══════════════════════════════════════════╝", Colors.BLUE, bold=True)
    
    while True:
        print(f"\n{Colors.BOLD}Options:{Colors.RESET}")
        print(f"{Colors.GREEN}1.{Colors.RESET} Check weather for ANY city")
        print(f"{Colors.CYAN}2.{Colors.RESET} Nairobi 🇰🇪")
        print(f"{Colors.CYAN}3.{Colors.RESET} Mombasa 🇰🇪")
        print(f"{Colors.CYAN}4.{Colors.RESET} Kisumu 🇰🇪")
        print(f"{Colors.CYAN}5.{Colors.RESET} Nakuru 🇰🇪")
        print(f"{Colors.CYAN}6.{Colors.RESET} Eldoret 🇰🇪")
        print(f"{Colors.YELLOW}7.{Colors.RESET} List all Kenyan cities")
        print(f"{Colors.RED}8.{Colors.RESET} Exit")
        
        choice = input(f"\n{Colors.YELLOW}Enter your choice (1-8): {Colors.RESET}").strip()
        
        if choice == "1":
            city = input(f"{Colors.CYAN}Enter city name: {Colors.RESET}").strip()
            if city:
                get_weather(city)
            else:
                print_colored("❌ Please enter a city name!", Colors.RED)
        
        elif choice == "2":
            get_weather("Nairobi")
        elif choice == "3":
            get_weather("Mombasa")
        elif choice == "4":
            get_weather("Kisumu")
        elif choice == "5":
            get_weather("Nakuru")
        elif choice == "6":
            get_weather("Eldoret")
        elif choice == "7":
            print_colored("\n🇰🇪 KENYAN CITIES AVAILABLE:", Colors.GREEN, bold=True)
            cities = list(KENYAN_CITIES.keys())
            for i in range(0, len(cities), 4):
                row = cities[i:i+4]
                print("   ", end="")
                for city in row:
                    print_colored(f"• {city.title():12}", Colors.CYAN, end="")
                print()
            print()
        elif choice == "8":
            print_colored("\n👋 Kwaheri! Stay weather-aware!\n", Colors.PINK, bold=True)
            break
        else:
            print_colored("❌ Invalid choice! Please enter 1-8.", Colors.RED)

if __name__ == "__main__":
    main()