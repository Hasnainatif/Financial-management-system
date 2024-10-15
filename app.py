import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = []
if 'user_balance' not in st.session_state:
    st.session_state['user_balance'] = 0.0

# User Authentication Functions
def authenticate_user(username, password):
    # This is a simplified example. In a real app, you would check a database.
    return username == "user" and password == "password"

# Transaction Management Functions
def add_transaction(category, amount, type, description):
    transaction = {
        'date': datetime.date.today(),
        'category': category,
        'amount': amount,
        'type': type,
        'description': description
    }
    st.session_state['transactions'].append(transaction)
    # Update balance
    if type == 'Income':
        st.session_state['user_balance'] += amount
    elif type == 'Expense':
        st.session_state['user_balance'] -= amount

# Visualization of Financial Goals
def plot_transactions(transactions):
    if not transactions:
        return
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['amount'].where(df['type'] == 'Expense'), marker='o', label='Expenses', color='red')
    plt.plot(df['date'], df['amount'].where(df['type'] == 'Income'), marker='o', label='Income', color='green')
    plt.title('Income and Expenses Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.legend()
    st.pyplot(plt)

# Streamlit App
def main():
    st.title('Personal Finance Management System')

    # User Authentication
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state['logged_in'] = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")
    else:
        st.write("Welcome to the Personal Finance Management System!")

        # Display User Balance
        st.write(f"Your current balance is: ${st.session_state['user_balance']:.2f}")

        # Expense Tracking
        st.subheader("Add Transaction")
        category = st.selectbox("Category", ["Food", "Bills", "Entertainment", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        type = st.selectbox("Type", ["Income", "Expense"])
        description = st.text_input("Description")
        if st.button("Add Transaction"):
            add_transaction(category, amount, type, description)
            st.success("Transaction added!")

        # View and Visualize Transactions
        st.subheader("Your Transactions")
        if st.session_state['transactions']:
            transaction_df = pd.DataFrame(st.session_state['transactions'])
            st.dataframe(transaction_df)
            plot_transactions(st.session_state['transactions'])
        else:
            st.write("No transactions yet.")

        # Logout Option
        if st.button("Logout"):
            st.session_state['logged_in'] = False

if __name__ == '__main__':
    main()
