from main import get_billboard_data
from spotify import get_auth_cl

spo = get_auth_cl()
song_lis, yr = get_billboard_data()
sp_uri = []

for s in song_lis:
    try:
        res = spo.search(
            q = f'track:{s} year:{yr}',
            type = 'track',
            limit = 1
        )
        uri = res['tracks']['items'][0]['uri']
        sp_uri.append(uri)

    except IndexError as i:
        print(f"\nSong {s} not found\nSkipping..")