
from crewai import Task
from agents import senior_technical_writer, summarizer_agent, research_agent, summarizer_research_agent, fact_checker_agent
from tools import file_read_tool, serper_dev_tool

writing_task = Task(
    description="""Write a well-structured, engaging,
                   and technically accurate article
                   on {topic}.""",    
    agent=senior_technical_writer,         
    expected_output="""A polished, detailed, and easy-to-read
                       article on the given topic.""",
)

summarizer_task = Task(
    description=(
        "Use the FileReadTool to read the contents of {file_path} "
        "and provide a summary in 20 words or less. "
        "Ensure the summary captures the key insights "
        "and main points from the document."
    ),
    agent=summarizer_agent,
    tools=[file_read_tool],
    expected_output="A concise 20-word summary of the key points from the file.",
)

research_task = Task(
    description="""Use the SerperDevTool to search for the 
                   most relevant and recent data about {topic}."""
                "Extract the key insights from multiple sources.",
    agent=research_agent,
    tools=[serper_dev_tool],
    expected_output="A detailed research report with key insights and source references."
)

summarization_task = Task(
    description="Summarize the research report into a concise and informative paragraph. "
                "Ensure clarity, coherence, and completeness.",
    agent=summarizer_research_agent,
    expected_output="A well-structured summary with the most important insights."
)

fact_checking_task = Task(
    description="Verify the summarized information for accuracy using the SerperDevTool. "
                "Cross-check facts with reliable sources and correct any errors.",
    agent=fact_checker_agent,
    tools=[serper_dev_tool],
    expected_output="A fact-checked, verified summary of the research topic."
)
