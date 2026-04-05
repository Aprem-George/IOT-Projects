import threading
import time

from arp_monitor import run_arp_monitor
from dhcp_monitor import run_dhcp_monitor
from traffic_monitor import run_traffic_monitor


def main():
    threads = []

    # Create threads for each monitor
    t1 = threading.Thread(target=run_arp_monitor, daemon=True)
    t2 = threading.Thread(target=run_dhcp_monitor, daemon=True)
    t3 = threading.Thread(target=run_traffic_monitor, daemon=True)

    threads.extend([t1, t2, t3])

    # Start all threads
    for t in threads:
        t.start()

    print("All monitors started (ARP, DHCP, Traffic)...")

    # Keep the program running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitors...")


if __name__ == "__main__":
    main()