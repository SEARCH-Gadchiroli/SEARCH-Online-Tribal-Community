import streamlit as st
import pandas as pd
import plotly.express as px

# Load all data
blocks_df = pd.read_excel("blocks-3.xlsx")
village_info = pd.read_excel("villages-5.xlsx")
birth_data = pd.read_excel("birth22-23.xlsx")
place_codes = pd.read_excel("place_coding-2.xlsx")
sex_codes = pd.read_excel("Sex Coding.xlsx")
delivery_codes = pd.read_excel("delivery_coding-2.xlsx")
delivery_type_codes = pd.read_excel("Delivery Type Coding.xlsx")
pregnancy_codes = pd.read_excel("Pregnancy Birth data.xlsx")
villages_demo = pd.read_excel("villages-5.xlsx")
profile_df = pd.read_excel("khutgaon_village_info-2.xlsx", sheet_name=None)

# Merge village data
village_df = pd.merge(blocks_df, village_info, on=["Village No"], how="left")
village_info_df = profile_df["Village Info"]
contacts_df = profile_df["Key Contacts"]

# -------- Sidebar Filters --------
st.sidebar.title("🔍 Filters")
block = st.sidebar.selectbox("Select Block", blocks_df["Block"].unique())
villages_in_block = village_df[village_df["Block"] == block]
village_name = st.sidebar.selectbox("Select Village", villages_in_block["Village Name_x"].unique())
selected_village = villages_in_block[villages_in_block["Village Name_x"] == village_name].iloc[0]
village_no = selected_village["Village No"]

# -------- Tabs --------
tab1, tab2, tab3 = st.tabs([ "Village Profile","Demographics", "Birth Data"])

# -------- TAB 1: Demographics --------
with tab2:
    st.title(f"Demographics of {village_name}")
    demo_data = villages_demo[villages_demo["Village No"] == village_no]

    if demo_data.empty:
        st.warning("No demographics data available for this village.")
    else:
        demo_data = demo_data.iloc[0]

        # Bar chart: Population breakdown
        pop_df = pd.DataFrame({
            "Category": ["Total", "Males", "Females", "Under 5"],
            "Count": [
                demo_data["Population"],
                demo_data["No of Males"],
                demo_data["No of Females"],
                demo_data["Under Five Child"]
            ]
        })
        st.subheader("👪 Population Breakdown")
        st.plotly_chart(px.bar(pop_df, x="Category", y="Count", color="Category", title="Population Overview"), use_container_width=True)

        # Literacy Rates
        literacy_df = pd.DataFrame({
            "Category": ["Total", "Male", "Female"],
            "Rate": [
                demo_data["Literacy Rate (%)"],
                demo_data["Male Literacy (%)"],
                demo_data["Female Literacy (%)"]
            ]
        })
        st.subheader("📚 Literacy Rates")
        st.plotly_chart(px.bar(literacy_df, x="Category", y="Rate", color="Category", title="Literacy (%)"), use_container_width=True)

        # Infrastructure Access
        infra_df = pd.DataFrame({
            "Facility": [
                "Electricity", "Mobile Phone", "Toilet (HH)", 
                "Toilet (Use)", "Mosquito Net", "Well", 
                "Handpump", "Tap", "LPG/Electric Cooking"
            ],
            "Percentage": [
                demo_data["Households with Electricity (%)"],
                demo_data["Households with Mobile Phone"],
                demo_data["Households with Toilet (%)"],
                demo_data["Families Using Toilet (%)"],
                demo_data["Families Using Mosquito Net (%)"],
                demo_data["Water Source (Well %)"],
                demo_data["Water Source (Handpump %)"],
                demo_data["Water Source (Tap %)"],
                demo_data["Cooking Fuel (LPG/Electric)"]
            ]
        })
        st.subheader("🏠 Household Facilities & Utilities")
        st.plotly_chart(px.bar(infra_df, x="Facility", y="Percentage", color="Facility", title="Access to Facilities (%)"), use_container_width=True)

# -------- TAB 2: Birth Data --------
with tab3:
    st.title("AROGYA SWARAJ")
    st.title("People's Health in People's Hands")

    st.markdown("### 🏞️ Village View")
    if village_name.lower() == "bamhani":
        st.image("bamhani.jpg", caption="Bamhani Village")
    else:
        st.info("No image available for this village.")

    st.markdown("## 📊 Village-Level Visualizations 2022-23")

    def decode_column(series, code_df, col="Code", label="Description"):
        code_map = dict(zip(code_df[col], code_df[label]))
        return series.map(code_map)

    # Decode mappings
    fields = {
        "bplace": place_codes,
        "sex": sex_codes,
        "deliv": delivery_codes,
        "deliv_t": delivery_type_codes,
        "preg": pregnancy_codes
    }
    village_data = birth_data[birth_data["villno"] == village_no]

    field_items = list(fields.items())
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

with tab1:
    st.title("📄 Village Profile")

    st.subheader("🏡 General Village Information")
    st.dataframe(village_info_df)

    st.subheader("👥 Key Village Contacts")
    st.dataframe(contacts_df)