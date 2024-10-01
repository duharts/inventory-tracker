import streamlit as st
import pandas as pd
from datetime import datetime

# Title for the app
st.title("Food Pantry Inventory Tracker")

# Create an example DataFrame
if 'inventory' not in st.session_state:
    st.session_state['inventory'] = pd.DataFrame(columns=['Item Name', 'Category', 'Quantity', 'Received Date', 'Expiration Date'])

# Categories for food items
categories = ['Non-perishable', 'Perishable', 'Beverage', 'Snack', 'Other']

# Form to add new items to the inventory
with st.form(key='add_item'):
    item_name = st.text_input('Item Name')
    category = st.selectbox('Category', categories)
    quantity = st.number_input('Quantity', min_value=1)
    received_date = st.date_input('Received Date', value=datetime.today())
    expiration_date = st.date_input('Expiration Date', value=datetime.today())

    submit_button = st.form_submit_button(label='Add Item')

    if submit_button:
        new_item = {
            'Item Name': item_name,
            'Category': category,
            'Quantity': quantity,
            'Received Date': received_date,
            'Expiration Date': expiration_date
        }
        st.session_state['inventory'] = st.session_state['inventory'].append(new_item, ignore_index=True)
        st.success(f'Added {quantity} units of {item_name} to the inventory.')

# Display the current inventory
st.subheader('Current Inventory')
st.write(st.session_state['inventory'])

# Search functionality
st.subheader('Search Inventory')
search_term = st.text_input('Search by Item Name')
if search_term:
    filtered_inventory = st.session_state['inventory'][st.session_state['inventory']['Item Name'].str.contains(search_term, case=False)]
    st.write(filtered_inventory)

# Function to remove expired items
st.subheader('Remove Expired Items')
today = datetime.today().date()
expired_items = st.session_state['inventory'][st.session_state['inventory']['Expiration Date'] < today]

if not expired_items.empty:
    st.write('The following items have expired:')
    st.write(expired_items)

    if st.button('Remove Expired Items'):
        st.session_state['inventory'] = st.session_state['inventory'][st.session_state['inventory']['Expiration Date'] >= today]
        st.success('Expired items removed from inventory.')
else:
    st.write('No expired items found.')

# Option to download inventory as CSV
st.subheader('Download Inventory')
st.download_button(
    label="Download inventory as CSV",
    data=st.session_state['inventory'].to_csv(index=False),
    file_name='food_pantry_inventory.csv',
    mime='text/csv',
)

