import streamlit as st
import scrape
from scrape import split_dom_content

st.set_page_config(initial_sidebar_state="collapsed", page_title="Home page")
st.title(":green[AI Web Scraper]")
url = st.text_input("Enter a Website URL: ")



if st.button("Scrape Site"):
    st.write("Scraping the website")
    result = scrape.scrape_website(url)
    body_content = scrape.extract_body_content(result)
    cleaned_content = scrape.clean_body_content(body_content)

    st.session_state.dom_content = cleaned_content
    with st.expander("View DOM Content"):
        st.text_area("DOM Content", cleaned_content, height=300)

if "dom_content" in st.session_state:
    parse_descripion = st.text_area("Describe what yoy want to parse?")

    if st.button("Parse Content"):
        if parse_descripion:
            st.write("Parsing the content")

            dom_chunks = split_dom_content(st.session_state.dom_content)

st.selectbox('Select', options=['Manila', 'Tokyo', 'Beijing'], key='country')


