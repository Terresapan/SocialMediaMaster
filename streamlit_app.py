import streamlit as st
import time
from utils import save_feedback
import google.generativeai as genai

# Enhanced Streamlit chatbot interface
st.sidebar.header("✨ Short Video Content Master")
st.sidebar.markdown(
    "This app answer your questions about Short Video Content Strategy and Execution. "
    "To use this App, you need to provide a Google Gemini API key, which you can get [here](https://aistudio.google.com/app/apikey) for free.")
st.sidebar.write("### Instructions")
st.sidebar.write(":pencil: Enter your video topic, target audience, theme, and question you want to ask.")
st.sidebar.write(":point_right: Click 'Generate Suggestions' to receive suggestions.")
st.sidebar.write(":point_right: Click 'Click me if you have no idea what to ask' to get inspired.")
st.sidebar.write(":heart_decoration: Tell me your thoughts and feedback about the App.")

# Initialize session state for feedback storage if not already done
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# Feedback Form
st.sidebar.subheader("Feedback Form")
feedback = st.sidebar.text_area("Your Thoughts and Feedback", value=st.session_state.feedback, placeholder="Share your feedback here...")
    
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

st.sidebar.image("assets/logo01.jpg", use_column_width=True)

# ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password", placeholder="Your Gemini API Key here...")

if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # create an openai client
    genai.configure(api_key=gemini_api_key)

    def upload_to_gemini(path, mime_type=None):
       """Uploads the given file to Gemini."""
       file = genai.upload_file(path, mime_type=mime_type)
       print(f"Uploaded file '{file.display_name}' as: {file.uri}")
       return file

    def wait_for_files_active(files):
        """Waits for the given files to be active."""
        print("Waiting for file processing...")
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
            print(file)
        print("...all files ready")
   
    # Make these files available on the local file system
    # You may need to update the file paths
    files = [
        upload_to_gemini("assets/Social Media Blogs.pdf", mime_type="application/pdf"),
        upload_to_gemini("assets/Social Media Video Marketing for small business owers.pdf", mime_type="application/pdf")
    ]

    # Some files have a processing delay. Wait for them to be ready.
    wait_for_files_active(files)


    # input field for user to input a product description
    st.header("Enter Your Video Details")
    video_topic_input = st.text_input("Enter a Video topic", placeholder="organic soup")
    target_audience_input = st.text_input("Enter the Target Audience", placeholder="for busy working adults")
    selling_point_input = st.text_input("Enter Unique Selling Points or Opinion", placeholder="ready in 5 minutes")
    question_input = st.text_input("Enter Your Question", placeholder="How can I make the video hook?")

    system_message = f"""
        You are a highly skilled expert in social media strategies, specializing in the creation of engaging short video content to drive lead generation.
        You will be provided the basic info about the user, including {video_topic_input},{target_audience_input},{selling_point_input}.
        Your role is to anwser {question_input} and assist users in producing effective short videos based on a series of provided PDFs, which serve as your primary source of information.
        Adhere strictly to the content in these PDFs. If the information requested is nothing to do with the provided materials,
        clearly state that you do not have the answer, rather than providing speculative responses.
        If users raise questions unrelated to content creation, politely remind them to focus on the topic at hand.
    """

    # button to trigger tagline generation
    if st.button("Generate Suggestions"):
        # Validate inputs
        if not video_topic_input or not target_audience_input or not selling_point_input or not question_input:
            st.error("Please fill out all fields to generate suggestions.", icon="🚫")
        else:
            generation_config = {
                "temperature": 0,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
                }
            
            model = genai.GenerativeModel(
                model="gemini-1.5-flash", 
                generation_config=generation_config,
                system_instruction=system_message,
            )
    
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                        *files,
                        ],
                    },
                    ]
                )
            response = chat_session.send_message(question_input)
                # Display messages
            st.subheader("Generated Suggestions")
            st.write(f"🤖 AI: {response.text}")
