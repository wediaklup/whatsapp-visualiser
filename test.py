import __init__

with open("input/shittalk/messages.txt", "r", encoding="utf-8") as f:
    x = __init__.parse(f)

for msg in x:
    print(f"{msg.author}> {msg.content}")

print(x)
