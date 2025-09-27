import sys, os, time, serial
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

SERIAL_PORT = 'COM13'
BAUD_RATE = 115200
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f" Puerto serial abierto: {SERIAL_PORT}")
except Exception as e:
    print(f" Error abriendo puerto serial: {e}")
    ser = None

class GestureDetector:
    def __init__(self):
        self.last_time = 0

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma_np = np.array([hand.palm.position.x, hand.palm.position.y, hand.palm.position.z])
                    puntas = [np.array([d.bones[3].next_joint.x, d.bones[3].next_joint.y, d.bones[3].next_joint.z]) for d in hand.digits]
                    distancias = [np.linalg.norm(palma_np - p) for p in puntas]
                    dedos_ext = [1 if d > 40 else 0 for d in distancias]
                    total = sum(dedos_ext)

                    cmd = ''
                    if total == 5:
                        cmd = 'e'
                        msg = " Todos abiertos"
                    elif total == 0:
                        cmd = 'z'
                        msg = " Todos cerrados"
                    else:
                        msg = ''

                    now = time.time()
                    if cmd and (now - self.last_time > 0.1):
                        if ser: ser.write(cmd.encode())
                        print(f"📤 {msg} → Enviado: {cmd}")
                        self.last_time = now

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Conectado a Leap Motion")

def main():
    conn = connection.Connection()
    listener = GestureDetector()
    conn.add_listener(listener)

    with conn.open():
        print(" Detectando gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            if ser: ser.close()
            print(" Finalizado")

if __name__ == "__main__":
    main()