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

    # Add External URLs to content-based recommendations
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

st.header("Music Recommendation System")
text = st.selectbox(
    'Select music you want recommendation for', 
    music_df['Track Name'].values,
    key='song_selector'
)

if st.button("Recommend"):
    df = hybrid_recommendations(text)

   # Convert Track Name to HTML hyperlink
df['Track Name'] = df.apply(
    lambda row: f'<a href="{row["External URLs"]}" target="_blank">{row["Track Name"]}</a>',
    axis=1
)

# Drop External URLs for cleaner view
df_display = df.drop(columns=['External URLs'])

# Reset index from 1
df_display.index = np.arange(1, len(df_display) + 1)
df_display.index.name = "No."

# Display interactive HTML table
st.markdown("Recommended Songs")
st.markdown("Click on a song title to listen on an external platform.")

# Render HTML-formatted dataframe using st.write with unsafe HTML
st.write(
    df_display.to_html(escape=False),
    unsafe_allow_html=True
)


