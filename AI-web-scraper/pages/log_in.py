from operator import index

import pymysql
import streamlit_authenticator as stauth
import streamlit as st
import re
import yaml

from auth import usernames

timeout = 10
connection = pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    db="defaultdb",
    host="data-ai-web-scraper.d.aivencloud.com",
    password="AVNS_vXefrJYtYdAMfKfERON",
    read_timeout=timeout,
    port=10523,
    user="avnadmin",
    write_timeout=timeout,
)




def insert_user(username, password):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)", (username, password, None, None))
    connection.commit()
    cursor.close()

def fetch_users():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM accounts")
    return cursor.fetchall()

def get_usernames():
    cursor = connection.cursor()
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

st.write("Do you want craate an account?")
with st.form(key="signup", clear_on_submit=True):
    st.subheader(":green[Sign Up]")
    username = st.text_input(":blue[Username]", placeholder="Enter Username")
    password1 = st.text_input(":blue[Password]", placeholder="Enter Password", type="password")
    password2 = st.text_input(":blue[ConfirmPassword]", placeholder="Confirm Your Password", type="password")

    btn1, btn2, btn3, btn4, btn5 = st.columns(5)
    with btn3:
        st.form_submit_button("Sign Up")

    if username:
        if validate_username(username):
            if username not in get_usernames():
                if len(username) > 3:
                    if len(password1) > 3:
                        if password1 == password2:
                            hashed_password = stauth.Hasher(password1).generate()
                            insert_user(username, hashed_password)
                            st.success("Account Created Successfully")
                            st.balloons()
                        else:
                            st.warning("Password Does Not Match")
                    else:
                        st.warning("Password must be longer than 3 characters.")
                else:
                    st.warning("Username too short")
            else:
                st.warning("Username already exists")
        else:
            st.warning('Username is not valid')

st.write("Do you have an account?")
users = fetch_users()
usernames = []
passwords = []
for user in users:
    usernames.append(user['username'])
    passwords.append(user['password'])

credentials = {'usernames':{}}
for index in range(len(usernames)):
    credentials['usernames'][usernames[index]] = {'email' : usernames[index] + '@aut.ac.ir','name': usernames[index], 'password': stauth.Hasher.hash(passwords[index])}
a = {"credentials":credentials}
st.write(a)
with open('data.yaml', 'w') as file:
    yaml.dump(a, file)

Authenticator = stauth.Authenticate(credentials=a, cookie_name='Streamlit', cookie_key="abcdef", cookie_expiry_days=4)
name, authentication_status, username = Authenticator.login('main')
#
# if username:
#     if username in usernames:
#         if authentication_status:
#             st.success("You are logged in")
#         elif not authentication_status:
#             st.warning("Incorrect password")
#     else:
#         st.warning("Username does not exist")

# with st.form(key="signin", clear_on_submit=False):
#     username = st.text_input(":blue[Username]", placeholder="Enter Username")
#     password = st.text_input(":blue[Password]", placeholder="Enter Password", type="password")
#     if st.form_submit_button("sign in"):
#         if username in information:
#             if information[username] == password:
#                 st.write("You have successfully logged in")
#             else:
#                 st.write("Incorrect Password")
#         else:
#             st.write("Username does not exist")

    #hashed_password = stauth.Hasher(password).generate()


