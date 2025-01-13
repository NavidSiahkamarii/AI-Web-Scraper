import hashlib

from SQL_Connection import get_connection
import streamlit as st
import re
import streamlit_authenticator as stauth

def insert_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)", (username, password, None, None))
    connection.commit()
    cursor.close()


def fetch_users():
    cursor = get_connection().cursor()
    cursor.execute("SELECT * FROM accounts")
    return cursor.fetchall()

def get_usernames():
    cursor = get_connection().cursor()
    cursor.execute("SELECT * FROM accounts")
    users = cursor.fetchall()
    usernames = []
    for user in users:
        usernames.append(user['username'])

    return usernames

def validate_username(username):
    pattern = re.compile(r"^[a-zA-Z0-9]+$")
    if pattern.match(username):
        return True
    else:
        return False

def log_in():
    users = fetch_users()

    credentials = {}
    for index in range(len(users)):
        credentials[users[index]['username']] = users[index]['password']

    with st.form(key="signin", clear_on_submit=False):
        username = st.text_input(":blue[Username]", placeholder="Enter Username")
        password = st.text_input(":blue[Password]", placeholder="Enter Password", type="password")

        if st.form_submit_button("sign in"):
            if username in credentials:
                if credentials[username] == password:
                    st.success("You have successfully logged in")
                    st.session_state.logged_in = True
                    st.session_state.username = username
                else:
                    st.warning("Incorrect Password")
            else:
                st.warning("Username does not exist")