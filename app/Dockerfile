FROM golang:1.23-alpine AS builder
WORKDIR /app

RUN go mod init demo-app

RUN go get github.com/prometheus/client_golang/prometheus
RUN go get github.com/prometheus/client_golang/prometheus/promhttp

COPY main.go .
RUN go build -o server main.go

FROM alpine:latest
WORKDIR /root/
COPY --from=builder /app/server .
CMD ["./server"]