# app.py
from streamlit_extras.stylable_container import stylable_container
import streamlit as st
import pandas as pd
import streamlit_analytics
import json
from datetime import date, datetime
import requests
import pytz


# Import utility functions and session state manager
from utils import (
    MyList,
    load_from_firestore,
    save_to_firestore,
    format_data,
    filter_ids,
    get_top_50_ids,
    make_search_string,
    format_data_top,
    calculate_days_since,
    get_last_updated_date
)
from session_state_manager import (
    initialize_session_state,
    update_top_num,
    upd_shadow,
    upd_tab_str,
    upd_xl,
    upd_seas,
    upd_cust,
    upd_inv,
    little_but,
    great_but,
    ultra_but,
    master_but
)

# Initialize session state
initialize_session_state()

#st.set_page_config(layout="wide")

season_start = date(2024, 9, 3)

# Set GitHub API URL based on 'show_custom' flag
if not st.session_state['show_custom']:
    GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pvpogo/commits?path=pvp_data.csv"
else:
    GITHUB_API_URL = "https://api.github.com/repos/pvpiv/pvpogo/commits?path=pvp_data_fossil.csv"

# Load data
if st.session_state['show_custom']:
    df = pd.read_csv('pvp_data_fossil.csv')
else:
    df = pd.read_csv('pvp_data.csv')

query_params = st.experimental_get_query_params()
st.set_page_config(layout = "wide")
cols = st.columns((2,8,1))

with cols[0]:
   

    with stylable_container(
    key= "Settings" ,
    css_styles="""
        button {
            width: 150px;
            height: 45px;
            background-color: green;
            color: white;
            border-radius: 5px;
            white-space: nowrap;
        }
        """,
):
        popover = st.popover('Settings' ,use_container_width =True)
        if not st.session_state['table_string_butt']:


            show_custom_boxz = popover.checkbox('Sunshine Cup', on_change=upd_cust, key='sho_cust')
            show_shadow_boxz = popover.checkbox('Include Shadow Pokémon', on_change=upd_shadow, key='sho_shad', value=st.session_state['get_shadow'])

        else:

            show_custom_boxz = popover.checkbox('Sunshine Cup', on_change=upd_cust, key='sho_cust')
            topstrin = str(st.session_state.top_num)
            fam_box = popover.checkbox('Include pre-evolutions', value=True)
            show_xl_boxz = popover.checkbox('Include XL Pokémon \n\n(No XL Candy needed)', on_change=upd_xl, key='sho_xl', value=st.session_state['show_xl'])
            iv_box = popover.checkbox('Include IV Filter \n\n(Works for Non XL Pokémon)', value=False)
            popover.subheader("Rankings Tables",divider="blue")
            popover.button("Show Little", key='little_table', on_click=little_but)
            popover.button("Show Great", key='great_table', on_click=great_but)
            popover.button("Show Ultra", key='ultra_table', on_click=ultra_but)
            popover.button("Show Master", key='master_table', on_click=master_but)
            # tables_pop = st.popover("League Tables")
            
        
    if st.session_state['table_string_butt']:
        butt_label = "Switch to Pokémon Lookup"
    else: 
        butt_label = "Switch to Search Strings"
    st.toggle(
        label=butt_label,
        key= "tab_str_butt",
        value = st.session_state['table_string_butt'],
        on_change = upd_tab_str
    )
