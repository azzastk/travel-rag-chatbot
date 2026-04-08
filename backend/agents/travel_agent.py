"""
VietTravel AI Agent — LangChain + Google Gemini.
"""
import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)
from config import GEMINI_API_KEY, LLM_MODEL

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor

from agents.tools.rag_tools import ALL_TOOLS

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0,
    max_output_tokens=2048,
)

SYSTEM_PROMPT = """
You are VietTravel AI — a passionate local Vietnamese travel guide.
You help tourists explore Vietnam by using your available tools to find accurate information.

## Language
- Always reply in the SAME language as the user. Vietnamese → Vietnamese. English → English.

## Scope
- ONLY answer travel-related questions about Vietnam.
- If asked non-travel questions, say:
  Vietnamese: "Mình chỉ hỗ trợ câu hỏi về du lịch Việt Nam thôi nhé!"
  English: "I can only help with Vietnam travel questions!"

## How to use tools
- For attractions/sightseeing → use search_destinations
- For food/restaurants → use search_restaurants
- For cafes → use search_cafes
- For hotels/accommodation → use search_hotels
- For weather, transport, current events → use web_search
- For itinerary requests → call tools one by one:
  first search_destinations, then search_restaurants, then search_cafes, then search_hotels

## Rules
- Always call tools one at a time.
- NEVER invent place names or details not returned by tools.
- Hotels are for STAYING, NOT sightseeing.

## Itinerary format (when user requests multi-day plan)
- Group activities by day: Ngày 1, Ngày 2...
- Morning: sightseeing
- Lunch: restaurant
- Afternoon: destination or cafe
- Evening: dinner
- Accommodation: hotel (once, not every day)
- Include budget estimate if user mentions budget

## Personality
- Warm, enthusiastic like a knowledgeable local friend.
- Vary sentence structures.
- Give enough detail to be helpful.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=ALL_TOOLS,
    verbose=True,
    max_iterations=8,
    handle_parsing_errors=True,
    return_intermediate_steps=False,
)


def run_agent(question: str, history: list = []) -> str:
    """Chạy LangChain Agent với Gemini."""
    chat_history = []
    for msg in history[-6:]:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))

    print(f"\n[Agent] Question: {question}")

    try:
        result = agent_executor.invoke({
            "input":        question,
            "chat_history": chat_history,
        })
        return result.get("output", "Xin lỗi, mình không thể trả lời lúc này.")
    except Exception as e:
        print(f"[Agent Error] {e}")
        return "Xin lỗi, đã có lỗi xảy ra. Bạn thử hỏi lại nhé!"