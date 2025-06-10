import pdfplumber
import json
import re

# Path to your PDF file
pdf_path = "New Employee Onboarding Survey - Google Forms.pdf"

# Field names as they appear in the form (order matters for value matching)
field_names = [
    "Full Legal Name",
    "Date of Birth",
    "Phone Number",
    "Position Title",
    "Expected Salary/Hourly Rate (USD)",
    "Reporting Manager"
]

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []
        for page in pdf.pages:
            # Extract text with layout preservation
            text = page.extract_text()
            if text:
                all_text.append(text)
    return "\n".join(all_text)

def parse_fields(text, field_names):
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    result = {}
    start_idx = -1
    for i, line in enumerate(lines):
        if "New Employee Onboarding Survey" in line:
            start_idx = i
            break
    if start_idx == -1:
        raise ValueError("Could not find the start of the form")

    # Footer or irrelevant lines to ignore
    footer_lines = [
        "This content is neither created nor endorsed by Google.",
        "Forms",
        "Google Forms"
    ]

    # Helper: check if a line is a help text (in parentheses)
    def is_help_text(line):
        return bool(line) and (line.startswith('(') and line.endswith(')'))

    i = start_idx
    while i < len(lines):
        line = lines[i]
        if any(footer in line for footer in footer_lines):
            i += 1
            continue
        for field in field_names:
            if field in line:
                # Try to get value on the same line
                value = line.replace(field, "").strip()
                j = i + 1
                # If no value, look for the next non-footer, non-help line
                while (not value or is_help_text(value)) and j < len(lines):
                    next_line = lines[j]
                    if any(footer in next_line for footer in footer_lines):
                        j += 1
                        continue
                    if is_help_text(next_line):
                        j += 1
                        continue
                    value = next_line.strip()
                    break
                i = j  # Move index to the value line
                result[field] = value
                break
        i += 1
    return result

def main():
    try:
        text = extract_text(pdf_path)
        data = parse_fields(text, field_names)
        # Save the extracted data to a JSON file
        with open('extracted_data.json', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Data extracted and saved to extracted_data.json")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    main()
