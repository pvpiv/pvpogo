import streamlit as st
import pandas as pd
import streamlit_analytics
import json
import base64
import tempfile
from google.cloud import firestore
 
counts = {"loaded_from_firestore": False}
# Load your dataset
df = pd.read_csv('pvp_data.csv')
url = "https://pvpcalc.streamlit.app/"
st.write("[Check CP for all IVs here](%s)" % url)
# Define a function to format the data as required

#fbase = st.secrets["fbase"]
#fbase = json.dumps(fbase.to_dict())


#key_dict = json.loads(st.secrets["textkey"])
#creds = service_account.Credentials.from_service_account_info(key_dict)
#db = firestore.Client(credentials=creds, project="Pvpogo")


def load_new(counts, collection_name):
    """Load count data from firestore into `counts`."""

    # Retrieve data from firestore.
    key_dict = json.loads(st.secrets["fbase"].to_dict())
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="Pvpogo")
   
    col = db.collection(collection_name)
    firestore_counts = col.document("counts").get().to_dict()

    # Update all fields in counts that appear in both counts and firestore_counts.
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]


def save_new(counts, collection_name):
    """Save count data from `counts` to firestore."""
    key_dict = json.loads(st.secrets["fbase"].to_dict())
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="Pvpogo")
    col = db.collection(collection_name)
    doc = col.document("counts")
    doc.set(counts)  # creates if doesn't exist
    

#with open("/mount/src/pvpogo/cred.json", "w") as json_file:
    #json_file.write(fbase)
    
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

# Set up UI elements
#streamlit_analytics.start_tracking(load_from_json='data/data.json')
streamlit_analytics.start_tracking()
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
#streamlit_analytics.track(firestore_key_file="firebase-key.json", firestore_collection_name="counts")

streamlit_analytics.stop_tracking()
save_new(counts,"counts")
#streamlit_analytics.stop_tracking(firestore_key_file="/mount/src/pvpogo/cred.json", firestore_collection_name="counts")
#streamlit_analytics.stop_tracking(firestore_key_file="cred.json", firestore_collection_name="pvpogo")
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
