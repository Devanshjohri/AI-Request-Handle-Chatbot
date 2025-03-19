from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from agents.main_agent import main_agent
from leave_AI.leave_approval_model import predict_leave_approval
from agents.certificate_agents import certificate_agent
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from transformers import pipeline

app = FastAPI()

# Initialize NLP Model
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

# ✅ Serve the 'students_pdfs' directory
app.mount("/students_pdf", StaticFiles(directory="students_pdf"), name="students_pdf")

class LeaveRequest(BaseModel):
    student_id: str   # User enters leave request in text format
    leave_type: str
    start_date: str
    end_date: str
    reason: str

@app.post("/apply_leave/")
def apply_leave(request: LeaveRequest):
    """Process leave request with AI before submitting"""
    leave_details = leave_details = {
        "student_id": request.student_id,
        "leave_type": request.leave_type,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "reason": request.reason
    }
    
    if None in leave_details.values():
        return {"error": "AI could not extract leave details. Please rephrase your request."}
    
    # Predict approval
    approval = predict_leave_approval(leave_details["leave_type"], 3, leave_details["reason"])
    leave_details["approval_prediction"] = "Approved" if approval == 1 else "Rejected"

    response = main_agent.run("leave_agent", leave_details)
    return response

@app.get("/predict_leave/")
def predict_leave(leave_type: str, duration: int, reason: str):
    """Test AI leave approval predictions"""
    prediction = predict_leave_approval(leave_type, duration, reason)
    return {"prediction": "Approved" if prediction == 1 else "Rejected"}

@app.post("/fetch_certificate/")
def fetch_certificate(student_id: str = Form(...), certificate_type: str = Form(...)):
    """API to fetch a student's certificate"""
    response = certificate_agent.fetch_certificate(student_id, certificate_type)
    return response

@app.post("/upload_certificate/")
def upload_certificate(student_id: str = Form(...), certificate_type: str = Form(...), file: UploadFile = File(...)):
    """API to upload a certificate"""
    file_path = f"students_pdf/{student_id}_{certificate_type}.pdf"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    response = certificate_agent.upload_certificate(student_id, certificate_type, file_path)
    return response
@app.get("/download_certificate/{filename}")
def download_certificate(filename: str):
    """Allow users to download the certificate file"""
    file_path = f"students_pdf/{filename}"

    # ✅ Check if file exists before sending
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        return {"error": "File not found ❌"}
    
# Context about mentorship at KIIT (You can enhance this)
MENTOR_CONTEXT = """
KIIT University provides mentorship for students in academics, placements, research, and general guidance.
Mentors help students in career development, projects, internship opportunities, and resolving doubts.
"""

# Pydantic model for request validation
class MentorQuery(BaseModel):
    question: str

# Mentor Interaction API
@app.post("/mentor_interaction/")
def mentor_interaction(request: MentorQuery):
    """Handles mentor-related queries dynamically using NLP."""
    response = qa_pipeline(question=request.question, context=MENTOR_CONTEXT)

    # Ensure the answer is confident enough
    if response["score"] > 0.5:
        return {"answer": response["answer"]}
    else:
        return {"answer": "I couldn't find an exact answer. Could you clarify?"}