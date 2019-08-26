import uuid

name = "test_name"
namespace = "test_namespace"

print(len(str(uuid.uuid1()).replace('-','')))
# print(uuid.uuid3(namespace,name))
print(uuid.uuid4())
# print(uuid.uuid5(namespace,name))