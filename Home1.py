import streamlit as st
import requests
from transformers import pipeline
from datetime import datetime
from leave_AI.nlp_leave_extraction import extract_leave_details
from leave_AI.leave_approval_model import predict_leave_approval
from agents.leave_agent import show_leave_details
from utils.pdf_processor import extract_text_from_pdf

BASE_URL = "http://localhost:8000"

st.title("🤖 KIIT Request Handle Chatbot")

# Initialize NLP model
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# Store user details
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_request" not in st.session_state:
    st.session_state.current_request = None  # Track active request type
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_roll" not in st.session_state:
    st.session_state.user_roll = None
if "request_type" not in st.session_state:
    st.session_state.request_type = None  # Track what request the user wants
if "certificate_action" not in st.session_state:
    st.session_state.certificate_action = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "mentor_interaction" not in st.session_state:
    st.session_state.mentor_interaction = False

# Step 1: Ask for Roll No & Name
if st.session_state.user_roll is None or st.session_state.user_name is None:
    with st.chat_message("assistant"):
        st.write("👋 Hello! Welcome to KIIT Agent System.")
        st.write("Please enter your details to continue.")
    
    user_name = st.text_input("Enter your Name:")
    user_roll = st.text_input("Enter your Roll Number:")

    if user_name and user_roll:
        st.session_state.user_name = user_name
        st.session_state.user_roll = user_roll
        # st.success(f"Thank you, {user_name}! What request would you like to make?")
        st.rerun()

st.sidebar.subheader("📄 Upload a File for Processing")
uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    extracted_text = extract_text_from_pdf(uploaded_file)
    st.sidebar.subheader("📜 Extracted Text from PDF:")
    st.markdown(
    """
    <style>
    .stTextArea textarea { height: auto !important; min-height: 150px !important; max-height: 500px !important; }
    </style>
    """,
    unsafe_allow_html=True,
    )
    st.sidebar.text_area("Extracted Content", extracted_text, height=1000, key="extracted_text")

    # Determine the relevant agent task
    if "leave" in extracted_text.lower():
        st.sidebar.write("📝 Detected a **Leave Request**. Processing...")

        # Extract leave details
        leave_details = extract_leave_details(extracted_text)
        missing_fields = [field for field in ["leave_type", "start_date", "end_date", "reason"] if not leave_details.get(field)]

        if missing_fields:
            st.sidebar.write("⚠️ Missing Details:")
            for field in missing_fields:
                leave_details[field] = st.sidebar.text_input(f"Enter {field.capitalize()}:")

        if st.sidebar.button("Submit Leave Request"):
            response = requests.post(f"{BASE_URL}/apply_leave/", json=leave_details)
            st.sidebar.success("Leave request submitted successfully! ✅" if response.status_code == 200 else "Error submitting leave request. ❌")
        
        else:
            st.sidebar.write("🤖 No specific task detected. The file will be stored for manual review.")


# Step 2: Ask what type of request the user wants
st.session_state.request_type=None
if st.session_state.request_type is None:
    with st.chat_message("assistant"):
        st.write(f"Hi **{st.session_state.user_name}**! What would you like to do today?")
        request_options = [
        "Leave Request","Check Leave Details", "Certificate Request", "Fee Inquiry", "Exam Info",
        "Placement Assistance", "Mentor Interaction", "Compliance Inquiry"
    ]
    selected_request = st.selectbox("Select a request type:", request_options)
    if selected_request:
        st.session_state.request_type = selected_request
        #st.rerun()  # Optimized rerun

# ** Clear chat history when switching requests **
if st.session_state.request_type != st.session_state.current_request:
    st.session_state.chat_history = []  # ✅ Clear chat history for fresh request
    st.session_state.current_request = st.session_state.request_type  # ✅ Update current request

