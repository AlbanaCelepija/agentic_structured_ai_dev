
from crewai import Crew
from agents import senior_technical_writer, summarizer_agent
from tasks import writing_task, summarizer_task

OUTPUT_TECHNICAL_WRITER_FILE = "output_technical_writer.md"
OUTPUT_SUMMARIZER_FILE = "output_summarizer.md"


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


if __name__ == "__main__":
    write_article("AI Agents")
    summarize_file(OUTPUT_TECHNICAL_WRITER_FILE)
    
   
