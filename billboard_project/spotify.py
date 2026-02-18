import spotipy as sp
import os as o
import time as ti
from spotipy.oauth2 import SpotifyOAuth

#Static and Secret Variables
SCOPE = "playlist-modify-private user-read-private"
RED_URL = o.getenv("SPOTIPY_REDIRECT_URI")
CL_ID = o.getenv("SPOTIPY_CLIENT_ID")
CL_SEC =  o.getenv("SPOTIPY_CLIENT_SECRET")
C_PATH = 'token.txt'
D_NAME = 'Ramrup Satpati'

if not CL_ID or not CL_SEC or not RED_URL:
    print("\nSecret Env Vars Not Set")
    exit()

spo = sp.Spotify(
    auth_manager=SpotifyOAuth(
        scope= SCOPE,
        redirect_uri= RED_URL,
        client_id= CL_ID,
        client_secret= CL_SEC,
        show_dialog= True,
        cache_path= C_PATH,
        username= D_NAME, 
        open_browser= False
    )
)
print('Processing ...')
ti.sleep(1)
print('Done')
u_id = spo.current_user()
print("Successfully Authenticated")
print(f"Details :-\nDisplay Name :- {u_id['display_name']}\nCountry :- {u_id.get('country', 'Not Provided')}\nID : {u_id['id']}")