import streamlit as st
import pandas as pd
import streamlit_analytics
import json
from google.cloud import firestore
from google.oauth2 import service_account

# Load your dataset
df = pd.read_csv('pvp_data.csv')
url = "https://pvpcalc.streamlit.app/"
st.write("[Check CP for all IVs here](%s)" % url)

def load_new(counts, collection_name):
    """Load count data from firestore into `counts`."""
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    firestore_counts = col.document("counts").get().to_dict()
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]

def save_new(counts, collection_name):
    """Save count data from `counts` to firestore."""
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    doc = col.document("counts")
    doc.set(counts)

def format_data(pokemon_family, shadow_only):
    if shadow_only:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == True)]
    else:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == False)]
    formatted_data = []
    attributes = ['Rank', 'CP', 'IVs', 'Level', 'MoveSet']
    leagues = ['Little', 'Great', 'Ultra', 'Master']
    for _, row in family_data.iterrows():
        for attr in attributes:
            entry = {'Pokemon': row['Pokemon'], 'Attribute': attr}
            for league in leagues:
                value = row[f'{league}_{attr}']
                if pd.notna(value) and isinstance(value, (int, float)):
                    entry[league] = f'{int(value):,}'
                else:
                    entry[league] = value if pd.notna(value) else ''
            formatted_data.append(entry)
    return formatted_data

# Initialize session state for checkbox and selectbox
if 'show_shadow' not in st.session_state:
    st.session_state.show_shadow = False
if 'show_shadow_user_interaction' not in st.session_state:
    st.session_state.show_shadow_user_interaction = False

if 'pokemon_choice' not in st.session_state:
    st.session_state.pokemon_choice = ""
if 'pokemon_choice_user_interaction' not in st.session_state:
    st.session_state.pokemon_choice_user_interaction = False

# Checkbox for shadow Pokémon
show_shadow = st.checkbox('Show only Shadow Pokémon', value=st.session_state.show_shadow)

# Update session state and log interaction only if user interaction
if show_shadow != st.session_state.show_shadow:
    st.session_state.show_shadow = show_shadow
    st.session_state.show_shadow_user_interaction = True
else:
    st.session_state.show_shadow_user_interaction = False

# Filter the dropdown list based on the checkbox
if show_shadow:
    pokemon_list = df[df['Shadow']]['Pokemon'].unique()
else:
    pokemon_list = df[~df['Pokemon'].str.contains("Shadow")]['Pokemon'].unique()

# Add an empty option for the selectbox
pokemon_list = [""] + list(pokemon_list)

# Selectbox for Pokémon selection
pokemon_choice = st.selectbox('Select a Pokémon:', pokemon_list, index=pokemon_list.index(st.session_state.pokemon_choice) if st.session_state.pokemon_choice in pokemon_list else 0)

# Update session state and log interaction only if user interaction
if pokemon_choice != st.session_state.pokemon_choice:
    st.session_state.pokemon_choice = pokemon_choice
    st.session_state.pokemon_choice_user_interaction = True
else:
    st.session_state.pokemon_choice_user_interaction = False

# Process data only if a valid Pokémon is selected
if st.session_state.pokemon_choice_user_interaction and st.session_state.pokemon_choice:
    pokemon_family = df[df['Pokemon'] == st.session_state.pokemon_choice]['Family'].iloc[0]
    family_data = format_data(pokemon_family, show_shadow)
    if family_data:
        df_display = pd.DataFrame(family_data)
        df_display.rename(columns={df.columns[0]: 'Pokemon'})
        df_display.rename(columns={df.columns[1]: 'Attribute'})
        df_display.set_index(['Pokemon'], inplace=True)
        st.table(df_display)
    else:
        st.write("No data available for the selected options.")

# Save and stop tracking analytics only if user interaction
if st.session_state.show_shadow_user_interaction or st.session_state.pokemon_choice_user_interaction:
    save_new(streamlit_analytics.counts, "counts")

streamlit_analytics.stop_tracking(unsafe_password=st.secrets["pass"])

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
            -webkit-overflow-scrolling: touch;
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
