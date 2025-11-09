# ==============================================================
# Programa desarrollado por Marcela Padilla
# Detección de gestos con Leap Motion y envío a MATLAB por UDP
# ==============================================================
# Este script utiliza el sensor Leap Motion (SDK Gemini v5) para detectar 
# gestos básicos de la mano derecha e izquierda, como “abierta”, “cerrada”, 
# “abierta izquierda”, “abierta derecha” y “parar”.
#
# Los gestos son enviados en tiempo real a MATLAB mediante comunicación UDP, 
# donde otros programas controlan agentes virtuales o robots físicos. 
# El sistema analiza la distancia promedio entre la palma y las puntas 
# de los dedos para determinar el estado de la mano, y usa la normal de 
# la palma para identificar inclinaciones hacia izquierda o derecha.
# ==============================================================

import sys, os, time, socket
import numpy as np

# --------------------------------------------------------------
# CONFIGURACIÓN DEL ENTORNO Y API DE LEAP MOTION
# --------------------------------------------------------------
# Se agrega la ruta del API de Leap Motion Gemini (v5)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# --------------------------------------------------------------
# CONFIGURACIÓN DE COMUNICACIÓN UDP (envío hacia MATLAB)
# --------------------------------------------------------------
UDP_IP = "127.0.0.1"
UDP_PORT = 50010
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR: calcula distancia entre dos puntos 3D
# --------------------------------------------------------------
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# --------------------------------------------------------------
# CLASE PRINCIPAL: detección de gestos y envío de comandos
# --------------------------------------------------------------
class GestureAndSender:
    def on_event(self, event):
        # Evento de rastreo de manos (Tracking)
        if isinstance(event, events.TrackingEvent):
            gesto = ""
            mano_izquierda_abierta = False

            # Analiza cada mano detectada
            for hand in event.hands:
                palma = hand.palm.position
                normal = hand.palm.normal
                puntas = [d.bones[3].next_joint for d in hand.digits]
                distancias = [distancia(palma, p) for p in puntas]
                promedio = np.mean(distancias)

                # Mano izquierda: usada para detener movimiento
                if hand.type == enums.HandType.Left:
                    if promedio > 70:
                        mano_izquierda_abierta = True

                # Mano derecha: controla gestos de movimiento
                elif hand.type == enums.HandType.Right:
                    if promedio > 70:
                        gesto = "abierta"
                    elif promedio < 40:
                        gesto = "cerrada"
                    else:
                        gesto = "desconocida"

                    # Orientación lateral (inclinación de la palma)
                    if abs(normal.x) > 0.6:
                        if normal.x > 0:
                            gesto += " izquierda"
                        else:
                            gesto += " derecha"

            # Si la mano izquierda está abierta, se envía el comando "parar"
            if mano_izquierda_abierta:
                gesto = "parar"

            # Envío del gesto a MATLAB
            sock.sendto(gesto.encode(), (UDP_IP, UDP_PORT))
            print(f" Enviado a MATLAB: {gesto}")

        # Evento de conexión al dispositivo Leap Motion
        elif isinstance(event, events.ConnectionEvent):
            print(" Conexión establecida con Leap Motion")

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------
def main():
    conn = connection.Connection()
    listener = GestureAndSender()
    conn.add_listener(listener)

    with conn.open():
        print(" Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.005)
        except KeyboardInterrupt:
            sock.close()
            print(" Finalizado")

# --------------------------------------------------------------
# EJECUCIÓN DEL PROGRAMA
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