with cols[1]:

    #str_tab_but = st.button(butt_label,key="tab_str_butt",on_click=upd_tab_str,use_container_width =True)
    
    today = date.today()
    
    # Section 1 - PVP Pokemon Search Table
    show_shadow = st.session_state['get_shadow']
    pokemon_list = MyList(df[~df['Pokemon'].str.contains("Shadow", na=False)]['Pokemon'].unique())

    if not st.session_state['table_string_butt']:
        if pokemon_list:
            poke_label = 'All League Rankings, IVs, & Moves Table' if not st.session_state['show_custom'] else 'Sunshine Cup Rankings, IVs, & Moves Table'
            st.subheader(poke_label)
            pokemon_choice = st.selectbox(
                "",
                pokemon_list,
                index=pokemon_list.last_index(),
                key="poke_choice",label_visibility='hidden',
                on_change=lambda: st.session_state.update({'get_dat': True})
            )
        
            if pokemon_choice != "Select a Pokemon" and pokemon_choice != "Select a Shadow Pokemon":
                if st.session_state['get_dat'] and pokemon_choice:
                    if st.session_state['last_sel'] != pokemon_choice or st.session_state['last_sel'] is None:
                        load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                        streamlit_analytics.start_tracking()
        
                    st.session_state['last_sel'] = pokemon_choice
                    pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]
                    family_data = format_data(pokemon_family, show_shadow, df,show_xl_boxz)
        
                    if family_data:
                        st.text_input(
                            label=today.strftime("%m/%d/%y"),
                            value=pokemon_choice,
                            disabled=True,
                            label_visibility='hidden'
                        )
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
        else:
            try:
                streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
            except:
                pass
        
        st.divider()
    else:
        # Section 2 - PVP Pokemon Search String
        
        
        st.subheader("PVP Poké Search Strings")
        if st.session_state.show_string:
            top_nbox = st.number_input(
                'Showing Top:',
                value=st.session_state.top_num,
                key='top_no',
                on_change=update_top_num,
                min_value=5,
                max_value=200,
                step=5
            )
            inv_box = st.checkbox('Invert strings', value=st.session_state.show_inverse, key='show_inv')
            #tables_pop = st.popover("League Tables")
            
            if not st.session_state['show_custom']:
                try:
                    st.write(f'Little League Top {st.session_state.top_num} Search String:')

        
                    if st.session_state['little_clicked']:
                        family_data_Little = format_data_top(df, 'Little', st.session_state.top_num,show_xl_boxz)
                        df_display_Little = pd.DataFrame(family_data_Little)
                        df_display_Little.set_index(['Pokemon'], inplace=True)
                        st.table(df_display_Little)
                    st.code(make_search_string(df, "little", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                except:
                    pass
        
                try:
                    st.write(f'Great League Top {st.session_state.top_num} Search String:')
                    if st.session_state['great_clicked']:
                        family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                        df_display_Great = pd.DataFrame(family_data_Great)
                        df_display_Great.set_index(['Pokemon'], inplace=True)
                        st.table(df_display_Great)
                    st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz,False))
                except:
                    pass
        
                try:
                    st.write(f'Ultra League Top {st.session_state.top_num} Search String:')
                    if st.session_state['ultra_clicked']:
                        family_data_Ultra = format_data_top(df, 'Ultra', st.session_state.top_num,show_xl_boxz)
                        df_display_Ultra = pd.DataFrame(family_data_Ultra)
                        df_display_Ultra.set_index(['Pokemon'], inplace=True)
                        st.table(df_display_Ultra)
                    st.code(make_search_string(df, "ultra", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                except:
                    pass
        
                try:
                    st.write(f'Master League Top {st.session_state.top_num} Search String:')
                    if st.session_state['master_clicked']:
                        family_data_master = format_data_top(df, 'Master', st.session_state.top_num)
                        df_display_master = pd.DataFrame(family_data_master)
                        df_display_master.set_index(['Pokemon'], inplace=True)
                        st.table(df_display_master)
                    st.code(make_search_string(df, "master", st.session_state.top_num, fam_box, iv_box, inv_box,True))
                except:
                    pass
        
                try:
                    st.write(f'All Leagues Top {st.session_state.top_num} Search String:')
                    st.code(make_search_string(df, "all", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                except:
                    pass
            else:
                try:
                    tables_pop.button("Show Sunshine Cup Table", key='sun_table', on_click=great_but)
                    days_since_date = calculate_days_since(season_start)
                    age_string = f"age0-{days_since_date}&"
                    st.write(f'Sunshine Cup Top {st.session_state.top_num} Search String:')
                    if st.session_state['great_clicked']:
                        family_data_Great = format_data_top(df, 'Great', st.session_state.top_num,show_xl_boxz)
                        df_display_Great = pd.DataFrame(family_data_Great)
                        df_display_Great.set_index(['Pokemon'], inplace=True)
                        st.table(df_display_Great)
                    st.code(make_search_string(df, "great", st.session_state.top_num, fam_box, iv_box, inv_box,show_xl_boxz))
                except:
                    pass
        
            try:
                load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                streamlit_analytics.start_tracking()
        
                st.text_input(
                    label=today.strftime("%m/%d/%y"),
                    value=f'*Click string to show Copy button and Paste Top {topstrin} into PokeGO*',
                    label_visibility='hidden',
                    disabled=True,
                    key="sstring"
                )
                st.divider()
                st.text_input(label="Feedback", key="fstring")
                save_to_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
        
                load_from_firestore(streamlit_analytics.counts, st.secrets["fb_col"])
                streamlit_analytics.start_tracking()
                if st.session_state['little_clicked']:
                    st.text_input(
                        label=today.strftime("%m/%d/%y"),
                        value='Little Table',
                        label_visibility='hidden',
                        disabled=True,
                        key="little_text"
                    )
                if st.session_state['great_clicked']:
                    st.text_input(
                        label=today.strftime("%m/%d/%y"),
                        value='Great Table',
                        label_visibility='hidden',
                        disabled=True,
                        key="great_text"
                    )
                if st.session_state['ultra_clicked']:
                    st.text_input(
                        label=today.strftime("%m/%d/%y"),
                        value='Ultra Table',
                        label_visibility='hidden',
                        disabled=True,
                        key="ultra_text"
                    )
                if st.session_state['master_clicked']:
                    st.text_input(
                        label=today.strftime("%m/%d/%y"),
                        value='Master Table',
                        label_visibility='hidden',
                        disabled=True,
                        key="master_text"
                    )
                streamlit_analytics.stop_tracking(unsafe_password=st.secrets['pass'])
        
            # Get the last updated date

            except:
                pass
    last_updated = get_last_updated_date(GITHUB_API_URL)
    st.write(f"Last updated: {last_updated} (EST)")
# Custom CSS for mobile view and table fit
st.markdown("""
<style>
button {
    height: 50px;
    width: 200px;
    color: blue;
}
</style>
""", unsafe_allow_html=True)
