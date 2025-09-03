import json

test = list()
test.append("testA")
test.append("testB")

rand = json.dumps("test")
rand2 = json.dumps(test)
print(rand)
print(rand2)