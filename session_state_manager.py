# session_state_manager.py

import streamlit as st

def initialize_session_state():
    if 'get_dat' not in st.session_state:
        st.session_state['get_dat'] = False
    if 'get_shadow' not in st.session_state:
        st.session_state['get_shadow'] = True
    if 'show_xl' not in st.session_state:
        st.session_state['show_xl'] = False
    if 'get_season' not in st.session_state:
        st.session_state['get_season'] = True
    if 'last_sel' not in st.session_state:
        st.session_state['last_sel'] = None
    if 'last_n' not in st.session_state:
        st.session_state['last_n'] = 0
    if 'top_num' not in st.session_state:
        st.session_state['top_num'] = 50
    if 'show_string' not in st.session_state:
        st.session_state['show_string'] = True
    if 'show_custom' not in st.session_state:
        st.session_state['show_custom'] = False
    if 'show_inverse' not in st.session_state:
        st.session_state['show_inverse'] = False
    if 'little_clicked' not in st.session_state:
        st.session_state['little_clicked'] = False
    if 'great_clicked' not in st.session_state:
        st.session_state['great_clicked'] = False
    if 'ultra_clicked' not in st.session_state:
        st.session_state['ultra_clicked'] = False
    if 'master_clicked' not in st.session_state:
        st.session_state['master_clicked'] = False
    if 'table_gen' not in st.session_state:
        st.session_state['table_gen'] = ''

def update_top_num():
    st.session_state.top_num = st.session_state.top_no

def upd_shadow():
    st.session_state.get_shadow = st.session_state.sho_shad
def upd_xl():
    st.session_state.show_xl = st.session_state.sho_xl
def upd_seas():
    st.session_state.get_season = st.session_state.sho_seas

def upd_cust():
    st.session_state.show_custom = st.session_state.sho_cust

def upd_inv():
    st.session_state.show_inverse = st.session_state.sho_inv

def little_but():
    st.session_state['little_clicked'] = not st.session_state['little_clicked']

def great_but():
    st.session_state['great_clicked'] = not st.session_state['great_clicked']

def ultra_but():
    st.session_state['ultra_clicked'] = not st.session_state['ultra_clicked']

def master_but():
    st.session_state['master_clicked'] = not st.session_state['master_clicked']
