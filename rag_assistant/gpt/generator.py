from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser


class Generator:
    def __init__(self, model):
        self.model = model

    def format_prompt(
        self,
        system_prompt_path="prompts/system_prompt.txt",
        user_prompt_path="prompts/user_prompt.txt",
        card_id="123",
        section="test_case",
    ):

        system_prompt = open(system_prompt_path, "r").read()
        user_prompt = open(user_prompt_path, "r").read()
        user_prompt = user_prompt.format(str(card_id), section)
        template = "{} \n {}".format(system_prompt, user_prompt)
        return template
    
    def format_prompt_codegen(
        self,
        system_prompt_path="prompts/system_prompt.txt",
        user_prompt_path="prompts/user_prompt.txt"
    ):

        system_prompt = open(system_prompt_path, "r").read()
        user_prompt = open(user_prompt_path, "r").read()
        template = "{} \n {}".format(system_prompt, user_prompt)
        return template

    def generate_response(self, question):
        template = self.format_prompt(question)
        prompt = ChatPromptTemplate.from_template(template)
        return prompt

    def generate_response_messages(
        self,
        system_prompt_path="prompts/system_prompt.txt",
        user_prompt_path="prompts/user_prompt.txt",
    ):
        system_prompt = open(system_prompt_path, "r").read()
        user_prompt = open(user_prompt_path, "r").read()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", "Write a function that {task}"),
            ]
        )
        # chain = prompt | llm
        return prompt
