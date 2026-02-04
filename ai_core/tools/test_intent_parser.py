from tools.intent_parser import parse_intent

queries = [
    "show me 2 bhk in rohini under 1.5 crore park facing",
    "need 3 bhk dwarka under 2",
    "commercial property in noida",
]

for q in queries:
    print(q)
    print(parse_intent(q))
    print("-" * 40)
