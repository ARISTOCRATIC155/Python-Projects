import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from opencage.geocoder import OpenCageGeocode
import folium
from folium import plugins
import webbrowser
import os
from datetime import datetime
import json

# ============================================
# PART 1: COLOR CODES FOR BEAUTIFUL OUTPUT
# ============================================

class Colors:
    """ANSI color codes for terminal output"""
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # Resets color back to normal

def print_color(text, color=Colors.GREEN, bold=False):
    """Helper function to print colored text"""
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.END}")
    else:
        print(f"{color}{text}{Colors.END}")

def print_header(text):
    """Print a header in pink and bold"""
    print(f"\n{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PINK}🔍 {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PINK}{'='*60}{Colors.END}")

def print_success(text):
    """Print success message in green"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_info(text):
    """Print info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def print_warning(text):
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    """Print error message in red"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_data(label, value, label_color=Colors.CYAN, value_color=Colors.GREEN):
    """Print labeled data with colors"""
    print(f"{label_color}{label}:{Colors.END} {value_color}{value}{Colors.END}")

# ============================================
# PART 2: YOUR OPENCAGE API KEY
# ============================================

# !!! REPLACE THIS WITH YOUR ACTUAL API KEY !!!
OPENCAGE_API_KEY = "ba5badabd2b349fca709f994e5c51fb4"

# ============================================
# PART 3: MAIN PHONE TRACKER CLASS
# ============================================

class PhoneNumberTracker:
    def __init__(self, api_key):
        """Initialize the tracker with OpenCage API key"""
        self.geocoder = OpenCageGeocode(api_key)
        
    def get_phone_info(self, phone_number):
        """Extract all available information from the phone number"""
        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_number)
            
            # Check if number is valid
            if not phonenumbers.is_valid_number(parsed_number):
                return {"error": "Invalid phone number"}
            
            # Get basic information
            location = geocoder.description_for_number(parsed_number, "en")
            service_provider = carrier.name_for_number(parsed_number, "en")
            time_zones = timezone.time_zones_for_number(parsed_number)
            is_possible = phonenumbers.is_possible_number(parsed_number)
            number_type = phonenumbers.number_type(parsed_number)
            
            # Convert number type to readable format
            type_mapping = {
                0: "Fixed Line",
                1: "Mobile",
                2: "Fixed Line or Mobile",
                3: "Toll Free",
                4: "Premium Rate",
                5: "Shared Cost",
                6: "VoIP",
                7: "Personal Number",
                8: "Pager",
                9: "Universal Access",
                10: "Unknown"
            }
            
            return {
                "phone_number": phone_number,
                "national_format": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                "international_format": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "location": location,
                "carrier": service_provider if service_provider else "Unknown",
                "timezones": ", ".join(time_zones),
                "is_valid": phonenumbers.is_valid_number(parsed_number),
                "is_possible": is_possible,
                "number_type": type_mapping.get(number_type, "Unknown"),
                "country_code": parsed_number.country_code,
                "national_number": parsed_number.national_number
            }
            
        except Exception as e:
            return {"error": f"Error processing number: {str(e)}"}
    
    def get_coordinates(self, location):
        """Get coordinates and detailed location data from OpenCage"""
        try:
            results = self.geocoder.geocode(
                location,
                language='en',
                limit=1,
                no_annotations=0  # Get all available annotations
            )
            
            if results and len(results) > 0:
                result = results[0]
                
                # Extract all useful information from the response
                location_data = {
                    "lat": result['geometry']['lat'],
                    "lng": result['geometry']['lng'],
                    "formatted_address": result['formatted'],
                    "confidence": result.get('confidence', 0),
                    "components": result.get('components', {}),
                    "bounds": result.get('bounds', None)
                }
                
                # Add annotations if available
                if 'annotations' in result:
                    location_data['annotations'] = result['annotations']
                    
                return location_data
            else:
                return {"error": "Location not found"}
                
        except Exception as e:
            return {"error": f"Geocoding error: {str(e)}"}
    
    def create_map(self, location_data, phone_info):
        """Create an interactive map with the location and multiple view options"""
        try:
            # Create map centered on the location
            m = folium.Map(
                location=[location_data['lat'], location_data['lng']],
                zoom_start=15,  # Closer zoom for better detail
                control_scale=True
            )
            
            # ===== ADD REAL MAP LAYERS (Like Google Maps) =====
            
            # 1. OpenStreetMap (Standard Street Map)
            folium.TileLayer(
                tiles='OpenStreetMap',
                name='Street Map',
                attr='OpenStreetMap',
                overlay=False,
                control=True
            ).add_to(m)
            
            # 2. Satellite View (Like Google Maps Satellite)
            folium.TileLayer(
                tiles='https://server.arthurqm-tile.osgeo.org/google/sat/{z}/{x}/{y}.jpg',
                name='Satellite View',
                attr='Google Satellite',
                overlay=False,
                control=True,
                max_zoom=20
            ).add_to(m)
            
            # 3. Hybrid View (Satellite with Labels)
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                name='Hybrid (Satellite + Labels)',
                attr='Google Hybrid',
                overlay=False,
                control=True,
                max_zoom=20
            ).add_to(m)
            
            # 4. Terrain View
            folium.TileLayer(
                tiles='https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}',
                name='Terrain View',
                attr='Google Terrain',
                overlay=False,
                control=True,
                max_zoom=20
            ).add_to(m)
            
            # 5. CartoDB Dark Matter (your dark/white map)
            folium.TileLayer('cartodbpositron', name='Light Map').add_to(m)
            folium.TileLayer('cartodbdark_matter', name='Dark Map').add_to(m)
            
            # Create popup content with all phone info
            popup_html = f"""
            <div style="font-family: Arial; width: 350px; background: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h4 style="color: #ff69b4; margin-top: 0; border-bottom: 2px solid #ff69b4; padding-bottom: 10px;">📱 Phone Number Details</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px; background: #f0f0ff;"><b>📞 Number:</b></td>
                        <td style="padding: 8px;">{phone_info.get('international_format', 'N/A')}</td></tr>
                    <tr><td style="padding: 8px; background: #f0fff0;"><b>📍 Location:</b></td>
                        <td style="padding: 8px;">{phone_info.get('location', 'N/A')}</td></tr>
                    <tr><td style="padding: 8px; background: #f0f0ff;"><b>📱 Carrier:</b></td>
                        <td style="padding: 8px;">{phone_info.get('carrier', 'N/A')}</td></tr>
                    <tr><td style="padding: 8px; background: #f0fff0;"><b>🔍 Type:</b></td>
                        <td style="padding: 8px;">{phone_info.get('number_type', 'N/A')}</td></tr>
                    <tr><td style="padding: 8px; background: #f0f0ff;"><b>⏰ Timezone:</b></td>
                        <td style="padding: 8px;">{phone_info.get('timezones', 'N/A')}</td></tr>
                </table>
                
                <h4 style="color: #ff69b4; margin: 15px 0 10px 0; border-bottom: 2px solid #ff69b4; padding-bottom: 10px;">📍 Location Details</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px; background: #f0f0ff;"><b>🏠 Address:</b></td>
                        <td style="padding: 8px;">{location_data.get('formatted_address', 'N/A')}</td></tr>
                    <tr><td style="padding: 8px; background: #f0fff0;"><b>🌍 Coordinates:</b></td>
                        <td style="padding: 8px;">{location_data['lat']:.4f}, {location_data['lng']:.4f}</td></tr>
                    <tr><td style="padding: 8px; background: #f0f0ff;"><b>🎯 Confidence:</b></td>
                        <td style="padding: 8px;">{location_data.get('confidence', 'N/A')}/10</td></tr>
                </table>
                
                <p style="text-align: center; margin-top: 15px; color: #666; font-size: 12px;">
                    Click on the layer control (top right) to change map view
                </p>
            </div>
            """
            
            # Add marker with popup
            folium.Marker(
                [location_data['lat'], location_data['lng']],
                popup=folium.Popup(popup_html, max_width=400),
                tooltip="📍 Click for phone details",
                icon=folium.Icon(color='red', icon='phone', prefix='fa')
            ).add_to(m)
            
            # Add a circle to show approximate area
            folium.Circle(
                [location_data['lat'], location_data['lng']],
                radius=1000,  # 1km radius
                color='#ff69b4',  # Pink color
                weight=3,
                fill=True,
                fillColor='#ff69b4',
                fillOpacity=0.1,
                popup='Approximate area (1km radius)'
            ).add_to(m)
            
            # Add layer control (allows switching between map styles)
            folium.LayerControl(position='topright', collapsed=False).add_to(m)
            
            # Add fullscreen button
            plugins.Fullscreen().add_to(m)
            
            return m
            
        except Exception as e:
            print_error(f"Error creating map: {str(e)}")
            return None
    
    def save_location_details(self, phone_info, location_data):
        """Save all details to a JSON file"""
        details = {
            "phone_info": phone_info,
            "location_data": location_data,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"phone_location_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(details, f, indent=2)
        
        return filename
    
    def track(self, phone_number):
        """Main method to track a phone number with colored output"""
        print_header(f"PHONE NUMBER TRACKER")
        
        # Step 1: Get phone number information
        print_info(f"Analyzing number: {Colors.BOLD}{phone_number}{Colors.END}")
        phone_info = self.get_phone_info(phone_number)
        
        if "error" in phone_info:
            print_error(phone_info['error'])
            return
        
        # Display phone information with colors
        print_color("\n📊 Phone Number Information:", Colors.MAGENTA, bold=True)
        print_data("   • International", phone_info['international_format'], Colors.CYAN, Colors.GREEN)
        print_data("   • National", phone_info['national_format'], Colors.CYAN, Colors.GREEN)
        print_data("   • Location", phone_info['location'], Colors.CYAN, Colors.PINK)
        print_data("   • Carrier", phone_info['carrier'], Colors.CYAN, Colors.YELLOW)
        print_data("   • Type", phone_info['number_type'], Colors.CYAN, Colors.BLUE)
        print_data("   • Timezone", phone_info['timezones'], Colors.CYAN, Colors.CYAN)
        
        validity = "✅ Valid" if phone_info['is_valid'] else "❌ Invalid"
        print_data("   • Status", validity, Colors.CYAN, Colors.GREEN if phone_info['is_valid'] else Colors.RED)
        
        # Step 2: Get coordinates from OpenCage
        print_info(f"Geocoding location: {Colors.BOLD}{phone_info['location']}{Colors.END}")
        location_data = self.get_coordinates(phone_info['location'])
        
        if "error" in location_data:
            print_error(location_data['error'])
            return
        
        # Display location information with colors
        print_color("\n📍 Location Details:", Colors.MAGENTA, bold=True)
        print_data("   • Address", location_data['formatted_address'], Colors.CYAN, Colors.PINK)
        print_data("   • Coordinates", f"{location_data['lat']:.4f}, {location_data['lng']:.4f}", Colors.CYAN, Colors.GREEN)
        print_data("   • Confidence", f"{location_data['confidence']}/10", Colors.CYAN, 
                  Colors.GREEN if location_data['confidence'] >= 8 else Colors.YELLOW)
        
        # Show country info if available
        if 'components' in location_data:
            comp = location_data['components']
            city = comp.get('city', comp.get('town', comp.get('village', 'N/A')))
            country = comp.get('country', 'N/A')
            print_data("   • Country", country, Colors.CYAN, Colors.BLUE)
            print_data("   • City", city, Colors.CYAN, Colors.CYAN)
        
        # Step 3: Create and save map
        print_info("Creating interactive map with multiple views...")
        print_color("   • Try switching between Street, Satellite, Hybrid, and Terrain views!", Colors.YELLOW)
        
        map_obj = self.create_map(location_data, phone_info)
        
        if map_obj:
            # Save map
            map_filename = f"phone_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            map_obj.save(map_filename)
            print_success(f"Map saved as: {Colors.BOLD}{map_filename}{Colors.END}")
            
            # Save details to JSON
            json_filename = self.save_location_details(phone_info, location_data)
            print_success(f"Details saved as: {Colors.BOLD}{json_filename}{Colors.END}")
            
            # Open map in browser
            webbrowser.open('file://' + os.path.realpath(map_filename))
            print_success(f"Map opened in your browser!")
            print_info("Look for the layer control in the top-right corner to switch between map views!")
        else:
            print_error("Failed to create map")
        
        print_color("\n" + "="*60, Colors.PINK)
        print_success("Tracking complete!")
        print_color("="*60, Colors.PINK)

# ============================================
# PART 4: MAIN PROGRAM LOOP
# ============================================

def main():
    """Main function to run the tracker"""
    print_color("📱 PHONE NUMBER GEO-TRACKER", Colors.PINK, bold=True)
    print_color("-" * 40, Colors.CYAN)
    print_color("This tool shows the general location associated with a phone number's area code.", Colors.YELLOW)
    print_color("Note: This is for educational purposes only.", Colors.YELLOW)
    print_color("-" * 40, Colors.CYAN)
    
    # Check for API key
    if OPENCAGE_API_KEY == "YOUR_API_KEY_HERE" or len(OPENCAGE_API_KEY) < 10:
        print_error("Please set your OpenCage API key in the script!")
        print_info("Get a free key at: https://opencagedata.com/users/sign_up")
        print_info("Then replace 'YOUR_API_KEY_HERE' with your actual key")
        return
    
    # Get phone number from user
    print_color("\n📞 Enter the phone number with country code", Colors.CYAN)
    print_color("Example: +14155552671 (US) or +447911123456 (UK)", Colors.YELLOW)
    phone_number = input(f"{Colors.GREEN}Number: {Colors.END}").strip()
    
    # Validate input
    if not phone_number:
        print_error("Please enter a phone number!")
        return
    
    # Create tracker and run
    tracker = PhoneNumberTracker(OPENCAGE_API_KEY)
    tracker.track(phone_number)
    
    # Ask if user wants to track another
    while True:
        again = input(f"\n{Colors.PINK}🔄 Track another number? (y/n): {Colors.END}").lower().strip()
        if again == 'y':
            phone_number = input(f"\n{Colors.GREEN}📞 Enter new number: {Colors.END}").strip()
            tracker.track(phone_number)
        elif again == 'n':
            print_color("\n👋 Goodbye!", Colors.MAGENTA, bold=True)
            break
        else:
            print_warning("Please enter 'y' or 'n'")

# ============================================
# PART 5: RUN THE PROGRAM
# ============================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n👋 Program interrupted. Goodbye!", Colors.YELLOW, bold=True)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")