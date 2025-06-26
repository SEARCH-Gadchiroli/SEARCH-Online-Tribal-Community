import streamlit as st
import pandas as pd

# Load data
blocks_df = pd.read_excel("blocks.xlsx")
village_info = pd.read_excel("villages-2.xlsx")
birth_data = pd.read_excel("birth22-23.xlsx")

# Merge to enrich data
village_df = pd.merge(blocks_df, village_info, on=["Village No"], how="left")

# UI
st.title("Search Tribal Community App")

# Dropdown 1 - Block
block = st.selectbox("Select Block", blocks_df["Block"].unique())
villages_in_block = village_df[village_df["Block"] == block]

# st.write("Village columns:", villages_in_block.columns.tolist())

# Dropdown 2 - Village
village_name = st.selectbox("Select Village", villages_in_block["Village Name_x"].unique())
selected_village = villages_in_block[villages_in_block["Village Name_x"] == village_name].iloc[0]

# Show village image if available
if village_name == "Bamani":
    st.image("bamhani.jpg", caption="Bamani Village")

# Filter birth data for village
village_no = selected_village["Village No"]
village_data = birth_data[birth_data["villno"] == village_no]

st.subheader(f"Village Data: {village_name}")
st.dataframe(village_data)

# Dropdown 3 - House No
if not village_data.empty and "hno" in village_data.columns:
    house_no = st.selectbox("Select House Number", village_data["hno"].dropna().unique())
    house_data = village_data[village_data["hno"] == house_no]
    st.subheader(f"House Data for House No: {house_no}")
    st.dataframe(house_data)
else:
    st.warning("No house number data available.")
