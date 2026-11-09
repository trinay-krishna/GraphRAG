# GraphRAG Movie Assistant

A command-line chatbot that answers questions about movies, actors, directors, producers, writers and reviews by querying a Neo4j graph database. It uses a local LLM (Ollama `llama3.2`) orchestrated with LangGraph.

## How it works

```
User question
     │
     ▼
┌──────────┐  tool call   ┌─────────────────────────────┐
│ LLM node │ ───────────▶ │ Tool node                   │
│ (Ollama) │              │  • text2cypher              │
│          │ ◀─────────── │  • fetch_subgraph_from_query│
└──────────┘  tool result └──────────────┬──────────────┘
     │                                   │
     ▼                                   ▼
  Answer                          Neo4j Aura (Movies graph)
```

1. The agent receives a question and decides which tool to call.
2. `text2cypher` converts the question into a Cypher query using the graph schema and few-shot examples.
3. `fetch_subgraph_from_query` runs the Cypher query against Neo4j Aura and returns the results.
4. The LLM turns the results into a clear answer, streamed to the terminal.

The graph follows the Neo4j Movies schema: `Person` and `Movie` nodes connected by `ACTED_IN`, `DIRECTED`, `PRODUCED`, `WROTE`, `REVIEWED` and `FOLLOWS` relationships.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | Interactive CLI entry point |
| `graph_rag.py` | LangGraph agent (LLM node, tool node, conversation memory) |
| `text2cypher.py` | Natural language → Cypher tool |
| `fetch_graph.py` | Runs Cypher queries on Neo4j Aura |
| `.env.example` | Template for environment variables |

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) with the `llama3.2` model
- A [Neo4j Aura](https://neo4j.com/cloud/aura/) instance loaded with the Movies dataset

## Installation

```bash
git clone <repo-url>
cd GraphRag1.0

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

ollama pull llama3.2
```

## Configuration

Copy the example file and fill in your values:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

| Variable | Description |
| --- | --- |
| `AURA_URI` | Neo4j Aura HTTP Query API URL |
| `NEO4J_CONNECTION_URI` | Neo4j connection URI (`neo4j+s://...`) |
| `NEO4J_USER` | Neo4j username |
| `NEO4J_PASS` | Neo4j password |
| `LANGSMITH_TRACING` | Set to `true` to enable LangSmith tracing (optional) |
| `LANGSMITH_API_KEY` | LangSmith API key (optional) |

## Usage

Make sure Ollama is running, then start the assistant:

```bash
python main.py
```

Ask questions in plain English; type `q` to quit.

```
Which actors starred in The Matrix?
Who directed the movies Tom Hanks acted in?
How many movies did Steven Spielberg direct?
Which people reviewed The Matrix and what ratings did they give?
```
