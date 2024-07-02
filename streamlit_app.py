import streamlit as st
import pandas as pd

# Load your dataset
df = pd.read_csv('pokemon_data.csv')

# Define a function to format the data as required
def format_data(pokemon_family):
    # Filter data for the family
    family_data = df[df['Family'] == pokemon_family]
    
    # Prepare the data for display
    columns = ['League', 'Rank', 'CP', 'IVs', 'Level', 'MoveSet']
    leagues = ['Little', 'Great', 'Ultra', 'Master']
    
    formatted_data = {}
    for _, row in family_data.iterrows():
        pokemon_name = row['Pokemon']
        formatted_data[pokemon_name] = {col: [] for col in columns}
        formatted_data[pokemon_name]['League'] = leagues
        
        for league in leagues:
            formatted_data[pokemon_name]['Rank'].append(row[f'{league}_Rank'] if pd.notna(row[f'{league}_Rank']) else 'NA')
            formatted_data[pokemon_name]['CP'].append(row[f'{league}_CP'] if pd.notna(row[f'{league}_CP']) else 'NA')
            formatted_data[pokemon_name]['IVs'].append(row[f'{league}_IVs'] if pd.notna(row[f'{league}_IVs']) else 'NA')
            formatted_data[pokemon_name]['Level'].append(row[f'{league}_Level'] if pd.notna(row[f'{league}_Level']) else 'NA')
            formatted_data[pokemon_name]['MoveSet'].append(row[f'{league}_MoveSet'] if pd.notna(row[f'{league}_MoveSet']) else 'NA')

    return formatted_data

# User selects a Pokémon
pokemon_choice = st.selectbox('Select a Pokémon:', df['Pokemon'].unique())

# Find the family of the selected Pokémon
pokemon_family = df[df['Pokemon'] == pokemon_choice]['Family'].iloc[0]

# Display formatted data for the selected Pokémon's family
family_data = format_data(pokemon_family)
for pokemon, data in family_data.items():
    st.write(f"### {pokemon}")
    for i, league in enumerate(data['League']):
        st.write(f"#### {league} League")
        st.write(f"Rank: {data['Rank'][i]}")
        st.write(f"CP: {data['CP'][i]}")
        st.write(f"IVs: {data['IVs'][i]}")
        st.write(f"Level: {data['Level'][i]}")
        st.write(f"MoveSet: {data['MoveSet'][i]}")
