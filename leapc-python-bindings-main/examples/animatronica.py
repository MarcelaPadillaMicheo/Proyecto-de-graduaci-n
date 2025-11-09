import sys, os, time, serial, math
import numpy as np

# ==== Ruta al API de Leap Motion Gemini ====
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


# ==== FUNCIONES AUXILIARES ====
def distancia(v1, v2):
    """Distancia euclidiana entre dos puntos Leap."""
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

def map_val(v, in_min, in_max, out_min, out_max):
    """Mapeo lineal limitado."""
    return int(np.clip(np.interp(v, [in_min, in_max], [out_min, out_max]), out_min, out_max))


# ==== CLASE PRINCIPAL ====
class LeapSender:
    def __init__(self):
        self.last_sent_time = 0
        self.last_buffer = [0] * 10

    def send_buffer(self, buffer):
        if ser:
            now = time.time()
            if buffer != self.last_buffer and now - self.last_sent_time > 0.08:
                ser.write(bytearray(buffer))
                self.last_sent_time = now
                self.last_buffer = buffer.copy()
                print(" Buffer enviado:", buffer)

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    normal = hand.palm.normal
                    direction = hand.palm.direction

                    # === Movimientos de antebrazo y muñeca ===
                    ante = map_val(direction.y, -0.7, 0.7, 0, 255)
                    mune_des = map_val(normal.z, -0.7, 0.7, 0, 255)

                    mune_ext = map_val(normal.x, -0.8, 0.8, 0, 255)

                    # === Detección binaria de dedos ===
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]

                    # Umbral de apertura (ajustable)
                    umbral = 45  # mm

                    dedos_abiertos = [1 if d > umbral else 0 for d in distancias]

                    pulg = dedos_abiertos[0]
                    pulg_meta = dedos_abiertos[0]
                    indi, medi, anul, meni = dedos_abiertos[1:5]

                    # Escalar 0/1 a 0/255 si querés seguir usando el firmware igual
                    dedos_byte = [x * 255 for x in [pulg, pulg_meta, indi, medi, anul, meni]]

                    # === Buffer a enviar ===
                    buffer = [
                        255,
                        ante, mune_des, mune_ext,
                        *dedos_byte
                    ]

                    print(f"ÁNGULOS → ANTE:{ante:3d}  M_DES:{mune_des:3d}  M_EXT:{mune_ext:3d} | "
                          f"DEDO(bin) → P:{pulg} I:{indi} M:{medi} A:{anul} Me:{meni}")
                    self.send_buffer(buffer)


# ==== MAIN ====
def main():
    print(" Conectando con Leap Motion...")
    conn = connection.Connection()
    listener = LeapSender()
    conn.add_listener(listener)

    with conn.open():
        print("Conexión establecida. Detectando movimientos y dedos binarios... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            if ser:
                ser.close()
            print("Programa finalizado.")


if __name__ == "__main__":
    main()
