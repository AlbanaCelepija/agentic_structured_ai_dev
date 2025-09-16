
from crewai import Agent
from crewai import LLM 
from tools import file_read_tool

# -------------------------------------------------------------The Model 
llm = LLM(
    model="ollama/llama3.2:1b",
    base_url="http://localhost:11434"
)

# -------------------------------------------------------------The Agents
senior_technical_writer = Agent(

    role="Senior Technical Writer",    
    goal="""Craft clear, engaging, and well-structured
            technical content based on research findings""",    
    backstory="""You are an experienced technical writer
                 with expertise in simplifying complex
                 concepts, structuring content for readability,
                 and ensuring accuracy in documentation.""",   
    llm=llm,              
    verbose=True  # Enable logging for debugging
)

code_reviewer = Agent(
    role="Senior Code Reviewer",
    goal="""Review code for bugs, inefficiencies, and 
            security vulnerabilities while ensuring adherence 
            to best coding practices.""",
    backstory="""You are a seasoned software engineer with years of 
                 experience in writing, reviewing, and optimizing 
                 production-level code in multiple programming languages.""",
    llm=llm,
    verbose=True
)


summarizer_agent = Agent(
    role="Senior Document Summarizer",
    goal="Extract and summarize key insights from provided files in 20 words or less.",
    backstory="""You are an expert in document analysis, skilled at extracting 
                 key details, summarizing content, and identifying critical 
                 insights from structured and unstructured text.""",
    llm=llm,
    tools=[file_read_tool],
    verbose=True
)
