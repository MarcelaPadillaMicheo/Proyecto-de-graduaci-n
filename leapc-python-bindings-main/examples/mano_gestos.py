import sys, os, time, serial
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Configuración Serial
SERIAL_PORT = 'COM13'  # Asegúrate que sea el correcto
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
print(f"✅ Puerto abierto correctamente: {SERIAL_PORT}")

# Función para calcular distancia entre dos puntos 3D
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# Clase para manejo de eventos y envío serial
class GestureAndSender:
    def __init__(self):
        self.last_cmd = ""

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    normal = hand.palm.normal

                    # Calcular distancias entre palma y puntas de dedos
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]
                    promedio = np.mean(distancias)

                    # Gesto base por apertura
                    if promedio > 70:
                        cmd = 'a'  # Mano abierta
                    elif promedio < 40:
                        cmd = 's'  # Mano cerrada
                    else:
                        cmd = 'd'  # Neutral / Reposo

                    # Solo enviar si el comando cambió
                    if cmd != self.last_cmd:
                        ser.write(cmd.encode())
                        print(f"📤 Enviado a OpenCM: {cmd}")
                        self.last_cmd = cmd

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Conectado a Leap Motion")

    def on_error(self, error):
        print("❌ Error Leap Motion:", error)

def main():
    conn = connection.Connection()
    listener = GestureAndSender()
    conn.add_listener(listener)

    with conn.open():
        print("🟢 Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.02)
        except KeyboardInterrupt:
            ser.close()
            print("⏹️ Finalizado")

if __name__ == "__main__":
    main()
