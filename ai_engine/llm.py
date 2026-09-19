import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in the .env file.")

    if not model:
        raise ValueError("GROQ_MODEL is not set in the .env file.")

    return ChatGroq(
        model=model,
        temperature=0,
        api_key=api_key,
    )