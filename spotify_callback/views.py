import requests
import spotipy
from django.shortcuts import render, redirect
from django.conf import settings
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from django.contrib.auth import logout
from django.shortcuts import redirect
from spotipy import oauth2


SPOTIPY_CLIENT_ID = 'b198cb4b0e1145808e6b1a5d3a9abadd'
SPOTIPY_CLIENT_SECRET = 'c19526e617984c1fab1dfbb9d3f866c1'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/spotify_callback/'  # Update with your callback URL

# Define the required scopes
SPOTIPY_SCOPES = ['user-top-read', 'user-read-private']

def get_spotify_auth_url(request):
    sp_oauth = oauth2.SpotifyOAuth(
        SPOTIPY_CLIENT_ID,
        SPOTIPY_CLIENT_SECRET,
        SPOTIPY_REDIRECT_URI,
        scope=SPOTIPY_SCOPES,
    )

    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def spotify_callback(request):
    # Obtain the access token and store it in the session
    sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI)
    code = request.GET.get('code', None)

    if code:
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        request.session['access_token'] = access_token

    return redirect('spotify_top_tracks_artists')

def spotify_top_tracks_artists(request):
    # Get the user's access token from the session
    access_token = request.session.get('access_token')

    # Check if the access token is available
    if access_token:
        # Fetch top tracks data
        top_tracks_response = requests.get(
            'https://api.spotify.com/v1/me/top/tracks',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        top_tracks_data = top_tracks_response.json()

        # Fetch top artists data
        top_artists_response = requests.get(
            'https://api.spotify.com/v1/me/top/artists',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        top_artists_data = top_artists_response.json()

        # Get artwork URLs for top tracks
        top_tracks = []
        for track in top_tracks_data['items']:
            name = track['name']
            artist = track['artists'][0]['name']
            popularity = track['popularity']
            # Get the URL of the first available artwork image (assuming there's at least one image)
            image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
            top_tracks.append({'name': name, 'artist': artist, 'popularity': popularity, 'image_url': image_url})

        context = {
            'top_tracks': top_tracks,
            'top_artists': top_artists_data['items'],
        }
        return render(request, 'top_tracks_artists.html', context)
    else:
        # If access token is not available, redirect to the Spotify authentication URL
        return redirect('get_spotify_auth_url')

def logout_view(request):
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'refresh_token' in request.session:
        del request.session['refresh_token']
    logout(request)
    return redirect('home')  # Redirect to the desired page after logout
def revoke_spotify_access_token(access_token):
    revoke_url = 'https://accounts.spotify.com/api/token/revoke'
    data = {'token': access_token}
    requests.post(revoke_url, data=data)
def home_view(request):
    # Your implementation for the 'home_view' function
    # ...
    return render(request, 'home.html')