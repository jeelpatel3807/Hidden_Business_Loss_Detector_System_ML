import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hidden Business Loss Detector", page_icon="📊")

st.title("📊 Hidden Business Loss Detection System")

st.write("Analyze product performance and detect hidden losses using clustering.")

df = pd.read_csv("processed_data.csv")

st.subheader("📄 Product Data")
st.dataframe(df)

category = st.selectbox(
    "Select Category",
    df['Category'].unique()
)

filtered_data = df[df['Category'] == category]

st.write(filtered_data)

st.subheader("🚨 High Risk Products")

risk_data = df[df['Insight'].str.contains("Loss|Risk")]

st.dataframe(risk_data)

st.subheader("📊 Revenue vs Return Rate")

st.scatter_chart(
    df[['TotalRevenue', 'ReturnRate']]
)

st.subheader("📈 Cluster Summary")

summary = df.groupby('Category').mean(numeric_only=True)

st.dataframe(summary)


