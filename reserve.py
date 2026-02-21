"""
Daily reservation script for MSA UofA Iftar Portal.
Uses a saved session (from login.py) so it never needs to touch Google OAuth.

Usage:
    python reserve.py

In GitHub Actions this runs automatically at noon MST every day.
"""

import json
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SITE_URL = "https://iftar.msauofa.ca"
SESSION_FILE = "session.json"


def load_session():
    """Load session from file or from GitHub Actions secret env var."""
    # In GitHub Actions, the session is stored as an env var (base64 encoded)
    session_env = os.environ.get("IFTAR_SESSION")
    if session_env:
        print("Loading session from environment variable...")
        return json.loads(session_env)

    # Locally, load from file
    if not os.path.exists(SESSION_FILE):
        print(f"ERROR: No session found. Run login.py first to generate {SESSION_FILE}")
        sys.exit(1)

    print("Loading session from file...")
    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def reserve():
    session = load_session()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=session)
        page = context.new_page()

        print(f"[{datetime.now()}] Navigating to Iftar portal...")
        page.goto(SITE_URL, wait_until="networkidle")

        # Check if we got redirected to login (session expired)
        if page.locator("text=Sign in with Google").is_visible():
            print("ERROR: Session has expired. Please run login.py again to refresh it.")
            browser.close()
            sys.exit(2)

        print("Session valid — looking for reservation button...")

        # Try common button texts for reservation
        reserve_selectors = [
            "text=Reserve",
            "text=Reserve Spot",
            "text=Reserve My Spot",
            "text=Book",
            "text=Register",
            "button:has-text('Reserve')",
            "button:has-text('Book')",
            "[data-testid='reserve-button']",
        ]

        clicked = False
        for selector in reserve_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    print(f"Found button: '{selector}' — clicking...")
                    btn.click()
                    clicked = True
                    break
            except PlaywrightTimeout:
                continue

        if not clicked:
            # Take a screenshot for debugging
            page.screenshot(path="debug_screenshot.png")
            print("Could not find reservation button. Screenshot saved to debug_screenshot.png")
            print("Current page title:", page.title())
            print("Current URL:", page.url)
            browser.close()
            sys.exit(3)

        # Wait for confirmation
        page.wait_for_timeout(3000)

        # Look for success indicators
        success_indicators = [
            "text=Reserved",
            "text=Confirmed",
            "text=Success",
            "text=You're registered",
            "text=Spot reserved",
            "text=already reserved",
            "text=Already registered",
        ]

        success = False
        for indicator in success_indicators:
            try:
                if page.locator(indicator).is_visible(timeout=2000):
                    print(f"SUCCESS: Reservation confirmed! ({indicator})")
                    success = True
                    break
            except PlaywrightTimeout:
                continue

        if not success:
            page.screenshot(path="post_click_screenshot.png")
            print("Clicked the button but could not confirm success. Screenshot saved.")
            print("Current URL:", page.url)
            # Don't exit with error — the click may have worked
            print("(Check the screenshot to verify manually)")

        browser.close()
        print("Done.")


if __name__ == "__main__":
    reserve()
