import streamlit as st
import sys
import os

st.set_page_config(
    page_title="산업안전기사 취득 도우미",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.switch_page("pages/0_학습안내.py")
