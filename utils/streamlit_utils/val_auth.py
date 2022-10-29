import streamlit as st


def auth_simple(func):
    OK = '\033[92m'  # GREEN
    INFO = '\033[90m'  # GRAY
    FAIL = '\033[91m'  # RED
    RESET = '\033[0m'  # RESET

    def wrapper(*args, **kwargs):
        admin = kwargs.get("admin", False)
        user_category = "ADMINS" if admin else "USERS"
        print(INFO, "Authenticating {user_category}...", end=" ")
        admins = list(st.secrets[user_category].keys())
        auth_user = st.session_state["username"]
        if auth_user in admins:
            func()
            print(OK, "OK", RESET)
        else:
            st.warning(f"Access denied for user {auth_user}")
            print(FAIL, "FAILED", RESET)

    return wrapper
