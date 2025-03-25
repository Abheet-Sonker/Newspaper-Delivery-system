import streamlit as st
import pandas as pd
import re
from collections import defaultdict

# Function to parse delivery days
def parse_delivery_days(delivery_days):
    if pd.isna(delivery_days):
        return 0
    days = delivery_days.strip('"').split(',')
    return len(days)  # Returns the number of delivery days

# Function to safely convert a string to a float
def safe_float(value):
    try:
        return float(re.sub(r'[^\d.]', '', str(value)))
    except ValueError:
        return 0.0

# Streamlit UI
st.title("Delivery Data Analysis App 📦")
st.write("Upload a CSV file containing delivery data to analyze.")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    # Load CSV file
    df = pd.read_csv(uploaded_file)

    # Ensure necessary columns exist
    required_columns = {'Delivery Person ID', 'Customer ID', 'Delivery Days', 'Monthly Billing (Estimated)', 'Weekly Billing (Estimated)', 'Individual Cost (Estimated)'}
    if not required_columns.issubset(df.columns):
        st.error("Error: The uploaded CSV file is missing required columns.")
    else:
        # Initialize dictionaries to store results
        deliveries_per_person = defaultdict(int)
        deliveries_per_day = defaultdict(int)
        monthly_deliveries = defaultdict(int)
        weekly_deliveries = defaultdict(int)
        cost_per_customer = defaultdict(float)

        # Process data
        for _, row in df.iterrows():
            delivery_person = row['Delivery Person ID']
            customer_id = row['Customer ID']
            delivery_days = str(row['Delivery Days'])
            delivery_count = parse_delivery_days(delivery_days)

            # Count deliveries per delivery person
            deliveries_per_person[delivery_person] += delivery_count

            # Count deliveries per day of the week
            for day in delivery_days.split(','):
                day = day.strip()
                if day:
                    deliveries_per_day[day] += 1

            # Calculate costs based on subscription type
            if 'Monthly' in delivery_days:
                monthly_deliveries[delivery_person] += 1
                cost_per_customer[customer_id] += safe_float(row.get('Monthly Billing (Estimated)', 0))
            elif 'Weekly' in delivery_days:
                weekly_deliveries[delivery_person] += 1
                cost_per_customer[customer_id] += safe_float(row.get('Weekly Billing (Estimated)', 0)) * 4.33
            else:
                cost_per_customer[customer_id] += safe_float(row.get('Individual Cost (Estimated)', 0)) * delivery_count * 4.33

        # Convert results to DataFrames for better visualization
        df_deliveries_per_person = pd.DataFrame(list(deliveries_per_person.items()), columns=["Delivery Person ID", "Total Deliveries"])
        df_deliveries_per_day = pd.DataFrame(list(deliveries_per_day.items()), columns=["Day of the Week", "Total Deliveries"])
        df_monthly_deliveries = pd.DataFrame(list(monthly_deliveries.items()), columns=["Delivery Person ID", "Monthly Deliveries"])
        df_weekly_deliveries = pd.DataFrame(list(weekly_deliveries.items()), columns=["Delivery Person ID", "Weekly Deliveries"])
        df_cost_per_customer = pd.DataFrame(list(cost_per_customer.items()), columns=["Customer ID", "Total Cost ($)"])
        df_cost_per_customer["Total Cost ($)"] = df_cost_per_customer["Total Cost ($)"].apply(lambda x: f"${x:.2f}")

        # Display results
        st.subheader("📊 Deliveries per Delivery Person")
        st.dataframe(df_deliveries_per_person)

        st.subheader("📆 Deliveries per Day of the Week")
        st.dataframe(df_deliveries_per_day)

        st.subheader("📅 Monthly Deliveries per Delivery Person")
        st.dataframe(df_monthly_deliveries)

        st.subheader("📅 Weekly Deliveries per Delivery Person")
        st.dataframe(df_weekly_deliveries)

        st.subheader("💰 Cost per Customer")
        st.dataframe(df_cost_per_customer)

        # Downloadable CSV
        st.download_button(
            "Download Processed Data as CSV",
            df_cost_per_customer.to_csv(index=False).encode("utf-8"),
            "processed_data.csv",
            "text/csv",
        )
