from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    # Create a new context without loading a session
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.instagram.com/accounts/login/")
    print("🔐 Please log in manually in the browser. Then press ENTER here.")
    input()

    # Save the authenticated session
    context.storage_state(path="auth.json")
    print("✅ Session saved to auth.json")

    browser.close()
