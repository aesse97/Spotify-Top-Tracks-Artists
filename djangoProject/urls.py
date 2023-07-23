"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from spotify_callback import views

urlpatterns = [
    # URL pattern for initiating Spotify authentication
    path('spotify_top_tracks_artists/', views.spotify_top_tracks_artists, name='spotify_top_tracks_artists'),
    # Add this line

    path('get_spotify_auth_url/', views.get_spotify_auth_url, name='get_spotify_auth_url'),

    # URL pattern for handling Spotify callback
    path('spotify_callback/', views.spotify_callback, name='spotify_callback'),

    path('logout/', views.logout_view, name='logout'),

    path('home', views.home_view, name='home'),
]
