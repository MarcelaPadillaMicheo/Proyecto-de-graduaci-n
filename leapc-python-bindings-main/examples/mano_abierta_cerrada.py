import sys, os, time
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Función para calcular distancia entre dos puntos 3D
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# Clase para manejo de eventos
class GestureDetector:
    def __init__(self):
        self.last_msg = ""

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]
                    dedos_ext = [1 if d > 40 else 0 for d in distancias]
                    total = sum(dedos_ext)

                    if total == 5 and self.last_msg != "🖐️ Todos abiertos":
                        print("🖐️ Todos abiertos")
                        self.last_msg = "🖐️ Todos abiertos"
                    elif total == 0 and self.last_msg != "✊ Todos cerrados":
                        print("✊ Todos cerrados")
                        self.last_msg = "✊ Todos cerrados"
                    elif total not in [0, 5]:
                        self.last_msg = ""

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Conectado a Leap Motion")

def main():
    conn = connection.Connection()
    listener = GestureDetector()
    conn.add_listener(listener)

    with conn.open():
        print("🟢 Detectando mano abierta/cerrada... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("⏹️ Finalizado")

if __name__ == "__main__":
    main()
