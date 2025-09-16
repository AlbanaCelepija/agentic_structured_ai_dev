
from crewai import Task
from agents import senior_technical_writer, summarizer_agent
from tools import file_read_tool

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