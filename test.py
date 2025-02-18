import streamlit as st
import bcrypt
import json
import os
from doctor_dashboard  import doctor_dashboard
from nurse_dashboard import nurse_functions

# For simplicity, store user data in a dictionary (you could also use a database)
USER_DATA = {}
USER_ROLES = {}  # Dictionary to store user roles (doctor, nurse, etc.)
DOCTOR_EMAIL = "doctor@example.com"  # Hardcoded doctor email (can be changed)

# Helper function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Helper function to verify passwords
def verify_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Check if we need to load existing user data
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        USER_DATA = json.load(f)

# Function to save user data to a file
def save_user_data():
    with open("users.json", "w") as f:
        json.dump(USER_DATA, f)

# Function to save user roles to a file
def save_user_roles():
    with open("user_roles.json", "w") as f:
        json.dump(USER_ROLES, f)

# Create the Streamlit form for Sign-Up and Login
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
            if email in USER_DATA:
                st.error("Email already exists. Please choose a different one.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                hashed_password = hash_password(password)
                USER_DATA[email] = hashed_password.decode('utf-8')
                
                # Assign role based on the email
                if email == DOCTOR_EMAIL:
                    USER_ROLES[email] = "doctor"
                else:
                    USER_ROLES[email] = "nurse"
                
                save_user_data()
                save_user_roles()
                st.success("Account created successfully! You can now log in.")

    elif choice == "Login":
        st.subheader("Login to Your Account")

        # Login form
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if email in USER_DATA:
                stored_password_hash = USER_DATA[email].encode('utf-8')
                if verify_password(stored_password_hash, password):
                    st.session_state["email"] = email
                    st.session_state["role"] = USER_ROLES.get(email, "nurse")  # Default to nurse if no role is found
                    st.success(f"Logged in as {email}")
                    
                    # Perform role-based redirection by simulating page load change
                    if email == DOCTOR_EMAIL:
                        st.session_state["role"] = "doctor"
                        st.rerun()  # Forces the page to reload and show doctor's dashboard
                    else:
                        st.session_state["role"] = "nurse"
                        st.rerun()  # Forces the page to reload and show nurse's dashboard
                else:
                    st.error("Incorrect password.")
            else:
                st.error("Email not found. Please sign up first.")

# Function for doctor's landing page
def doctor_landing_page():
    from doctor_dashboard  import doctor_dashboard
    doctor_dashboard()

# Function for nurse's landing page
def nurse_landing_page():
    from nurse_dashboard import nurse_functions
    nurse_functions()

if __name__ == '__main__':
    main()
