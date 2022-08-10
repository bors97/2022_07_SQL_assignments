import json

with open("test.json", "w+") as f:
    try:
        data = json.load(f)
    except ValueError:
        data = {}
    print(data)
    json.dump(data, f, indent=4)