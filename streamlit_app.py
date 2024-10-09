import streamlit as st
import pandas as pd
import streamlit_analytics
import json
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import date
from datetime import datetime
import requests
import pytz

# URL to get commit information for your file


#from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode,GridUpdateMode




if 1 != 0:
    class MyList(list):
        def last_index(self):
            return len(self) - 1
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

        if shadow_only == True:
            family_data = df[(df['Family'] == pokemon_family)].sort_values(by=['Shadow','ID'])
        #elif shadow_only == True:
            #family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == True)]
        elif shadow_only == False:
            family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == False)]
        
        formatted_data = []
        attributes = ['Rank','IVs','CP', 'Level', 'MoveSet']
        leagues = ['Little', 'Great', 'Ultra', 'Master']
        for _, row in family_data.iterrows():
            #for attr in attributes:
            for league in leagues:
                #entry = {'Pokemon': row['Pokemon'], 'Attribute': attr}
                entry = {'Pokemon': row['Pokemon'], 'League': league}
                #for league in leagues:
                for attr in attributes:
                    value = row[f'{league}_{attr}']
                    #entry[league] = f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value if pd.notna(value) else ''
                    entry[attr] = f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value if pd.notna(value) else ''
                formatted_data.append(entry)
        return formatted_data
        #pvpogo.streamlit.app 
    def filter_ids(row):
        current_id = row['ID']
        evo_next_list = row['Evo_Fam'].split(';')
        if str(current_id) in evo_next_list:
            position = evo_next_list.index(str(current_id))
            filtered_list = evo_next_list[:position + 1]
        else:
            filtered_list = evo_next_list
        return list(filtered_list)
    def get_top_50_ids(rank_column, league, top_n,fam,iv_bool,inv_bool,all=False):
        df_all = df.sort_values(by=rank_column)
        df_filtered = df.dropna(subset=[rank_column])
        df_filtered = df_filtered[df_filtered[rank_column] <= top_n]
        top_df = df_filtered.sort_values(by=rank_column).drop_duplicates(subset=['ID'])
        seen = set()
        if fam:
            top_df['Filtered_Evo_next'] = top_df.apply(filter_ids, axis=1)
            all_ids_set = set([item for sublist in top_df['Filtered_Evo_next'] for item in sublist])
            all_ids = df_all['ID'].astype(str).tolist()
            all_ids = [element for element in all_ids if element in all_ids_set and not (element in seen or seen.add(element))]
        else:
            all_ids = top_df['ID'].astype(str).tolist()
        if all:
            prefix = ''
        else:
            prefix = 'cp-500&' if league == 'little' else 'cp-1500&' if league == 'great' else 'cp-2500&' if league == 'ultra' else ''
       # ids_string = prefix + ','.join(all_ids)

        if not all:
            if inv_bool:
                prefix = 'cp501-&' if league == 'little' else 'cp1501-&' if league == 'great' else 'cp2501-&' if league == 'ultra' else ''
                ids_string = prefix + '!' + '&!'.join(all_ids)
            else:
                ids_string = prefix + ','.join(all_ids)
        else:
            if inv_bool:
                
                #prefix = 'cp500-&' if league == 'little' else 'cp1500-&' if league == 'great' else 'cp2500-&' if league == 'ultra' else ''
                ids_string = prefix + '!' + '&!'.join(all_ids)
            else:
                ids_string = prefix + ','.join(all_ids)

            
        if iv_bool:
            if league != 'master':
                ids_string = ids_string + "&0-1attack&3-4defense,3-4hp&2-4defense&2-4hp"
            if league == 'master':
                ids_string = ids_string + "&3*,4*"
        return ids_string.replace("&,", "&")
    # Generate search string based on league
    def make_search_string(league, top_n,fam,iv_b,inv_b,all_pre = False):
        if league == 'little':
            return get_top_50_ids('Little_Rank', 'little', top_n,fam,iv_b,inv_b)
        elif league == 'great':
            return get_top_50_ids('Great_Rank', 'great', top_n,fam,iv_b,inv_b)
        elif league == 'ultra':
            return get_top_50_ids('Ultra_Rank', 'ultra', top_n,fam,iv_b,inv_b)
        elif league == 'master':
            return get_top_50_ids('Master_Rank', 'master', top_n,fam,iv_b,inv_b)
        elif league == 'all':
            return get_top_50_ids('Little_Rank', 'little', top_n,fam,iv_b,inv_b,all_pre)+','+get_top_50_ids('Great_Rank', 'great', top_n,fam,iv_b,inv_b,all_pre)+','+get_top_50_ids('Ultra_Rank', 'ultra', top_n,fam,iv_b,inv_b,all_pre)+','+get_top_50_ids('Master_Rank', 'master', top_n,fam,iv_b,inv_b,all_pre)
    # Update session state for top number
    def update_top_num():
        st.session_state.top_num = st.session_state.top_no
    def upd_shadow():
        st.session_state.get_shadow = st.session_state.sho_shad
    def upd_seas():
        st.session_state.get_season = st.session_state.sho_seas
    def upd_cust():
        st.session_state.show_custom = st.session_state.sho_cust
    def upd_inv():
        st.session_state.show_inverse = st.session_state.sho_inv

      
    if "lit_clicked" not in st.session_state:
        st.session_state["little_clicked"] = False
    if "great_clicked" not in st.session_state:
        st.session_state["great_clicked"] = False
    if "ult_clicked" not in st.session_state:
        st.session_state["ultra_clicked"] = False
    if "master_clicked" not in st.session_state:
        st.session_state["master_clicked"] = False
          
    def little_but():
        st.session_state["little_clicked"] =  not st.session_state["little_clicked"]
    def great_but():
        st.session_state["great_clicked"] = not st.session_state["great_clicked"]
    def ultra_but():
        st.session_state["ultra_clicked"] = not st.session_state["ultra_clicked"]
    def master_but():
        st.session_state["master_clicked"] = not st.session_state["master_clicked"]
      
    def format_data_top(pokes_df, league_top,num_rank):
        family_data = pokes_df
        
        formatted_data = []
        attributes = ['Rank','IVs','CP', 'Level', 'MoveSet']
        leagues = [league_top]
        for _, row in family_data.iterrows():
            #for attr in attributes:
            for league in leagues:
                #entry = {'Pokemon': row['Pokemon'], 'Attribute': attr}
                entry = {'Pokemon': row['Pokemon'], 'League': league}
                #for league in leagues:
                for attr in attributes:
                    if attr == 'Rank':
                        if int(value) <= num_rank:
                            value = row[f'{league}_{attr}']
                            #entry[league] = f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value if pd.notna(value) else ''
                            entry[attr] = f'{int(value):,}' if pd.notna(value) and isinstance(value, (int, float)) else value if pd.notna(value) else ''
                formatted_data.append(entry)
        return formatted_data
    
    def calculate_days_since(xDate):
        # Define the date range
        start_date = xDate
        end_date = date.today()
        # Calculate the number of days since June 30
        days_since = (end_date - start_date).days
        return days_since
        
