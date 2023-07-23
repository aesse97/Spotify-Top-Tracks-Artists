from django.urls import path
from SpotifyApp.views import LogoutView
from django.contrib import admin
from django.views.generic.base import RedirectView
from SpotifyApp.views import GetSpotifyAuthURLView, SpotifyCallbackView, LogoutView, HomeView, SpotifyTopTracksView, SpotifyTopTracksLongTermView, SpotifyTopTracksMediumTermView, SpotifyCreatePlaylistView

urlpatterns = [
    path('', RedirectView.as_view(url='home/')),
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', HomeView.as_view(), name='home'),
    path('top_tracks/', SpotifyTopTracksView.as_view(), name='spotify_top_tracks'),
    path('top_tracks_long_term/', SpotifyTopTracksLongTermView.as_view(), name='spotify_top_tracks_long_term'),
    path('top_tracks_medium_term/', SpotifyTopTracksMediumTermView.as_view(), name='spotify_top_tracks_medium_term'),
    path('get_spotify_auth_url/', GetSpotifyAuthURLView.as_view(), name='get_spotify_auth_url'),
    path('spotify_callback/', SpotifyCallbackView.as_view(), name='spotify_callback'),
    path('create_playlist/<str:time_range>/', SpotifyCreatePlaylistView.as_view(), name='create_playlist'),
]
