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
        family_data = df[(df['Family'] == pokemon_family) & (df['Shadow'] == False)]
    
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

# Set up UI elements
st.write("### Pokémon Selection")
show_shadow = st.checkbox('Show only Shadow Pokémon', False)

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
    df_display = df_display.pivot_table(index=['Pokemon', 'League'], values=['Rank', 'CP', 'IVs', 'Level', 'MoveSet'], aggfunc=lambda x: x)
    st.table(df_display)
else:
    st.write("No data available for the selected options.")
