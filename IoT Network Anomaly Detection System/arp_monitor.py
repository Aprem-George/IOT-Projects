import os
import time
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
TOPIC = "network/alert"


def get_gateway_ip():
    """
    Returns the default gateway IP using `ip route`.
    """
    with os.popen("ip route | awk '/default/ {print $3; exit}'") as f:
        gw = f.read().strip()
    return gw or None


def get_gateway_mac(gw_ip):
    """
    Returns the MAC address for the gateway IP from `ip neigh`.
    """
    if gw_ip is None:
        return None

    with os.popen("ip neigh") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.split()
        if not parts:
            continue

        ip = parts[0]
        if ip == gw_ip and "lladdr" in parts:
            return parts[parts.index("lladdr") + 1]

    return None


def run_arp_monitor():
    client = mqtt.Client()
    client.connect(BROKER)

    gateway_ip = get_gateway_ip()
    print("ARP Monitor: gateway IP =", gateway_ip)

    baseline_mac = get_gateway_mac(gateway_ip)
    print("ARP Monitor started... Baseline MAC:", baseline_mac)

    while True:
        current_mac = get_gateway_mac(gateway_ip)

        if (
            gateway_ip is not None
            and baseline_mac is not None
            and current_mac is not None
            and current_mac != baseline_mac
        ):
            alert = (
                f"ARP anomaly detected! Gateway ({gateway_ip}) MAC changed: "
                f"{baseline_mac} -> {current_mac}"
            )

            client.publish(TOPIC, alert)
            print(alert)

            # Update baseline to avoid repeated alerts
            baseline_mac = current_mac

        time.sleep(3)


if __name__ == "__main__":
    run_arp_monitor()