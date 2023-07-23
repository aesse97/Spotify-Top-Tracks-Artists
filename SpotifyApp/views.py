import spotipy
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from spotipy.exceptions import SpotifyException
import random
from django.views import View
from .spotify import SpotifyHandler
from .spotify import SpotifyOAuthHandler
from .models import SpotifyToken
from django.conf import settings
from django.contrib import messages

class GetSpotifyAuthURLView(View):
    def get(self, request, *args, **kwargs):
        handler = SpotifyOAuthHandler(request)
        auth_url = handler.get_auth_url()
        return redirect(auth_url)

class SpotifyCallbackView(View):
    def get(self, request, *args, **kwargs):
        handler = SpotifyOAuthHandler(request)
        return handler.handle_callback()

class LogoutView(View):
    def get(self, request):
        spotify_user_id = request.session.get('spotify_user_id')
        if spotify_user_id:
            SpotifyToken.objects.filter(user_id=spotify_user_id).delete()
            logout(request)
        return redirect('home')

class HomeView(View):
    def get(self, request):
        spotify_user_id = request.session.get('spotify_user_id')
        if spotify_user_id:
            try:
                token = SpotifyToken.objects.get(user_id=spotify_user_id)
            except SpotifyToken.DoesNotExist:
                return redirect('get_spotify_auth_url')

            access_token = token.access_token

            if not access_token:
                return redirect('get_spotify_auth_url')

            sp = spotipy.Spotify(auth=access_token)

            try:
                playlist_id = settings.PLAYLIST_ID
                playlist_tracks_response = sp.playlist_tracks(playlist_id)

                playlist_tracks = [
                    {
                        'name': track['track']['name'],
                        'artist': track['track']['artists'][0]['name'],
                        'image_url': track['track']['album']['images'][0]['url']
                        if track['track']['album']['images'] else None
                    } for track in playlist_tracks_response['items']
                ]

                random.shuffle(playlist_tracks)

                context = {'playlist_tracks': playlist_tracks}
                return render(request, 'home.html', context)

            except SpotifyException as e:
                if 'access token expired' in str(e).lower():
                    return redirect('get_spotify_auth_url')
        else:
            # Redirect to the login page if the user is not authenticated
            return redirect('get_spotify_auth_url')

class SpotifyTopTracksView(View):
    def get(self, request, time_range='medium_term'):
        spotify_user_id = request.session.get('spotify_user_id')
        if spotify_user_id:
            try:
                token = SpotifyToken.objects.get(user_id=spotify_user_id)
            except SpotifyToken.DoesNotExist:
                return redirect('get_spotify_auth_url')

            handler = SpotifyHandler(request)
            return handler.render_top_tracks(time_range)

class SpotifyTopTracksLongTermView(SpotifyTopTracksView):
    def get(self, request):
        return super().get(request, time_range='long_term')

class SpotifyTopTracksMediumTermView(SpotifyTopTracksView):
    def get(self, request):
        return super().get(request, time_range='medium_term')

class SpotifyCreatePlaylistView(View):
    def get(self, request, time_range='medium_term'):
        handler = SpotifyHandler(request)
        result = handler.create_playlist(time_range=time_range)
        if result:
            messages.success(request, 'Playlist created successfully!')
        return result