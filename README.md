# KVSC Spotify Playlist Generator

### Developer: Beck Christensen  
### Date Started: 8-7-2024  

---

## Introduction

Welcome to the **KVSC Spotify Playlist Generator**! This app leverages the Spotify API and KVSC's weekly Top 30 charts to generate a Spotify playlist of the current top albums, which you can listen to directly through Spotify. It also includes a correlation matrix to explore relationships between Spotify audio features like *danceability*, *energy*, *acousticness*, etc.

---

## Features

- **Web Scraping**: Scrapes KVSC's Top 30 NACC chart.
- **Spotify Playlist Generation**: Automatically creates a Spotify playlist of the chart.
- **Audio Feature Correlation Matrix**: Visualizes relationships between key audio features.

---

## Requirements

This app requires the following Python libraries:
- `spotipy`
- `streamlit`
- `pandas`
- `seaborn`
- `matplotlib`
- `requests`
- `BeautifulSoup`

You will also need:
- Spotify Developer credentials (client ID, secret).
- Python 3.x installed.

---

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/beck-christensen/kvsc-spotify-generator.git
   cd kvsc-spotify-generator
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt   
3. Create a '.env' file with your Spotify credentials
   ```bash
   SPOTIPY_CLIENT_ID='your-client-id'
   SPOTIPY_CLIENT_SECRET='your-client-secret'
   SPOTIPY_REDIRECT_URI='http://localhost:8080'
4. Run the app:
   ```bash
   streamlit run spotify_app.py

---

## Usage

1. Launch the app or go to the [kvsc website](https://www.kvsc.org/music/nacc-charts/) to see KVSC's Top 30 chart.
2. Click Generate Spotify Playlist to create a Spotify playlist with those albums.
3. The app will display a correlation matrix visualizing relationships between audio features of the Top 30 songs.

---

### Developed by: Beck Christensen
