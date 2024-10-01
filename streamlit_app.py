import streamlit as st
import pandas as pd

# Title of the app
st.title("Inventory Tracker")

# Sample data for the inventory
data = {
    'Item': ['Apple', 'Banana', 'Orange', 'Grapes'],
    'Quantity': [10, 20, 15, 12],
    'Price': [1.00, 0.50, 0.75, 2.00]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Remove the 'Price' column
df = df.drop(columns=['Price'])

# Display the inventory table
st.write("Inventory Table:")
st.table(df)

# Add user input functionality
st.write("Add new item to the inventory:")
new_item = st.text_input("Item Name")
new_quantity = st.number_input("Quantity", min_value=0)

# Button to add a new item
if st.button("Add Item"):
    if new_item and new_quantity:
        new_data = {'Item': new_item, 'Quantity': new_quantity}
        df = df.append(new_data, ignore_index=True)
        st.success(f"{new_item} added to the inventory!")

# Display updated table
st.write("Updated Inventory Table:")
st.table(df)

# Optional: Downloadable CSV of the inventory
@st.cache
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df)

st.download_button(
    label="Download Inventory as CSV",
    data=csv,
    file_name='inventory.csv',
    mime='text/csv',
)
