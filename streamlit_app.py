import os
import streamlit as st
from utils import save_feedback
from backend import upload_to_gemini, wait_for_files_active, generate_suggestions

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]["API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = "Video_Content_Master"

# enhanced streamlit chatbot interface
st.sidebar.header("✨ Short Video Content Master")
st.sidebar.markdown(
    "This app answers your questions about short video content strategy and execution. "
    "To use this app, you'll need to provide a Google Gemini API key, which you can obtain for free [here](https://aistudio.google.com/app/apikey)."
)
st.sidebar.write("### Instructions")
st.sidebar.write(":pencil: Enter your video topic or theme, target audience, unique selling points, and question you want to ask.")
st.sidebar.write(":point_right: Click 'Generate Suggestions' to get inspired.")
st.sidebar.write(":heart_decoration: Let me know your thoughts and feedback about the app.")

# Initialize session state for feedback storage if not already done
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# Feedback form
st.sidebar.subheader("Feedback Form")
feedback = st.sidebar.text_area("Your thoughts and feedback", value=st.session_state.feedback, placeholder="Share your feedback here...")

if st.sidebar.button("Submit Feedback"):
    if feedback:
        try:
            save_feedback(feedback)
            st.session_state.feedback = ""  # Clear feedback after submission
            st.sidebar.success("Thank you for your feedback! 😊")
        except Exception as e:
            st.sidebar.error(f"Error saving feedback: {str(e)}")
    else:
        st.sidebar.error("Please enter your feedback before submitting.")

st.sidebar.image("assets/logo01.jpg", use_container_width=True)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password", placeholder="Your Gemini API key here...")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Input fields for user to input video details
    st.header("Enter Your Video Details")
    video_topic_input = st.text_input("Enter a Video Topic or Theme", placeholder="Organic Soup")
    target_audience_input = st.text_input("Enter the Target Audience", placeholder="For busy working adults")
    selling_point_input = st.text_input("Enter Unique Selling Points or Opinion", placeholder="Ready in 5 minutes")
    question_input = st.text_input("Enter Your Question", placeholder="How can I make the video hook?")

    # Button to trigger suggestions generation
    if st.button("Generate Suggestions"):
        # Validate inputs
        if not video_topic_input or not target_audience_input or not selling_point_input or not question_input:
            st.error("Please fill out all fields to generate suggestions.", icon="🚫")
        else:
            with st.spinner("Generating suggestions..."):
                files = [
                    "assets/Blogs.pdf",  # path to your PDFs
                    "assets/Book.pdf"
                ]
                try:
                    upload_results = upload_to_gemini(gemini_api_key, files, mime_type="application/pdf")
                    wait_for_files_active(upload_results)

                    response = generate_suggestions(
                        gemini_api_key,
                        video_topic_input,
                        target_audience_input,
                        selling_point_input,
                        question_input,
                        upload_results
                    )

                    st.subheader("Generated Suggestions")
                    st.write(f"🤖 AI: {response}")
                except Exception as e:
                    st.error(f"Error encountered: {str(e)}")