# Step 3: Handle Leave Requests
if st.session_state.request_type == "Leave Request":
    st.subheader("📆 Leave Request Chat")

    # Ensure session state variables exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "leave_details" not in st.session_state:
        st.session_state.leave_details = None
    if "awaiting_confirmation" not in st.session_state:
        st.session_state.awaiting_confirmation = False
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    #bot_response = ""

    text_area_style = """
    <style>
        textarea { resize: none !important; height: 100px !important; }
    </style>
    """
    st.markdown(text_area_style, unsafe_allow_html=True)

     # **Ensure Input Box is Always at Bottom**
    input_placeholder = st.empty()

    # Determine which input field to show
    if not st.session_state.submitted:
        if not st.session_state.awaiting_confirmation:
            user_input = input_placeholder.text_area(
                "Describe your leave request (e.g., 'I need sick leave from March 15 to March 18 because I have a fever.')",
                height=68,
                max_chars=500,
                key="leave_request_input"
            )
        else:
            user_input = input_placeholder.text_input(
                "Would you like to submit this leave request? (yes/no)",
                key="confirmation_input"
            )
    else:
        user_input = None  # No input box after submission

    # Display chat history

    if user_input:
        st.session_state.chat_history.append(("User", user_input))

        if not st.session_state.awaiting_confirmation:
            # Extract leave details using AI
            leave_details = extract_leave_details(user_input)

            missing_fields = []
            for field in ["leave_type", "start_date", "end_date", "reason"]:
                if not leave_details.get(field):
                    missing_fields.append(field)

            if missing_fields:
                # Suggest possible rephrasing based on missing fields
                suggestions = {
                    "leave_type": "Make sure to mention the type of leave (e.g., Sick, Casual, Medical).",
                    "start_date": "Provide a start date (e.g., 'March 15').",
                    "end_date": "Provide an end date (e.g., 'March 18').",
                    "reason": "Mention the reason clearly (e.g., 'because I have a fever')."
                }

                missing_details_response = "I couldn't extract all details. Please provide:\n"
                for field in missing_fields:
                    missing_details_response += f"- {suggestions[field]}\n"
                missing_details_response += "\nCan you rephrase your request?"
                
                bot_response = missing_details_response
                st.session_state.chat_history.append(("Bot", bot_response))
            else:
                # Predict leave approval

                start_date = datetime.strptime(leave_details["start_date"].split()[0], "%Y-%m-%d")

                end_date = datetime.strptime(leave_details["end_date"].split()[0], "%Y-%m-%d")

                leave_duration = (end_date - start_date).days + 1
                approval = predict_leave_approval(leave_details["leave_type"], leave_duration, leave_details["reason"])
                decision = "Approved" if approval == 1 else "Rejected"

                bot_response = f"Here's what I understood:\n\n"
                bot_response += f"**Leave Type:** {leave_details['leave_type']}\n\n"
                bot_response += f"**Start Date:** {leave_details['start_date']}\n\n"
                bot_response += f"**End Date:** {leave_details['end_date']}\n\n"
                bot_response += f"**Reason:** {leave_details['reason']}\n\n"
                bot_response += f"**AI Prediction:** `{decision}`\n\n"
                bot_response += "Would you like to submit this leave request? (yes/no)"

                # Store extracted details
                st.session_state.leave_details = leave_details
                st.session_state.awaiting_confirmation = True

        elif st.session_state.awaiting_confirmation and not st.session_state.submitted:
            if user_input.lower() == "yes":
                st.session_state.submitted = True  # Update immediately

                leave_data = st.session_state.leave_details
                leave_data["student_id"] = st.session_state.user_roll  
                response = requests.post(f"{BASE_URL}/apply_leave/", json={
                    "student_id": leave_data.get("student_id", ""),
                    "leave_type": leave_data.get("leave_type", ""),
                    "start_date": leave_data.get("start_date", ""),
                    "end_date": leave_data.get("end_date", ""),
                    "reason": leave_data.get("reason", "")
                })

                if response.status_code == 200:
                    bot_response = "Leave request submitted successfully! ✅"
                else:
                    bot_response = "Error submitting leave request. ❌"

                # Reset state for new requests
                st.session_state.leave_details = None
                st.session_state.awaiting_confirmation = False  

            elif user_input.lower() == "no":
                bot_response = "Leave request cancelled."
                st.session_state.leave_details = None
                st.session_state.awaiting_confirmation = False  

        st.session_state.chat_history.append(("Bot", bot_response))
    
    if st.session_state.submitted:
        if st.button("Apply for Another Leave"):
            st.session_state.submitted = False  # ✅ Reset submitted status
            st.session_state.awaiting_confirmation = False
            st.session_state.leave_details = None
            st.session_state.chat_history = []  # Clear chat history for fresh request
            st.rerun()  # 🔄 Refresh UI
            st.rerun()  # 🔄 Refresh UI
            
    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.chat_history:
            with st.chat_message("user" if role == "User" else "assistant"):
                st.write(message)

