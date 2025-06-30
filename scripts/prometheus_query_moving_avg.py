import requests
import pandas as pd
import time
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
QUERY = 'container_cpu_usage_seconds_total'
ANOMALY_THRESHOLD = 50
INTERVAL = 30
cpu_values = []

def fetch_prometheus_metric():
    response = requests.get(PROMETHEUS_URL, params={'query': QUERY})
    result = response.json()
    if result['status'] == 'success' and result['data']['result']:
        value = float(result['data']['result'][0]['value'][1])
        return value
    else:
        print("⚠️  No data returned from Prometheus.")
        return None

def check_for_anomaly(latest_value, moving_avg):
    if moving_avg == 0:
        return False
    deviation = ((latest_value - moving_avg) / moving_avg) * 100
    return deviation > ANOMALY_THRESHOLD

def log_anomaly(value, moving_avg, deviation):
    with open("anomalies.log", "a") as logfile:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | Anomaly detected! Value: {value}, Moving Avg: {moving_avg}, Deviation: {deviation:.2f}%\n"
        logfile.write(log_entry)
    print("🚨 Anomaly detected and logged.")

def main():
    while True:
        value = fetch_prometheus_metric()
        if value is not None:
            cpu_values.append(value)
            if len(cpu_values) >= 5:
                moving_avg = pd.Series(cpu_values[-5:]).mean()
                if check_for_anomaly(value, moving_avg):
                    deviation = ((value - moving_avg) / moving_avg) * 100
                    log_anomaly(value, moving_avg, deviation)
                print(f"Value: {value}, Moving Average (5): {moving_avg:.5f}")
            else:
                print(f"Value: {value} (waiting for 5 values for Moving Average)")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
