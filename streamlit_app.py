import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
blocks_df = pd.read_excel("blocks.xlsx")
village_info = pd.read_excel("villages-2.xlsx")
birth_data = pd.read_excel("birth22-23.xlsx")

# Load coding files
place_codes = pd.read_excel("place_coding-2.xlsx")
sex_codes = pd.read_excel("Sex Coding.xlsx")
delivery_codes = pd.read_excel("delivery_coding-2.xlsx")
delivery_type_codes = pd.read_excel("Delivery Type Coding.xlsx")
pregnancy_codes = pd.read_excel("Pregnancy Birth data.xlsx")

# Merge to enrich data
village_df = pd.merge(blocks_df, village_info, on=["Village No"], how="left")

# Sidebar for Filters
st.sidebar.title("🔍 Filters")
block = st.sidebar.selectbox("Select Block", blocks_df["Block"].unique())
villages_in_block = village_df[village_df["Block"] == block]
village_name = st.sidebar.selectbox("Select Village", villages_in_block["Village Name_x"].unique())
selected_village = villages_in_block[villages_in_block["Village Name_x"] == village_name].iloc[0]

# Get village data
village_no = selected_village["Village No"]
village_data = birth_data[birth_data["villno"] == village_no]

# Main Panel Layout
st.title("SEARCH Tribal Community Dashboard")

# Centered Village Image
st.markdown("### 🏞️ Village View")
if village_name.lower() == "bamhani":
    st.image("bamhani.jpg", caption="Bamhani Village")
else:
    st.info("No image available for this village.")

# Pie Charts Below
st.markdown("## 📊 Village-Level Visualizations 2022-23")

def decode_column(series, code_df, col="Code", label="Description"):
    code_map = dict(zip(code_df[col], code_df[label]))
    return series.map(code_map)

# Define fields and codes
fields = {
    "bplace": place_codes,
    "sex": sex_codes,
    "deliv": delivery_codes,
    "deliv_t": delivery_type_codes,
    "preg": pregnancy_codes
}
field_items = list(fields.items())

# Show 2 charts per row
for i in range(0, len(field_items), 2):
    cols = st.columns(2)
    for j, (field, code_df) in enumerate(field_items[i:i+2]):
        with cols[j]:
            if field in village_data.columns:
                decoded = decode_column(village_data[field], code_df)
                counts = decoded.value_counts().reset_index()
                counts.columns = ["Category", "Count"]
                fig = px.pie(counts, values="Count", names="Category", title=field.upper(), hole=0.3)
                st.plotly_chart(fig, use_container_width=True)

# House Summary in Sidebar
if "hno" in village_data.columns:
    st.sidebar.markdown("## 🏠 House Details")
    house_no = st.sidebar.selectbox("Select House Number", village_data["hno"].dropna().unique())
    house_data = village_data[village_data["hno"] == house_no]

    if not house_data.empty:
        st.sidebar.markdown("### Summary:")
        latest = house_data.iloc[-1]

        summary_items = {
            "Place of Birth/Death": decode_column(pd.Series(latest["bplace"]), place_codes).values[0],
            "Sex": decode_column(pd.Series(latest["sex"]), sex_codes).values[0],
            "Delivery Location": decode_column(pd.Series(latest["deliv"]), delivery_codes).values[0],
            "Delivery Type": decode_column(pd.Series(latest["deliv_t"]), delivery_type_codes).values[0],
            "Pregnancy Duration": decode_column(pd.Series(latest["preg"]), pregnancy_codes).values[0],
        }

        for key, val in summary_items.items():
            st.sidebar.markdown(f"- **{key}**: {val}")
else:
    st.sidebar.warning("No house number data available.")
