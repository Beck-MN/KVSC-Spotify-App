"""Developer: Beck Christensen
   Date Started: 8-7-2024
   
   What is this shit? tbh brother i dont really know 
   im just trying out the spotify API requests to potentially
   help with my radio job"""

import os

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

# Importing .env file
from dotenv import load_dotenv, dotenv_values
# Loading in enviroment values
load_dotenv()

today = str(date.today())

# Connect to spotify an give proper permissions for playlist customization
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope="playlist-modify-private,playlist-modify-public",
    )
)


# Request headers for webscraper so it has proper permissions
request_headers = {
    "referer": "https://www.kvsc.org/wp-content/themes/kvsc/css/style.css?ver=6.6.1",
    "accept-language": "en-US,en;q=0.9",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Opera GX";v="112"',
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua-platform-version": '"10.0.0"',
    "sec-ch-viewport-width": "792",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}


# Get the HTML of the kvsc top 30 page
response = requests.get(
    "https://www.kvsc.org/music/nacc-charts/", headers=request_headers
)


# Funtion to get a return the current KVSC top 30 via a web scraper
def get_nacc_chart():

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

    df = df.drop(index=0)

    return df


# Creates a correlation matrix comparing the audio features of a spotify playlist
def gen_corr_matrix(playlist_id):

    # Get track ID's of songs from generated playlist
    # Get audio features of each track
    playlist_tracks = sp.playlist_tracks(playlist_id)
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


# Function to creat a spotify playlist of the top 30
def generate_playlist(nacc_df):

    # Get user id
    user_id = sp.me()["id"]

    # Create Playlist
    st.write("Generating Playlist of NACC Top 30 as of ", today)
    playlist = sp.user_playlist_create(
        user_id,
        "KVSC Top 30: Week of" + get_date().text.replace('Updated',''),
        description="Playlist of the top 30 albums on KVSC. " + get_date().text,
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

    st.subheader(
        "Playlist Generated! Find it in your library or here: " + playlist["external_urls"]["spotify"], divider="red"
    )

    return playlist["id"]


# Gets the update date for the top 30 on kvsc.org
def get_date():

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("body")
    div = body.find("div", class_="content clearfix")
    date = div.find("h3")

    return date


# Gets the custom paragraph made each week for the top 30
def get_paragraph():

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find("body")
    div = body.find("div", class_="content clearfix")
    p1 = div.find("p")
    p2 = p1.find_next("p")

    return p2


# Main function
def main():

    # Get the current top 30 from kvsc.org
    nacc_df = get_nacc_chart()

    st.logo("/img/Kvsc_official_logo_2009.png", link="https://kvsc.org")
    st.header("KVSC Weekly Top 30","https://www.kvsc.org/music/nacc-charts/", divider="red")
    
    st.write(
        "The North American College and Community radio, or NACC chart, tabulates weekly the top 200 artists being spun on about 200 member stations. Member stations represent a vast array of non-commercial college and community-based radio services throughout the US and Canada. NACC also compiles charts on a number of specialty genres, including jazz, blues, folk, and hip-hop."
    )
    st.write(get_paragraph().text)
    st.write("Click \"Generate Spotify Playlist \" below to create a playlist of the current top 30 so you can listen along with us!")
    st.subheader(get_date().text, anchor=None, divider="gray")
    st.dataframe(nacc_df, hide_index=True)

    if st.button("Generate Spotify Playlist", type="primary"):

        # Create spotify playlist of the current top 30
        playlist_id = generate_playlist(nacc_df)

        st.subheader("Correlation matix of the spotify audio features", anchor=None)
        st.write("A correlation matrix is a tool used to measure how strongly different variables relate to each other. Spotify uses something called audio features which are terms like danceability, energy, speechiness, acousticness, instrumentalness, liveness, valence, and tempo. A correlation matrix helps us understand how these features interact.")
        st.write("Each number in the matrix, called a correlation coefficient, ranges from -1 to 1. A coefficient close to 1 means two features increase together (for example, as energy goes up, danceability might also increase), while a value near -1 means that when one feature increases, the other decreases (like if acousticness tends to go down when energy goes up). A coefficient close to 0 means there’s little to no relationship between the features.")     
        st.write(
             "Generating correlation matix of the auido features of the NACC top 30..."
        )
        
        gen_corr_matrix(playlist_id)
    
    st.caption("Developed by: Beck Christensen")


if __name__ == "__main__":
    main()
