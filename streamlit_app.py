import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "You can learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Get API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not found in .env file. Please add it to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": "Tu aides à modéliser des circuits électriques. Quand on te parle de format Grafit, tu sauras qu'il s'agit de formatter sous format JSON de la manière suivante {\"type\":\"grafit/clipboard\",\"nodes\":[{\"element\":{\"note\":\"\",\"quantity\":null},\"purchases\":[],\"tasks\":[],\"customPropertyValues\":[],\"node\":{\"id\":\"6005f4a1-d3e3-4ff8-b0f3-51f58c2c8111\",\"position\":{\"x\":380,\"y\":90},\"name\":\"Équipement\"}},{\"element\":{\"note\":\"\",\"quantity\":null},\"purchases\":[],\"tasks\":[],\"customPropertyValues\":[],\"node\":{\"id\":\"2d7e3b05-a303-408e-81e7-02b8c265beaf\",\"position\":{\"x\":400,\"y\":280},\"name\":\"\"}}],\"edges\":[{\"element\":{\"note\":\"\",\"quantity\":\"100\"},\"purchases\":[{\"unitPrice\":\"10\",\"name\":\"R2V 3G25\",\"reference\":\"Schneider electric\",\"quantity\":\"1\"}],\"tasks\":[{\"name\":\"Pose\",\"estimatedTime\":\"1\",\"flatRate\":null,\"quantity\":null,\"workerProfileId\":\"924d42f6-42ec-480f-bdfe-96a32a919e1e\"}],\"customPropertyValues\":[],\"edge\":{\"sourceId\":\"6005f4a1-d3e3-4ff8-b0f3-51f58c2c8111\",\"targetId\":\"2d7e3b05-a303-408e-81e7-02b8c265beaf\",\"name\":\"Câble test\"}}]}"
            }
        ]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Add audio input for voice dictation
    st.write("Vous pouvez dicter votre question :")
    audio_bytes = st.audio_input("Enregistrer un message vocal")
    
    # Process audio input if provided
    if audio_bytes:
        # First, transcribe the audio using OpenAI's Whisper model
        audio_file = audio_bytes
        
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            # Use the transcribed text as the prompt
            prompt = transcript.text
            
            # Display the transcribed text
            st.info(f"Transcription: {prompt}")
            
            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Erreur lors de la transcription audio: {str(e)}")

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
