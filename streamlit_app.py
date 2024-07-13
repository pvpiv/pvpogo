import streamlit as st
import pandas as pd
import streamlit_analytics
import os
import requests

# Load your dataset
df = pd.read_csv('pvp_data.csv')
url = "https://pvpcalc.streamlit.app/"
st.write("[Check CP for all IVs here](%s)" % url)
# Define a function to format the data as required
def format_data(pokemon_family, shadow_only):
    # Filter data for the family and shadow condition
    if shadow_only:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == True)]
    else:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == False)]
    
    # Prepare the data for display
    formatted_data = []
    attributes = ['Rank', 'CP', 'IVs', 'Level', 'MoveSet']
    leagues = ['Little', 'Great', 'Ultra', 'Master']
    for _, row in family_data.iterrows():
        for attr in attributes:
            entry = {'Pokemon': row['Pokemon'], 'Attribute': attr}
            for league in leagues:
                value = row[f'{league}_{attr}']
                if pd.notna(value) and isinstance(value, (int, float)):
                    entry[league] = f'{int(value):,}'  # Remove decimals and format as integer
                else:
                    entry[league] = value if pd.notna(value) else ''
            formatted_data.append(entry)
    return formatted_data
    
def download_data_file():
    link = st.secrets["link"]
    response = requests.get(link)
    if response.status_code == 200:
        with open("data.json", "wb") as file:
            file.write(response.content)
    else:
        st.error("Failed to download data.json")
        
def upload_data_file():
    link = st.secrets["link"]
    with open("data.json", "rb") as file:
        response = requests.put(link, files={"file": file})
    if response.status_code == 200:
        st.success("data.json uploaded successfully")
    else:
        st.error("Failed to upload data.json")

# Set up UI elements
#streamlit_analytics.start_tracking(load_from_json='data/data.json')

if not os.path.exists("data.json"):
    download_data_file()

# If data.json exists and is empty, start tracking without loading
if os.path.exists("data.json") and os.path.getsize("data.json") == 0:
    streamlit_analytics.start_tracking()
else:
    streamlit_analytics.start_tracking(load_from_json='data.json')
    
st.write("### Pokémon Selection")
show_shadow = st.checkbox('Show only Shadow Pokémon', False)
#streamlit_analytics.track(save_to_json="analytics.json")

# Filter the dropdown list based on the checkbox
if show_shadow:
    pokemon_list = df[df['Shadow']]['Pokemon'].unique()
else:
    pokemon_list = df[~df['Pokemon'].str.contains("Shadow")]['Pokemon'].unique()

pokemon_choice = st.selectbox('Select a Pokémon:', pokemon_list)

# Find the family of the selected Pokémon
pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]

# Display formatted data for the selected Pokémon's family
family_data = format_data(pokemon_family, show_shadow)
if family_data:
    
    df_display = pd.DataFrame(family_data)
    # Set up DataFrame for proper display
    df_display.rename(columns={df.columns[0]: 'Pokemon'})
    df_display.rename(columns={df.columns[1]: 'Attribute'})
    df_display.set_index(['Pokemon'], inplace=True)
    st.table(df_display)
else:
    st.write("No data available for the selected options.")
#streamlit_analytics.track(save_to_json="analytics.json")
streamlit_analytics.stop_tracking(save_to_json='data/data.json')
upload_data_file()
# Custom CSS to improve mobile view and table fit
st.markdown(
    """
    <style>
    @media (max-width: 600px) {
        .css-18e3th9 {
            padding: 0.5rem 1rem;
        }
        .css-1d391kg {
            font-size: 1rem;
        }
        .css-1i0h2kc {
            width: 100% !important;
            display: block;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch; /* Smooth scrolling for iOS */
        }
        .css-1i0h2kc table {
            width: 100%;
        }
        .css-1i0h2kc table th,
        .css-1i0h2kc table td {
            padding: 0.25rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
