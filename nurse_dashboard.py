import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from reportlab.pdfgen import canvas
from io import BytesIO

# Load environment variables
load_dotenv()

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("nursebot.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

def display_chat():
    st.title("Nurse Chat Assistance")
    st.chat_message("assistant").write("Hello! I'm here to help with patient data and assessments.")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("Type your message here...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            response = f"You said: {prompt}. How can I assist further?"
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_pdf(patient_name, patient_data):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 750, f"Patient Name: {patient_name}")
    pdf.drawString(100, 730, "Eligibility Assessment:")
    y = 710
    for question, answer in patient_data.items():
        pdf.drawString(100, y, f"{question}: {answer}")
        y -= 20

    pdf.save()
    buffer.seek(0)
    return buffer

def run_clinical_test():
    st.title("Eligibility Assessment")
    inclusion_criteria = ["Is the patient above 18 years?", "Does the patient have a history of diabetes?"]
    exclusion_criteria = ["Does the patient have any active infections?", "Is the patient pregnant?"]

    patient_name = st.text_input("Enter Patient Name")
    if not patient_name:
        st.warning("Please enter a patient name to proceed.")
        return

    responses = {}
    exclusion_flag = False
    unconcluded_flag = False

    st.subheader("Inclusion Criteria")
    for idx, question in enumerate(inclusion_criteria, 1):
        response = st.radio(f"{idx}. {question}", ("yes", "no", "not sure"), key=f"inclusion_{idx}")
        responses[question] = response
        if response == "not sure":
            unconcluded_flag = True

    st.subheader("Exclusion Criteria")
    for idx, question in enumerate(exclusion_criteria, 1):
        response = st.radio(f"{idx}. {question}", ("yes", "no", "not sure"), key=f"exclusion_{idx}")
        responses[question] = response
        if response == "yes":
            exclusion_flag = True
        if response == "not sure":
            unconcluded_flag = True

    if exclusion_flag:
        st.error("Patient is NOT eligible for the clinical trial due to exclusion criteria.")
    elif unconcluded_flag:
        st.warning("Eligibility inconclusive. Please review the answers.")
    else:
        st.success("Patient is eligible for the clinical trial!")

    if st.button("Generate PDF Report"):
        pdf_buffer = generate_pdf(patient_name, responses)
        st.download_button(
            label="Download Patient Report",
            data=pdf_buffer,
            file_name=f"{patient_name}_report.pdf",
            mime="application/pdf",
        )

def nurse_functions():
    db = initialize_firebase()

    st.sidebar.title("Nurse Dashboard")
    option = st.sidebar.selectbox("Choose Functionality", ["Chat Assistance", "Eligibility Assessment", "Patient Records"])

    if option == "Chat Assistance":
        display_chat()

    elif option == "Eligibility Assessment":
        run_clinical_test()

    elif option == "Patient Records":
        st.title("Patient Records")
        patient_id = st.text_input("Enter Patient ID")
        if st.button("Download Report"):
            try:
                patient_ref = db.collection("patients").document(patient_id)
                patient_data = patient_ref.get().to_dict()
                if not patient_data:
                    st.error("No data found for this patient ID.")
                else:
                    pdf_buffer = generate_pdf(patient_id, patient_data)
                    st.download_button(
                        label="Download Patient Report",
                        data=pdf_buffer,
                        file_name=f"{patient_id}_report.pdf",
                        mime="application/pdf",
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    nurse_functions()
