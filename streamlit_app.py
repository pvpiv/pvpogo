import streamlit as st
import pandas as pd
import streamlit_analytics
import json
import base64
import tempfile
from google.cloud import firestore
from google.oauth2 import service_account
#counts = {"loaded_from_firestore": False}
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

class MyList(list):
    def last_index(self):
        return len(self)-1
        
def load_new(counts, collection_name):
    """Load count data from firestore into `counts`."""

    # Retrieve data from firestore.
    key_dict = json.loads(st.secrets["textkey"])
    #creds = firestore.Client.from_service_account_json(key_dict)
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
   
    col = db.collection(collection_name)
    firestore_counts = col.document("counts").get().to_dict()

    # Update all fields in counts that appear in both counts and firestore_counts.
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]


def save_new(counts, collection_name):
    """Save count data from `counts` to firestore."""
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    #creds = firestore.Client.from_service_account_json(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
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

#if 'show_shadow' not in st.session_state:
    #st.session_state.show_shadow = False

if 'get_dat' not in st.session_state:
    st.session_state['get_dat'] = False
if 'last_sel' not in st.session_state:
    st.session_state['last_sel'] = None
#else:
     #if not st.session_state['get_dat'] and st.session_state['last_sel'] is not None:
         #st.session_state['get_dat'] = True

def poke_search():
    if not st.session_state['get_dat']:
        st.session_state['get_dat'] = True
        st.session_state['last_sel'] = st.session_state.poke_choice
        #del pokemon_choice
#pokemon_choice_new = ""


#st.write("### Pokémon Selection")
#show_shadow = st.checkbox('Show only Shadow Pokémon', value=st.session_state.show_shadow, on_change=None)

show_shadow = st.checkbox('Show only Shadow Pokémon')#, on_change= track_shadow)

#if show_shadow != st.session_state.show_shadow:
    #st.session_state.show_shadow = show_shadow

#show_shadow = st.checkbox('Show only Shadow Pokémon', False)
#streamlit_analytics.track(save_to_json="analytics.json")

# Filter the dropdown list based on the checkbox
if show_shadow:
    pokemon_list = df[df['Shadow']]['Pokemon'].unique()
else:
    pokemon_list = df[~df['Pokemon'].str.contains("Shadow", na= False)]['Pokemon'].unique()

pokemon_list = MyList(pokemon_list)            
#pokemon_list = list(pokemon_list) + [""]

if pokemon_list:
    #pokemon_choice = st.selectbox('Select a Pokémon:',pokemon_list,index = pokemon_list.last_index(), label_visibility = 'hidden',key="poke_choice")
    pokemon_choice = st.selectbox('Select a Pokémon:',pokemon_list,index = pokemon_list.last_index(), label_visibility = 'hidden',key="poke_choice",on_change = poke_search)
    
    if st.session_state['get_dat']:
        if pokemon_choice is not None:
            if pokemon_choice != "Select a pokemon" or pokemon_choice != "Select a Shadow pokemon":
                load_new(streamlit_analytics.counts,"counts")
                streamlit_analytics.start_tracking()
            st.text_input(label = " ",value = st.session_state['last_sel'],disabled = True,label_visibility = 'hidden')
        #if pokemon_choice != "Select a pokemon" or pokemon_choice != "Select a Shadow pokemon":
            #sel_pok = st.selectbox('Select a Pokémon:',pokemon_list,index = pokemon_list.index(pokemon_choice), label_visibility = 'hidden',key="pcn")
            #pokemon_choice = sel_pok
            
            
            #pokemon_choice = pokemon_choice
            #with streamlit_analytics.track():
            #track = st.selectbox('Select a Pokémon:',pokemon_list,index = pokemon_list.index(sel_pok), label_visibility="hidden")
        
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
                if pokemon_choice != "Select a pokemon" or pokemon_choice != "Select a Shadow pokemon":
                    try:
                        save_new(streamlit_analytics.counts,"counts")
                        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
                    pass:
                        print(':)')
            else:
                if pokemon_choice != "Select a pokemon" or pokemon_choice != "Select a Shadow pokemon":
                    try:
                        save_new(streamlit_analytics.counts,"counts")
                        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
                    pass:
                        print(':)')
        else:
            #streamlit_analytics.counts["widgets"]["Select a Pokémon:"][pokemon_choice] -= 1
            #streamlit_analytics.counts["total_script_runs"] -= 1
            #streamlit_analytics.counts["per_day"]["script_runs"][-1] -= 1
            #save_new(streamlit_analytics.counts,"counts")
            try: 
                streamlit_analytics.stop_tracking()
            pass:
                print(':)')
        st.session_state['get_dat'] = False
#streamlit_analytics.track(save_to_json="analytics.json")
#streamlit_analytics.track(firestore_key_file="firebase-key.json", firestore_collection_name="counts")

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
