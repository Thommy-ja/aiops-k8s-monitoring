#!/bin/bash

echo "🚀 Starting Minikube cluster..."
minikube start

echo "🔗 Forwarding Prometheus API (Port 9090)..."
kubectl port-forward -n monitoring svc/prometheus-stack-kube-prom-prometheus 9090:9090 &
PROMETHEUS_PID=$!

echo "📊 Forwarding Grafana UI (Port 3000)..."
kubectl port-forward -n monitoring svc/prometheus-stack-grafana 3000:80 &
GRAFANA_PID=$!

sleep 5

echo "🖥️  Activating Python virtual environment..."
source venv/bin/activate

echo "📈 Starting anomaly detection script..."
python scripts/prometheus_query_moving_avg.py

# Nach dem Beenden des Python-Skripts
echo "🛑 Stopping Port-Forwards..."
kill $PROMETHEUS_PID
kill $GRAFANA_PID

echo "✅ Project environment stopped."
