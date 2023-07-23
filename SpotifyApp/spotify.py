from django.shortcuts import render, redirect
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyException
import spotipy
from django.conf import settings
from django.contrib import messages
from .models import SpotifyToken
from datetime import datetime
from SpotifyApp.CacheHandler import NullCacheHandler
from django.contrib import messages

class SpotifyOAuthHandler:
    def __init__(self, request):
        self.request = request
        self.sp_oauth = SpotifyOAuth(
            settings.SPOTIPY_CLIENT_ID,
            settings.SPOTIPY_CLIENT_SECRET,
            settings.SPOTIPY_REDIRECT_URI,
            scope=settings.SPOTIPY_SCOPES,
            cache_handler = NullCacheHandler())

    def get_auth_url(self):
        auth_url = self.sp_oauth.get_authorize_url()
        return auth_url

    def handle_callback(self):
        code = self.request.GET.get('code')

        if code:
            try:
                token_info = self.sp_oauth.get_access_token(code)

                sp = spotipy.Spotify(auth=token_info['access_token'])
                spotify_user_id = sp.me()['id']

                self.request.session['spotify_user_id'] = spotify_user_id

                SpotifyToken.objects.update_or_create(
                    user_id=spotify_user_id,
                    defaults={
                        'access_token': token_info['access_token'],
                        'token_type': token_info['token_type'],
                        'expires_in': token_info['expires_in'],
                        'refresh_token': token_info['refresh_token'],
                        'scope': ' '.join(token_info['scope']),  # Convert scopes list to space-separated string
                        'expires_at': datetime.fromtimestamp(token_info['expires_at']),
                    }
                )

                return redirect('home')
            except Exception as e:
                print(f"Error while getting access token: {str(e)}")
                messages.error(self.request, 'An error occurred. Please try again.')

        return redirect('get_spotify_auth_url')


class SpotifyHandler:
    def __init__(self, request):
        self.request = request

    def fetch_top_tracks(self, time_range='medium_term'):
        spotify_user_id = self.request.session.get('spotify_user_id')

        if spotify_user_id:
            try:
                token = SpotifyToken.objects.get(user_id=spotify_user_id)
            except SpotifyToken.DoesNotExist:
                return redirect('get_spotify_auth_url')

            access_token = token.access_token
            sp = spotipy.Spotify(auth=access_token)

            try:
                if time_range not in ['medium_term', 'long_term']:
                    raise ValueError("Invalid time_range. Must be 'medium_term' or 'long_term'.")

                top_tracks_response = sp.current_user_top_tracks(limit=20, time_range=time_range)
                top_tracks_data = top_tracks_response['items']

                top_tracks = []
                for track in top_tracks_data:
                    id = track['id']
                    name = track['name']
                    artist = track['artists'][0]['name']
                    popularity = track['popularity']
                    image_url = track['album']['images'][0]['url'] if track['album']['images'] else None
                    top_tracks.append({
                        'id': id,
                        'name': name,
                        'artist': artist,
                        'popularity': popularity,
                        'image_url': image_url
                    })

                return top_tracks
            except SpotifyException as e:
                if 'access token expired' in str(e).lower():
                    return redirect('get_spotify_auth_url')
        else:
            return redirect('get_spotify_auth_url')

    def render_top_tracks(self, time_range='medium_term'):
        spotify_user_id = self.request.session.get('spotify_user_id')

        if spotify_user_id:
            try:
                token = SpotifyToken.objects.get(user_id=spotify_user_id)
            except SpotifyToken.DoesNotExist:
                return redirect('get_spotify_auth_url')

            access_token = token.access_token
            sp = spotipy.Spotify(auth=access_token)

            top_tracks = self.fetch_top_tracks(time_range)
            top_artists_response = sp.current_user_top_artists(limit=10, time_range=time_range)
            top_artists_data = top_artists_response['items']

            context = {
                'top_tracks_medium': top_tracks if time_range == 'medium_term' else None,
                'top_artists_medium': top_artists_data if time_range == 'medium_term' else None,
                'top_tracks_long': top_tracks if time_range == 'long_term' else None,
                'top_artists_long': top_artists_data if time_range == 'long_term' else None
            }

            template_name = 'top_medium_term.html' if time_range == 'medium_term' else 'top_long_term.html'
            return render(self.request, template_name, context)
        else:
            return redirect('get_spotify_auth_url')

    def create_playlist(self, playlist_name='Top Tracks Based Playlist', time_range='medium_term'):
            spotify_user_id = self.request.session.get('spotify_user_id')

            if spotify_user_id:
                try:
                    token = SpotifyToken.objects.get(user_id=spotify_user_id)
                except SpotifyToken.DoesNotExist:
                    return redirect('get_spotify_auth_url')

                access_token = token.access_token
                sp = spotipy.Spotify(auth=access_token)

                playlist = sp.user_playlist_create(spotify_user_id, playlist_name)

                top_tracks = self.fetch_top_tracks(time_range)

                if top_tracks:
                    # Extract the IDs of the top tracks
                    track_ids = [track['id'] for track in top_tracks]

                    # Split the top tracks into two sets of 5
                    track_ids_1 = track_ids[:5]
                    track_ids_2 = track_ids[5:10] if len(track_ids) > 5 else []

                    recommended_track_ids = []

                    # Get recommendations based on the first set of top tracks
                    if track_ids_1:
                        recommendations_1 = sp.recommendations(seed_tracks=track_ids_1)
                        recommended_track_ids += [track['id'] for track in recommendations_1['tracks']]

                    # Get recommendations based on the second set of top tracks
                    if track_ids_2:
                        recommendations_2 = sp.recommendations(seed_tracks=track_ids_2)
                        recommended_track_ids += [track['id'] for track in recommendations_2['tracks']]

                    # Add the recommended tracks to the playlist
                    if recommended_track_ids:
                        sp.user_playlist_add_tracks(spotify_user_id, playlist['id'], recommended_track_ids)

                return redirect('home')
            else:
                return redirect('get_spotify_auth_url')