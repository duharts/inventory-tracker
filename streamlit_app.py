import streamlit as st
import pandas as pd

# Title for the app
st.title("Food Pantry Inventory Tracker")

# Sample data for Food Pantry (adjusted for pantry use)
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=['Food Item', 'Category', 'Quantity', 'Units Donated'])

# Form to add new food items to the inventory
with st.form(key='add_food_item'):
    food_item = st.text_input('Food Item Name')
    category = st.text_input('Category')
    quantity = st.number_input('Quantity Available', min_value=1)
    units_donated = st.number_input('Units Donated', min_value=0)

    submit_button = st.form_submit_button(label='Add Food Item')

    if submit_button:
        new_food_item = {
            'Food Item': food_item,
            'Category': category,
            'Quantity': quantity,
            'Units Donated': units_donated
        }
        st.session_state['inventory'] = st.session_state['inventory'].append(new_food_item, ignore_index=True)
        st.success(f'Added {quantity} units of {food_item} to the inventory.')

# Display the current pantry inventory
st.subheader('Current Pantry Inventory')
st.write(st.session_state['inventory'])

# Search functionality
st.subheader('Search Inventory')
search_term = st.text_input('Search by Food Item Name')
if search_term:
    filtered_inventory = st.session_state['inventory'][st.session_state['inventory']['Food Item'].str.contains(search_term, case=False)]
    st.write(filtered_inventory)

# Option to download inventory as CSV
st.subheader('Download Inventory')
st.download_button(
    label="Download pantry inventory as CSV",
    data=st.session_state['inventory'].to_csv(index=False),
    file_name='food_pantry_inventory.csv',
    mime='text/csv',
)
