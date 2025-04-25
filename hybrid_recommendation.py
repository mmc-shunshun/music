import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from contentbasedrecommendation import content_based_recommendations

# Load the music dataset
music_df = pd.read_csv('music.csv')

# Function to calculate weighted popularity based on release date
def calculate_weighted_popularity(release_date):
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    time_span = datetime.now() - release_date
    weight = 1 / (time_span.days + 1)
    return weight

# Function to get hybrid recommendations
def hybrid_recommendations(input_song_name, num_recommendations=5):
    if input_song_name not in music_df['Track Name'].values:
        st.warning(f"'{input_song_name}' not found in the dataset. Please enter a valid song name.")
        return pd.DataFrame()

    # Content-based recommendations
    content_based_rec = content_based_recommendations(input_song_name, num_recommendations)

    # Weighted popularity of the input song
    popularity_score = music_df.loc[music_df['Track Name'] == input_song_name, 'Popularity'].values[0]
    release_date = music_df.loc[music_df['Track Name'] == input_song_name, 'Release Date'].values[0]
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(release_date)

    # Create weighted popularity DataFrame
    weighted_pop_df = pd.DataFrame({
        'Track Name': [input_song_name],
        'Artists': [music_df.loc[music_df['Track Name'] == input_song_name, 'Artists'].values[0]],
        'Album Name': [music_df.loc[music_df['Track Name'] == input_song_name, 'Album Name'].values[0]],
        'Release Date': [release_date],
        'Popularity': [weighted_popularity_score],
        'External URLs': [music_df.loc[music_df['Track Name'] == input_song_name, 'External URLs'].values[0]]
    })

    # Add External URLs to recommendations
    content_based_rec['External URLs'] = content_based_rec['Track Name'].apply(
        lambda name: music_df.loc[music_df['Track Name'] == name, 'External URLs'].values[0]
    )

    # Combine content and weighted popularity
    hybrid_df = pd.concat([content_based_rec, weighted_pop_df], ignore_index=True)
    hybrid_df = hybrid_df.sort_values(by='Popularity', ascending=False)
    hybrid_df = hybrid_df[hybrid_df['Track Name'] != input_song_name]

    return hybrid_df

# Streamlit UI
st.title("🎵 Music Recommendation System")

# Dropdown to select song
selected_song = st.selectbox("Select a track for recommendations:", music_df['Track Name'].unique())

# Recommend button with unique key
if st.button("Recommend", key="unique_recommend_btn"):
    recommendations = hybrid_recommendations(selected_song)

    if not recommendations.empty:
        # Create HTML hyperlinks for Track Name
        recommendations['Track Name'] = recommendations.apply(
            lambda row: f'<a href="{row["External URLs"]}" target="_blank">{row["Track Name"]}</a>',
            axis=1
        )

        # Drop External URLs column for clean view
        display_df = recommendations.drop(columns=['External URLs'])

        # Reset index starting from 1
        display_df.index = np.arange(1, len(display_df) + 1)
        display_df.index.name = "No."

        st.markdown("#### Recommended Songs (click track name to open)")
        st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
