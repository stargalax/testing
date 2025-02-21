import streamlit as st
import bcrypt
import psycopg2
import os
from doctor_dashboard import doctor_dashboard
from nurse_dashboard import nurse_functions

# PostgreSQL connection details (replace with your actual connection info)
DATABASE_URL = os.getenv("DATABASE_URL")  # Set this environment variable in Render

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Helper function to verify passwords
def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Function to connect to PostgreSQL
def connect_db():
    conn = psycopg2.connect(DATABASE_URL)  # Database URL from Render environment variables
    return conn

# Function to check if the email exists and verify password
def authenticate_user(email, password):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash, role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user and verify_password(user[0], password):
        return user[1]  # Return the role
    return None

# Function to create a new user
def create_user(email, password, role):
    conn = connect_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        conn.close()
        return "Email already exists."
    
    # Hash password and insert the new user into the database
    password_hash = hash_password(password).decode('utf-8')
    cursor.execute("INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)", (email, password_hash, role))
    conn.commit()
    conn.close()
    
    return "Account created successfully!"

# Streamlit app logic
def main():
    st.title("Authentication System")

    # Check if user is already logged in
    if "email" in st.session_state:
        st.write(f"Welcome back, {st.session_state['email']}!")
        if st.button("Logout"):
            del st.session_state["email"]
            del st.session_state["role"]
            st.rerun()  # Reload the page on logout

        # Redirect to the appropriate dashboard based on role
        role = st.session_state.get("role")
        if role == "doctor":
            doctor_landing_page()
        elif role == "nurse":
            nurse_landing_page()
        return

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Select Action", menu)

    if choice == "Sign Up":
        st.subheader("Create a New Account")

        # Sign-up form
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                role = "doctor" if email == "doctor@example.com" else "nurse"
                result = create_user(email, password, role)
                st.success(result)

    elif choice == "Login":
        st.subheader("Login to Your Account")

        # Login form
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            role = authenticate_user(email, password)
            if role:
                st.session_state["email"] = email
                st.session_state["role"] = role
                st.success(f"Logged in as {email}")
                st.rerun()  # Forces the page to reload and show the appropriate dashboard
            else:
                st.error("Incorrect email or password.")

# Function for doctor's landing page
def doctor_landing_page():
    doctor_dashboard()

# Function for nurse's landing page
def nurse_landing_page():
    nurse_functions()

if __name__ == '__main__':
    main()
