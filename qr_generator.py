import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
import segno
from fpdf import FPDF
import os
from PIL import Image
import json
import csv
from datetime import datetime

class QRCodeGenerator:
    def __init__(self):
        self.output_dir = "generated_qrcodes"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def format_data(self, data_type, **kwargs):
        """Format data based on type"""
        if data_type == "url":
            return kwargs.get('url', '')
        
        elif data_type == "text":
            return kwargs.get('text', '')
        
        elif data_type == "contact":
            name = kwargs.get('name', '')
            phone = kwargs.get('phone', '')
            email = kwargs.get('email', '')
            company = kwargs.get('company', '')
            # vCard format
            return f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL:{phone}
EMAIL:{email}
ORG:{company}
END:VCARD"""
        
        elif data_type == "email":
            recipient = kwargs.get('recipient', '')
            subject = kwargs.get('subject', '')
            body = kwargs.get('body', '')
            return f"mailto:{recipient}?subject={subject}&body={body}"
        
        elif data_type == "phone":
            number = kwargs.get('number', '')
            return f"tel:{number}"
        
        elif data_type == "wifi":
            ssid = kwargs.get('ssid', '')
            password = kwargs.get('password', '')
            encryption = kwargs.get('encryption', 'WPA')  # WEP, WPA, or nopass
            return f"WIFI:T:{encryption};S:{ssid};P:{password};;"
        
        elif data_type == "sms":
            number = kwargs.get('number', '')
            message = kwargs.get('message', '')
            return f"smsto:{number}:{message}"
        
        elif data_type == "location":
            lat = kwargs.get('latitude', '')
            lon = kwargs.get('longitude', '')
            return f"geo:{lat},{lon}"
        
        return ""
    
    def generate_basic_qr(self, data, filename="basic_qr", format="PNG", 
                          fill_color="black", back_color="white", 
                          box_size=10, border=4):
        """Generate a basic QR code"""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size,
                border=border,
            )
            
            # Add data
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Save based on format
            if format.upper() == "PNG":
                filepath = os.path.join(self.output_dir, f"{filename}.png")
                img.save(filepath)
                print(f"✅ QR Code saved as PNG: {filepath}")
                
            elif format.upper() == "JPG" or format.upper() == "JPEG":
                filepath = os.path.join(self.output_dir, f"{filename}.jpg")
                # Convert to RGB for JPG
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(filepath, 'JPEG', quality=95)
                print(f"✅ QR Code saved as JPG: {filepath}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
            return None
    
    def generate_styled_qr(self, data, filename="styled_qr", format="PNG",
                           fill_color="darkblue", back_color="lightyellow",
                           module_drawer="rounded", logo_path=None):
        """Generate a styled QR code with custom modules and optional logo"""
        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Choose module drawer
            if module_drawer == "rounded":
                drawer = RoundedModuleDrawer()
            elif module_drawer == "circle":
                drawer = CircleModuleDrawer()
            else:
                drawer = None
            
            # Create styled image
            if drawer:
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=drawer,
                    fill_color=fill_color,
                    back_color=back_color
                )
            else:
                img = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Add logo if provided
            if logo_path and os.path.exists(logo_path):
                img = self._add_logo_to_qr(img, logo_path)
            
            # Save
            if format.upper() == "PNG":
                filepath = os.path.join(self.output_dir, f"{filename}.png")
                img.save(filepath)
                print(f"✅ Styled QR Code saved: {filepath}")
                return filepath
            elif format.upper() == "JPG":
                filepath = os.path.join(self.output_dir, f"{filename}.jpg")
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(filepath, 'JPEG', quality=95)
                print(f"✅ Styled QR Code saved: {filepath}")
                return filepath
            
        except Exception as e:
            print(f"❌ Error generating styled QR: {e}")
            return None
    
    def _add_logo_to_qr(self, qr_image, logo_path, logo_size_ratio=0.2):
        """Add a logo to the center of QR code"""
        try:
            # Open logo
            logo = Image.open(logo_path)
            
            # Calculate logo size (20% of QR code by default)
            qr_width, qr_height = qr_image.size
            logo_max_size = int(min(qr_width, qr_height) * logo_size_ratio)
            
            # Resize logo
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
            
            # Calculate position (center)
            pos = ((qr_width - logo.size[0]) // 2, (qr_height - logo.size[1]) // 2)
            
            # Paste logo
            if logo.mode == 'RGBA':
                qr_image.paste(logo, pos, logo)
            else:
                qr_image.paste(logo, pos)
            
            return qr_image
        except Exception as e:
            print(f"⚠️ Could not add logo: {e}")
            return qr_image
    
    def generate_svg_qr(self, data, filename="qrcode", scale=10):
        """Generate SVG QR code using segno library"""
        try:
            # Generate QR code
            qr = segno.make(data, error='h')
            
            # Save as SVG
            filepath = os.path.join(self.output_dir, f"{filename}.svg")
            qr.save(filepath, scale=scale)
            print(f"✅ SVG QR Code saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generating SVG QR: {e}")
            return None
    
    def generate_pdf_qr(self, data, filename="qrcode", size_mm=50):
        """Generate QR code in PDF format"""
        try:
            # First generate PNG
            png_path = self.generate_basic_qr(data, "temp_qr", "PNG")
            
            if png_path:
                # Create PDF
                pdf = FPDF()
                pdf.add_page()
                
                # Convert mm to points for FPDF (1 mm = 2.83465 points)
                size_pt = size_mm * 2.83465
                
                # Add QR code to PDF
                pdf.image(png_path, x=10, y=10, w=size_pt, h=size_pt)
                
                # Save PDF
                filepath = os.path.join(self.output_dir, f"{filename}.pdf")
                pdf.output(filepath)
                
                # Clean up temp PNG
                os.remove(png_path)
                
                print(f"✅ PDF QR Code saved: {filepath}")
                return filepath
            
        except Exception as e:
            print(f"❌ Error generating PDF QR: {e}")
            return None
    
    def batch_generate_from_csv(self, csv_file):
        """Generate multiple QR codes from a CSV file"""
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                generated_files = []
                
                for row in reader:
                    data_type = row.get('type', 'text')
                    filename = row.get('filename', f"qr_{datetime.now().timestamp()}")
                    
                    # Prepare data based on type
                    if data_type == "url":
                        data = self.format_data("url", url=row.get('data', ''))
                    elif data_type == "wifi":
                        data = self.format_data("wifi", 
                                              ssid=row.get('ssid', ''),
                                              password=row.get('password', ''),
                                              encryption=row.get('encryption', 'WPA'))
                    elif data_type == "contact":
                        data = self.format_data("contact",
                                              name=row.get('name', ''),
                                              phone=row.get('phone', ''),
                                              email=row.get('email', ''),
                                              company=row.get('company', ''))
                    else:
                        data = row.get('data', '')
                    
                    # Generate QR
                    filepath = self.generate_basic_qr(data, filename, "PNG")
                    if filepath:
                        generated_files.append(filepath)
                
                print(f"\n✅ Generated {len(generated_files)} QR codes from CSV")
                return generated_files
                
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return []
    
    def interactive_mode(self):
        """Interactive command-line interface"""
        print("\n" + "="*50)
        print("📱 PYTHON QR CODE GENERATOR")
        print("="*50)
        
        # Choose data type
        print("\n📋 Select data type:")
        print("1. URL/Website link")
        print("2. Plain text")
        print("3. Contact information (vCard)")
        print("4. Email address")
        print("5. Phone number")
        print("6. Wi-Fi credentials")
        print("7. SMS message")
        print("8. Location (GPS coordinates)")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        # Get data based on choice
        if choice == "1":  # URL
            url = input("Enter URL (include https://): ").strip()
            data = self.format_data("url", url=url)
            data_type_name = "URL"
            
        elif choice == "2":  # Text
            text = input("Enter text: ").strip()
            data = self.format_data("text", text=text)
            data_type_name = "Text"
            
        elif choice == "3":  # Contact
            print("\nEnter contact details:")
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email: ").strip()
            company = input("Company (optional): ").strip()
            data = self.format_data("contact", name=name, phone=phone, 
                                   email=email, company=company)
            data_type_name = "Contact"
            
        elif choice == "4":  # Email
            recipient = input("Recipient email: ").strip()
            subject = input("Subject (optional): ").strip()
            body = input("Body (optional): ").strip()
            data = self.format_data("email", recipient=recipient, 
                                   subject=subject, body=body)
            data_type_name = "Email"
            
        elif choice == "5":  # Phone
            number = input("Phone number (with country code): ").strip()
            data = self.format_data("phone", number=number)
            data_type_name = "Phone"
            
        elif choice == "6":  # WiFi
            print("\nEnter Wi-Fi details:")
            ssid = input("Network name (SSID): ").strip()
            password = input("Password: ").strip()
            print("Encryption type: WPA, WEP, or nopass")
            encryption = input("Encryption (WPA): ").strip() or "WPA"
            data = self.format_data("wifi", ssid=ssid, password=password, 
                                   encryption=encryption)
            data_type_name = "WiFi"
            
        elif choice == "7":  # SMS
            number = input("Phone number: ").strip()
            message = input("Message: ").strip()
            data = self.format_data("sms", number=number, message=message)
            data_type_name = "SMS"
            
        elif choice == "8":  # Location
            lat = input("Latitude: ").strip()
            lon = input("Longitude: ").strip()
            data = self.format_data("location", latitude=lat, longitude=lon)
            data_type_name = "Location"
            
        else:
            print("❌ Invalid choice")
            return
        
        # Choose output format
        print("\n💾 Select output format:")
        print("1. PNG (best for web/printing)")
        print("2. JPG (smaller file size)")
        print("3. SVG (scalable vector)")
        print("4. PDF (document ready)")
        
        format_choice = input("Enter choice (1-4): ").strip()
        
        format_map = {"1": "PNG", "2": "JPG", "3": "SVG", "4": "PDF"}
        output_format = format_map.get(format_choice, "PNG")
        
        # Filename
        filename = input(f"\nEnter filename (without extension): ").strip()
        if not filename:
            filename = f"{data_type_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate QR
        print(f"\n🔄 Generating {data_type_name} QR code...")
        
        if output_format == "SVG":
            self.generate_svg_qr(data, filename)
        elif output_format == "PDF":
            self.generate_pdf_qr(data, filename)
        else:
            # Ask if they want styling for PNG/JPG
            style = input("\nApply styling? (y/n): ").strip().lower()
            
            if style == 'y':
                color = input("Fill color (default 'darkblue'): ").strip() or "darkblue"
                bg_color = input("Background color (default 'lightyellow'): ").strip() or "lightyellow"
                module = input("Module shape (square/rounded/circle): ").strip().lower()
                
                logo = input("Logo path (optional, press Enter to skip): ").strip()
                logo_path = logo if logo else None
                
                self.generate_styled_qr(data, filename, output_format,
                                      fill_color=color, back_color=bg_color,
                                      module_drawer=module if module in ['rounded', 'circle'] else 'square',
                                      logo_path=logo_path)
            else:
                self.generate_basic_qr(data, filename, output_format)
        
        print(f"\n✨ Check the '{self.output_dir}' folder for your QR code!")

def main():
    """Main function to run the QR code generator"""
    generator = QRCodeGenerator()
    
    print("\n🎯 QR CODE GENERATOR")
    print("===================")
    print("1. Interactive mode (guided generation)")
    print("2. Quick generate from command line")
    print("3. Batch generate from CSV")
    
    mode = input("\nSelect mode (1-3): ").strip()
    
    if mode == "1":
        generator.interactive_mode()
        
    elif mode == "2":
        # Quick command line generation
        data = input("Enter data for QR code: ").strip()
        filename = input("Enter filename (without extension): ").strip() or "quick_qr"
        generator.generate_basic_qr(data, filename, "PNG")
        print(f"✅ QR Code saved in '{generator.output_dir}' folder")
        
    elif mode == "3":
        csv_path = input("Enter path to CSV file: ").strip()
        if os.path.exists(csv_path):
            generator.batch_generate_from_csv(csv_path)
        else:
            print("❌ CSV file not found!")
            
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()