# Initialize session state variables
    if 'get_dat' not in st.session_state:
        st.session_state['get_dat'] = False
    if 'get_shadow' not in st.session_state:
        st.session_state['get_shadow'] = True
    if 'get_season' not in st.session_state:
        st.session_state['get_season'] = True   
    if 'last_sel' not in st.session_state:
        st.session_state['last_sel'] = None
    if 'last_n' not in st.session_state:
        st.session_state['last_n'] = 0
    if "top_num" not in st.session_state:
        st.session_state['top_num'] = 50
    if "show_string" not in st.session_state:
        st.session_state['show_string'] = True #st.checkbox('View Top PVP Pokemon Search Strings')
    if "show_custom" not in st.session_state:
        st.session_state['show_custom'] = False
    if "show_inverse" not in st.session_state:
        st.session_state['show_inverse'] = False
    season_start = date(2024,9,3)
    # Replace 'username', 'repo', and 'path_to_csv' with your actual GitHub details

    if not st.session_state['show_custom']:
        GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pvpogo/commits?path=pvp_data.csv"
    else:
        GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pvpogo/commits?path=pvp_data_fossil.csv"
    def get_last_updated_date():
        response = requests.get(GITHUB_API_URL)
        if response.status_code == 200:
            commit_data = response.json()[0]  # Get the latest commit
            commit_date = commit_data['commit']['committer']['date']  # Access the commit date
            est_time =  datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
            est_time = est_time.astimezone(pytz.timezone('America/New_York'))
            st.write(f"Last updated: " + str(est_time) +  " (EST)" )


 


