from spotify import u_id
from songs import sp_uri
from main import val
import spotipy as sp
import os as o
import time as ti
from spotipy.oauth2 import SpotifyOAuth

#Static and secret variables
CL_ID = o.getenv("SPOTIPY_CLIENT_ID")
CL_SEC =  o.getenv("SPOTIPY_CLIENT_SECRET")
RED_URL = o.getenv("SPOTIPY_REDIRECT_URI")

spk = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope= "playlist-modify-private",
        redirect_uri= RED_URL,
        client_id= CL_ID,
        client_secret= CL_SEC,
        show_dialog= True,
        cache_path= "token.txt"
    )
)
user_id = spk.current_user()["id"]
dtr = val
song_uris = [uri for uri in sp_uri]

print("Creating Playlist....")
ti.sleep(1)
ply = spk.user_playlist_create(
    user=user_id, 
    name=f"{dtr} Billboard 100", 
    public=False
    )

print("Created Playlist....")
ti.sleep(1)

P_ID = ply['id']

print("Adding Songs....")
ti.sleep(1)

sp.playlist_add_items(
    playlist_id = P_ID, 
    items = song_uris
    )

print("Added Songs....")
ti.sleep(1)