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

# Webscraper libraries
import requests
from bs4 import BeautifulSoup

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

# Funtion to get a return the current KVSC top 30 via a web scraper
def get_nacc_chart():

    request_headers = {
        "referer": "https://www.kvsc.org/wp-content/themes/kvsc/css/style.css?ver=6.6.1",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Opera GX";v="112"',
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua-platform-version": '"10.0.0"',
        "sec-ch-viewport-width": "792",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }

    response = requests.get(
        "https://www.kvsc.org/music/nacc-charts/", headers=request_headers
    )

    soup = BeautifulSoup(response.text, "html.parser")
    album_list = soup.find("body")
    album_list_items = album_list.find("ol", class_="chart")
    positions = []
    artists = []
    albums = []
    labels = []

    chart_items = album_list_items.find_all("li")

    for item in chart_items:

        if item.find("span", class_="position"):
            position = item.find("span", class_="position").text.strip()
            artist = item.find("span", class_="artist").text.strip()
            album = item.find("span", class_="album").text.strip()
            label = item.find("span", class_="label").text.strip()

            positions.append(position)
            artists.append(artist)
            albums.append(album)
            labels.append(label)

    df = pd.DataFrame(
        {"Position": positions, "Artist": artists, "Recording": albums, "Label": labels}
    )

    return df

# Organize NACC chart into needed columns and group by category
keep = ["TW", "Artist", "Recording", "Label"]

if st.button("Generate Playlist"):

    # Make dataframe of file
    nacc_df = get_nacc_chart()
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
        artist = row["Artist"]

        # search spotify for album
        query = f'artist:"{artist}" album:"{search}"'
        result = sp.search(q=query, limit=1, type="album", market="US")
        search_result = result["albums"]["items"]

        # Check if spotify was able to find the album
        if search_result:
            st.write(
                search_result[0]["name"],
                "by",
                search_result[0]["artists"][0]["name"],
                "added, Spotify link:",
                search_result[0]["external_urls"]["spotify"],
            )

            # Organize search results for playlist
            tracks = sp.album_tracks(search_result[0]["id"])
            songs = tracks["items"]

            # Add songs to playlist
            for track in songs:
                sp.playlist_add_items(playlist_id=playlist["id"], items=[track["id"]])

        # Spotify couln't find the album
        else:
            st.write("Couldn't find", search, "by", artist)

    st.write(
        "Playlist Generated! Find it in your library or at: ",
        playlist["external_urls"]["spotify"],
    )

    st.write("Generating correlation matix of the auido features of the NACC top 30...")

    # Get track ID's of songs from generated playlist
    # Get audio features of each track
    playlist_tracks = sp.playlist_tracks(playlist["id"])
    tracks = playlist_tracks["items"]
    track_ids = [track["track"]["id"] for track in tracks]
    audio_features = sp.audio_features(track_ids)

    # Generate data frame of audio features
    audio_features_df = pd.DataFrame(audio_features)
    audio_features_df = audio_features_df[
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
    matrix = audio_features_df.corr()

    # Display matrix
    sns.heatmap(matrix, annot=True, cmap="rocket")

    st.pyplot(plt.gcf())



