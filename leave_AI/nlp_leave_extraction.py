import re
from dateutil import parser

def extract_leave_details(text):
    """Extracts leave type, start date, end date, and reason from user input."""
    leave_types = ["Casual", "Sick", "Vacation", "Maternity", "Paternity"]
    extracted_data = {"leave_type": None, "start_date": None, "end_date": None, "reason": None}

    # Extract leave type
    for leave in leave_types:
        if leave.lower() in text.lower():
            extracted_data["leave_type"] = leave
            break  # Stop after finding the first match

    # Extract reason
    reason_match = re.search(r"because (.+)", text, re.IGNORECASE)
    if reason_match:
        extracted_data["reason"] = reason_match.group(1)

    # Extract dates manually with regex
    date_range_match = re.search(r"(\w+\s\d{1,2})\s*to\s*(\w+\s\d{1,2})", text, re.IGNORECASE)
    single_date_match = re.search(r"(\w+\s\d{1,2})", text, re.IGNORECASE)

    try:
        if date_range_match:
            extracted_data["start_date"] = str(parser.parse(date_range_match.group(1)))
            extracted_data["end_date"] = str(parser.parse(date_range_match.group(2)))
        elif single_date_match:
            extracted_data["start_date"] = str(parser.parse(single_date_match.group(1)))
            extracted_data["end_date"] = extracted_data["start_date"]  # Assume single-day leave
    except Exception as e:
        extracted_data["start_date"], extracted_data["end_date"] = None, None  # Fallback if parsing fails

    return extracted_data

# Example usage
if __name__ == "__main__":
    user_input = "I need sick leave from March 15 to March 18 because of fever."
    print(extract_leave_details(user_input))
