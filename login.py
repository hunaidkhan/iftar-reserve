"""
Run this ONCE manually on your Mac to save your Google session.
It will open a visible browser window so you can log in normally.

Usage:
    pip install playwright
    playwright install chromium
    python login.py
"""

import json
from playwright.sync_api import sync_playwright

SITE_URL = "https://iftar.msauofa.ca"
SESSION_FILE = "session.json"

def login_and_save():
    with sync_playwright() as p:
        # Launch a VISIBLE browser (not headless) so Google doesn't block you
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Opening the Iftar portal...")
        page.goto(SITE_URL)

        print("\n>>> Please sign in with your @ualberta.ca Google account in the browser window.")
        print(">>> The script will wait until you're fully logged in and can see the reservation page.")
        print(">>> DO NOT close the browser window.\n")

        # Wait for the Google OAuth flow to complete and redirect back to the Iftar site.
        # The flow is: Iftar site -> Google login -> back to Iftar site (with auth token).
        # We watch for the URL to return to the iftar domain after leaving for Google.
        print("Waiting for you to complete sign-in and be redirected back to the Iftar portal...")

        def is_back_on_iftar(url):
            return "msauofa.ca" in url and "google.com" not in url and "ualberta.ca" not in url

        # First, wait until we leave the iftar site (redirected to Google)
        try:
            page.wait_for_url(lambda url: "google.com" in url or "ualberta.ca" in url, timeout=60_000)
            print("Detected redirect to Google/UAlberta login — complete your sign-in there...")
        except Exception:
            pass  # May have already redirected or used a popup

        # Then wait until we come back to the iftar site (OAuth complete)
        page.wait_for_url(is_back_on_iftar, timeout=180_000)

        # Give the page a moment to fully settle and load auth state
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Confirm the Sign In button is gone (i.e., we are authenticated)
        if page.locator("text=Sign in with Google").is_visible(timeout=3000):
            print("ERROR: Still seeing login page after redirect. Please try again.")
            browser.close()
            return

        print("Logged in successfully! Saving session...")

        # Save cookies + local storage
        storage = context.storage_state()
        with open(SESSION_FILE, "w") as f:
            json.dump(storage, f)

        print(f"Session saved to {SESSION_FILE}")
        print("You can now close the browser window.")
        print("\nNext steps:")
        print("  1. Run: python reserve.py  (to test the reservation manually)")
        print("  2. Follow README.md to set up GitHub Actions for daily automation")

        browser.close()

if __name__ == "__main__":
    login_and_save()
