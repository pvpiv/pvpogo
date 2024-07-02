import streamlit as st
import pandas as pd

# Load your dataset
df = pd.read_csv('pokemon_data.csv')

# Define a function to format the data as required
def format_data(pokemon_family, shadow_only):
    # Filter data for the family and shadow condition
    if shadow_only:
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == True)]
    else:
        family_data = df[(df['Family'] == pokemon_family) & (~df['Pokemon'].str.contains("Shadow"))]
    
    # Prepare the data for display
    formatted_data = []
    leagues = ['Little', 'Great', 'Ultra', 'Master']
    for _, row in family_data.iterrows():
        for league in leagues:
            formatted_data.append({
                'Pokemon': row['Pokemon'],
                'League': league,
                'Rank': int(row[f'{league}_Rank']) if pd.notna(row[f'{league}_Rank']) else 'NA',
                'CP': int(row[f'{league}_CP']) if pd.notna(row[f'{league}_CP']) else 'NA',
                'IVs': row[f'{league}_IVs'] if pd.notna(row[f'{league}_IVs']) else 'NA',
                'Level': int(row[f'{league}_Level']) if pd.notna(row[f'{league}_Level']) else 'NA',
                'MoveSet': row[f'{league}_MoveSet'] if pd.notna(row[f'{league}_MoveSet']) else 'NA'
            })
    return formatted_data

# User controls grouped next to each other
st.write("### Pokémon Selection")
col1, col2 = st.columns([4, 1])
with col1:
    if st.checkbox('Show only Shadow Pokémon', False):
        pokemon_choice = st.selectbox('Select a Pokémon:', df[df['Pokemon'].str.contains("Shadow")]['Pokemon'].unique())
    else:
        pokemon_choice = st.selectbox('Select a Pokémon:', df[~df['Pokemon'].str.contains("Shadow")]['Pokemon'].unique())
with col2:
    pass

# Find the family of the selected Pokémon
pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]

# Display formatted data for the selected Pokémon's family
family_data = format_data(pokemon_family, 'Shadow' in pokemon_choice)
if family_data:
    df_display = pd.DataFrame(family_data)
    df_display = df_display.pivot_table(index=['Pokemon', 'League'], values=['Rank', 'CP', 'IVs', 'Level', 'MoveSet'], aggfunc=lambda x: x)
    st.table(df_display)
else:
    st.write("No data available for the selected options.")
