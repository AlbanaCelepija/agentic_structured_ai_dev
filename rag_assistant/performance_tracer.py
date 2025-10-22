import os
from dotenv import load_dotenv, find_dotenv 
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from opik import configure 
from opik.integrations.langchain import OpikTracer 

configure() 
_ = load_dotenv(find_dotenv())

opik_tracer = OpikTracer(project_name="ai_engineers_agents_project") 
llm = OpenAI(
    temperature=0,
    callbacks=[opik_tracer], 
)
prompt_template = PromptTemplate(
    input_variables=["input"], template="Write a report about {input}"
)
llm_chain = prompt_template | llm
print(
    llm_chain.invoke(
        {"input": "AI engineering"},
        callbacks=[opik_tracer], 
    )
)
