import requests
import time

TARGET_URL = "https://ruby-network.net/MilitaryPanel"

def measure_response_time(email, password):
    payload = {"email": email, "password": password}
    
    # Record precise start time
    start_time = time.perf_counter()
    
    try:
        requests.post(TARGET_URL, json=payload)
    except requests.exceptions.RequestException:
        return None
        
    # Record precise end time
    end_time = time.perf_counter()
    return end_time - start_time

def audit_timing_uniformity():
    print("[*] Auditing login endpoint timing behaviors...")
    
    # Test a known valid username layout vs a completely random one
    time_known_user = measure_response_time("admin@example.local", "WrongPassword123")
    time_unknown_user = measure_response_time("doesnotexist_987@example.local", "WrongPassword123")
    
    if time_known_user is None or time_unknown_user is None:
        print("[ERROR] Audit failed: Staging server unreachable.")
        return

    print(f"[-] Known user validation time:   {time_known_user:.4f} seconds")
    print(f"[-] Unknown user validation time: {time_unknown_user:.4f} seconds")
    
    # Calculate the variance
    variance = abs(time_known_user - time_unknown_user)
    print(f"[-] Total Timing Variance:        {variance:.4f} seconds")
    
    # Safety threshold: Variance greater than 0.05 seconds may leak user existence
    if variance > 0.05:
        print("[WARNING] Significant timing variance detected. Consider adding a constant-delay or padding logic to authentication routines.")
    else:
        print("[SUCCESS] Response times are uniform. Endpoint is resilient against basic timing side-channel enumeration.")

if __name__ == "__main__":
    audit_timing_uniformity()
