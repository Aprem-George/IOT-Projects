IoT Network Anomaly Detection System

🔐 IoT Network Anomaly Detection using Raspberry Pi

A lightweight network anomaly detection system designed for IoT environments, implemented on a Raspberry Pi. The system detects ARP spoofing, DHCP/DNS manipulation, and traffic anomalies, and publishes alerts using MQTT.

📌 Overview

IoT devices typically operate on shared networks where protocols such as ARP and DHCP are unauthenticated and vulnerable. This project demonstrates how an IoT node can act as a network-aware security sensor by continuously monitoring network behaviour and detecting anomalies in real time.

🎯 Objectives

Detect ARP spoofing / MITM attacks
Identify DHCP or DNS configuration anomalies
Detect traffic bursts (e.g., scanning or DoS patterns)
Provide real-time alerts using MQTT
Implement everything using lightweight, IoT-friendly methods

🏗️ System Architecture

                +----------------------+
                |   Raspberry Pi       |
                |  (Monitoring Node)   |
                +----------+-----------+
                           |
         -----------------------------------------
         |              |              |
   ARP Monitor     DHCP Monitor   Traffic Monitor
         |              |              |
         -----------------------------------------
                           |
                    MQTT Publisher
                           |
                   Mosquitto Broker
                           |
                    MQTT Subscriber
                    (Alert Output)

⚙️ Technologies Used

Python 3
Raspberry Pi OS (Linux)
NetworkManager (nmcli)
Mosquitto MQTT Broker
MQTT (paho-mqtt)
Linux networking tools (ip, /sys/class/net)
Nmap (for traffic simulation)

📁 Project Structure

network-anomaly-detector/
│
├── main_detector.py      # Runs all monitors using threading
├── arp_monitor.py        # Detects ARP spoofing (gateway MAC change)
├── dhcp_monitor.py       # Detects DHCP/DNS anomalies via nmcli
├── traffic_monitor.py    # Detects traffic bursts using packet counters
└── README.md

🧠 Implementation Details

🔹 1. main_detector.py — Orchestration
Uses Python threading
Runs:
ARP monitor
DHCP monitor
Traffic monitor
All monitors run concurrently as daemon threads
Keeps system lightweight and continuously active

🔹 2. ARP Monitor

Identifies default gateway using:

ip route

Retrieves MAC using:

ip neigh
Stores baseline MAC
Detects changes → triggers alert

📌 Detects:

ARP spoofing
Man-in-the-middle attacks

🔹 3. DHCP / DNS Monitor

Uses:

nmcli -g IP4.ADDRESS,IP4.GATEWAY,IP4.DNS dev show wlan0
Hashes output to create baseline
Detects any change in:
IP address
Gateway
DNS servers

📌 Detects:

Rogue DHCP servers
DNS poisoning

🔹 4. Traffic Monitor

Reads packet counters from:

/sys/class/net/wlan0/statistics/
Calculates packet rate over time
Compares against threshold

📌 Detects:

Port scanning (e.g., Nmap)
Traffic bursts
Potential DoS behaviour

🔹 5. MQTT Alerting

Uses Mosquitto broker

Publishes alerts to topic:

network/alert

Example alert:

ARP anomaly detected! Gateway MAC changed...

🚀 Setup & Installation

1. Install dependencies

sudo apt update
sudo apt install python3-pip mosquitto mosquitto-clients nmap -y
sudo apt install python3-paho-mqtt -y

2. Start MQTT broker

sudo systemctl enable mosquitto
sudo systemctl start mosquitto

3. Run subscriber (for alerts)

mosquitto_sub -t network/alert

4. Run detector

python3 main_detector.py
🧪 Attack Simulation (Testing)
🔹 ARP Spoofing (Simulated)

Due to Wi-Fi/VM isolation, ARP spoofing was simulated locally:

sudo ip neigh replace <gateway_ip> lladdr 00:11:22:33:44:55 dev wlan0

Restore:

sudo ip neigh del <gateway_ip> dev wlan0
ping -c 2 <gateway_ip>

🔹 DHCP / DNS Manipulation

nmcli connection modify "preconfigured" ipv4.ignore-auto-dns yes
nmcli connection modify "preconfigured" ipv4.dns "8.8.8.8"
nmcli connection down "preconfigured"
nmcli connection up "preconfigured"

🔹 Traffic Burst (Nmap)

From another machine:

nmap -sS -p 1-1000 <raspberry_pi_ip>

OR locally:

for i in {1..200}; do ping -c 1 8.8.8.8 > /dev/null; done

📊 Results

ARP anomalies detected instantly
DHCP/DNS manipulation detected correctly
Traffic bursts detected within seconds
Minimal CPU and memory usage

⚠️ Limitations

Detection only (no automatic mitigation)
Threshold tuning required for traffic monitoring
Wi-Fi/VM environment restricted real ARP spoofing
No deep packet inspection

🔮 Future Improvements

TLS-secured MQTT communication
Machine learning-based anomaly detection
Automated response (e.g., blocking traffic)
Centralised dashboard for monitoring

🎓 Academic Context

This project was developed as part of:

Module: COM744 IoT Networks & Protocols
Assessment: Coursework 2
Focus: IoT protocols, security, and anomaly detection

📌 Key Learning Outcomes

Practical implementation of IoT network monitoring
Understanding vulnerabilities in ARP and DHCP
Use of MQTT for IoT communication
Real-world limitations of network-based attacks