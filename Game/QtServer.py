width = 600
height = width
walls = []

for i in range(4):
    for j in range(4):
        a = []
        a.append(width / 4 * j)
        a.append(height / 4 * i)
        walls.append(a)
walls[0].append(2)

for j in range(16):
    print(walls[j])