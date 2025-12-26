# Kyle - AI Voice Assistant
<div style="width:700px;height:200px;overflow:hidden"><img src="banner_kyle.png" style="width:70%;height:30%;object-fit:cover"></div>



Kyle is an AI voice assistant developed using the LiveKit framework. 
It has the following features:
- Web search
- Memory (Persistent and session memory)
- Email sending from a given account (provided by the user via Google App Password)

Tech stack and Working
- uses the LiveKit framework for LLM <-> STT <-> TTS orchestration
- DDGS library for web search
- mem0 for robust memory support
- Pydantic for schema validation
- stmplib for email sending functionality

# Installation and Running
1. Clone the GitHub repo
2. Open in the IDE of choice
3. Install the dependencies with:
   pip install -r requirements.txt
   or
   uv add -r requirements.txt
4. Run the following command to run the agent locally
   python agents.py console


Made with 💖

