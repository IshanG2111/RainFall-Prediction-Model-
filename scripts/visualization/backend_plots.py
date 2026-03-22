import requests
import time
import matplotlib.pyplot as plt
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/health"
NUM_REQUESTS = 50
response_times = []
status_codes = []
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = PROJECT_ROOT / "reports" / "backend"
print("Starting API Performance Test...\n")

for i in range(NUM_REQUESTS):
    start = time.time()
    try:
        response = requests.get(BASE_URL + ENDPOINT)
        elapsed = (time.time() - start) * 1000
        response_times.append(elapsed)
        status_codes.append(response.status_code)
        print(f"Request {i+1}: {elapsed:.2f} ms | Status: {response.status_code}")
    except Exception as e:
        print(f"Request {i+1} failed: {e}")
        response_times.append(None)
        status_codes.append(None)

plt.figure()
plt.plot(range(1, NUM_REQUESTS + 1), response_times)
plt.xlabel("Request Number")
plt.ylabel("Response Time (ms)")
plt.title("API Response Time Analysis")
plt.grid()
plt.savefig(FIGURES_DIR / "api_response_time.png")
plt.show()

allowed = 0
blocked = 0
print("\nStarting Rate Limit Test...\n")
for i in range(NUM_REQUESTS):
    try:
        response = requests.get(BASE_URL + ENDPOINT)
        if response.status_code == 200:
            allowed += 1
        else:
            blocked += 1
        print(f"Burst Request {i+1}: Status {response.status_code}")
    except:
        blocked += 1

labels = ["Allowed", "Blocked"]
values = [allowed, blocked]
plt.figure()
plt.bar(labels, values)
plt.xlabel("Request Status")
plt.ylabel("Count")
plt.title(FIGURES_DIR / "API Rate Limiting Behavior")
plt.savefig("rate_limiting.png")
plt.show()
print("\nTest Completed!")