import pandas as pd
import json
import streamlit as st
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyC8k8b_2dzknLVb1jvelOx6u7TmSedbLnI")

def extract_text_from_image(image_file):
    model = genai.GenerativeModel("gemini-1.5-flash")
    image_bytes = image_file.getvalue()

    try:
        response = model.generate_content([ 
            "Extract all visible content from this image (text, formulas, notes, etc.) as clearly as possible.",
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

def validate_information(extracted_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
You are an expert tutor.

Review the following extracted content from a handwritten image:

{extracted_text}

Your task:
- Identify any incorrect facts or formulas.
- Correct them.
- Explain the correct concept clearly as a tutor would to a student.

Use a friendly tone, and keep your explanations simple and clear.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Streamlit UI ---
st.set_page_config(page_title="Image Data Extractor and Validator 🖼✅", layout="wide")

# Custom Stylish Theme with Interactive Elements
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #FF6F61, #D53369);
            color: #ecf0f1;
            font-family: 'Poppins', sans-serif;
        }
        .stButton {
            background-color: #f39c12;
            color: white;
            border-radius: 30px;
            padding: 12px 20px;
            font-size: 16px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
        }
        .stButton:hover {
            background-color: #e67e22;
        }
        .stFileUploader {
            background-color: #2c3e50;
            color: #ecf0f1;
            border-radius: 8px;
            padding: 15px;
        }
        .stTitle {
            font-size: 40px;
            font-weight: bold;
            color: #fff;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
        }
        .stMarkdown {
            font-size: 18px;
        }
        .stCode {
            font-size: 16px;
            background-color: #34495e;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
        .stTextInput, .stFileUploader, .stDownloadButton {
            background-color: #2c3e50;
            color: #ecf0f1;
            border-radius: 8px;
            padding: 10px;
        }
        .stSubheader {
            font-size: 24px;
            font-weight: 600;
            color: #f39c12;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            margin: 15px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease-in-out;
        }
        .card:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

# Title and Description
st.title("🖼 Image Data Extractor and Validator")
st.markdown("""
Welcome to the *Image Data Extractor and Validator*! Upload a handwritten image containing formulas, notes, or definitions, and we will extract the content, validate its accuracy, and provide detailed feedback.

Let’s get started! 🤓
""")

# File Upload Section
st.subheader("📂 Upload Your Handwritten Image")
uploaded_image = st.file_uploader("Upload a JPG, JPEG, or PNG file", type=["jpg", "jpeg", "png"])

if uploaded_image:
    with st.spinner("🧠 Processing image content..."):
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="🖼 Uploaded Image Preview", use_container_width=True)

            # Extract & Validate
            extracted = extract_text_from_image(uploaded_image)
            validation = validate_information(extracted)

            # Card for Extracted Content
            with st.container():
                st.markdown("<div class='card'><h3>📝 Extracted Data:</h3><pre>" + extracted + "</pre></div>", unsafe_allow_html=True)

            # Card for Explanation
            with st.container():
                st.markdown("<div class='card'><h3>✅ Detailed Explanation & Corrections:</h3><p>" + validation + "</p></div>", unsafe_allow_html=True)

            # --- Download Buttons ---
            st.subheader("📥 Download Extracted Data")
            st.download_button(
                label="Download Extracted Data as .txt file",
                data=extracted,
                file_name="extracted_data.txt",
                mime="text/plain",
                help="Click to download the extracted data as a text file.",
                use_container_width=True
            )

            json_data = {
                "extracted_data": extracted,
                "validated_data": validation
            }
            st.download_button(
                label="Download Extracted Data as JSON file",
                data=json.dumps(json_data, indent=4),
                file_name="extracted_data.json",
                mime="application/json",
                help="Click to download the extracted data as a JSON file.",
                use_container_width=True
            )

        except UnidentifiedImageError:
            st.error("❌ Unable to identify the image. Please upload a valid JPG, JPEG, or PNG file.")
        except Exception as e:
            st.error(f"❌ Error processing the image: {e}")
