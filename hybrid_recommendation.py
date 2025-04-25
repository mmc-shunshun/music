import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from contentbasedrecommendation import content_based_recommendations

# Load dataset
music_df = pd.read_csv('music.csv')

# Function to calculate weighted popularity scores based on release date
def calculate_weighted_popularity(release_date):
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    time_span = datetime.now() - release_date
    weight = 1 / (time_span.days + 1)
    return weight

# Function to get hybrid recommendations
def hybrid_recommendations(input_song_name, num_recommendations=5):
    if input_song_name not in music_df['Track Name'].values:
        st.error(f"'{input_song_name}' not found in the dataset.")
        return pd.DataFrame()

    # Content-based recommendations
    content_based_rec = content_based_recommendations(input_song_name, num_recommendations)

    # Get input song details
    input_song_data = music_df[music_df['Track Name'] == input_song_name].iloc[0]
    popularity_score = input_song_data['Popularity']
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(input_song_data['Release Date'])

    # Add URLs to content-based
    content_based_rec['External URLs'] = content_based_rec['Track Name'].apply(
        lambda name: music_df.loc[music_df['Track Name'] == name, 'External URLs'].values[0]
    )

    # Create DataFrame for the input song
    weighted_pop_df = pd.DataFrame([{
        'Track Name': input_song_name,
        'Artists': input_song_data['Artists'],
        'Album Name': input_song_data['Album Name'],
        'Release Date': input_song_data['Release Date'],
        'Popularity': weighted_popularity_score,
        'External URLs': input_song_data['External URLs']
    }])

    # Combine and sort
    hybrid_df = pd.concat([content_based_rec, weighted_pop_df], ignore_index=True)
    hybrid_df = hybrid_df.sort_values(by='Popularity', ascending=False)
    hybrid_df = hybrid_df[hybrid_df['Track Name'] != input_song_name]

    return hybrid_df.reset_index(drop=True)

# Streamlit UI
st.header("🎵 Music Recommendation System")

selected_track = st.selectbox(
    'Select a song to get recommendations:',
    music_df['Track Name'].values,
    key='song_selector'
)

if st.button("Recommend", key="hybrid_recommend_button"):
    df = hybrid_recommendations(selected_track)

    if not df.empty:
        # Make Track Name clickable
        df['Track Name'] = df.apply(
            lambda row: f'<a href="{row["External URLs"]}" target="_blank">{row["Track Name"]}</a>',
            axis=1
        )

        # Remove External URLs for display
        df_display = df.drop(columns=['External URLs'])

        # Reset index starting from 1
        df_display.index = np.arange(1, len(df_display) + 1)
        df_display.index.name = "No."

        st.markdown("### 🔗 Recommended Songs")
        st.markdown("Click on a song title to listen on an external platform.")
        st.markdown(df_display.to_html(escape=False), unsafe_allow_html=True)
