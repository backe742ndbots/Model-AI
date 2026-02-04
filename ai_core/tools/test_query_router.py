from tools.query_router import handle_user_query

query = "show me property in rohini"



response = handle_user_query(query, limit=3)

print("Filters used:")
print(response["filters_used"])
print("\nResults:\n")

for r in response["results"]:
    print(r)
