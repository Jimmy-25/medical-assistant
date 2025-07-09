import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDF
import google.generativeai as genai

st.set_page_config(page_title="Medical Diagnosis AI Assistant", layout="centered")

st.title("🧠 Medical Diagnosis Interpreter")
st.markdown("""
Upload a **CSV, Excel, or PDF file**, or **paste the test results** below.  
This AI tool will analyze the content and suggest possible diagnoses based on the information.
""")

# Show Gemini SDK version
st.sidebar.write("🔍 Gemini SDK version:", genai.__version__)

# Configure API key from Streamlit secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Debug: List available models
with st.expander("🧪 Debug: Available Gemini Models"):
    try:
        models = genai.list_models()
        for m in models:
            st.text(m.name)
    except Exception as e:
        st.error(f"Could not list models: {e}")

# Use the correct model path
model = genai.GenerativeModel("models/gemini-pro")

# File uploader
uploaded_file = st.file_uploader(
    "📂 Upload medical report (CSV, Excel, or PDF)",
    type=["csv", "xlsx", "xls", "pdf"]
)

# Manual text input
text_input = st.text_area("📝 Or paste clinical/lab results manually below:", height=200)

# When user clicks the button
if st.button("🩺 Interpret Results"):
    combined_text = ""

    if uploaded_file:
        file_type = uploaded_file.name.split(".")[-1].lower()
        try:
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
                combined_text += df.to_string(index=False)
            elif file_type in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
                combined_text += df.to_string(index=False)
            elif file_type == "pdf":
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = ""
                for page in pdf:
                    text += page.get_text()
                combined_text += text.strip()
        except Exception as e:
            st.error(f"❌ Failed to read uploaded file: {e}")

    if text_input.strip():
        combined_text += "\n\n" + text_input.strip()

    if combined_text.strip() == "":
        st.warning("Please provide some medical content to analyze.")
    else:
        with st.spinner("Analyzing patient data..."):
            prompt = (
                f"Based on these medical test results or descriptions, "
                f"what could be the possible diagnosis?\n\n{combined_text}\n\nExplain simply."
            )
            try:
                response = model.generate_content([prompt])  # Note: prompt must be a list
                st.success("✅ Possible Interpretation:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"❌ Gemini error: {e}")
