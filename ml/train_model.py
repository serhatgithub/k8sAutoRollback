import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. AYARLAR
NORMAL_SAMPLES = 2000
ANOMALY_SAMPLES = 2000

print("Veri uretimi basladi...")

# 2. SENTETIK VERI URETIMI
def generate_data():
    
    norm_cpu = np.random.uniform(10, 60, NORMAL_SAMPLES)
    norm_err = np.random.uniform(0, 1, NORMAL_SAMPLES)
    norm_lat = np.random.uniform(20, 200, NORMAL_SAMPLES)
    norm_rps = np.random.uniform(50, 500, NORMAL_SAMPLES)
    X_norm = np.column_stack((norm_cpu, norm_err, norm_lat, norm_rps))
    y_norm = np.zeros(NORMAL_SAMPLES)

    err_cpu = np.random.uniform(20, 80, ANOMALY_SAMPLES // 2)
    err_err = np.random.uniform(5, 50, ANOMALY_SAMPLES // 2)
    err_lat = np.random.uniform(50, 300, ANOMALY_SAMPLES // 2)
    err_rps = np.random.uniform(100, 500, ANOMALY_SAMPLES // 2)
    X_err = np.column_stack((err_cpu, err_err, err_lat, err_rps))
    y_err = np.ones(ANOMALY_SAMPLES // 2)

    lat_cpu = np.random.uniform(50, 95, ANOMALY_SAMPLES // 2)
    lat_err = np.random.uniform(0, 2, ANOMALY_SAMPLES // 2)
    lat_lat = np.random.uniform(2000, 8000, ANOMALY_SAMPLES // 2)
    lat_rps = np.random.uniform(200, 800, ANOMALY_SAMPLES // 2)
    X_lat = np.column_stack((lat_cpu, lat_err, lat_lat, lat_rps))
    y_lat = np.ones(ANOMALY_SAMPLES // 2)

    # Birlestir
    X = np.vstack((X_norm, X_err, X_lat))
    y = np.hstack((y_norm, y_err, y_lat))
    return X, y

# 3. EGITIM
X, y = generate_data()
print("Model egitiliyor (Random Forest)...")

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

# 4. KAYDET
joblib.dump(clf, 'model.pkl')
print("Tamamlandi. model.pkl dosyasi olusturuldu.") 