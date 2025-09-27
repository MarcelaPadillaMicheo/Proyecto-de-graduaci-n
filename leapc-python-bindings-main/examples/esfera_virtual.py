import sys, os, time, socket
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap  import connection, events, enums

# Configuración UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 50010
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

class GestureAndSender:
    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            gesto = ""
            mano_izquierda_abierta = False

            for hand in event.hands:
                palma = hand.palm.position
                normal = hand.palm.normal
                puntas = [d.bones[3].next_joint for d in hand.digits]
                distancias = [distancia(palma, p) for p in puntas]
                promedio = np.mean(distancias)

                if hand.type == enums.HandType.Left:
                    if promedio > 70:
                        mano_izquierda_abierta = True

                elif hand.type == enums.HandType.Right:
                    if promedio > 70:
                        gesto = "abierta"
                    elif promedio < 40:
                        gesto = "cerrada"
                    else:
                        gesto = "desconocida"

                    if abs(normal.x) > 0.6:
                        if normal.x > 0:
                            gesto += " izquierda"
                        else:
                            gesto += " derecha"

            if mano_izquierda_abierta:
                gesto = "parar"

            sock.sendto(gesto.encode(), (UDP_IP, UDP_PORT))
            print(f" Enviado a MATLAB: {gesto}")

        elif isinstance(event, events.ConnectionEvent):
            print(" Conexión establePcida con Leap Motion")

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

if __name__ == "__main__":
    main()

