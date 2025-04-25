import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from contentbasedrecommendation import content_based_recommendations

music_df = pd.read_csv('music.csv')

# Function to calculate weighted popularity scores based on release date
def calculate_weighted_popularity(release_date):
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    time_span = datetime.now() - release_date
    weight = 1 / (time_span.days + 1)
    return weight

# Hybrid recommendation function
def hybrid_recommendations(input_song_name, num_recommendations=5, alpha=0.5):
    if input_song_name not in music_df['Track Name'].values:
        st.warning(f"'{input_song_name}' not found in the dataset.")
        return pd.DataFrame()

    # Content-based recommendations
    content_based_rec = content_based_recommendations(input_song_name, num_recommendations)

    # Add External URLs to content-based results
    content_based_rec['External URLs'] = content_based_rec['Track Name'].apply(
        lambda name: music_df.loc[music_df['Track Name'] == name, 'External URLs'].values[0]
        if name in music_df['Track Name'].values else ''
    )

    # Weighted popularity for input song
    input_data = music_df[music_df['Track Name'] == input_song_name].iloc[0]
    weighted_popularity_score = input_data['Popularity'] * calculate_weighted_popularity(input_data['Release Date'])

    weighted_pop_df = pd.DataFrame({
        'Track Name': [input_song_name],
        'Artists': [input_data['Artists']],
        'Album Name': [input_data['Album Name']],
        'Release Date': [input_data['Release Date']],
        'Popularity': [weighted_popularity_score],
        'External URLs': [input_data['External URLs']],
    })

    hybrid_df = pd.concat([content_based_rec, weighted_pop_df], ignore_index=True)
    hybrid_df = hybrid_df.sort_values(by='Popularity', ascending=False)
    hybrid_df = hybrid_df[hybrid_df['Track Name'] != input_song_name]

    return hybrid_df

# Streamlit UI
st.header("🎶 Content-Type Music Recommender")

text = st.selectbox(
    'Select a song to get recommendations:',
    music_df['Track Name'].unique(),
    key='song_selector_2'
)

if st.button("Recommend", key="recommend_button"):
    df = hybrid_recommendations(text)

    if not df.empty:
        # Create HTML links for track names
        df['Track Name'] = df.apply(
            lambda row: f'<a href="{row["External URLs"]}" target="_blank">{row["Track Name"]}</a>',
            axis=1
        )

        # Drop URLs column for display
        display_df = df.drop(columns=['External URLs'])
        display_df.index = np.arange(1, len(display_df) + 1)
        display_df.index.name = "No."

        st.markdown("#### Recommended Songs")
        st.markdown("Click on the song title to listen:")

        st.write(display_df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("No recommendations found.")