# Step 4: Handle Other Requests
else:
    if st.session_state.request_type == "Check Leave Details":
        show_leave_details()
    
    elif st.session_state.request_type == "Certificate Request":
        st.subheader("📜 Certificate Request Bot")

        if "certificate_step" not in st.session_state:
            st.session_state.certificate_step = "greet"  # Start at greeting
        if "certificate_data" not in st.session_state:
            st.session_state.certificate_data = {}  # Store user inputs

        input_placeholder = st.empty()

        # if st.session_state.certificate_action is None:
        #     bot_response = f"Hello {st.session_state.user_name}, do you want to **fetch** a certificate or **upload** a certificate?"
        #     st.session_state.chat_history.append(("Bot", bot_response))

        user_input = st.chat_input("Your response...")

        if st.session_state.certificate_step == "greet":
            bot_response = f"Hello {st.session_state.user_name}, do you want to **fetch** a certificate or **upload** a certificate?"
            st.session_state.chat_history.append(("Bot", bot_response))
            st.session_state.certificate_step = "ask_action"

        elif st.session_state.certificate_step == "ask_action" and user_input:
            st.session_state.chat_history.append(("User", user_input))
            if user_input.lower() == "fetch":
                st.session_state.certificate_data["action"] = "fetch"
                bot_response = "Please enter your **Student ID**."
                st.session_state.chat_history.append(("Bot", bot_response))
                st.session_state.certificate_step = "ask_student_id"
            elif user_input.lower() == "upload":
                st.session_state.certificate_data["action"] = "upload"
                bot_response = "Please enter your **Student ID**."
                st.session_state.chat_history.append(("Bot", bot_response))
                st.session_state.certificate_step = "ask_student_id_upload"
            else:
                bot_response = "Invalid choice. Please type **'fetch'** or **'upload'**."
                st.session_state.chat_history.append(("Bot", bot_response))
        elif st.session_state.certificate_step == "ask_student_id" and user_input:
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.certificate_data["student_id"] = user_input
            bot_response = "What **type of certificate** do you want (e.g., Bonafide, Internship, etc.)?"
            st.session_state.certificate_step = "ask_certificate_type"
            st.session_state.chat_history.append(("Bot", bot_response))

        elif st.session_state.certificate_step == "ask_student_id_upload" and user_input:
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.certificate_data["student_id"] = user_input
            bot_response = "What **type of certificate** do you want (e.g., Bonafide, Internship, etc.) to upload?"
            st.session_state.certificate_step = "upload_certificate_type"
            st.session_state.chat_history.append(("Bot", bot_response))

        elif st.session_state.certificate_step in["upload_certificate_type", "ask_certificate_type"] and user_input :
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.certificate_data["certificate_type"] = user_input

            if st.session_state.certificate_data["action"] == "fetch":
                bot_response = "Fetching your certificate... ⏳"
                st.session_state.chat_history.append(("Bot", bot_response))

                # **API Call for Fetching Certificate**
                response = requests.post(
                    f"{BASE_URL}/fetch_certificate/",
                    data={
                        "student_id": st.session_state.certificate_data["student_id"],
                        "certificate_type": st.session_state.certificate_data["certificate_type"],
                    },
                )
                api_response = response.json()
                 # **Display Certificate Download Link if Found**
                if "certificate_url" in api_response:
                    certificate_url = api_response["certificate_url"]
                    st.markdown(f"[📥 Click here to download your certificate]({certificate_url})", unsafe_allow_html=True)
                else:
                    st.write(api_response.get("message", "No Certificate Found ❌"))
                st.session_state.chat_history.append(("Bot", bot_response))
                st.session_state.certificate_step = "done"
            else:  # **Upload Flow**
                bot_response = "Please upload the certificate file (PDF only)."
                st.session_state.certificate_step = "ask_upload"
                st.session_state.chat_history.append(("Bot", bot_response))
        elif st.session_state.certificate_step == "ask_upload":
                
                uploader_placeholder = st.empty()

                with uploader_placeholder:
                    uploaded_file = st.file_uploader("Upload Certificate (PDF)", type=["pdf"], key="certificate_file")

                    if uploaded_file and st.button("Submit Certificate"):
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        data = {
                            "student_id": st.session_state.certificate_data["student_id"],
                            "certificate_type": st.session_state.certificate_data["certificate_type"],
                        }
                        response = requests.post(f"{BASE_URL}/upload_certificate/", files=files, data=data)

                        api_response = response.json()
                        st.session_state.chat_history.append(("Bot", api_response.get("message", "Error uploading certificate. ❌")))
                        st.session_state.certificate_step = "done"

        # **Reset Button**
        if st.session_state.certificate_step == "done":
            button_placeholder = st.empty()
            with button_placeholder:
                if st.button("Request Another Certificate"):
                    st.session_state.certificate_step = "greet"
                    st.session_state.certificate_data = {}
                    st.session_state.chat_history = []
                    st.rerun()

        for role, message in st.session_state.chat_history:
            with st.chat_message("user" if role == "User" else "assistant"):
                st.write(message)

    elif st.session_state.request_type == "Mentor Interaction":
        st.subheader("👨‍🏫 Mentor Interaction Bot")

        # Input for user query
        user_input = st.text_area("Ask your mentor anything...", height=70, max_chars=500, key="mentor_input")

        if user_input:
            st.session_state.chat_history.append(("User", user_input))

            # Process user query using NLP
            context = "KIIT University provides mentorship in academics, placements, research, and general guidance."
            nlp_response = qa_pipeline(question=user_input, context=context)

            bot_response = nlp_response["answer"] if nlp_response["score"] > 0.5 else "I couldn't find an exact answer. Could you clarify?"

            st.session_state.chat_history.append(("Bot", bot_response))

        # Display chat history
        for role, message in st.session_state.chat_history:
            with st.chat_message("user" if role == "User" else "assistant"):
                st.write(message)

        # Reset conversation
        if st.button("Start New Conversation"):
            st.session_state.chat_history = []
            st.session_state.mentor_interaction = False
            st.rerun()

    elif st.session_state.request_type == "Exam Info":
        student_id = st.session_state.user_roll

        if st.button("Check Backlog Exams"):
            response = requests.get(f"{BASE_URL}/backlog_exams/{student_id}")
            if response.status_code == 200:
                st.write(response.json())
            else:
                st.error("Error fetching exam details.")

    elif st.session_state.request_type == "Placement Info":
        if st.button("View Job Openings"):
            response = requests.get(f"{BASE_URL}/job_openings/")
            if response.status_code == 200:
                st.write(response.json())
            else:
                st.error("Error fetching job openings.")

        if st.button("View Company Visits"):
            response = requests.get(f"{BASE_URL}/company_visits/")
            if response.status_code == 200:
                st.write(response.json())
            else:
                st.error("Error fetching company visit schedule.")

    elif st.session_state.request_type == "Compliance":
        student_id = st.session_state.user_roll
        complaint_text = st.text_area("Enter your complaint")

        if st.button("Submit Complaint"):
            response = requests.post(f"{BASE_URL}/submit_complaint/", json={
                "student_id": student_id,
                "complaint": complaint_text
            })
            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error("Error submitting complaint.")
