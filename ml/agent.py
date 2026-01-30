import time
import requests
import joblib
import numpy as np
from kubernetes import client, config
import os

# AYARLAR
PROMETHEUS_URL = "http://prometheus-service:9090"
MODEL_PATH = "model.pkl"
CHECK_INTERVAL = 5

print("ML Ajani Baslatiliyor...")

# 1. MODELI YUKLE
try:
    model = joblib.load(MODEL_PATH)
    print("Model yuklendi.")
except Exception as e:
    print(f"Model hatasi: {e}")
    exit(1)

# 2. KUBERNETES BAGLANTISI
try:
    config.load_incluster_config()
    k8s_apps = client.AppsV1Api()
    print("K8s baglantisi saglandi.")
except:
    print("Uyari: K8s baglantisi yok (Localde olabilirsin). Rollback calismaz.")
    k8s_apps = None

def get_metrics():
    # Prometheus'tan verileri cek
    try:
        # Hata Orani
        err = requests.get(PROMETHEUS_URL + '/api/v1/query', params={'query': 'sum(rate(http_requests_total{status="500"}[1m]))'}).json()
        error_rate = float(err['data']['result'][0]['value'][1]) if err['data']['result'] else 0

        # Gecikme
        lat = requests.get(PROMETHEUS_URL + '/api/v1/query', params={'query': 'rate(http_request_duration_seconds_sum[1m]) / rate(http_request_duration_seconds_count[1m])'}).json()
        latency = float(lat['data']['result'][0]['value'][1]) * 1000 if lat['data']['result'] else 0

        # RPS
        rps_data = requests.get(PROMETHEUS_URL + '/api/v1/query', params={'query': 'sum(rate(http_requests_total[1m]))'}).json()
        rps = float(rps_data['data']['result'][0]['value'][1]) if rps_data['data']['result'] else 0

        # CPU (Simulasyon)
        cpu = np.random.uniform(20, 50)

        return [cpu, error_rate * 100, latency, rps]
    except:
        return None

def rollback():
    if k8s_apps:
        print("!!! ROLLBACK BASLATILIYOR !!!")
        
        patch = {"spec": {"template": {"spec": {"containers": [{"name": "app", "image": "serhatsdocker/go-app:v4"}]}}}}
        try:
            k8s_apps.patch_namespaced_deployment(name="app-deployment", namespace="default", body=patch)
            print("Rollback komutu gonderildi.")
        except Exception as e:
            print(f"Rollback hatasi: {e}")

# ANA DONGU
while True:
    data = get_metrics()
    if data:
        prediction = model.predict([data])[0]
        state = "NORMAL" if prediction == 0 else "ROLLBACK"
        print(f"Veri: {data} -> Karar: {state}")
        
        if prediction == 1:
            rollback()
            time.sleep(30) # Rollback yapinca biraz bekle
            
    time.sleep(CHECK_INTERVAL)