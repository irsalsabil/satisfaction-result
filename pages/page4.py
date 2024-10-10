from navigation import make_sidebar
import streamlit as st

st.set_page_config(
    page_title='NPS',
    page_icon=':🗣️:', 
)

make_sidebar()

st.write(
    """
# 🕵️ EVEN MORE SECRET

This is a secret page that only logged-in users can see.

Super duper secret.

Shh....

"""
)