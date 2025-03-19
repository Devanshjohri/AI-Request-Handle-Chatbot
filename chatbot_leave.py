import streamlit as st
import requests
from leave_AI.nlp_leave_extraction import extract_leave_details
from leave_AI.leave_approval_model import predict_leave_approval

BASE_URL = "http://localhost:8000"

st.title("🤖 AI Leave Request Chatbot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask about leave (e.g., 'I need sick leave from March 15 to March 18 because I have a fever.')")

if user_input:
    st.session_state.chat_history.append(("User", user_input))

    # Extract leave details using AI
    leave_details = extract_leave_details(user_input)

    if None in leave_details.values():
        bot_response = "I couldn't extract all leave details. Could you rephrase it?"
    else:
        # Predict leave approval
        approval = predict_leave_approval(leave_details["leave_type"], 3, leave_details["reason"])  # Assume 3-day leave for now
        decision = "Approved" if approval == 1 else "Rejected"

        bot_response = f"Here's what I understood:\n\n"
        bot_response += f"**Leave Type:** {leave_details['leave_type']}\n"
        bot_response += f"**Start Date:** {leave_details['start_date']}\n"
        bot_response += f"**End Date:** {leave_details['end_date']}\n"
        bot_response += f"**Reason:** {leave_details['reason']}\n"
        bot_response += f"**AI Prediction:** `{decision}`\n\n"
        bot_response += "Would you like to submit this leave request? (yes/no)"

        # Store extracted details for later confirmation
        st.session_state.leave_details = leave_details

    st.session_state.chat_history.append(("Bot", bot_response))

# Display chat history
for role, message in st.session_state.chat_history:
    with st.chat_message("user" if role == "User" else "assistant"):
        st.write(message)

# Handle user confirmation for submission
if st.session_state.chat_history and "Would you like to submit this leave request?" in st.session_state.chat_history[-1][1]:
    confirmation = st.chat_input("Type 'yes' to submit, 'no' to cancel.")
    
    if confirmation.lower() == "yes":
        response = requests.post(f"{BASE_URL}/apply_leave/", json=st.session_state.leave_details)
        if response.status_code == 200:
            st.session_state.chat_history.append(("Bot", "Leave request submitted successfully! ✅"))
        else:
            st.session_state.chat_history.append(("Bot", "Error submitting leave request. ❌"))
    elif confirmation.lower() == "no":
        st.session_state.chat_history.append(("Bot", "Leave request cancelled."))
