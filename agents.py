from dotenv import load_dotenv
from livekit.plugins import groq
from livekit.plugins import google
from livekit import agents, rtc
from livekit.plugins import deepgram
from livekit.plugins import silero
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import (
    noise_cancellation,
)
import os
from tools import web_search, send_email, write_memory, read_memory

from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS




load_dotenv(".env.local")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS             
),
        

server = AgentServer()



@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=groq.LLM(
        model="meta-llama/llama-4-maverick-17b-128e-instruct"
        ),
        tts=deepgram.TTS(
        model="aura-asteria-en",
   ),
        stt=groq.STT(
      model="whisper-large-v3-turbo",
      language="en",
   ),
    vad=silero.VAD.load(),
    tools=[

        web_search,
        send_email,
        read_memory,
        write_memory,
    ],
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
            ),
        ),
    )

    await session.generate_reply(
        instructions=SESSION_INSTRUCTIONS,
    )


if __name__ == "__main__":
    
    agents.cli.run_app(server)
    