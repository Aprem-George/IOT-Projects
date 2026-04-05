import time
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
TOPIC = "network/alert"
INTERFACE = "wlan0"   # Change if needed
INTERVAL = 5          # seconds
THRESHOLD = 500       # packets per interval


def read_packet_counters():
    """
    Reads RX and TX packet counts from system interface stats.
    """
    base_path = f"/sys/class/net/{INTERFACE}/statistics"

    try:
        with open(f"{base_path}/rx_packets") as f:
            rx = int(f.read().strip())

        with open(f"{base_path}/tx_packets") as f:
            tx = int(f.read().strip())

        return rx + tx

    except Exception as e:
        print("DEBUG: Could not read interface counters:", e)
        return None


def run_traffic_monitor():
    client = mqtt.Client()
    client.connect(BROKER)

    prev = read_packet_counters()
    print(f"Traffic Monitor started on {INTERFACE}... Initial count:", prev)

    if prev is None:
        return

    while True:
        time.sleep(INTERVAL)

        current = read_packet_counters()
        if current is None:
            continue

        delta = current - prev
        prev = current

        rate = delta / INTERVAL

        if delta > THRESHOLD:
            alert = (
                f"Traffic anomaly detected! {delta} packets in {INTERVAL}s "
                f"on {INTERFACE} (~{rate:.1f} pkt/s)"
            )

            client.publish(TOPIC, alert)
            print(alert)


if __name__ == "__main__":
    run_traffic_monitor()