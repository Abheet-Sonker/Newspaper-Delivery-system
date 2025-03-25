import streamlit as st
import pandas as pd
from collections import defaultdict

# Define a function to parse delivery days into a countable format
def parse_delivery_days(delivery_days):
    days = delivery_days.strip('"').split(',')
    return len(days)  # Returns the number of delivery days

st.title("Newspaper Delivery System")

# File uploader
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Initialize dictionaries to store data
    deliveries_per_person = defaultdict(int)
    deliveries_per_day = defaultdict(int)
    monthly_deliveries = defaultdict(int)
    weekly_deliveries = defaultdict(int)
    cost_per_customer = defaultdict(float)

    for index, row in df.iterrows():
        # Count deliveries per delivery person
        deliveries_per_person[row['Delivery Person ID']] += parse_delivery_days(row['Delivery Days'])

        # Count deliveries per day of the week
        for day in ['M', 'T', 'W', 'Th', 'F']:
            if day in row['Delivery Days']:
                deliveries_per_day[day] += 1

        # Calculate costs based on subscription type
         if 'Monthly' in delivery_days:
            monthly_deliveries[delivery_person] += 1
            cost_per_customer[customer_id] += safe_float(row.get('Monthly Billing (Estimated)', '0'))
        elif 'Weekly' in delivery_days:
            weekly_deliveries[delivery_person] += 1
            cost_per_customer[customer_id] += safe_float(row.get('Weekly Billing (Estimated)', '0')) * 4.33
        else:
            cost_per_customer[customer_id] += safe_float(row.get('Individual Cost (Estimated)', '0')) * delivery_count * 4.33

    # Display results in Streamlit
    st.subheader("Deliveries per Delivery Person")
    st.dataframe(pd.DataFrame(deliveries_per_person.items(), columns=["Delivery Person ID", "Total Deliveries"]))

    st.subheader("Deliveries per Day of the Week")
    st.dataframe(pd.DataFrame(deliveries_per_day.items(), columns=["Day of the Week", "Total Deliveries"]))

    st.subheader("Monthly Deliveries per Delivery Person")
    st.dataframe(pd.DataFrame(monthly_deliveries.items(), columns=["Delivery Person ID", "Monthly Deliveries"]))

    st.subheader("Weekly Deliveries per Delivery Person")
    st.dataframe(pd.DataFrame(weekly_deliveries.items(), columns=["Delivery Person ID", "Weekly Deliveries"]))

    st.subheader("Cost per Customer")
    cost_df = pd.DataFrame(cost_per_customer.items(), columns=["Customer ID", "Total Cost ($)"])
    cost_df["Total Cost ($)"] = cost_df["Total Cost ($)"].apply(lambda x: f"{x:.2f}")
    st.dataframe(cost_df)
