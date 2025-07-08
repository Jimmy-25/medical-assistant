import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="Medical Diagnosis AI Assistant", layout="centered")

st.title("🧠 Medical Diagnosis Interpreter")
st.markdown("Upload a CSV file or paste test results manually. The AI will analyze the data and suggest possible diagnoses.")

# Configure API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# CSV Upload
uploaded_file = st.file_uploader("📁 Upload CSV file with test results (optional)", type=["csv"])

# Text Input
text_input = st.text_area("📝 Or paste the lab test results or clinical notes here:", height=200)

# Interpret Button
if st.button("🩺 Interpret Results"):
    if not uploaded_file and not text_input.strip():
        st.warning("Please upload a CSV or enter some text to proceed.")
    else:
        combined_text = ""

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                combined_text += df.to_string(index=False)
            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
        
        if text_input.strip():
            combined_text += "\n\n" + text_input.strip()

        with st.spinner("Analyzing patient data..."):
            prompt = f"Based on these medical test results or descriptions, what could be the possible diagnosis?\n\n{combined_text}\n\nExplain simply."
            response = model.generate_content(prompt)
            st.success("✅ Possible Interpretation:")
            st.markdown(response.text)
