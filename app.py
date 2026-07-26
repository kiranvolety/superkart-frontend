import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:7860")

st.set_page_config(page_title="SuperKart Sales Forecaster", layout="wide")
st.title("SuperKart Sales Forecaster")
st.markdown("Predict total sales revenue for a product in a given store.")

tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction"])

with tab1:
    st.subheader("Single Prediction")
    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight (kg)", min_value=0.0, value=10.0, step=0.1)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.05, step=0.001, format="%.3f")
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=150.0, step=1.0)
        product_type = st.selectbox("Product Type", [
            "Fruits and Vegetables", "Dairy", "Meat", "Breads", "Breakfast", "Seafood",
            "Snack Foods", "Canned", "Frozen Foods", "Health and Hygiene", "Household",
            "Baking Goods", "Starchy Foods", "Others", "Soft Drinks", "Hard Drinks"
        ])
        product_id_char = st.selectbox("Product Id Prefix", ["FD", "DR", "NC"])
    with col2:
        store_size = st.selectbox("Store Size", ["High", "Medium", "Small"])
        store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
        store_age = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=20, step=1)

    if st.button("Predict Sales"):
        perishables = ["Fruits and Vegetables", "Dairy", "Meat", "Breads", "Breakfast", "Seafood"]
        beverages = ["Soft Drinks", "Hard Drinks"]
        if product_type in perishables:
            category = "Perishables"
        elif product_type in beverages:
            category = "Beverages"
        else:
            category = "Non Perishables"

        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": product_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": category,
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=30)
            result = resp.json()
            if "prediction" in result:
                st.success(f"Predicted Sales Revenue: **${result['prediction']:,.2f}**")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Request failed: {e}")

with tab2:
    st.subheader("Batch Prediction")
    st.markdown("Upload a CSV file with the required columns for batch predictions.")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:", df.head())
        if st.button("Run Batch Prediction"):
            records = df.to_dict(orient="records")
            try:
                resp = requests.post(f"{BACKEND_URL}/batch_predict", json=records, timeout=60)
                result = resp.json()
                if "predictions" in result:
                    df["Predicted_Sales"] = result["predictions"]
                    st.write("Results:", df)
                    csv = df.to_csv(index=False)
                    st.download_button("Download Results", csv, "batch_predictions.csv", "text/csv")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"Request failed: {e}")