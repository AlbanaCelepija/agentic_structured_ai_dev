
# install ollama
curl -fsSL https://ollama.com/install.sh | sh
#ollama run llama3.2
ollama pull llama3.2:1b # run llama3.2 in 1b mode since it's small'
ollama run llama3.2:1b


# generate response
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'