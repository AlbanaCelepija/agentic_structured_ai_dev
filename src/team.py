
import os
from crewai import Crew, Process
from agents import senior_technical_writer, summarizer_agent, research_agent, summarizer_research_agent, fact_checker_agent
from tasks import writing_task, summarizer_task, research_task, summarization_task, fact_checking_task
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OUTPUT_TECHNICAL_WRITER_FILE = "output_technical_writer.md"
OUTPUT_SUMMARIZER_FILE = "output_summarizer.md"
OUTPUT_RESEARCH_ASSISTANT = "output_research_assistant.md"


def write_article(topic, output_file=OUTPUT_TECHNICAL_WRITER_FILE):
    crew = Crew(
        agents=[senior_technical_writer],
        tasks=[writing_task],
        verbose=True
    )
    response = crew.kickoff(inputs={"topic": topic})
    with open(output_file, "w") as f:
        f.write(response.raw)
    return response.raw


def summarize_file(file_path, output_file=OUTPUT_SUMMARIZER_FILE):
    crew = Crew(
        agents=[summarizer_agent],
        tasks=[summarizer_task],
        verbose=True
    )
    response = crew.kickoff(inputs={"file_path": file_path})
    with open(output_file, "w") as f:
        f.write(response.raw)
    return response.raw

def ai_powered_research_assistant(topic, output_file=OUTPUT_RESEARCH_ASSISTANT):
    research_crew = Crew(
        agents=[research_agent, summarizer_research_agent], # fact_checker_agent
        tasks=[research_task, summarization_task], # fact_checking_task
        process=Process.sequential,
        verbose=True
    )
    result = research_crew.kickoff(inputs={"topic": topic})
    print("\nFinal Verified Summary:\n", result)
    with open(output_file, "w") as f:
        f.write(result.raw)
    return result

if __name__ == "__main__":
    #write_article("AI Agents")
    #summarize_file(OUTPUT_TECHNICAL_WRITER_FILE)
    ai_powered_research_assistant("The impact of AI on job markets")
    
   
