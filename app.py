import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.hash import pbkdf2_sha256
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Setup Database
Base = declarative_base()
engine = create_engine('sqlite:///finance.db')
Session = sessionmaker(bind=engine)
session = Session()

# User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    balance = Column(Float, default=0.0)

# Transaction Model
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    date = Column(Date)
    category = Column(String)
    amount = Column(Float)
    type = Column(String)  # income or expense
    description = Column(String)

Base.metadata.create_all(engine)

# Authentication functions
def create_user(username, password):
    hashed_pw = pbkdf2_sha256.hash(password)
    user = User(username=username, password=hashed_pw)
    session.add(user)
    session.commit()

def authenticate_user(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and pbkdf2_sha256.verify(password, user.password):
        return user
    return None

# Budget and Expense Functions
def add_transaction(user_id, category, amount, type, description):
    transaction = Transaction(
        user_id=user_id,
        date=datetime.date.today(),
        category=category,
        amount=amount,
        type=type,
        description=description
    )
    session.add(transaction)
    session.commit()

def get_transactions(user_id):
    return session.query(Transaction).filter_by(user_id=user_id).all()

# Visualization of Financial Goals
def plot_transactions(transactions):
    df = pd.DataFrame(transactions, columns=['date', 'category', 'amount'])
    df['date'] = pd.to_datetime(df['date'])
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['amount'])
    plt.title('Spending Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
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
            user = authenticate_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user'] = user
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

        st.subheader("Create an Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            create_user(new_username, new_password)
            st.success("Account created successfully!")
    else:
        user = st.session_state['user']
        st.write(f"Welcome, {user.username}!")

        # Expense Tracking
        st.subheader("Add Transaction")
        category = st.selectbox("Category", ["Food", "Bills", "Entertainment", "Other"])
        amount = st.number_input("Amount", min_value=0.0, step=0.01)
        type = st.selectbox("Type", ["Income", "Expense"])
        description = st.text_input("Description")
        if st.button("Add Transaction"):
            add_transaction(user.id, category, amount, type, description)
            st.success("Transaction added!")

        # View and Visualize Transactions
        transactions = get_transactions(user.id)
        st.subheader("Your Transactions")
        if transactions:
            transaction_df = pd.DataFrame([(t.date, t.category, t.amount, t.type, t.description) for t in transactions],
                                          columns=['Date', 'Category', 'Amount', 'Type', 'Description'])
            st.dataframe(transaction_df)
            plot_transactions([(t.date, t.category, t.amount) for t in transactions])
        else:
            st.write("No transactions yet.")

        # Logout Option
        if st.button("Logout"):
            st.session_state['logged_in'] = False

if __name__ == '__main__':
    main()
