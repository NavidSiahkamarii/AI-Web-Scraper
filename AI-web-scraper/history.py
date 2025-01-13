from SQL_Connection import get_connection
import streamlit as st
import json
import random

def add_history(username, history_item):
    connection = get_connection()
    cursor = connection.cursor()
    histories= fetch_histories(username)

    histories.append(history_item)
    json_histories = json.dumps(histories)

    cursor.execute(
        "UPDATE accounts SET histories = %s WHERE username = %s",
        (json_histories, username)
    )
    connection.commit()

def show_histories(histories):
    if not histories:
        st.write("No histories found")
    else:
        for history in histories:
            url, prompt , result= history
            with st.expander(f"Search: {prompt}", expanded=False):
                st.write(f"**URL:** {url}")
                st.write(f"**Prompt:** {prompt}")
                st.text_area(result,key=prompt + str(random.randint(1, 10000)), height=300)

def fetch_histories(username):
    cursor = get_connection().cursor()
    cursor.execute(
        "SELECT histories FROM accounts WHERE username = %s",
        (username,)
    )

    result = cursor.fetchone()
    cursor.close()

    if result['histories']:
        return json.loads(result['histories'])
    else:
        return []