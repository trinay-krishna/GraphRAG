import os
import requests

from dotenv import load_dotenv
load_dotenv()

from langchain.tools import tool



@tool
def fetch_subgraph_from_query( cypher_query: str ):
    """
    Executes a Cypher query against a Neo4j Aura database and retrieves
    the resulting response.

    Args:
        query (str): The Cypher query used to fetch the desired subgraph.

    Returns:
        dict: A dictionary containing:
            - status_code (int): HTTP status code of the API response.
            - json (dict): JSON data returned by the Neo4j Aura API.
    """

    AURA_URI = os.getenv("AURA_URI")

    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASS = os.getenv("NEO4J_PASS")

    payload = {
        "statement" : cypher_query
    }

    response = requests.post(
        url = AURA_URI,
        auth = ( NEO4J_USER, NEO4J_PASS ),
        json = payload
    )

    return {
        "status_code" : response.status_code,
        "json" : response.json()
    }

