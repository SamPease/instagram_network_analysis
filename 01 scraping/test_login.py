import instaloader

USERNAME = "sampease24"

# Initialize Instaloader
L = instaloader.Instaloader()

# Try to load existing session
try:
    print("Trying to load existing session...")
    L.load_session_from_file(USERNAME)
except FileNotFoundError:
    print("No saved session found. Logging in manually.")
    L.login(USERNAME, input("🔐 Enter Instagram password: "))
    L.save_session_to_file()

# Load profile
print("Fetching profile info...")
profile = instaloader.Profile.from_username(L.context, USERNAME)

# Print basic info
print("\n✅ Login successful!")
print(f"Username: {profile.username}")
print(f"Full Name: {profile.full_name}")
print(f"Bio: {profile.biography}")
print(f"Followers: {profile.followers}")
print(f"Following: {profile.followees}")
print(f"Posts: {profile.mediacount}")
