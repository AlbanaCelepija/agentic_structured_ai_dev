from openai import OpenAI

client = OpenAI(
    base_url = "http://localhost:11434/api/generate",
)

response = client.chat.completions.create(
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Why the sky is blue?",
                },
            ],
        },
    ],
    model = "llama3.2",
    max_tokens = 80000,
    temperature = 0.6,
)

print(response.choices[0].message.content)