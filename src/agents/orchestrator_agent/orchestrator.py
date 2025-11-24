import os
from dotenv import load_dotenv, find_dotenv 
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from opik import configure 
from opik.integrations.langchain import OpikTracer 

_ = load_dotenv(find_dotenv())

opik_tracer = OpikTracer() 

def ask_model(opik_tracer):    
    llm = OpenAI(
        temperature=0,
        callbacks=[opik_tracer], 
    )
    prompt_template = PromptTemplate(
        input_variables=["input"], template="Write a pipeline for {input}"
    )
    llm_chain = prompt_template | llm
    print(
        llm_chain.invoke(
            {"input": "AI solution development"},
            callbacks=[opik_tracer], 
        )
    )


def ask_for_confirmation():
    """ Human in the loop (HITL)"""
    pass





if __name__ == "__main__":
    ask_model(opik_tracer)