from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Inventory tracker",
    page_icon=":shopping_bags:",  # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

def connect_db():
    """Connects to the sqlite database."""
    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    """Initializes the inventory table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            units_sold INTEGER,
            units_left INTEGER,
            cost_ REAL,
            reorder_point INTEGER,
            description TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO inventory
            (item_name, units_sold, units_left, cost_, reorder_point, description)
        VALUES
            -- Beverages
            ('Bottled Water (500ml)', 115, 15, 0.80, 16, 'Hydrating bottled water'),
            ('Soda (355ml)', 93, 8, 1.20, 10, 'Carbonated soft drink'),
            ('Energy Drink (250ml)', 12, 18, 1.50, 8, 'High-caffeine energy drink'),
            ('Coffee (hot, large)', 11, 14, 1.80, 5, 'Freshly brewed hot coffee'),
            ('Juice (200ml)', 11, 9, 1.30, 5, 'Fruit juice blend'),

            -- Snacks
            ('Potato Chips (small)', 34, 16, 1.00, 10, 'Salted and crispy potato chips'),
            ('Candy Bar', 6, 19, 0.80, 15, 'Chocolate and candy bar'),
            ('Granola Bar', 3, 12, 1.30, 8, 'Healthy and nutritious granola bar'),
            ('Cookies (pack of 6)', 8, 8, 1.50, 5, 'Soft and chewy cookies'),
            ('Fruit Snack Pack', 5, 10, 1.00, 8, 'Assortment of dried fruits and nuts'),

            -- Personal Care
            ('Toothpaste', 1, 9, 2.00, 5, 'Minty toothpaste for oral hygiene'),
            ('Hand Sanitizer (small)', 2, 13, 1.20, 8, 'Small sanitizer bottle for on-the-go'),
            ('Pain Relievers (pack)', 1, 5, 3.00, 3, 'Over-the-counter pain relief medication'),
            ('Bandages (box)', 0, 10, 2.00, 5, 'Box of adhesive bandages for minor cuts'),
            ('Sunscreen (small)', 6, 5, 3.50, 3, 'Small bottle of sunscreen for sun protection'),

            -- Household
            ('Batteries (AA, pack of 4)', 1, 5, 2.50, 3, 'Pack of 4 AA batteries'),
            ('Light Bulbs (LED, 2-pack)', 3, 3, 4.00, 2, 'Energy-efficient LED light bulbs'),
            ('Trash Bags (small, 10-pack)', 5, 10, 2.00, 5, 'Small trash bags for everyday use'),
            ('Paper Towels (single roll)', 3, 8, 1.50, 5, 'Single roll of paper towels'),
            ('Multi-Surface Cleaner', 2, 5, 3.00, 3, 'All-purpose cleaning spray'),

            -- Others
            ('Lottery Tickets', 17, 20, 1.50, 10, 'Assorted lottery tickets'),
            ('Newspaper', 22, 20, 1.00, 5, 'Daily newspaper')
        """
    )
    conn.commit()


def load_data(conn):
    """Loads the inventory data from the database."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
    except:
        return None

    df = pd.DataFrame(
        data,
        columns=[
            "id",
            "item_name",
            "units_sold",
            "units_left",
            "cost_",
            "reorder_point",
            "description",
        ],
    )

    # Remove the 'cost_' column
    df = df.drop(columns=["cost_"])

    return df


def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            """
            UPDATE inventory
            SET
                item_name = :item_name,
                units_sold = :units_sold,
                units_left = :units_left,
                reorder_point = :reorder_point,
                description = :description
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO inventory
                (id, item_name, units_sold, units_left, reorder_point, description)
            VALUES
                (:id, :item_name, :units_sold, :units_left, :reorder_point, :description)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )

    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM inventory WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )

    conn.commit()


# -----------------------------------------------------------------------------
# Draw the actual page, starting with the inventory table.

"""
# :shopping_bags: Inventory tracker

**Welcome to Alice's Corner Store's inventory tracker!**
This page reads and writes directly from/to our inventory database.
"""

st.info(
    """
    Use the table below to add, remove, and edit items.
    And don't forget to commit your changes when you're done.
    """
)

# Connect to database and create table if needed
conn, db_was_just_created = connect_db()

# Initialize data.
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")

# Load data from database
df = load_data(conn)

# Display data with editable table
edited_df = st.data_editor(
    df,
    disabled=["id"],  # Don't allow editing the 'id' column.
    num_rows="dynamic",  # Allow appending/deleting rows.
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)

# ----------------------------------------------------------------------------- 
# Now some cool charts 

# Add some space 
"" 
"" 
"" 

st.subheader("Units left", divider="red") 

need_to_reorder = df[df["units_left"] < df["reorder_point"]].loc[:, "item_name"]

if len(need_to_reorder) > 0:
    items = "\n".join(f"* {name}" for name in need_to_reorder)
    st.error(f"We're running dangerously low on the items below:\n {items}")

"" 
"" 

st.altair_chart( 
    alt.Chart(df) 
    .mark_bar( 
        orient="horizontal", 
    ) 
    .encode( 
        x="units_left", 
        y="item_name", 
    ) 
    + alt.Chart(df) 
    .mark_point( 
        shape="diamond", 
        filled=True, 
        size=50, 
        color="salmon", 
        opacity=1, 
    ) 
    .encode( 
        x="reorder_point", 
        y="item_name", 
    ), 
    use_container_width=True, 
) 

st.caption("NOTE: The :diamonds: location shows the reorder point.") 

"" 
"" 
"" 

# ----------------------------------------------------------------------------- 

st.subheader("Best sellers", divider="orange") 

"" 
"" 

st.altair_chart( 
    alt.Chart(df) 
    .mark_bar(orient="horizontal") 
    .encode( 
        x="units_sold", 
        y=alt.Y("item_name").sort("-x"), 
    ), 
    use_container_width=True, 
)
