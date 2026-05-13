# AI-assisted structured and compliant AI development lifecycle

In this repo we propose a structured framework that enables the operationalisation of system-wide objectives throughout the various phases of the AI lifecycle, while systematically leveraging existing open source toolkits.
The framework implementation is based on AI agents that contribute to different planning and implementation aspects.


The project  contributes to the development phase of an AI product and act as an AI-assisted AI development system that helps AI practitioners scaffold an AI product with the necessary extension points to address the requirements of an AI-enabled system

## Key Capabilities

- **High-Quality Content Retrieval**: Search and retrieve relevant content from open-source toolkit official documentation
- **Code Sample Discovery**: Find  toolkit code snippets and examples .
- **Real-time Updates**: Access the latest documentation as it's published.

## Supported Tools

| Tool Name | Description | Input Parameters |
|-----------|-------------|------------------|
| `tai_mlops_docs_search` | Performs semantic search against open source trustworthy AI toolkits official technical documentation | `query` (string): The search query for retrieval |
| `tai_mlops_code_sample_search` | Search for official toolkits code snippets and examples | `query` (string): Search query for  code snippets<br/>|


## Features of the TAI Engineers agentic system

- we use prompt versioning, using Opik as a tool for Agents observability.
- we use LangGraph for reasoning, tools and multi-step reasoning workflows
