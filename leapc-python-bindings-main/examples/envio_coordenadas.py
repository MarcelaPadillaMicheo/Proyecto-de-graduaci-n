import sys
import os
import time
import socket

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

UDP_IP = "127.0.0.1"
UDP_PORT = 5006

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class LeapToUDP:
    def __init__(self, conn):
        self.conn = conn
        self.tracking_mode = enums.TrackingMode.HMD
        self.conn.set_tracking_mode(self.tracking_mode)

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    pos = hand.palm.position
                    msg = f"{pos.x:.2f},{pos.y:.2f},{pos.z:.2f}"
                    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
                    print(f" Enviado: {msg}")

    def on_error(self, exc):
        print(f"Error Leap: {exc}")

def main():
    conn = connection.Connection()
    listener = LeapToUDP(conn)
    conn.add_listener(listener)

    with conn.open():
        print(f" Enviando coordenadas a {UDP_IP}:{UDP_PORT}... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n Finalizado.")
            sock.close()

if __name__ == "__main__":
    main()