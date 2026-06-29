with open('git_diff.txt', 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 'AlarmIntervals' in line:
            print(f"Line {idx+1}: {line.strip()}")