if st.session_state['show_custom']:
    df = pd.read_csv('pvp_data_fossil.csv')
else:
    df = pd.read_csv('pvp_data.csv')


today = date.today()
query_params = st.experimental_get_query_params()

#Section 1 - PVP Pokemon Search Table
show_shadow = st.session_state['get_shadow']
#pokemon_list = df[df['Shadow']]['Pokemon'].unique() if show_shadow else df[~df['Pokemon'].str.contains("Shadow", na=False)]['Pokemon'].unique()
pokemon_list = MyList(df[~df['Pokemon'].str.contains("Shadow", na=False)]['Pokemon'].unique())
#pokemon_list = MyList(pokemon_list)
show_custom_box = st.checkbox('Sunshine Cup',on_change=upd_cust,key='sho_cust') 
show_shadow_box = st.checkbox('Include Shadow Pokémon in Rankings Table',on_change=upd_shadow,key='sho_shad',value = st.session_state['get_shadow'])
st.divider()
if pokemon_list:
    if not st.session_state['show_custom']:
        poke_label = 'All League Rankings, IVs, & Moves Table'
    else:
        poke_label = 'Sunshine Cup Rankings, IVs, & Moves Table'
    pokemon_choice = st.selectbox(poke_label, pokemon_list, index=pokemon_list.last_index(), key="poke_choice", on_change=lambda: st.session_state.update({'get_dat': True}))
     
    #show_season_box = st.checkbox('New Season Rankings (Sept 3)',on_change=upd_seas,key='sho_seas',value=True) 
    #show_custom_box = st.checkbox('Sunshine Cup',on_change=upd_cust,key='sho_cust') 
    if pokemon_choice != "Select a Pokemon" and pokemon_choice != "Select a Shadow Pokemon":
        if st.session_state['get_dat'] and pokemon_choice:
            if st.session_state['last_sel'] != pokemon_choice or st.session_state['last_sel'] is None:
                load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                streamlit_analytics.start_tracking()
    
            st.session_state['last_sel'] = pokemon_choice
            pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]
            family_data = format_data(pokemon_family, show_shadow)

            if family_data:
                if pokemon_choice != "Select a Pokemon" and pokemon_choice != "Select a Shadow Pokemon":
 
                    st.text_input(label=today.strftime("%m/%d/%y"), value=pokemon_choice, disabled=True, label_visibility='hidden')
                    df_display = pd.DataFrame(family_data)
                    df_display.set_index(['Pokemon'], inplace=True)
                    st.table(df_display)

                    
                    #if pokemon_choice != "Select a Pokemon" and pokemon_choice != "Select a Shadow Pokemon":
                    try:
                        save_to_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
                    except:
                        pass
                else:
                    try: 
                        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
                    except:
                        pass
            else:
                st.session_state['get_dat'] = False
else:
    try: 
        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
    except:
        pass

st.divider()      



