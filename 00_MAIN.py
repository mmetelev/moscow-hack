import streamlit as st
from utils.streamlit_utils.st_constants import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)


def main():
    st.info("Main page")


if __name__ == "__main__":
    main()