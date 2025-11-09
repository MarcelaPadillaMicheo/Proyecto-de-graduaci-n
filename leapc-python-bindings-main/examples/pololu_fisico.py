# ==============================================================
# Programa desarrollado por Marcela Padilla
# Control del robot Pololu 3Pi+ mediante gestos con Leap Motion
# ==============================================================
# Este script conecta el sensor Leap Motion (SDK Gemini v5) con el 
# robot Pololu 3Pi+ para permitir el control directo del movimiento 
# a través de gestos de la mano.
#
# La mano derecha controla el desplazamiento (avanzar, retroceder, girar), 
# mientras que la mano izquierda abierta actúa como freno de emergencia.
# Los comandos se envían en tiempo real al Pololu mediante conexión TCP 
# utilizando la clase Pololu3Pi.
#
# Reglas de control principales:
#   - “abierta”              → avanzar recto
#   - “abierta derecha”      → avanzar con giro a la derecha
#   - “abierta izquierda”    → avanzar con giro a la izquierda
#   - “cerrada”              → retroceder recto
#   - “cerrada derecha”      → retroceder girando a la derecha
#   - “cerrada izquierda”    → retroceder girando a la izquierda
#   - “parar”                → frenar completamente
# ==============================================================

import sys, os, time
import numpy as np

# --------------------------------------------------------------
# IMPORTACIÓN DE LA CLASE DEL ROBOT
# --------------------------------------------------------------
# Asegúrate de que Pololu3Pi esté disponible en el mismo directorio o PYTHONPATH
from robot_example import Pololu3Pi

# --------------------------------------------------------------
# CONFIGURACIÓN DE LEAP MOTION (Gemini v5)
# --------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# --------------------------------------------------------------
# CONFIGURACIÓN DEL ROBOT
# --------------------------------------------------------------
USE_IP = True
ROBOT_ID = 15
ROBOT_IP = "192.168.50.115"

BASE_RPM = 70.0       # Velocidad base (ajustable)
DELTA_TURN = 40.0     # Diferencia de velocidad para giros
KEEPALIVE_S = 0.25    # Tiempo máximo entre comandos consecutivos

# --------------------------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------------------------
def distancia(v1, v2):
    """Calcula la distancia euclidiana entre dos puntos 3D del Leap Motion."""
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

def clamp_rpm(v):
    """Limita el valor de RPM dentro del rango [-999, 999] como seguridad."""
    return float(max(-999.0, min(999.0, v)))

# --------------------------------------------------------------
# MAPEOS DE GESTOS A VELOCIDADES DE RUEDA
# --------------------------------------------------------------
def gesture_to_rpms(gesto: str):
    """
    Convierte el gesto reconocido en velocidades de rueda (izquierda, derecha).
    """
    g = gesto.strip().lower()

    if g == "parar":
        return 0.0, 0.0

    # Avance
    if g == "abierta":
        return BASE_RPM, BASE_RPM
    if g == "abierta derecha":
        return clamp_rpm(BASE_RPM), clamp_rpm(BASE_RPM - DELTA_TURN)
    if g == "abierta izquierda":
        return clamp_rpm(BASE_RPM - DELTA_TURN), clamp_rpm(BASE_RPM)

    # Retroceso
    if g == "cerrada":
        return -BASE_RPM, -BASE_RPM
    if g == "cerrada derecha":
        return clamp_rpm(-BASE_RPM), clamp_rpm(-(BASE_RPM - DELTA_TURN))
    if g == "cerrada izquierda":
        return clamp_rpm(-(BASE_RPM - DELTA_TURN)), clamp_rpm(-BASE_RPM)

    # Gesto no reconocido → detener suavemente
    return 0.0, 0.0

# --------------------------------------------------------------
# CLASE PRINCIPAL: CONEXIÓN LEAP MOTION → POLOLU
# --------------------------------------------------------------
class GestureToRobot:
    """Traduce los gestos detectados por Leap Motion en comandos para el Pololu."""
    def __init__(self, robot: Pololu3Pi, max_hz=30, keepalive_s=KEEPALIVE_S):
        self.robot = robot
        self.dt_min = 1.0 / max_hz
        self.keepalive_s = keepalive_s
        self.last_send_t = 0.0
        self.last_print_t = 0.0
        self.last_gesture = ""
        self.last_cmd = (0.0, 0.0)

    def _apply_command(self, gesto):
        now = time.time()
        changed = (gesto != self.last_gesture)
        due_time = (now - self.last_send_t) >= self.dt_min
        keepalive_due = (now - self.last_send_t) >= self.keepalive_s

        if not (changed or keepalive_due):
            return

        if due_time:
            L, R = gesture_to_rpms(gesto)
            self.robot.set_wheel_velocities(L, R)
            self.last_cmd = (L, R)
            self.last_send_t = now
            self.last_gesture = gesto

            if (now - self.last_print_t) >= 1.0:
                print(f"Gesto='{gesto:>17}'  cmd=({L:.1f}, {R:.1f}) rpm")
                self.last_print_t = now

    def on_event(self, event):
        try:
            if isinstance(event, events.TrackingEvent):
                gesto = ""
                mano_izquierda_abierta = False

                for hand in event.hands:
                    palma = hand.palm.position
                    normal = hand.palm.normal
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]
                    promedio = float(np.mean(distancias))

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
                            gesto += " izquierda" if normal.x > 0 else " derecha"

                if mano_izquierda_abierta:
                    gesto = "parar"
                if gesto == "":
                    gesto = "desconocida"

                self._apply_command(gesto)

            elif isinstance(event, events.ConnectionEvent):
                print("Conexión establecida con Leap Motion")

        except Exception as e:
            print(f"[WARN] Excepción en on_event: {e}. Enviando STOP.")
            try:
                self.robot.force_stop()
            except Exception:
                pass

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------
def main():
    # Conectar al robot Pololu 3Pi+
    bot = Pololu3Pi()
    if USE_IP:
        print(f"Conectando por IP a {ROBOT_IP} ...")
        bot.connect(ip=ROBOT_IP)
    else:
        print(f"Conectando por ID a {ROBOT_ID} ...")
        bot.connect(agent_id=ROBOT_ID)

    # Inicializa Leap Motion
    conn = connection.Connection()
    listener = GestureToRobot(bot, max_hz=30, keepalive_s=KEEPALIVE_S)
    conn.add_listener(listener)

    # Bucle de operación principal
    with conn.open():
        print("Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            try:
                bot.force_stop()
            except Exception:
                pass
            bot.disconnect()
            print("Finalizado y robot detenido correctamente.")

# --------------------------------------------------------------
# EJECUCIÓN DIRECTA
# --------------------------------------------------------------
if __name__ == "__main__":
    main()


