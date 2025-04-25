import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from contentbasedrecommendation import content_based_recommendations
from streamlit import column_config

music_df = pd.read_csv('music.csv')

def calculate_weighted_popularity(release_date):
    release_date = datetime.strptime(release_date, '%Y-%m-%d')
    time_span = datetime.now() - release_date
    weight = 1 / (time_span.days + 1)
    return weight

def hybrid_recommendations(input_song_name, num_recommendations=5, alpha=0.5):
    if input_song_name not in music_df['Track Name'].values:
        return pd.DataFrame()

    content_based_rec = content_based_recommendations(input_song_name, num_recommendations)

    content_based_rec = pd.merge(
        content_based_rec,
        music_df[['Track Name', 'External URLs']],
        on='Track Name',
        how='left'
    )

    popularity_score = music_df.loc[music_df['Track Name'] == input_song_name, 'Popularity'].values[0]
    weighted_popularity_score = popularity_score * calculate_weighted_popularity(
        music_df.loc[music_df['Track Name'] == input_song_name, 'Release Date'].values[0]
    )

    weighted_pop_df = pd.DataFrame({
        'Track Name': [input_song_name],
        'Artists': [music_df.loc[music_df['Track Name'] == input_song_name, 'Artists'].values[0]],
        'Album Name': [music_df.loc[music_df['Track Name'] == input_song_name, 'Album Name'].values[0]],
        'Release Date': [music_df.loc[music_df['Track Name'] == input_song_name, 'Release Date'].values[0]],
        'Popularity': [weighted_popularity_score],
        'External URLs': [music_df.loc[music_df['Track Name'] == input_song_name, 'External URLs'].values[0]]
    })

    hybrid_recommendations = pd.concat([content_based_rec, weighted_pop_df], ignore_index=True)
    hybrid_recommendations = hybrid_recommendations.sort_values(by='Popularity', ascending=False)
    hybrid_recommendations = hybrid_recommendations[hybrid_recommendations['Track Name'] != input_song_name]

    return hybrid_recommendations


st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🎵 Intelligent Music Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Get personalized song recommendations based on your selection and popularity trends.</p>", unsafe_allow_html=True)
st.markdown("---")

selected_track = st.selectbox(
    '🎼 Choose a song you like:',
    sorted(music_df['Track Name'].unique()),
    key='song_selector_2'
)

if st.button("🔍 Recommend"):
    st.markdown("#### 📃 Top Recommendations:")
    df = hybrid_recommendations(selected_track)

    if not df.empty:
        df.index = np.arange(1, len(df) + 1)
        df.index.name = "No."

        # Show using data_editor with clickable links (Streamlit 1.22+)
        st.data_editor(
            df[["Track Name", "Artists", "Album Name", "Release Date", "Popularity", "External URLs"]],
            column_config={
                "External URLs": column_config.LinkColumn("🔗 Link", display_text="Open")
            },
            use_container_width=True,
            hide_index=False
        )
    else:
        st.info("🤔 No recommendations found. Try selecting another song.")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 13px;'>Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)
