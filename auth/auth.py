import streamlit as st
import hashlib

# Hash password
def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

from db.db import conn, cursor


def register_user():

    st.subheader("Create New Account")

    new_user = st.text_input("Username")

    new_password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        sql = """
        INSERT INTO users (username, password)
        VALUES (%s, %s)
        """

        hashed_password = hash_password(new_password)

        values = (
            new_user,
            hashed_password
        )

        cursor.execute(sql, values)

        conn.commit()

        st.success("Account Created Successfully!")


def login_user():

    st.subheader("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", key="login_button"):

        sql = """
        SELECT * FROM users
        WHERE username=%s
        AND password=%s
        """

        hashed_password = hash_password(password)

        values = (
            username,
            hashed_password
        )

        cursor.execute(sql, values)

        result = cursor.fetchone()

        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = result[3]  # lưu role
            st.success("Login Successful!")
            st.rerun()

        else:

            st.error("Invalid Username or Password")

