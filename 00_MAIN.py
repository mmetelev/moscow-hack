import streamlit as st

st.set_page_config(page_title="web-app", page_icon=":plane:", layout="wide",
                   menu_items={
                       'Get Help': 'https://github.com/CyberMaryVer',
                       'Report a bug': 'https://www.google.com',
                       'About': "### Erydo"
                   })


def main():
    st.info("Main page")


if __name__ == "__main__":
    main()