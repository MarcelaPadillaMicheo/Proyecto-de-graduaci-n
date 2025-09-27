import sys, os, time, socket
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Configuración UDP
UDP_IP = "127.0.0.1"
UDP_PORT = 5006
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Utilidad para calcular distancia entre 2 vectores
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

# Listener personalizado
class GestureAndSender:
    def __init__(self):
        # Inicializar posición del punto (X, Y, Z)
        self.position = [0.0, 0.0, 0.0]  # Coordenadas iniciales
        self.step = 5.0  # Incremento/decremento en Z por gesto (en mm)

    def on_event(self, event):
        if isinstance(event, events.TrackingEvent):
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]
                    promedio = np.mean(distancias)

                    if promedio > 70:
                        gesto = "ABIERTA"
                        # Mover hacia adelante (incrementar Z)
                        self.position[2] += self.step
                    elif promedio < 40:
                        gesto = "CERRADA"
                        # Mover hacia atrás (decrementar Z)
                        self.position[2] -= self.step
                    else:
                        gesto = "DESCONOCIDA"
                        # No cambiar la posición para gestos desconocidos

                    # Enviar coordenadas como "X,Y,Z"
                    message = f"{self.position[0]},{self.position[1]},{self.position[2]}"
                    sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
                    print(f"Enviado a MATLAB: {gesto}, Posición: {message}")

        elif isinstance(event, events.ConnectionEvent):
            print("🔌 Conexión establecida con Leap Motion")

def main():
    conn = connection.Connection()
    listener = GestureAndSender()
    conn.add_listener(listener)

    with conn.open():
        print("Reconociendo gestos y enviando a MATLAB (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            sock.close()
            print("Finalizado")

if __name__ == "__main__":
    main()