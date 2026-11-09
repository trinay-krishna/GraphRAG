from dotenv import load_dotenv
load_dotenv()

from llm import invoke_llm
from fetch_graph import fetch_subgraph_from_query

response = invoke_llm("How are you?")

subgraph_response = fetch_subgraph_from_query("MATCH (n:Person) RETURN n LIMIT 25;")

print(subgraph_response)
