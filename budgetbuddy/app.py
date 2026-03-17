import streamlit as st
import pandas as pd
from budgetbuddy.db import init_db, get_categories, add_category, get_transactions, add_transaction, get_recurring, add_recurring, get_pay_schedule, set_pay_schedule, get_incomes, add_income, update_income, delete_income
import plotly.express as px
from datetime import datetime, timedelta

def run_app():
    # Initialize DB
    init_db()
    st.set_page_config(page_title="Budget Buddy", layout="wide")
    # Sidebar Navigation
    st.sidebar.title("Budget Buddy 🐶")
    page = st.sidebar.radio(
        "Go to", ["Dashboard", "Transactions", "Recurring", "Incomes", "Pay Schedule", "Settings"]
    )
    # Dashboard Page
    if page == "Dashboard":
        st.title("Dashboard Overview")
        # Fetch data
        start_date, end_date = None, None
        today = datetime.today().date()
        ps = get_pay_schedule()
        # Default to this month
        start_date = today.replace(day=1)
        next_month = start_date + timedelta(days=32)
        next_month = next_month.replace(day=1)
        end_date = next_month - timedelta(days=1)
        # Transactions
        txns = get_transactions(start_date.isoformat(), end_date.isoformat())
        df_tx = pd.DataFrame(txns)
        total_expenses = df_tx['amount'].sum() if not df_tx.empty else 0.0
        # Incomes
        incs = get_incomes()
        # Filter incomes due in this period
        df_inc = pd.DataFrame([dict(i) for i in incs])
        if not df_inc.empty:
            df_inc['due_date'] = pd.to_datetime(df_inc['next_due']).dt.date
            incs_due = df_inc[(df_inc['due_date'] >= start_date) & (df_inc['due_date'] <= end_date)]
            total_income = incs_due['amount'].sum() if not incs_due.empty else df_inc['amount'].sum()
        else:
            total_income = 0.0
        # Net savings
        net = total_income - total_expenses
        # Upcoming bills (next 30 days)
        recs = [dict(r) for r in get_recurring()]
        df_rec = pd.DataFrame(recs)
        if not df_rec.empty:
            df_rec['due'] = pd.to_datetime(df_rec['next_due']).dt.date
            upcoming = df_rec[df_rec['due'] <= (today + timedelta(days=30))]
            upcoming_count = len(upcoming)
        else:
            upcoming_count = 0
        # Display metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Income", f"${total_income:,.2f}")
        m2.metric("Total Expenses", f"${total_expenses:,.2f}")
        m3.metric("Net Savings", f"${net:,.2f}")
        m4.metric("Upcoming Bills (30d)", f"{upcoming_count}")
        # Charts
        st.markdown("---")
        if not df_tx.empty:
            st.subheader("Expenses by Category")
            fig1 = px.pie(df_tx, names='category', values='amount', title='Expenses Split')
            st.plotly_chart(fig1, use_container_width=True)
            st.subheader("Spending Over Time")
            df_time = df_tx.copy()
            df_time['date'] = pd.to_datetime(df_time['date']).dt.date
            df_time_group = df_time.groupby('date')['amount'].sum().reset_index()
            fig2 = px.bar(df_time_group, x='date', y='amount', title='Daily Spend')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No transactions for this period.")
        # Monthly Bills for Selected Period
        st.markdown("---")
        # Label for current period, e.g., 'March 2025'
            period_label = start_date.strftime('%B %Y')
        st.subheader(f"Bills for {period_label}")
        # Filter bills within start and end dates
        df_rec['due'] = pd.to_datetime(df_rec['next_due']).dt.date
        period_bills = df_rec[(df_rec['due'] >= start_date) & (df_rec['due'] <= end_date)]
        if not period_bills.empty:
            st.table(period_bills[['name','amount','due','category']])
            total_bills = period_bills['amount'].sum()
            st.metric(
                "Total Bills", f"${total_bills:,.2f}"
            )
            leftover = total_income - total_bills
            st.metric(
                "Projected Savings After Bills", f"${leftover:,.2f}"
            )
            if total_income > 0:
                pct = total_bills / total_income
                st.progress(min(max(pct, 0), 1))
        else:
            st.write(f"No bills due in {period_label.lower()}.")
        st.markdown("---")
        st.title("Dashboard")
        # Default monthly summary
        st.subheader("All Recurring Bills")
        recs_raw = get_recurring()
        recs = [dict(r) for r in recs_raw]
        df_recs = pd.DataFrame(recs)
        if not df_recs.empty:
            display_cols = [col for col in ['name','amount','frequency','next_due','category'] if col in df_recs.columns]
            st.write(df_recs[display_cols])
        else:
            st.write("No recurring bills defined.")
        
        # Upcoming bills view
        st.subheader("Upcoming Bills")
        today = datetime.today().date()
        upcoming_span = st.selectbox("Show due in next:", ["7 days","30 days","60 days","90 days"], index=1)
        days_map = {"7 days":7, "30 days":30, "60 days":60, "90 days":90}
        span_days = days_map[upcoming_span]
        cutoff = today + timedelta(days=span_days)
        due_recs = [r for r in recs if datetime.fromisoformat(r['next_due']).date() <= cutoff]
        if due_recs:
            for r in due_recs:
                c1, c2, c3, c4, c5 = st.columns([2,1,1,1,1])
                c1.write(r['name'])
                c2.write(r['next_due'])
                c3.write(f"${r['amount']:,.2f}")
                c4.write(r['category'])
                btn_key = f"paid_{r['id']}"
                if c5.button("Mark Paid", key=btn_key):
                    # record transaction
                    add_transaction(r['next_due'], r['amount'], r['category_id'], f"Paid: {r['name']}")
                    # update next due
                    from budgetbuddy.db import update_recurring_next_due
                    update_recurring_next_due(r['id'], r['next_due'])
                    st.success(f"Recorded payment and updated next due for {r['name']}")
                    # refresh page
        else:
            st.write(f"No bills due in next {span_days} days.")
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
    # Incomes Page
    elif page == "Incomes":
        st.title("Manage Incomes")
        incs = get_incomes()
        if incs:
            for i in incs:
                c1, c2, c3, c4, c5 = st.columns([2,1,1,1,1])
                name = c1.text_input("Name", value=i['name'], key=f"inc_name_{i['id']}")
                amount = c2.number_input("Amount", value=i['amount'], key=f"inc_amt_{i['id']}")
                freq = c3.selectbox("Frequency", ["weekly","biweekly","monthly","yearly"], index=["weekly","biweekly","monthly","yearly"].index(i['frequency']), key=f"inc_freq_{i['id']}")
                next_due = c4.date_input("Next Due", datetime.fromisoformat(i['next_due']), key=f"inc_due_{i['id']}")
                if c5.button("Update", key=f"inc_update_{i['id']}"):
                    update_income(i['id'], name, amount, freq, next_due.isoformat())
                    st.success(f"Updated income {name}")
                    # Please refresh the page to see updates
                if c5.button("Delete", key=f"inc_delete_{i['id']}"):
                    delete_income(i['id'])
                    st.success(f"Deleted income {name}")
                    st.experimental_rerun()
        else:
            st.write("No incomes defined.")
        st.subheader("Add New Income")
        new_name = st.text_input("Name", key="new_inc_name")
        new_amount = st.number_input("Amount", value=0.0, key="new_inc_amt")
        new_freq = st.selectbox("Frequency", ["weekly","biweekly","monthly","yearly"], key="new_inc_freq")
        new_due = st.date_input("Next Due", datetime.today(), key="new_inc_due")
        if st.button("Add Income", key="new_inc_add"):
            add_income(new_name, new_amount, new_freq, new_due.isoformat())
            st.success(f"Added income {new_name}")
            st.experimental_rerun()

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
