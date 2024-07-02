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
    attributes = ['Rank', 'CP', 'IVs', 'Level', 'MoveSet']
    leagues = ['Little', 'Great', 'Ultra', 'Master']
    previous_pokemon = None
    for _, row in family_data.iterrows():
        if previous_pokemon and previous_pokemon != row['Pokemon']:
            # Insert an empty row for separation
            formatted_data.extend([{ 'Pokemon': '', 'Attribute': '', 'League': league } for league in leagues])
        for attr in attributes:
            entry = {'Pokemon': row['Pokemon'], 'Attribute': attr}
            for league in leagues:
                val = row[f'{league}_{attr}']
                if pd.notna(val):
                    if isinstance(val, float) and val.is_integer():
                        val = int(val)  # Convert float to int if it's an integer
                    entry[league] = val
                else:
                    entry[league] = 'NA'
            formatted_data.append(entry)
        previous_pokemon = row['Pokemon']
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
    # Convert all numerical columns to integers if applicable
    df_display[['Little', 'Great', 'Ultra', 'Master']] = df_display[['Little', 'Great', 'Ultra', 'Master']].applymap(lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)
    df_pivot = df_display.pivot_table(index=['Pokemon', 'Attribute'], columns='League', aggfunc=lambda x: x).fillna('NA')
    df_pivot.columns = df_pivot.columns.droplevel(0)  # Simplify the multi-index
    df_pivot.reset_index(inplace=True)
    # Display the DataFrame
    st.write(df_pivot)  # Using st.write to handle DataFrame directly
else:
    st.write("No data available for the selected options.")
