from tools.property_tool import search_properties

results = search_properties(
    city="ROHINI",
    bhk=2,
    max_price=1.5,
    limit=5
)

for r in results:
    print(r)
