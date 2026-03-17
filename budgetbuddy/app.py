import streamlit as st
import pandas as pd
from .db import init_db, get_categories, add_category, get_transactions, add_transaction, get_recurring, add_recurring, get_pay_schedule, set_pay_schedule
import plotly.express as px
from datetime import datetime, timedelta

def run_app():
    # Initialize DB
    init_db()
    st.set_page_config(page_title="Budget Buddy", layout="wide")
    # Sidebar Navigation
    st.sidebar.title("Budget Buddy 🐶")
    page = st.sidebar.radio(
        "Go to", ["Dashboard", "Transactions", "Recurring", "Pay Schedule", "Settings"]
    )
    # Dashboard Page
    if page == "Dashboard":
        st.title("Dashboard")
        date_range = st.selectbox("View", ["This Week", "This Pay Period", "This Month", "6 Months"])
        today = datetime.today().date()
        start_date = end_date = None
        ps = get_pay_schedule()
        if date_range == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_range == "This Month":
            start_date = today.replace(day=1)
            next_month = start_date + timedelta(days=32)
            next_month = next_month.replace(day=1)
            end_date = next_month - timedelta(days=1)
        elif date_range == "6 Months":
            start_date = today - timedelta(days=180)
            end_date = today
        elif date_range == "This Pay Period":
            if ps:
                next_pay = datetime.fromisoformat(ps['next_pay_date']).date()
                freq = ps['pay_frequency']
                mapping = {'weekly':7, 'biweekly':14, 'semimonthly':15, 'monthly':30}
                period_days = mapping.get(freq, 30)
                if next_pay >= today:
                    start_date = next_pay - timedelta(days=period_days)
                    end_date = next_pay
                else:
                    start_date = next_pay
                    end_date = next_pay + timedelta(days=period_days)
            else:
                st.warning("Please set your pay schedule first.")
        if start_date and end_date:
            st.write(f"From {start_date} to {end_date}")
            df = pd.DataFrame(get_transactions(start_date.isoformat(), end_date.isoformat()))
            total_spent = df['amount'].sum() if not df.empty else 0
            st.subheader("Transactions")
            st.write(df)
            fig = px.pie(df, names='category', values='amount', title='Spending by Category')
            st.plotly_chart(fig)
            st.metric("Total Spent", f"${total_spent:,.2f}")
            if date_range == "This Pay Period" and ps:
                income = ps['pay_amount']
                savings = income - total_spent
                st.metric("Income", f"${income:,.2f}")
                st.metric("Savings", f"${savings:,.2f}")
        else:
            st.write("Select a date range")
    # Transactions Page
    elif page == "Transactions":
        st.title("Add Transaction")
        date = st.date_input("Date", datetime.today())
        amount = st.number_input("Amount", value=0.0)
        categories = get_categories()
        cat_names = [c['name'] for c in categories]
        category = st.selectbox("Category", [None] + cat_names)
        description = st.text_input("Description")
        if st.button("Add"):
            if category:
                cat_id = next(c['id'] for c in categories if c['name'] == category)
            else:
                cat_id = None
            add_transaction(date.isoformat(), amount, cat_id, description)
            st.success("Transaction added!")
    # Recurring Page
    elif page == "Recurring":
        st.title("Manage Recurring Bills")
        recs = get_recurring()
        st.write(pd.DataFrame(recs))
        st.subheader("Add New Recurring Bill")
        name = st.text_input("Name")
        amount = st.number_input("Amount", value=0.0, key="rec_amt")
        category = st.selectbox("Category", [None] + [c['name'] for c in get_categories()], key="rec_cat")
        frequency = st.selectbox("Frequency", ["daily", "weekly", "biweekly", "monthly"], key="rec_freq")
        next_due = st.date_input("Next Due Date", datetime.today(), key="rec_due")
        if st.button("Add Recurring"):
            if category:
                cat_id = next(c['id'] for c in get_categories() if c['name'] == category)
            else:
                cat_id = None
            add_recurring(name, amount, cat_id, frequency, next_due.isoformat())
            st.success("Recurring bill added!")
    # Pay Schedule Page
    elif page == "Pay Schedule":
        st.title("Pay Schedule")
        ps = get_pay_schedule()
        if ps:
            st.write(f"Pay Amount: {ps['pay_amount']}")
            st.write(f"Frequency: {ps['pay_frequency']}")
            st.write(f"Next Pay Date: {ps['next_pay_date']}")
        st.subheader("Set Pay Schedule")
        pay_amount = st.number_input("Pay Amount", value=ps['pay_amount'] if ps else 0.0)
        pay_frequency = st.selectbox("Frequency", ["weekly", "biweekly", "semimonthly", "monthly"], index=0)
        next_pay_date = st.date_input("Next Pay Date", datetime.today())
        if st.button("Save Pay Schedule"):
            set_pay_schedule(pay_amount, pay_frequency, next_pay_date.isoformat())
            st.success("Pay schedule updated!")
    # Settings Page
    elif page == "Settings":
        st.title("Settings")
        st.subheader("Categories")
        new_cat = st.text_input("New Category")
        if st.button("Add Category"):
            if new_cat:
                add_category(new_cat)
                st.success("Category added!")
