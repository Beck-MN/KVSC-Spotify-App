"""Developer: Beck Christensen
   Date Started: 8-7-2024
   
   What is this shit? tbh brother i dont really know 
   im just trying out the spotify API requests to potentially
   help with my radio job"""

# Spotify API libraries
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

# Streamlit library for app development
import streamlit as st

# Pandas library for dataframe manipulation
import pandas as pd

# Graphing/Plotting libraries
import seaborn as sns
import matplotlib.pyplot as plt

# Date and time for labeling
from datetime import date

today = str(date.today())

# Connect to spotify an give proper permissions for playlist customization
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id="7444209f2bc34f7ba86b8ce6d7fe5ab7",
        client_secret="c2b5526ba53c46cdb770351224ce9612",
        redirect_uri="http://localhost:8080",
        scope="user-top-read,user-library-read,user-read-recently-played,playlist-modify-private,playlist-modify-public",
    )
)

# Organize NACC chart into needed columns and group by category
keep = ["TW", "Artist", "Recording", "Label"]
file = st.file_uploader("Upload a CSV or Excel file of the most recent NACC top 30 albums", type=["csv"])


if file is not None:

    # Make dataframe of file
    nacc_df = pd.read_csv(file, usecols=keep)
    st.dataframe(nacc_df)

    # Establish main user (only me for now)
    user_id = sp.me()["id"]

    # Create Playlist
    st.write("Generating Playlist of NACC Top 30 as of ", today)
    playlist = sp.user_playlist_create(
        user_id,
        "NACC Top 30 " + today,
        description="Playlist of the top 30 albums on the NACC charts as of " + today,
    )

    # Go through each artist on NACC chart, search via Spotipy and add each song off the top result
    for index, row in nacc_df.iterrows():

        # Get album name
        search = row["Recording"]

        # search spotify for album
        result = sp.search(q="album:" + search, limit=1, type="album", market="US")
        search_result = result["albums"]["items"]
        st.write(
            search_result[0]["name"],
            "by",
            search_result[0]["artists"][0]["name"],
            "added, Spotify ID:",
            search_result[0]["id"],
        )

        # Organize search results for playlist
        tracks = sp.album_tracks(search_result[0]["id"])
        songs = tracks["items"]

        # Add songs to playlist
        for track in songs:
            sp.playlist_add_items(playlist_id=playlist["id"], items=[track["id"]])

    st.write(
        "Playlist Generated! Find it in your library or at: ",
        playlist["external_urls"]["spotify"],
    )
    st.write("Generating correlation matix of the auido features of the NACC top 30...")

    # Get track ID's of songs from generated playlist
    # Get audio features of each track
    playlist_tracks = sp.playlist_tracks(playlist["id"])
    tracks = playlist_tracks["items"]
    track_ids = [track["id"] for item in tracks]
    audio_features = sp.audio_features(track_ids)

    # Generate data frame of audio features
    df = pd.DataFrame(audio_features)
    df = df[
        [
            "danceability",
            "energy",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
        ]
    ]

    # Create correlation matrix of audio features
    matrix = df.corr()

    # Display matrix
    sns.heatmap(matrix, annot=True, cmap="coolwarm")
