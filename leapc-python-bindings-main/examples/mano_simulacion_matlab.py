import sys, os, time, socket
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Configuración UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 50010
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

class GestureSender:
    def __init__(self):
        self.last_send = ""
        self.last_time = 0

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            mensaje = ""
            for hand in event.hands:
                palma = hand.palm.position
                normal = hand.palm.normal
                puntas = [d.bones[3].next_joint for d in hand.digits]
                distancias = [distancia(palma, p) for p in puntas]
                dedos_abiertos = [d > 40 for d in distancias]
                total_abiertos = sum(dedos_abiertos)

                if hand.type == enums.HandType.Right:
                    # Gesto base
                    if total_abiertos == 5:
                        mensaje = "mano=abierta"
                    elif total_abiertos == 0:
                        mensaje = "mano=cerrada"
                    else:
                        nombres = ['pulgar', 'indice', 'medio', 'anular', 'menique']
                        estados = [f"{n}:{'abierto' if a else 'cerrado'}" for n, a in zip(nombres, dedos_abiertos)]
                        mensaje = ";".join(estados)

                    # Dirección lateral (roll)
                    if abs(normal.x) > 0.5:
                        if normal.x > 0.5:
                            mensaje += " izquierda"
                        else:
                            mensaje += " derecha"

                    # Inclinación adelante/atrás (pitch)
                    if abs(normal.z) > 0.4:
                        if normal.z > 0.4:
                            mensaje += " atras"
                        else:
                            mensaje += " adelante"
                    else:
                        mensaje += " centro"

            if mensaje and mensaje != self.last_send and time.time() - self.last_time > 0.1:
                sock.sendto(mensaje.encode(), (UDP_IP, UDP_PORT))
                print("📤 Enviado:", mensaje)
                self.last_send = mensaje
                self.last_time = time.time()

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Conectado a Leap Motion")

def main():
    conn = connection.Connection()
    listener = GestureSender()
    conn.add_listener(listener)

    with conn.open():
        print("Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.005)
        except KeyboardInterrupt:
            sock.close()
            print("Finalizado")

if __name__ == "__main__":
    main()
