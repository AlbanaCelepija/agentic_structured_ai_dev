
# install ollama
curl -fsSL https://ollama.com/install.sh | sh
#ollama run llama3.2
ollama serve
ollama pull llama3.2:1b # run llama3.2 in 1b mode since it's small'
ollama run llama3.2:1b
####
ollama pull mistral:7b
ollama run mistral:7b
#### load fine tuned model
ollama create finetunedmodel -f modelfile
####### list 
ollama list
####### create model
ollama create unsloth_ft_model -f model/Modelfile


# generate response
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'


# LLM observability - Opik setup instructions
# Clone the Opik repository
git clone https://github.com/comet-ml/opik.git
# Navigate to the opik folder 
cd opik 
# Start the Opik platform
./opik.sh

# MCP server setup instructions
npx @modelcontextprotocol/inspector uv run mcp_server.py  # src/agents/coding_agents/fairness_agent
