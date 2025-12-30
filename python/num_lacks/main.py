from pprint import pprint

data = """
28
23
25
29
32
22
"""

existing_numbers = [int(x) for x in data.split()]
min_number = min(existing_numbers)
max_number = max(existing_numbers)

print('Initial data\n'+ '-'*20)
pprint(existing_numbers)
print(f"min: {min_number}, max: {max_number}")
print()

lacks: list[int] = []
# Мінімальний та максимальний номери вже, очевидно, присутні
for index in range(min_number+1, max_number):
    if index in existing_numbers:
        continue
    lacks.append(index)

print('Lack numbers\n'+ '-'*20)
pprint(lacks)