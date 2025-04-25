import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st
from contentbasedrecommendation import content_based_recommendations 

music_df = pd.read_csv('music.csv')

# Function to calculate weighted popularity scores based on release date
def calculate_weighted_popularity(release_date):
    # Convert the release date to datetime object
    release_date = datetime.strptime(release_date, '%Y-%m-%d')

    # Calculate the time span between release date and today's date
    time_span = datetime.now() - release_date

    # Calculate the weighted popularity score based on time span 
    #(e.g., more recent releases have higher weight)
    weight = 1 / (time_span.days + 1)
    return weight

# a function to get hybrid recommendations based on weighted popularity
def hybrid_recommendations(input_song_name, num_recommendations=5, alpha=0.5):
    if input_song_name not in music_df['Track Name'].values:
        print(f"'{input_song_name}' not found in the dataset. Please enter a valid song name.")
        return

    # Get content-based recommendations
    content_based_rec = content_based_recommendations(input_song_name,
                                                      num_recommendations)

    # Get the popularity score of the input song
    popularity_score = music_df.loc[music_df['Track Name'] == input_song_name,
                                    'Popularity'].values[0]

    # Calculate the weighted popularity score
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(music_df.loc[music_df['Track Name'] == input_song_name,
                                                                                              'Release Date'].values[0])

    # Combine content-based and popularity-based recommendations based on weighted popularity
    weighted_pop_df = pd.DataFrame({
        'Track Name': [input_song_name],
        'Artists': [music_df.loc[music_df['Track Name'] == input_song_name, 'Artists'].values[0]],
        'Album Name': [music_df.loc[music_df['Track Name'] == input_song_name, 'Album Name'].values[0]],
        'Release Date': [music_df.loc[music_df['Track Name'] == input_song_name, 'Release Date'].values[0]],
        'Popularity': [weighted_popularity_score],
        'External URLs': [music_df.loc[music_df['Track Name'] == input_song_name, 'External URLs'].values[0]]
    })


    content_based_rec['External URLs'] = content_based_rec['Track Name'].apply(
        lambda name: music_df.loc[music_df['Track Name'] == name, 'External URLs'].values[0]
    )

    hybrid_recommendations = pd.concat([content_based_rec, weighted_pop_df], ignore_index=True)

    # Sort the hybrid recommendations based on weighted popularity score
    hybrid_recommendations = hybrid_recommendations.sort_values(by='Popularity', 
                                                                ascending=False)

    # Remove the input song from the recommendations
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['Track Name'] != input_song_name]

   

    return hybrid_recommendations

st.set_page_config(page_title="Music Recommender 🎧", layout="centered")

st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🎵 Intelligent Music Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Get personalized song recommendations based on your selection and popularity trends.</p>", unsafe_allow_html=True)
st.markdown("---")

# Dropdown Selection
selected_track = st.selectbox(
    '🎼 Choose a song you like:',
    sorted(music_df['Track Name'].unique()),
    key='song_selector_2'
)

# Recommend Button
if st.button("🔍 Recommend"):
    st.markdown("#### 📃 Top Recommendations:")
    df = hybrid_recommendations(selected_track)
    df['Track Name'] = df.apply(
        lambda row: f"[{row['Track Name']}]({row['External URLs']})", axis=1
    )

    # Drop the raw URL column for display
    df_display = df.drop(columns=['External URLs'])

    if not df.empty:
        df.index = np.arange(1, len(df) + 1)
        df.index.name = "No."
        st.dataframe(df.style.format({"Popularity": "{:.2f}"}), use_container_width=True)
    else:
        st.info("🤔 No recommendations found. Try selecting another song.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)