import operator
from typing import Annotated, List, TypedDict, Literal
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7,
)


class SupervisorState(TypedDict):
    """State for supervisor pattern with multiple agents."""

    topic: str
    messages: Annotated[List[str], operator.add]
    next_agent: str
    final_answer: str


def researcher_agent(state: SupervisorState) -> dict:
    """Researcher agent gathers information about the topic."""
    sys = (
        "You are a researcher. Your job is to gather key facts and information "
        "about the given topic. Provide 2-3 key points. Be concise."
    )
    messages_for_llm = [
        ("system", sys),
        ("user", f"Research this topic: {state['topic']}"),
    ]
    resp = llm.invoke(messages_for_llm)
    research_msg = f"RESEARCHER: {resp.content}"
    return {"messages": [research_msg]}


def expert_agent(state: SupervisorState) -> dict:
    """Expert agent analyzes and provides insights based on research."""
    sys = (
        "You are an expert analyst. Review the research provided and give "
        "your expert analysis and conclusions. Be specific and insightful."
    )
    # Get context from previous messages
    context = "\n".join(state["messages"])
    messages_for_llm = [
        ("system", sys),
        (
            "user",
            f"Topic: {state['topic']}\n\nPrevious research:\n{context}\n\nProvide your expert analysis.",
        ),
    ]
    resp = llm.invoke(messages_for_llm)
    expert_msg = f"EXPERT: {resp.content}"
    return {"messages": [expert_msg]}


def supervisor_agent(state: SupervisorState) -> dict:
    """Supervisor decides which agent should act next or if discussion should end."""
    sys = (
        "You are a supervisor managing a research discussion between a RESEARCHER and an EXPERT. "
        "Based on the conversation so far, decide what should happen next:\n"
        "- Return 'researcher' if we need initial research or more information\n"
        "- Return 'expert' if research is done and we need expert analysis\n"
        "- Return 'end' if both research and expert analysis are complete\n\n"
        "Respond with ONLY one word: researcher, expert, or end"
    )

    context = "\n".join(state["messages"]) if state["messages"] else "No discussion yet"
    messages_for_llm = [
        ("system", sys),
        (
            "user",
            f"Topic: {state['topic']}\n\nConversation:\n{context}\n\nWhat's next?",
        ),
    ]
    resp = llm.invoke(messages_for_llm)
    next_step = resp.content.strip().lower()

    # Ensure valid response
    if next_step not in ["researcher", "expert", "end"]:
        next_step = "end"

    return {"next_agent": next_step}


def finalize_answer(state: SupervisorState) -> dict:
    """Compile final answer from the discussion."""
    sys = (
        "Summarize the research discussion into a clear, concise final answer. "
        "Include key findings and expert insights."
    )
    context = "\n".join(state["messages"])
    messages_for_llm = [
        ("system", sys),
        (
            "user",
            f"Topic: {state['topic']}\n\nDiscussion:\n{context}\n\nProvide final summary:",
        ),
    ]
    resp = llm.invoke(messages_for_llm)
    return {"final_answer": resp.content}


def route_supervisor(state: SupervisorState) -> str:
    """Route based on supervisor's decision."""
    next_agent = state.get("next_agent", "researcher")
    if next_agent == "end":
        return "finalize"
    return next_agent


def workflow_graph():
    supervisor_graph = StateGraph(SupervisorState)
    supervisor_graph.add_node("supervisor", supervisor_agent)
    supervisor_graph.add_node("researcher", researcher_agent)
    supervisor_graph.add_node("expert", expert_agent)
    supervisor_graph.add_node("finalize", finalize_answer)
    supervisor_graph.add_edge(START, "supervisor")
    supervisor_graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"researcher": "researcher", "expert": "expert", "finalize": "finalize"},
    )
    supervisor_graph.add_edge("researcher", "supervisor")
    supervisor_graph.add_edge("expert", "supervisor")
    supervisor_graph.add_edge("finalize", END)
    return supervisor_graph


def main():
    supervisor_graph = workflow_graph()
    supervisor_agent_graph = supervisor_graph.compile(debug=True)

    topic = "What are the main benefits of using LangGraph for building AI agents?"
    initial_state = {
        "topic": topic,
        "messages": [],
        "next_agent": "",
        "final_answer": "",
    }

    result = supervisor_agent_graph.invoke(initial_state)

    print(f"TOPIC: {topic}\n")
    print("=" * 80)
    print("\nDISCUSSION:")
    print("-" * 80)
    for msg in result["messages"]:
        print(f"\n{msg}\n")
    print("=" * 80)
    print(f"\nFINAL ANSWER:\n{result['final_answer']}")


if __name__ == "__main__":
    main()
