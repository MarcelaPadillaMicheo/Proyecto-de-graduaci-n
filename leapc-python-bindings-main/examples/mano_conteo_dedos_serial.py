import sys, os, time
import numpy as np
import serial

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Configura el puerto y velocidad (ajusta COM según tu sistema)
SERIAL_PORT = 'COM13'   # Cambia esto por el puerto que esté usando OpenCM
BAUD_RATE = 115200
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Función para calcular distancia entre dos puntos 3D
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# Clase para detectar el conteo de dedos
class ContadorDedos:
    def __init__(self):
        self.ultimo_envio = ""

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]

                    # Dedos extendidos si están a más de 40 mm de la palma
                    extendidos = [1 if d > 40 else 0 for d in distancias]
                    total_dedos = sum(extendidos)

                    conteo_a_letra = {
                        1: "a",
                        2: "b",
                        3: "c",
                        4: "d",
                        5: "e",
                        0: "z"  # mano cerrada
                    }

                    letra = conteo_a_letra.get(total_dedos, "x")

                    if letra != self.ultimo_envio:
                        ser.write(letra.encode())
                        print(f"📤 Enviado a OpenCM: {letra}")
                        self.ultimo_envio = letra

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Leap Motion conectado")

    def on_error(self, error):
        print("❌ Error:", error)

# Función principal
def main():
    conn = connection.Connection()
    listener = ContadorDedos()
    conn.add_listener(listener)

    with conn.open():
        print("🟢 Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            ser.close()
            print("⏹️ Finalizado")

if __name__ == "__main__":
    main()
