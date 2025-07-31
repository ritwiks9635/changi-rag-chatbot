import time
from app.chatbot import answer_user_query
from app.vector_store import retrieve_relevant_docs
start_time = time.time()
query = "Can a pet be brought on a flight from Changi?"
#results = retrieve_relevant_docs(query)
results = answer_user_query(query)
end_time = time.time()
print(results)
print(f"Execution time: {end_time - start_time:.2f} seconds")