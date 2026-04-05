import time
import subprocess
import hashlib
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
TOPIC = "network/alert"
INTERFACE = "wlan0"  # Change if using Ethernet


def get_dhcp_signature():
    """
    Uses nmcli to query IPv4 configuration.
    Returns a hash + length representing current state.
    """
    cmd = f"nmcli -g IP4.ADDRESS,IP4.GATEWAY,IP4.DNS dev show {INTERFACE}"

    try:
        output = subprocess.check_output(
            cmd,
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("DEBUG: nmcli failed or interface not managed:", INTERFACE)
        return None

    output = output.strip()

    if not output:
        print("DEBUG: nmcli returned empty output")
        return None

    digest = hashlib.sha256(output.encode("utf-8")).hexdigest()
    length = len(output)

    return digest, length


def run_dhcp_monitor():
    client = mqtt.Client()
    client.connect(BROKER)

    baseline = get_dhcp_signature()
    print(f"DHCP Monitor started... Baseline: {baseline}")

    while True:
        current = get_dhcp_signature()

        if baseline is not None and current is not None and current != baseline:
            alert = (
                f"DHCP anomaly detected! IPv4 config changed: "
                f"{baseline} -> {current}"
            )

            client.publish(TOPIC, alert)
            print(alert)

            # Update baseline
            baseline = current

        time.sleep(10)


if __name__ == "__main__":
    run_dhcp_monitor()