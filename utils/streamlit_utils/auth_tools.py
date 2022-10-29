import streamlit as st
import re

ADMINS = list(st.secrets["ADMINS"].keys())
MODERS = list(st.secrets["MODERS"].keys())


# import logging
def check_valid_email(email_sign_up: str) -> bool:
    """
    Checks if the user entered a valid email while creating the account.
    """
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email_sign_up):
        return True
    return False


def define_if_admin():
    user = st.session_state["username"] if 'username' in st.session_state.keys() else None
    # st.session_state["is_admin"] = False
    is_admin = user in ADMINS
    is_moder = user in MODERS

    if is_admin:
        with st.sidebar.form("Admin mode"):
            enable_admin_mode = st.checkbox("*️⃣ Admin Mode", value=is_admin)
            submit = st.form_submit_button("Save")
    else:
        enable_admin_mode = st.sidebar.checkbox("*️⃣ Admin Mode", value=is_admin, disabled=not is_moder)

    # if submit:
    if not is_admin:
        st.session_state["is_admin"] = is_admin
    else:
        st.session_state["is_admin"] = enable_admin_mode

    return enable_admin_mode, is_moder
