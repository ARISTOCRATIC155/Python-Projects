#!/usr/bin/env python3
"""
M-Pesa STK Push – Interactive Console with Full Debugging
"""

import os
import base64
import datetime
import sys
import requests
from dotenv import load_dotenv

# Optional: use rich for pretty output
try:
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt
    from rich.panel import Panel
    from rich.table import Table
    rich_available = True
except ImportError:
    rich_available = False
    # Fallback to simple prints
    def print_fallback(*args, **kwargs):
        print(*args, **kwargs)
    console = print_fallback

# Load environment variables
load_dotenv()

# Configuration from .env
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
BUSINESS_SHORTCODE = os.getenv("MPESA_BUSINESS_SHORTCODE", "174379")
PASSKEY = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://example.com/dummy-callback")

# Validate required credentials
if not CONSUMER_KEY or not CONSUMER_SECRET:
    print("ERROR: MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET must be set in .env file")
    sys.exit(1)

# Setup rich console if available
if rich_available:
    console = Console()
else:
    console = print

def get_access_token():
    """Get OAuth token from Safaricom sandbox."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = (CONSUMER_KEY, CONSUMER_SECRET)
    console.print("[yellow]Requesting access token...[/yellow]" if rich_available else "Requesting access token...")
    try:
        response = requests.get(url, auth=auth, timeout=30)
        console.print(f"[yellow]Token response status: {response.status_code}[/yellow]" if rich_available else f"Token response status: {response.status_code}")
        console.print(f"[yellow]Token response body: {response.text}[/yellow]" if rich_available else f"Token response body: {response.text}")
        response.raise_for_status()
        token = response.json()["access_token"]
        console.print(f"[green]Token obtained (first 20 chars): {token[:20]}...[/green]" if rich_available else f"Token obtained: {token[:20]}...")
        return token
    except Exception as e:
        console.print(f"[red]Failed to get access token: {e}[/red]" if rich_available else f"Failed to get access token: {e}")
        sys.exit(1)

def send_stk_push(phone, amount):
    """Send STK push request and return the response."""
    token = get_access_token()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{BUSINESS_SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "ConsoleTest",
        "TransactionDesc": "Interactive test",
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    console.print("[yellow]Sending STK push request...[/yellow]" if rich_available else "Sending STK push request...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        console.print(f"[yellow]STK push response status: {response.status_code}[/yellow]" if rich_available else f"STK push response status: {response.status_code}")
        console.print(f"[yellow]STK push response body: {response.text}[/yellow]" if rich_available else f"STK push response body: {response.text}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        console.print(f"[red]❌ STK push failed: {e}[/red]" if rich_available else f"STK push failed: {e}")
        sys.exit(1)

def main():
    if rich_available:
        console.print(Panel.fit("[bold cyan]M-Pesa STK Push - Sandbox Test[/bold cyan]", border_style="cyan"))
    else:
        console.print("=== M-Pesa STK Push - Sandbox Test ===")

    # Display current configuration (mask sensitive parts)
    console.print("\n[cyan]Configuration loaded:[/cyan]" if rich_available else "\nConfiguration loaded:")
    console.print(f"  Business Shortcode: {BUSINESS_SHORTCODE}")
    console.print(f"  Callback URL: {CALLBACK_URL}")
    masked_key = CONSUMER_KEY[:8] + "..." + CONSUMER_KEY[-4:] if len(CONSUMER_KEY) > 12 else "***"
    masked_secret = CONSUMER_SECRET[:8] + "..." + CONSUMER_SECRET[-4:] if len(CONSUMER_SECRET) > 12 else "***"
    console.print(f"  Consumer Key: {masked_key}")
    console.print(f"  Consumer Secret: {masked_secret}")

    if rich_available:
        console.print("\n[bold yellow]Enter payment details:[/bold yellow]")
        phone = Prompt.ask("[cyan]Phone number (e.g., 254708374149)[/cyan]")
        amount = IntPrompt.ask("[cyan]Amount (KES)[/cyan]")
    else:
        phone = input("Phone number (e.g., 254708374149): ")
        amount = int(input("Amount (KES): "))

    console.print(f"\n[green]Sending STK push to {phone} for KES {amount}...[/green]" if rich_available else f"\nSending STK push to {phone} for KES {amount}...")

    result = send_stk_push(phone, amount)

    console.print("\n[bold green]✅ STK push initiated successfully![/bold green]" if rich_available else "\n✅ STK push initiated successfully!")
    if rich_available:
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")
        for key, value in result.items():
            table.add_row(key, str(value))
        console.print(table)
    else:
        for key, value in result.items():
            console.print(f"{key}: {value}")

    console.print("\n[bold yellow]Next steps:[/bold yellow]" if rich_available else "\nNext steps:")
    console.print("1. Go to https://developer.safaricom.co.ke/")
    console.print("2. Navigate to APIs → Lipa Na M-Pesa → Simulate")
    console.print(f"3. Paste the [bold]CheckoutRequestID[/bold] above and click Simulate" if rich_available else f"3. Paste the CheckoutRequestID above and click Simulate")
    console.print("4. The transaction will be marked successful (no callback needed).\n")

if __name__ == "__main__":
    main()