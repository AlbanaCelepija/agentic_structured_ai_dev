from langchain_ollama import ChatOllama

os.environ["OPIK_PROJECT_NAME"] = "ai_engineers_agents_project"
opik.configure(use_local=True)
opik_tracer = OpikTracer(tags=["langchain", "ollama"])


class CodeGenerator:
    def __init__(self, model):
        self.llm = ChatOllama(
            model=model,
            temperature=0.7,
        ).with_config({"callbacks": [opik_tracer]})

    def generate_code(self, user_prompt, system_prompt):
        messages = [
            (
                "system",
                system_prompt,
            ),
            (
                "human",
                user_prompt,
            ),
        ]
        ai_msg = self.llm.invoke(messages)
        logger.info("Message from model: " + ai_msg.content)
        return ai_msg.content


async def expand_query(query: str) -> str:
    """Expand brief query into detailed version"""
    system_prompt = """You are a query expansion assistant.  
Take brief user queries and expand them into more detailed versions that:
1. Add relevant context and clarifications
2. Include related terminology and concepts
3. Specify what aspects should be covered
4. Maintain the original intent
5. Keep it as a single, coherent question
Expand the query to be 2-3x more detailed while staying focused."""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Expand this query: {query}"}
        ],
        temperature=0.3
    )
  
    return response.choices[0].message.content.strip()