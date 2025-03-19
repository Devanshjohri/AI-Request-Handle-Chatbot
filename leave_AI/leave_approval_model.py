import pandas as pd
import joblib

# Load trained model
model = joblib.load("leave_approval_model.pkl")

# Define category mappings (same as used during training)
leave_type_mapping = {"Sick": 0, "Casual": 1, "Vacation": 2, "Maternity": 3, "Paternity": 4}
reason_mapping = {"flu": 0, "personal": 1, "travel": 2, "headache": 3, "family": 4, "pregnancy": 5}  # Example

def predict_leave_approval(leave_type, duration, reason):
    """Predicts whether a leave request will be approved."""

    # Convert leave type to numeric
    leave_type_num = leave_type_mapping.get(leave_type, -1)  # Default to -1 if not found

    # Convert reason to numeric
    reason_num = reason_mapping.get(reason, -1)  # Default to -1 if not found

    # Ensure correct feature structure for the model
    input_data = pd.DataFrame([[leave_type_num, duration, reason_num]], 
                              columns=["leave_type", "duration_days", "reason"])
    
    return model.predict(input_data)[0]  # Returns 1 (Approved) or 0 (Rejected)
