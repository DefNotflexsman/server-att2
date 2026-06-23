import os
import re
from datetime import datetime

LOG_FILE_PATH = "logs/latest.log"
OUTPUT_REPORT_PATH = "backups/error_summary.txt"

# Keywords that indicate critical server issues
CRITICAL_KEYWORDS = [
    r"Can't keep up!",
    r"Exception in thread",
    r"OutOfMemoryError",
    r"MCON",
    r"WARN"
]

def analyze_server_logs():
    if not os.path.exists(LOG_FILE_PATH):
        print(f"Error: Log file not found at {LOG_FILE_PATH}")
        return

    os.makedirs(os.path.dirname(OUTPUT_REPORT_PATH), exist_ok=True)
    flagged_lines = []

    print("Analyzing server logs for issues...")
    
    with open(LOG_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            # Check if any error keywords match the current log line
            if any(re.search(keyword, line) for keyword in CRITICAL_KEYWORDS):
                flagged_lines.append(line.strip())

    # Write a summary file for the server administration team
    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as report_file:
        report_file.write(f"--- SERVER LOG ANALYSIS REPORT ({datetime.now()}) ---\n")
        report_file.write(f"Total issues found: {len(flagged_lines)}\n\n")
        
        if flagged_lines:
            for issue in flagged_lines:
                report_file.write(f"[FLAGGED] {issue}\n")
        else:
            report_file.write("No critical issues found in the current log file.\n")

    print(f"Analysis complete. Generated report with {len(flagged_lines)} alerts at {OUTPUT_REPORT_PATH}")

if __name__ == "__main__":
    analyze_server_logs()
