import os

print("CLIENT ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("CLIENT SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("REDIRECT URI:", os.getenv("SPOTIPY_REDIRECT_URI"))