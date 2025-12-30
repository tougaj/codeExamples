data = """
22
23
25
28
29
32
"""

existing_numbers = [int(x) for x in data.split()]

for index in range(existing_numbers[0], existing_numbers[-1]+1):
    if index in existing_numbers:
        continue
    print(index)

# total = 0
# for line in data.split():
#     h, m, s = map(int, line.split(":"))
#     total += h*3600 + m*60 + s

# print(f"{total//3600}:{(total%3600)//60:02d}:{total%60:02d}")
