from scrape import scrape_website
import parse
from history import *
from user_management import *
import streamlit as st
from SQL_Connection import get_connection
import json

st.set_page_config(initial_sidebar_state="collapsed", page_title="Home page")
page = st.sidebar.selectbox("select page", ("home page", "create account", "use account"))


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'predefined_mode' not in st.session_state:
    st.session_state.predefined_mode = False

if 'username' not in st.session_state:
    st.session_state.username = None

if 'predefined_new_added' not in st.session_state:
    st.session_state.predifined_new_added = False
def add_perdefined_search(username,  search_term):
    connection = get_connection()
    cursor = connection.cursor()
    predefined_searches = fetch_predefined_searches(username)
    if not predefined_searches:
        predefined_searches = list()

    predefined_searches.append(search_term)
    json_search = json.dumps(predefined_searches)

    # مرحله 4: ذخیره مجدد لیست
    cursor.execute(
        "UPDATE accounts SET pre_difined_search = %s WHERE username = %s",
        (json_search, username)
    )
    connection.commit()

def fetch_predefined_searches(username):
    cursor = get_connection().cursor()
    cursor.execute(
        "SELECT pre_difined_search FROM accounts WHERE username = %s",
        (username,)
    )

    result = cursor.fetchone()
    cursor.close()

    if result['pre_difined_search']:
        return json.loads(result['pre_difined_search'])
    else:
        return []

def show_and_use_predefined_searches(predefined_searches):
    for search in predefined_searches:
        url, prompt = search
        with st.expander(f"Search: {prompt}", expanded=False):
            st.write(f"**URL:** {url}")
            st.write(f"**Prompt:** {prompt}")
            if st.button("Use", key=prompt):  # استفاده از prompt به عنوان کلید
                if url:
                    result = pre_defined_answer_with_url(prompt, url)
                else:
                    result = answer_without_url(prompt)
                st.text_area("result", result , height=300)


def pre_defined_answer_with_url(Query, urls):
    urls = [url for url in urls.split(sep=', ')]
    page_text = ''
    for url in urls:
        page_text = page_text + scrape_website(url)
    with st.spinner("Fetching Relevant Info! (The app is working)"):
        try:
            answer = parse.parse_with_open_AI(context=page_text, query=Query)
        except:
            answer = "open ai free limit is over"
    # parse.parse_with_ollama(context=page_text,parse_description=Query)
    if st.session_state.logged_in:
        add_history(st.session_state.username, [urls, Query, answer])
    st.write(answer)
    return answer


def answer_with_url(Query):
    urls = st.text_input(
        "Enter the URL(s) of source webpage(s):  (Simply separate urls by comma/, followed by white space)")
    if st.button("Find Relevant Info!"):
        if not urls:
            st.error("You Have not Entered any URLs!")
        else:
            pre_defined_answer_with_url(Query, urls)


def answer_without_url(Query):
    with st.spinner("Fetching Relevant Info! (The app is working)"):
        # try:
        answer = parse.search_with_open_AI(query=Query)
        # except:
        #     answer = "open ai free limit is over"
        if st.session_state.logged_in:
            add_history(st.session_state.username, [None, Query, answer])

        st.write(answer)
        return answer

if page == "home page":
    st.title(":green[AI Web Scraper]")
    st.write("\n\nThis App makes finding the information you need from the web as easy as pie!\n")
    status = st.radio("Which one describes your needs better?",
                      ('Free Search!',
                       'Specific Search!'),
                      captions=['I am happy with the app doing a simple web search to find what I need!',
                                'I want the app to use specific webpages to answer a query of mine.']
                      )
    Query = st.text_input("Enter Your Query:")

    if status == 'Specific Search!':
        answer_with_url(Query)
    elif st.button("Find Relevant Info!"):
        answer_without_url(Query)

if page == "create account":
    st.write("Do you want to create an account?")
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
                                insert_user(username, password1)
                                st.success("Account Created Successfully")
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

if page == "use account":
    page2 = st.sidebar.radio("please select", ("log in","history", "pre-defined"))
    if page2 == "log in":
        log_in()
    if page2 == "pre-defined":
        if st.session_state.logged_in:
            tabs = st.tabs(["create a predefined search", "use a predefined search"])
            with tabs[0]:
                url = st.text_input("Enter a Website URL(optional)")
                prompt = st.text_input("Enter a prompt (necessary)")
                if st.button("add Pre-defined Search"):
                    if prompt:
                        add_perdefined_search(st.session_state.username, [url, prompt])
                        st.write("predifined search has been added to your search list")
                        st.session_state.predifined_new_added = True
                    else:
                        st.warning("please enter a predefined search prompt")


            with tabs[1]:
                predefined_searchs = fetch_predefined_searches(st.session_state.username)
                if predefined_searchs:
                    show_and_use_predefined_searches(predefined_searchs)
                elif st.session_state.predifined_new_added:
                    predefined_searchs = fetch_predefined_searches(st.session_state.username)
                    show_and_use_predefined_searches(predefined_searchs)
        else:
            st.warning("log in first")

    if page2 == "history":
        if st.session_state.logged_in:
            show_histories(fetch_histories(st.session_state.username))
        else:
            st.warning("log in first")




