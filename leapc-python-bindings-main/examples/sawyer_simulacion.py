# ==============================================================
# Programa desarrollado por Marcela Padilla
# Detección de gestos con Leap Motion y envío por UDP a MATLAB
# ==============================================================
# Este script utiliza el sensor Leap Motion (SDK Gemini v5) para 
# reconocer gestos de la mano y enviar los comandos detectados a MATLAB 
# mediante comunicación UDP.
#
# Reglas básicas:
#  - Mano derecha abierta         → "abierta"
#  - Mano derecha cerrada         → "cerrada"
#  - Mano derecha abierta/ cerrada + inclinación → "izquierda" o "derecha"
#  - Mano izquierda abierta       → "derecha completa" (acción especial)
#
# El programa envía los comandos solo cuando el gesto cambia.
# ==============================================================

import sys, os, time, socket
import numpy as np

# --------------------------------------------------------------
# CONFIGURACIÓN DE LEAP MOTION
# --------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# --------------------------------------------------------------
# CONFIGURACIÓN DE COMUNICACIÓN UDP
# --------------------------------------------------------------
UDP_IP = "127.0.0.1"
UDP_PORT = 50011
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR
# --------------------------------------------------------------
def distancia(v1, v2):
    """Calcula la distancia euclidiana entre dos puntos 3D."""
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# --------------------------------------------------------------
# CLASE PRINCIPAL
# --------------------------------------------------------------
class GestureAndSender:
    """Interpreta gestos del Leap Motion y los envía por UDP."""
    def __init__(self):
        self.last_gesture = ""

    def on_event(self, event):
        # Evento de rastreo de manos
        if isinstance(event, events.TrackingEvent):
            gesto = ""
            mano_izquierda_abierta = False

            for hand in event.hands:
                palma = hand.palm.position
                normal = hand.palm.normal
                puntas = [d.bones[3].next_joint for d in hand.digits]
                distancias = [distancia(palma, p) for p in puntas]
                promedio = np.mean(distancias)

                # Mano izquierda abierta → señal de acción especial
                if hand.type == enums.HandType.Left:
                    if promedio > 70:
                        mano_izquierda_abierta = True

                # Mano derecha controla gestos principales
                elif hand.type == enums.HandType.Right:
                    if promedio > 70:
                        gesto = "abierta"
                    elif promedio < 40:
                        gesto = "cerrada"
                    else:
                        gesto = "desconocida"

                    # Detección de orientación (izquierda/derecha)
                    if abs(normal.x) > 0.6:
                        if normal.x > 0:
                            gesto += " izquierda"
                        else:
                            gesto += " derecha"

            # Mano izquierda abierta sobreescribe el gesto
            if mano_izquierda_abierta:
                gesto = "derecha completa"

            # Enviar solo si hay un cambio de gesto
            if gesto != self.last_gesture and gesto != "":
                sock.sendto(gesto.encode(), (UDP_IP, UDP_PORT))
                print(f"Enviado a MATLAB: {gesto}")
                self.last_gesture = gesto

        # Evento de conexión
        elif isinstance(event, events.ConnectionEvent):
            print("Conexión establecida con Leap Motion")

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------
def main():
    conn = connection.Connection()
    listener = GestureAndSender()
    conn.add_listener(listener)

    with conn.open():
        print("Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            sock.close()
            print("Finalizado")

# --------------------------------------------------------------
# EJECUCIÓN DIRECTA
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
