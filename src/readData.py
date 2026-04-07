def parse_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    n = int(lines[0].strip())
    data = []
    for line in lines[1:n+1]:
        x, y = map(float, line.strip().split())
        data.append((x, y))
    return data