#Section 2 - PVP Pokemon Search String
if st.session_state.show_string:
    is_num = query_params.get("show_top", [50])[0]
    if is_num != 50:
        st.session_state.top_num = int(is_num)
        #is_string = bool(show_string)
        #st.query_params.string = bool(show_string)
    top_nbox = st.number_input('PVP Pokemon Search Strings | Showing Top:', value=st.session_state.top_num, key='top_no', on_change=update_top_num, min_value=5, max_value=200, step=5)
    topstrin = str(st.session_state.top_num)    
    fam_box = st.checkbox('Include pre-evolutions',value=True)
    iv_box = st.checkbox('Include IV Filter (Finds good IVs for 98% of Top performers)',value =  False)
    inv_box = st.checkbox('Invert strings',value=st.session_state.show_inverse,key='show_inv')
    

    if not st.session_state['show_custom']:    
        try:
            st.write('Little League Top ' + str(st.session_state.top_num) + ' Search String:')#:')
            st.code(make_search_string("little", st.session_state.top_num,fam_box,iv_box,inv_box))
            st.button("Show Little Table", key='little_table',on_click = little_but)
            

            if st.session_state.little_clicked:
                    family_data_lit = format_data_top(df,'little',st.session_state.top_num)
                    df_display_lit = pd.DataFrame(family_data_lit)
                    df_display_lit.set_index(['Pokemon'], inplace=True)
                    st.table(df_display_lit)
        
        except:
            pass
        #try:
        st.write('Great League Top ' + str(st.session_state.top_num) + ' Search String:')#: (For most PVP IVs add &0-1attack)')
        st.code(make_search_string("great", st.session_state.top_num,fam_box,iv_box,inv_box))
        st.button("Show Great Table", key='great_table',on_click = great_but)
        if st.session_state.great_clicked:
            family_data_Great = format_data_top(df,'great',st.session_state.top_num)
            df_display_Great = pd.DataFrame(family_data_Great)
            df_display_Great.set_index(['Pokemon'], inplace=True)
            st.table(df_display_Great)
        
        #except:
           #pass
        try:
            st.write('Ultra League Top ' + str(st.session_state.top_num) + ' Search String:')#:: (For most PVP IVs add &0-1attack)')
            st.code(make_search_string("ultra", st.session_state.top_num,fam_box,iv_box,inv_box))
            st.button("Show Ultra Table", key='ultra_table',on_click =  ultra_but)
            if st.session_state.ultra_clicked:
                family_data_ultra = format_data_top(df,'ultra',st.session_state.top_num)
                df_display_ultra = pd.DataFrame(family_data_ultra)
                df_display_ultra.set_index(['Pokemon'], inplace=True)
                st.table(df_display_ultra)
        
        except:
            pass
        try:
            st.write('Master League Top ' + str(st.session_state.top_num) + ' Search String:')#: (For BEST PVP IVs add &3*,4*)')
            st.code(make_search_string("master", st.session_state.top_num,fam_box,iv_box,inv_box))
            st.button("Show Master Table", key='master_table',on_click = master_but)
            if st.session_state.master_clicked:
                family_data_master = format_data_top(df,'master',st.session_state.top_num)
                df_display_master = pd.DataFrame(family_data_master)
                df_display_master.set_index(['Pokemon'], inplace=True)
                st.table(df_display_master)
            query_params = st.experimental_get_query_params()
        except:
            pass
        try:            
            st.write('All Leagues Top ' + str(st.session_state.top_num) + ' Search String:')
            st.code(make_search_string("all", st.session_state.top_num,fam_box,iv_box,inv_box,True))    
        except:
            pass
        #is_all = query_params.get("all", [False])[0]
           # if is_all:


    else:
        try:
            days_since_date = calculate_days_since(season_start)
            age_string = f"age0-{days_since_date}&"
            st.write('Sunshine Cup Top ' + str(st.session_state.top_num) + ' Search String:')#: (For most PVP IVs add &0-1attack)')
            st.code(make_search_string("great", st.session_state.top_num,fam_box,iv_box,inv_box))
        except:
            pass
            

    try:    
        load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
        streamlit_analytics.start_tracking()
        
        st.text_input(label=today.strftime("%m/%d/%y"), value='*Click string to show Copy button and Paste Top ' + topstrin + ' into PokeGO*', label_visibility='hidden', disabled=True, key="sstring")
        #st.text_input(label=today.strftime("%m/%d/%y"), value='Results for Top ' + str(st.session_state.top_num), label_visibility='hidden', disabled=True, key="nstring")
        st.divider()  
        st.text_input(label="Feedback", key="fstring")
        save_to_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
        streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
            # Get the last updated date
        last_updated = get_last_updated_date()
    except:
        pass  

# Custom CSS for mobile view and table fit
st.markdown(
    """
    <style>
    @media (max-width: 2000px) {
        .css-18e3th9 {
            padding: 1rem 1rem;
    }
    .stNumberInput [data-baseweb=input]{
        width: 100%;
    }
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
