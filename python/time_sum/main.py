data = """
0:01:32
0:01:26
"""

total = 0
for line in data.split():
    h, m, s = map(int, line.split(":"))
    total += h*3600 + m*60 + s

print(f"{total//3600}:{(total%3600)//60:02d}:{total%60:02d}")
