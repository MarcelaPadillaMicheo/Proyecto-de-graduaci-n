# control_pololu_leap.py
import sys, os, time
import numpy as np

# === Importa tu clase desde tu archivo ===
# Asegúrate que robot_example.py está en el mismo folder o en el PYTHONPATH
from robot_example import Pololu3Pi

# === Leap Motion (Gemini v5) ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# ========= Configuración del robot =========
USE_IP = True
ROBOT_ID = 15
ROBOT_IP = "192.168.50.115"

BASE_RPM = 70.0       # velocidad base (ajusta a gusto)
DELTA_TURN = 40.0     # diferencia para girar (ajusta a gusto)
KEEPALIVE_S = 0.25    # re-envío periódico para “mantener” el comando

# ========= Utilidades =========
def distancia(v1, v2):
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

def clamp_rpm(v):
    # límites se vuelven a chequear dentro de Pololu3Pi, esto es por seguridad
    return float(max(-999.0, min(999.0, v)))

# ========= Mapeo gesto → velocidades =========
def gesture_to_rpms(gesto: str):
    """
    Reglas (según tu póster):
      - 'abierta'              → avanzar recto
      - 'abierta derecha'      → avanzar con giro a la derecha
      - 'abierta izquierda'    → avanzar con giro a la izquierda
      - 'cerrada'              → retroceder recto
      - 'cerrada derecha'      → retroceder con giro a la derecha
      - 'cerrada izquierda'    → retroceder con giro a la izquierda
      - 'parar'                → frenar
    """
    g = gesto.strip().lower()

    if g == "parar":
        return 0.0, 0.0

    # Avanzar (mano derecha abierta)
    if g == "abierta":
        return BASE_RPM, BASE_RPM
    if g == "abierta derecha":
        # Giro a la derecha: rueda derecha más lenta
        return clamp_rpm(BASE_RPM), clamp_rpm(BASE_RPM - DELTA_TURN)
    if g == "abierta izquierda":
        # Giro a la izquierda: rueda izquierda más lenta
        return clamp_rpm(BASE_RPM - DELTA_TURN), clamp_rpm(BASE_RPM)

    # Retroceder (mano derecha cerrada)
    if g == "cerrada":
        return -BASE_RPM, -BASE_RPM
    if g == "cerrada derecha":
        # Retrocediendo y girando a la derecha: rueda derecha más lenta (en retroceso)
        return clamp_rpm(-BASE_RPM), clamp_rpm(-(BASE_RPM - DELTA_TURN))
    if g == "cerrada izquierda":
        # Retrocediendo y girando a la izquierda
        return clamp_rpm(-(BASE_RPM - DELTA_TURN)), clamp_rpm(-BASE_RPM)

    # Gesto desconocido → mantener (None) o frenar. Aquí opto por frenar suave:
    return 0.0, 0.0

# ========= Listener de gestos que comanda al robot =========
class GestureToRobot:
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

            # imprime máx 1 vez por segundo
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
                        # FRENAR: mano izquierda abierta
                        if promedio > 70:
                            mano_izquierda_abierta = True

                    elif hand.type == enums.HandType.Right:
                        # Clasificación abierta/cerrada por apertura de dedos
                        if promedio > 70:
                            gesto = "abierta"
                        elif promedio < 40:
                            gesto = "cerrada"
                        else:
                            gesto = "desconocida"

                        # Dirección por giro de la palma (±x del normal)
                        # umbral 0.6 ≈ palma claramente girada
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
            # seguridad: si algo falla, frenamos
            print(f"[WARN] Excepción en on_event: {e}. Enviando STOP.")
            try:
                self.robot.force_stop()
            except Exception:
                pass

# ========= Main =========
def main():
    # Conecta al Pololu
    bot = Pololu3Pi()
    if USE_IP:
        print(f"Conectando por IP a {ROBOT_IP} ...")
        bot.connect(ip=ROBOT_IP)
    else:
        print(f"Conectando por ID a {ROBOT_ID} ...")
        bot.connect(rob_id=ROBOT_ID)  # ajusta el nombre del argumento si tu API usa otro

    # Listener de Leap Motion
    conn = connection.Connection()
    listener = GestureToRobot(bot, max_hz=30, keepalive_s=KEEPALIVE_S)
    conn.add_listener(listener)

    # Bucle
    with conn.open():
        print("Reconociendo gestos... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            # STOP y desconexión segura
            try:
                bot.force_stop()
            except Exception:
                pass
            bot.disconnect()
            print("Finalizado y robot detenido.")

if __name__ == "__main__":
    main()
