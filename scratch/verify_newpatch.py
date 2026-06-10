"""Verify the new patch has correct threshold1 and threshold2 logic."""
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

result = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'sh', '-c',
     r"grep -o 'key:\"threshold[12][^}]*}' /usr/share/grafana/public/build/5017.aaaa340b86e350c74a1f.js"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print("threshold1/threshold2 handlers in new file:")
print(result.stdout[:3000])

result2 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'sh', '-c',
     r"grep -c 'threshold2' /usr/share/grafana/public/build/5017.aaaa340b86e350c74a1f.js"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"\nthreshold2 occurrences: {result2.stdout.strip()}")

result3 = subprocess.run(
    ['docker', 'exec', 'mes_grafana', 'sh', '-c',
     r"grep -o '#E32636\|#2FD06A' /usr/share/grafana/public/build/5017.aaaa340b86e350c74a1f.js | sort | uniq -c"],
    capture_output=True, text=True, encoding='utf-8', errors='replace'
)
print(f"\nColor occurrences: {result3.stdout.strip()}")
