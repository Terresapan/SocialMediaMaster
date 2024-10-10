import time
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

# Access the Gemini API key from the environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")  # Ensure this is the correct name as defined in your .env file

# Configure the gemini API with the API key
if gemini_api_key:  # Check if the API key was loaded successfully
    genai.configure(api_key=gemini_api_key)
else:
    raise ValueError("API key not found. Please set the GEMINI_API_KEY in your .env file.")
                
def upload_to_gemini(api_key, file_paths, mime_type=None):
    """Uploads the given files to Gemini."""
    genai.configure(api_key=api_key)
    uploaded_files = []
    for path in file_paths:
        file = genai.upload_file(path)
        uploaded_files.append(file)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return uploaded_files

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

def generate_suggestions(api_key, video_topic, target_audience, selling_point, question, files):
    """Generates suggestions based on user input."""
    generation_config = {
        "temperature": 0,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    system_message = f"""
        You are a highly skilled expert in social media strategies, specializing in the creation of engaging short video content to drive lead generation.
        You will be provided the basic info about the user, including {video_topic},{target_audience},{selling_point}.
        Your role is to answer {question} and assist users in producing effective short videos based on a series of provided PDFs, which serve as your primary source of information.
        
        Your response should include:
        1. A brief outline for a short video (30-60 seconds) that addresses the topic and appeals to the target audience.
        2. Suggestions on how to incorporate the unique selling points into the video.
        3. A response to the user's specific question, relating it back to the video content.
        4. Any relevant tips or strategies from the PDFs that could enhance the video's effectiveness for lead generation.       
                
        Adhere strictly to the content in these PDFs. If the information requested is unrelated to the provided materials,
        clearly state that you do not have the answer rather than providing speculative responses.
        If users raise questions unrelated to content creation, politely remind them to focus on the topic at hand.
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
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

    # Stream the response
    response = chat_session.send_message(question, stream=True)

    # Collect chunks of streamed output
    streamed_output = ""
    for chunk in response:
        streamed_output += chunk.text  # Append each chunk's text to the output string

    return streamed_output  # Return the complete streamed output
 