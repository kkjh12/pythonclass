import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Stock Price Analyst", layout="centered", initial_sidebar_state="collapsed")
# Streamlit page setup
st.title("📈 Stock Price Analyst: `GPT-4 Turbo with Vision` 👀")

# Retrieve the OpenAI API Key
api_key = st.secrets["api_secret"]

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image of a stock chart
uploaded_file = st.file_uploader("Upload an image of a stock chart", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
show_details = st.toggle("Add details about the stock chart", value=False)

if show_details:
    # Text input for additional details about the stock chart, shown only if toggle is True
    additional_details = st.text_area(
        "Add any additional details or context about the stock chart here:",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("Analyze the Stock Chart", type="secondary")

# Check if a stock chart has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analyzing the stock chart ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        # Optimized prompt for additional clarity and detail specific to stock price analysis
        prompt_text = (
            "You are a highly knowledgeable financial analyst equipped with a risk assessment skillset. "
            "Your task is to examine the following stock chart image in detail. "
            "Provide a comprehensive and accurate explanation of what the chart depicts. "
            "Highlight key elements and their significance in terms of stock price movement, trends, volume, and potential market signals. "
            "Present your analysis in a clear, well-structured markdown format, "
            "Based on the analysis, offer investment advice tailored to risk-averse, risk-loving, and risk-neutral investors. "
            "Clearly indicate whether each type of investor should consider investing in this stock, providing reasons for your recommendations. "
            "Present your analysis and advice in clear, well-structured markdown format, using relevant financial terminology. "
            "Assume the reader has a basic understanding of stock market concepts."
            "Additionally, create a detailed image caption in bold, summarizing the investment advice."
        )
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nAdditional Context Provided by the User:\n{additional_details}"
            )
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview", messages=messages, 
                max_tokens=1200, stream=True
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required
    if not uploaded_file and analyze_button:
        st.warning("Please upload an image of a stock chart.")
    if not api_key:
        st.warning("Please enter your OpenAI API key.")
