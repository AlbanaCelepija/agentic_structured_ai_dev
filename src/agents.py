
from crewai import Agent
from crewai import LLM 
from tools import file_read_tool, serper_dev_tool

############################################### Models
llm = LLM(
    model="ollama/llama3.2:1b",
    base_url="http://localhost:11434"
)

############################################### Agents
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


research_agent = Agent(
    role="Internet Researcher",
    goal="Find the most relevant and recent information about a given topic.",
    backstory="""You are a skilled researcher, adept at navigating the internet 
                 and gathering high-quality, reliable information.""",
    llm=llm,
    tools=[serper_dev_tool],
    verbose=True
)


summarizer_research_agent = Agent(
    role="Content Summarizer",
    goal="Condense the key insights from research into a short and informative summary.",
    backstory="""You are an expert in distilling complex information into concise, 
                 easy-to-read summaries.""",
    llm=llm,
    verbose=True
)

fact_checker_agent = Agent(
    role="Fact-Checking Specialist",
    goal="Verify the accuracy of information and remove any misleading or false claims.",
    backstory="""You are an investigative journalist with a knack for validating facts, 
                 ensuring that only accurate information is published.""",
    llm=llm,
    tools=[serper_dev_tool],
    verbose=True
)

