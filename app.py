import pandas as pd
import json
import streamlit as st
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
from difflib import SequenceMatcher, ndiff

# --- Configure Gemini API ---
genai.configure(api_key="AIzaSyC8k8b_2dzknLVb1jvelOx6u7TmSedbLnI")  # 👈 User's actual API key

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

def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def calculate_score(extracted, validation):
    similarity_score = calculate_similarity(extracted, validation)
    accuracy_score = round(similarity_score * 50, 2)
    explanation_score = 30 if "explanation" in validation.lower() else 20
    validation_thoroughness = 20 if "formula" in validation.lower() or "concept" in validation.lower() else 10
    total_score = accuracy_score + explanation_score + validation_thoroughness
    return round(total_score, 2)

def compare_data(extracted_data, validated_data):
    # Split both extracted and validated data into lines
    extracted_lines = extracted_data.splitlines()
    validated_lines = validated_data.splitlines()

    # Make both arrays the same length by padding the shorter one with empty strings
    max_len = max(len(extracted_lines), len(validated_lines))
    extracted_lines.extend([''] * (max_len - len(extracted_lines)))
    validated_lines.extend([''] * (max_len - len(validated_lines)))

    # Create a side-by-side comparison of extracted and validated data
    data = {
        "Extracted Data": extracted_lines,
        "Validated Data": validated_lines
    }

    # Create a pandas DataFrame for a table format
    df = pd.DataFrame(data)
    return df

# --- Streamlit UI ---
st.set_page_config(page_title="Image Data Extractor and Validator 🖼✅", layout="wide")

# Custom Stylish Theme with Interactive Elements
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #FF6F61, #D53369);  /* Gradient background for energy */
            color: #ecf0f1;  /* Light text color */
            font-family: 'Poppins', sans-serif;
        }
        .stButton {
            background-color: #f39c12;  /* Golden Button */
            color: white;
            border-radius: 30px;
            padding: 12px 20px;
            font-size: 16px;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 10px;
        }
        .stButton:hover {
            background-color: #e67e22;  /* On hover, change button color */
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
            background: rgba(255, 255, 255, 0.1);  /* Semi-transparent cards */
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
Welcome to the **Image Data Extractor and Validator**! Upload a handwritten image containing formulas, notes, or definitions, and we will extract the content, validate its accuracy, and provide detailed feedback and a score.

Let’s get started! 🤓
""")

# File Upload Section
st.subheader("📂 Upload Your Handwritten Image")
uploaded_image = st.file_uploader("Upload a JPG, JPEG, or PNG file", type=["jpg", "jpeg", "png"])

if uploaded_image:
    # Show spinner while processing
    with st.spinner("🧠 Processing image content..."):
        try:
            image = Image.open(uploaded_image)
            st.image(image, caption="🖼 Uploaded Image Preview", use_container_width=True)

            # Process extracted and validated data
            extracted = extract_text_from_image(uploaded_image)
            validation = validate_information(extracted)
            score = calculate_score(extracted, validation)

            # Card for Extracted Content
            with st.container():
                st.markdown("<div class='card'><h3>📝 Extracted Data:</h3><pre>" + extracted + "</pre></div>", unsafe_allow_html=True)

            # Card for Detailed Explanation and Corrections
            with st.container():
                st.markdown("<div class='card'><h3>✅ Detailed Explanation & Corrections:</h3><p>" + validation + "</p></div>", unsafe_allow_html=True)

            # Displaying the Score in a Card
            with st.container():
                st.markdown(f"""
                <div class='card'>
                    <h3>🏅 Score:</h3>
                    <p>Your final score for this image extraction and validation process is: <strong>{score}/100</strong></p>
                </div>
                """, unsafe_allow_html=True)

            # --- Comparison Section ---
            st.subheader("🔍 Data Comparison (Extracted vs. Validated)")

            # Show the comparison table
            comparison_df = compare_data(extracted, validation)
            st.dataframe(comparison_df)

            # Download Button for .txt file with Tooltip
            st.subheader("📥 Download Extracted Data")
            download_button_txt = st.download_button(
                label="Download Extracted Data as .txt file",
                data=extracted,
                file_name="extracted_data.txt",
                mime="text/plain",
                help="Click to download the extracted data as a text file.",
                use_container_width=True
            )

            # --- JSON Download Feature ---
            json_data = {
                "extracted_data": extracted,
                "validated_data": validation,
                "score": score
            }
            download_button_json = st.download_button(
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
