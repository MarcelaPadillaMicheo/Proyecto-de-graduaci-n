import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

class MyListener:
    def __init__(self, conn):
        self.conn = conn
        self.running = True
        self.tracking_mode = enums.TrackingMode.HMD
        self.conn.set_tracking_mode(self.tracking_mode)

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                palm = hand.palm.position
                tipo = "👉 Derecha" if hand.type == enums.HandType.Right else "👈 Izquierda"
                print(f"{tipo}: x={palm.x:.1f}, y={palm.y:.1f}, z={palm.z:.1f}")

    def on_error(self, exc):
        print(f"❌ Error en Leap: {exc}")

def main():
    conn = connection.Connection()
    listener = MyListener(conn)
    conn.add_listener(listener)

    with conn.open():
        print("✅ Conectado en modo HMD. Mueve las manos frente al sensor.\nPresiona Ctrl+C para salir.")
        try:
            while listener.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n⏹️ Finalizado.")

if __name__ == "__main__":
    main()
