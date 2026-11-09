import os

from dotenv import load_dotenv
load_dotenv()

from neo4j import GraphDatabase

from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.llm import OllamaLLM

from neo4j_graphrag.types import RetrieverResult

from langchain.tools import tool


URI = os.getenv("NEO4J_CONNECTION_URI")
AUTH = (
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASS")
)

driver = GraphDatabase.driver( URI, auth = AUTH )

llm = OllamaLLM("llama3.2")

neo4j_schema = """
NODE LABELS:
1. Person
   Properties:
   - name: STRING (unique, indexed)
   - born: INTEGER

2. Movie
   Properties:
   - title: STRING (unique, indexed)
   - tagline: STRING
   - released: INTEGER

RELATIONSHIPS:
1. (Person)-[:ACTED_IN {roles: LIST}]->(Movie)

2. (Person)-[:DIRECTED]->(Movie)

3. (Person)-[:PRODUCED]->(Movie)

4. (Person)-[:WROTE]->(Movie)

5. (Person)-[:REVIEWED {
       rating: INTEGER,
       summary: STRING
   }]->(Movie)

6. (Person)-[:FOLLOWS]->(Person)
"""

examples = [
    "USER INPUT: 'Which actors starred in The Matrix?' QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE m.title = 'The Matrix' RETURN p.name",

    "USER INPUT: 'Who directed The Matrix?' QUERY: MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE m.title = 'The Matrix' RETURN p.name",

    "USER INPUT: 'Which movies did Tom Hanks act in?' QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie) WHERE p.name = 'Tom Hanks' RETURN m.title",

    "USER INPUT: 'Who directed the movies Tom Hanks acted in?' QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(d:Person) WHERE p.name = 'Tom Hanks' RETURN DISTINCT d.name, m.title",

    "USER INPUT: 'Which actors acted alongside Keanu Reeves?' QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(coActor:Person) WHERE p.name = 'Keanu Reeves' AND coActor <> p RETURN DISTINCT coActor.name, m.title",

    "USER INPUT: 'How many movies did Steven Spielberg direct?' QUERY: MATCH (p:Person)-[:DIRECTED]->(m:Movie) WHERE p.name = 'Steven Spielberg' RETURN COUNT(m) AS movie_count",

    "USER INPUT: 'Which people reviewed The Matrix and what ratings did they give?' QUERY: MATCH (p:Person)-[r:REVIEWED]->(m:Movie) WHERE m.title = 'The Matrix' RETURN p.name, r.rating, r.summary",

    "USER INPUT: 'Which movies were produced by Jerry Bruckheimer?' QUERY: MATCH (p:Person)-[:PRODUCED]->(m:Movie) WHERE p.name = 'Jerry Bruckheimer' RETURN m.title",

    "USER INPUT: 'Which people follow Tom Hanks?' QUERY: MATCH (p:Person)-[:FOLLOWS]->(target:Person) WHERE target.name = 'Tom Hanks' RETURN p.name",

    "USER INPUT: 'Find all movies released after 2000.' QUERY: MATCH (m:Movie) WHERE m.released > 2000 RETURN m.title, m.released ORDER BY m.released",

    "USER INPUT: 'Who acted in and directed the same movie?' QUERY: MATCH (p:Person)-[:ACTED_IN]->(m:Movie)<-[:DIRECTED]-(p) RETURN DISTINCT p.name, m.title"
]

retriever = Text2CypherRetriever(
    driver = driver,
    llm = llm,
    neo4j_schema = neo4j_schema,
    examples = examples
)

@tool
def text2cypher( user_query: str )  -> RetrieverResult:
    """
    Generates a Cypher query from a natural language user query.

    Args:
        user_query (str): The user's natural language question.

    Returns:
        str: The generated Cypher query.
    """

    result = retriever.search(
        query_text = user_query 
    )

    return result.metadata["cypher"] 



