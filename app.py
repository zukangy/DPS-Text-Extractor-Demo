import streamlit as st
import pdfplumber
import json
import tempfile
import os
from docx import Document
from field_extractor import extract_text, parse_fields, field_names

def get_available_templates():
    """Get list of available templates from the templates directory."""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    return [f for f in os.listdir(templates_dir) if f.endswith('.txt')]

def load_template(template_name):
    """Load template content from file."""
    template_path = os.path.join("templates", template_name)
    with open(template_path, 'r') as f:
        return f.read()

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location and return the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def save_template_file(uploaded_file):
    """Save uploaded template file to a temporary location and return the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def fill_template(template_text, data):
    """Fill in the template with the provided data."""
    filled_text = template_text
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        filled_text = filled_text.replace(placeholder, str(value))
    return filled_text

def create_word_document(content, output_path):
    """Create a Word document with the filled content."""
    doc = Document()
    paragraphs = content.split('\n')
    for para in paragraphs:
        if para.strip():
            doc.add_paragraph(para)
    doc.save(output_path)

def main():
    st.title("Offer Letter Generator")
    st.write("Upload a survey PDF and select a template to generate an offer letter.")

    # Template selection
    available_templates = get_available_templates()
    if not available_templates:
        st.error("No templates found in the templates directory!")
        return

    # Add a default "none" option
    template_options = ["Select a template..."] + available_templates
    selected_template = st.selectbox(
        "Select Template",
        template_options,
        format_func=lambda x: x.replace('_', ' ').replace('.txt', '').title() if x != "Select a template..." else x
    )

    # Show template preview only if a template is selected (not the default option)
    if selected_template and selected_template != "Select a template...":
        template_content = load_template(selected_template)
        with st.expander("Preview Template", expanded=True):
            st.text_area("Template Content", template_content, height=300)

    # File uploader
    uploaded_pdf = st.file_uploader("Upload Survey PDF", type=['pdf'])

    if uploaded_pdf and selected_template and selected_template != "Select a template...":
        if st.button("Generate Offer Letter"):
            try:
                # Save uploaded file
                pdf_path = save_uploaded_file(uploaded_pdf)

                # Process PDF
                with st.spinner("Processing PDF..."):
                    text = extract_text(pdf_path)
                    data = parse_fields(text, field_names)
                    
                    # Display extracted data
                    st.subheader("Extracted Data")
                    st.json(data)

                    # Preview filled template
                    st.subheader("Preview Filled Template")
                    filled_content = fill_template(template_content, data)
                    st.text_area("Filled Template", filled_content, height=300)

                # Create Word document
                with st.spinner("Generating offer letter..."):
                    output_path = "offer_letter.docx"
                    create_word_document(filled_content, output_path)

                # Provide download button for the generated document
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="Download Offer Letter",
                        data=file,
                        file_name="offer_letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                # Cleanup temporary files
                os.unlink(pdf_path)
                os.unlink(output_path)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 