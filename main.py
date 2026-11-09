from graph_rag import chatbot

print(
    """
    Hey! I'm your Graph Database Assistant. I can help you explore movies,
    actors, directors, producers, writers, reviews, and their relationships.
    What would you like to know?
    """
)

while True:
    user_query = input()

    if user_query == "q":
        break

    chatbot( user_query = user_query, thread_id = "RAG-2" )

