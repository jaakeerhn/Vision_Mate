import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
from gtts import gTTS
import pytesseract
import tempfile
import base64

# Step 1: API Configuration
api_key_file = r"C:\Users\skjaa\.vscode\GEMINI\Python\.gemini.txt"

# Read API key from the file
with open(api_key_file, 'r') as file:
    GEMINI_API_KEY = file.read().strip()

os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# Set the Tesseract OCR executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path

# Function to generate a scene description
def generate_scene_description(input_prompt, image_data):
    """Generates a scene description using Google Generative AI."""
    response = model.generate_content([input_prompt, image_data[0]])
    return response.text

# Function to prepare the uploaded image
def input_image_setup(uploaded_file):
    """Prepares the uploaded image for processing."""
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded.")

# Function to convert text to speech and return audio file path using gTTS
def text_to_speech_file(text):
    """Converts text to speech and saves it to a temporary file using gTTS."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
        tts = gTTS(text=text, lang='en')
        tts.save(temp_audio_file.name)
        return temp_audio_file.name

# Function to encode the image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Function to extract text from an image
def extract_text_from_image(uploaded_file):
    """Extracts text from the uploaded image using pytesseract with error handling."""
    try:
        # Open the image file
        image = Image.open(uploaded_file)
        
        # Perform OCR using pytesseract
        extracted_text = pytesseract.image_to_string(image)
        
        # Return the extracted text
        return extracted_text
    
    except pytesseract.TesseractNotFoundError:
        # Handle case where Tesseract is not installed or not found
        raise RuntimeError("Tesseract is not installed or not configured properly. Please install Tesseract and configure the correct path.")
    
    except Exception as e:
        # Handle all other exceptions
        raise RuntimeError(f"An error occurred while extracting text: {str(e)}")

# Set the background image
background_image_path = "C:/Users/skjaa/Downloads/WhatsApp Image 2024-12-01 at 14.00.14_3c08e184.jpg"
base64_image = get_base64_image(background_image_path)

# Apply custom CSS for background and font styling
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;500&display=swap');
    .stApp {{
        background-image: url("data:image/jpeg;base64,{base64_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Roboto Mono', monospace;
    }}
    h1 {{
        text-align: center;
        font-size: 3rem;
    }}
    .stSidebar {{
        font-size: 1.2rem;
    }}
    .stButton>button {{
        font-size: 1.2rem;
        padding: 10px 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for application dashboard
st.sidebar.title("VisionMate+ Dashboard")
feature_selection = st.sidebar.radio("Features", ["Describe Scene", "Text-to-Speech", "Image to Text"])
st.sidebar.markdown("---")
st.sidebar.markdown("### Creator: Jaakeer")

# Main UI setup
st.markdown("<h1 style='text-align: center;'>VisionMate+</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.5rem;'>Empowering lives with AI: Image descriptions and voice guidance!</p>", unsafe_allow_html=True)

# Upload Image Section
uploaded_file = st.file_uploader("Upload an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

# Feature Selection Logic
if feature_selection == "Describe Scene":
    if st.button("🔍 Describe Scene"):
        if uploaded_file:
            input_prompt = """
            You are an AI assistant helping visually impaired individuals by describing the scene in the image. Provide:
            1. Contextual information about the real-life presence of the image.
            2. Identify the things, people, and places by accessing the information from your database.
            """
            image_data = input_image_setup(uploaded_file)
            with st.spinner("Processing..."):
                try:
                    description = generate_scene_description(input_prompt, image_data)
                    st.write("### Scene Description:")
                    st.write(description)
                    st.session_state.description_text = description  # Save for TTS
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please upload an image first.")

elif feature_selection == "Text-to-Speech":
    if st.button("🔊 Text-to-Speech"):
        if uploaded_file and "description_text" in st.session_state:
            with st.spinner("Generating audio..."):
                try:
                    audio_file = text_to_speech_file(st.session_state.description_text)
                    st.audio(audio_file)  # Play the audio in Streamlit
                    os.remove(audio_file)  # Clean up the temporary file
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please generate the scene description first.")

elif feature_selection == "Image to Text":
    if st.button("📜 Extract Text"):
        if uploaded_file:
            with st.spinner("Extracting text..."):
                try:
                    extracted_text = extract_text_from_image(uploaded_file)
                    st.write("### Extracted Text:")
                    st.text(extracted_text)
                except RuntimeError as re:
                    st.error(str(re))
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
        else:
            st.warning("Please upload an image first.")
