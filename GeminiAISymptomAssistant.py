import streamlit as st
import google.genai as genai
from google.genai.errors import APIError

# --- Configuration ---
# !!! IMPORTANT !!! Replace "YOUR_API_KEY" with your actual Google AI API key.
API_KEY = "YOUR_API_KEY"
MODEL_NAME = "gemini-2.5-flash" 

# --- Client Initialization (Attempt to connect) ---
client = None
if API_KEY == "YOUR_API_KEY":
    st.error("Please replace 'YOUR_API_KEY' with your actual API key in the script.")
else:
    try:
        # Note: Client initialization is typically done outside the function for efficiency
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        st.error(f"ERROR: Could not initialize GenAI Client: {e}")

def generate_remedies(symptoms: str) -> str:
    """Generates general wellness suggestions using the Gemini API."""
    if not client:
        return "API Client not ready due to missing or invalid key."

    # --- Core Prompt: Safety and Instruction Combined ---
    # This concise prompt is designed to minimize filtering and guarantee a safe response.
    combined_prompt = (
        "INSTRUCTIONS:\n"
        "1. **EMERGENCY STOP:** If symptoms are severe, urgent, or life-threatening (e.g., severe chest pain, major injury), DO NOT provide wellness advice. Return ONLY the following message and stop: "
        "'🚨 **Immediate Medical Attention Required** 🚨\n\nBased on the severity of the symptoms described, this tool cannot provide any suggestions. Please call emergency services or seek professional medical help immediately.'\n\n"
        "2. **WELLNESS GUIDE:** Otherwise, act as a general wellness guide. Start with a clear and concise **disclaimer** (e.g., 'This is general information, not medical advice.'). Then, provide 3 to 5 easy, safe, **general comfort and support measures** in a concise bulleted list. Focus only on **rest, hydration, and comfort techniques.**\n\n"
        f"USER SYMPTOMS: {symptoms}"
    )
    
    try:
        with st.spinner('Analyzing symptoms and suggesting remedies...'):
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=combined_prompt,
                config={"temperature": 0.5, "max_output_tokens": 500}
            )

        if response.text:
            return response.text
        else:
            # Fallback if the filter was still triggered despite the clear instruction
            return "The AI returned an empty response. This often means the content filter was triggered. Please try describing your symptoms differently."

    except APIError as e:
        return f"An API Error occurred: {e}. Check your API key and permissions."
    except Exception as e:
        # Catches the unexpected error from the prior attempt's incompatible SDK issue
        return f"An unexpected error occurred: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Simple AI Wellness Checker", layout="centered")
st.title("Simple AI Wellness Suggestion Tool")
st.markdown("Enter your symptoms below to receive immediate, general home wellness suggestions.")

# Input
symptoms_input = st.text_area(
    "What are your symptoms?",
    placeholder="e.g., Runny nose, mild cough, and slight fatigue."
)

# Button to trigger generation
if st.button("Get Home Remedies", type="primary", use_container_width=True):
    if symptoms_input.strip():
        # Call the generation function
        remedy_output = generate_remedies(symptoms_input)
        
        # Display the results
        st.subheader("Suggested Remedies:")
        st.markdown(remedy_output)
    else:
        st.warning("Please enter your symptoms to get suggestions.")
