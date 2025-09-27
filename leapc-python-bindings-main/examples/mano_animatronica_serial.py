import sys, os, time, serial
import numpy as np

# Ruta al API de Leap
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# ==== CONFIGURACIÓN SERIAL ====
SERIAL_PORT = 'COM7'
BAUD_RATE = 1000000

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Puerto serial abierto: {SERIAL_PORT}")
except Exception as e:
    print(f"Error abriendo puerto serial: {e}")
    ser = None

class LeapListener:
    def __init__(self):
        self.last_sent_time = 0
        self.last_buffer = [0] * 10

    def send_buffer(self, buffer):
        if ser:
            now = time.time()
            if buffer != self.last_buffer and now - self.last_sent_time > 0.08:
                enviados = ser.write(bytearray(buffer))
                self.last_sent_time = now
                self.last_buffer = buffer.copy()
                print(" Buffer enviado:", buffer)
                if enviados != 10:
                    print("⚠️ Solo se enviaron", enviados, "bytes")

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = np.array([hand.palm.position.x,
                                      hand.palm.position.y,
                                      hand.palm.position.z])
                    puntas = [
                        np.array([d.bones[3].next_joint.x,
                                  d.bones[3].next_joint.y,
                                  d.bones[3].next_joint.z])
                        for d in hand.digits
                    ]
                    distancias = [np.linalg.norm(palma - p) for p in puntas]

                    def map_dist(d):
                        val = int(np.clip(round(np.interp(d, [20, 70], [255, 0])), 0, 255))
                        return int(round(val / 10) * 10)

                    dedos = [map_dist(d) for d in distancias]

                    buffer = [
                        255,
                        127, 127, 127,        # ANTE, MUNE_DES, MUNE_EXT
                        dedos[0],             # Pulgar
                        dedos[0],             # Pulgar meta corregido
                        dedos[1],             # Índice
                        dedos[2],             # Medio
                        dedos[3],             # Anular
                        dedos[4],             # Meñique
                    ]
                    self.send_buffer(buffer)

def main():
    print("🎯 Conectando con Leap Motion...")
    conn = connection.Connection()
    listener = LeapListener()
    conn.add_listener(listener)

    with conn.open():
        print(" Conexión establecida. Detectando gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            if ser:
                ser.close()
            print("Programa finalizado.")

if __name__ == "__main__":
    main()
