import streamlit as st
import pandas as pd
import streamlit_analytics
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import date


# Load your dataset
df = pd.read_csv('pvp_data.csv')
url = "https://pvpcalc.streamlit.app/"
st.write("[Check CP for all IVs here](%s)" % url)

# Helper class for custom list behavior
class MyList(list):
    def last_index(self):
        return len(self) - 1
def unique(list1):

    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return(unique_list)        
# Firestore loading function
def load_from_firestore(counts, collection_name):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    firestore_counts = col.document(st.secrets["fb_col"]).get().to_dict()
    if firestore_counts is not None:
        for key in firestore_counts:
            if key in counts:
                counts[key] = firestore_counts[key]

# Firestore saving function
def save_to_firestore(counts, collection_name):
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="pvpogo")
    col = db.collection(collection_name)
    col.document(st.secrets["fb_col"]).set(counts)

# Format data for display
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
                entry[league] = f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value if pd.notna(value) else ''
            formatted_data.append(entry)
    return formatted_data
    
def filter_ids(row):
    current_id = row['ID']
    evo_next_list = row['Evo_Fam'].split(';')
    if str(current_id) in evo_next_list:
        position = evo_next_list.index(str(current_id))
        filtered_list = evo_next_list[:position + 1]
    else:
        filtered_list = evo_next_list
    return list(filtered_list)
# Generate top 50 IDs string for a league

def get_top_50_ids(rank_column, league, top_n,fam):
    df_filtered = df.dropna(subset=[rank_column])
    df_filtered = df_filtered[df_filtered[rank_column] <= top_n]
    #df_filtered = df_filtered.sort_values(by=rank_column)
    #top_df = df_filtered.sort_values(by=rank_column).drop_duplicates(subset=['ID']).head(top_n)
    top_df = df_filtered.sort_values(by=rank_column).drop_duplicates(subset=['ID'])
    seen = set()
    if fam:
        top_df['Filtered_Evo_next'] = top_df.apply(filter_ids, axis=1)
        all_ids_set = set([item for sublist in top_df['Filtered_Evo_next'] for item in sublist])
        all_ids = df['ID'].astype(str).tolist()
        all_ids = [element for element in all_ids if element in all_ids_set and not (element in seen or seen.add(element))]
        #all_ids = all_ids_set['ID'].astype(str).tolist()
    else:
        all_ids = top_df['ID'].astype(str).tolist()
    prefix = 'cp-500&' if league == 'little' else 'cp-1500&' if league == 'great' else 'cp-2500&' if league == 'ultra' else ''
    ids_string = prefix + ','.join(all_ids)
    return ids_string.replace("&,", "&")

# Generate search string based on league
def make_search_string(league, top_n,fam):
    if league == 'little':
        return get_top_50_ids('Little_Rank', 'little', top_n,fam)
    elif league == 'great':
        return get_top_50_ids('Great_Rank', 'great', top_n,fam)
    elif league == 'ultra':
        return get_top_50_ids('Ultra_Rank', 'ultra', top_n,fam)
    elif league == 'master':
        return get_top_50_ids('Master_Rank', '', top_n,fam)

# Update session state for top number
def update_top_num():
    st.session_state.top_num = st.session_state.top_no

# Initialize session state variables
if 'get_dat' not in st.session_state:
    st.session_state['get_dat'] = False
if 'last_sel' not in st.session_state:
    st.session_state['last_sel'] = None
if 'last_n' not in st.session_state:
    st.session_state['last_n'] = 0
if "top_num" not in st.session_state:
    st.session_state['top_num'] = 50

# UI elements
today = date.today()
show_string = st.checkbox('View Top PVP Pokemon Search String (copy/paste into POGO, 50 by default)')

if show_string:

    fam_box = st.checkbox('Include pre-evolutions',value=True)
    top_nbox = st.slider('Top', value=st.session_state.top_num, key='top_no', on_change=update_top_num, min_value=5, max_value=200, step=5)
    #placeholderlil = st.empty()
    #placeholdergrt = st.empty()
    #placeholderult = st.empty()
    #placeholdermstr = st.empty()
    load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
    streamlit_analytics.start_tracking()
    
    st.text_input(label=today.strftime("%m/%d/%y"), value='*Click string to show Copy button and Paste into PokeGO*', label_visibility='hidden', disabled=True, key="sstring")
    try:
        save_to_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
    except:
        pass
    #placeholderlil.text_input(label='Little League Top ' + str(st.session_state.top_num) + ' Search String:', value=make_search_string("little", st.session_state.top_num), disabled=True)
    #placeholdergrt.text_input(label='Great League Top ' + str(st.session_state.top_num) + ' Search String: (For most PVP IVs add &0-1attack)', value=make_search_string("great", st.session_state.top_num), disabled=True)
    #placeholderult.text_input(label='Ultra League Top ' + str(st.session_state.top_num) + ' Search String: (For most PVP IVs add &0-1attack)', value=make_search_string("ultra", st.session_state.top_num), disabled=True)
    #placeholdermstr.text_input(label='Master League Top ' + str(st.session_state.top_num) + ' Search String: (For BEST PVP IVs add &3-4*)', value=make_search_string("master", st.session_state.top_num), disabled=True)
    st.write('Little League Top ' + str(st.session_state.top_num) + ' Search String:')
    st.code(make_search_string("little", st.session_state.top_num,fam_box))
    st.write('Great League Top ' + str(st.session_state.top_num) + ' Search String: (For most PVP IVs add &0-1attack)')
    st.code(make_search_string("great", st.session_state.top_num,fam_box))
    st.write('Ultra League Top ' + str(st.session_state.top_num) + ' Search String: (For most PVP IVs add &0-1attack)')
    st.code(make_search_string("ultra", st.session_state.top_num,fam_box))
    st.write('Master League Top ' + str(st.session_state.top_num) + ' Search String: (For BEST PVP IVs add &3-4*)')
    st.code(make_search_string("master", st.session_state.top_num,fam_box))
show_shadow = st.checkbox('Show only Shadow Pokémon')

pokemon_list = df[df['Shadow']]['Pokemon'].unique() if show_shadow else df[~df['Pokemon'].str.contains("Shadow", na=False)]['Pokemon'].unique()
pokemon_list = MyList(pokemon_list)

if pokemon_list:
    pokemon_choice = st.selectbox('Select a Pokémon:', pokemon_list, index=pokemon_list.last_index(), label_visibility='hidden', key="poke_choice", on_change=lambda: st.session_state.update({'get_dat': True}))

    if st.session_state['get_dat'] and pokemon_choice:
        if st.session_state['last_sel'] != pokemon_choice or st.session_state['last_sel'] is None:
            load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
            streamlit_analytics.start_tracking()

        st.session_state['last_sel'] = pokemon_choice
        pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]
        family_data = format_data(pokemon_family, show_shadow)
        
        if family_data:
            st.text_input(label=today.strftime("%m/%d/%y"), value=pokemon_choice, disabled=True, label_visibility='hidden')
            df_display = pd.DataFrame(family_data)
            df_display.set_index(['Pokemon'], inplace=True)
            st.table(df_display)
            
            try:
                save_to_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
            except:
                pass
        else:
            st.session_state['get_dat'] = False

# Custom CSS for mobile view and table fit
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
