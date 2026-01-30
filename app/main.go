package main

import (
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	errorRate  = 0
	latencyMs  = 0
	mutex      sync.Mutex
	appVersion = os.Getenv("APP_VERSION")

	httpRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Toplam HTTP istek sayisi",
		},
		[]string{"status", "version"},
	)
	httpRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "Isteklerin suresi",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"version"},
	)
)

func init() {
	if appVersion == "" {
		appVersion = "v1"
	}
	prometheus.MustRegister(httpRequestsTotal)
	prometheus.MustRegister(httpRequestDuration)
}

func main() {
	rand.Seed(time.Now().UnixNano())

	http.HandleFunc("/", handler)
	http.HandleFunc("/set-chaos", setChaosHandler)
	http.Handle("/metrics", promhttp.Handler())

	fmt.Printf("App (%s) 8080 portunda basladi...\n", appVersion)
	http.ListenAndServe(":8080", nil)
}

func handler(w http.ResponseWriter, r *http.Request) {
	timer := prometheus.NewTimer(httpRequestDuration.WithLabelValues(appVersion))
	defer timer.ObserveDuration()

	mutex.Lock()
	currentError := errorRate
	currentLatency := latencyMs
	mutex.Unlock()

	// Gecikme Simülasyonu
	if currentLatency > 0 {
		time.Sleep(time.Duration(currentLatency) * time.Millisecond)
	}

	// Hata Simülasyonu
	if rand.Intn(100) < currentError {
		httpRequestsTotal.WithLabelValues("500", appVersion).Inc()
		w.WriteHeader(http.StatusInternalServerError)
		w.Write([]byte(fmt.Sprintf("HATA! (%s) - Sunucu Cevap Veremiyor!", appVersion)))
		return
	}

	httpRequestsTotal.WithLabelValues("200", appVersion).Inc()

	bgColor := "#3498db" // Mavi (v1)
	if appVersion == "v2" {
		bgColor = "#e74c3c" // Kırmızı (v2)
	}

	html := fmt.Sprintf(`
		<html>
		<body style="background-color:%s; color:white; text-align:center; padding-top:100px; font-family:sans-serif;">
			<h1>MERHABA - %s</h1>
			<p>Sistem Stabil.</p>
			<p>Aktif Hata: %% %d | Aktif Gecikme: %d ms</p>
			<p><small>Prometheus Metrics: /metrics</small></p>
		</body>
		</html>`, bgColor, appVersion, currentError, currentLatency)

	w.Write([]byte(html))
}

func setChaosHandler(w http.ResponseWriter, r *http.Request) {
	rateStr := r.URL.Query().Get("rate")
	latencyStr := r.URL.Query().Get("latency")

	rVal, _ := strconv.Atoi(rateStr)
	lVal, _ := strconv.Atoi(latencyStr)

	mutex.Lock()
	errorRate = rVal
	latencyMs = lVal
	mutex.Unlock()

	w.Write([]byte("OK"))
}