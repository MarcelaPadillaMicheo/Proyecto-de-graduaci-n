# ==============================================================
# Programa desarrollado por Marcela Padilla
# Detección de gestos con Leap Motion (modo DEBUG con archivo temporal)
# ==============================================================
# Este script utiliza el sensor Leap Motion (SDK Gemini v5) para detectar 
# gestos de la mano derecha (abierta, cerrada, abierta_derecha, etc.) 
# y controlar sistemas externos escribiendo el gesto en un archivo temporal.
#
# La mano izquierda abierta actúa como señal de “parar”.
# El programa incluye mensajes de depuración detallados (DEBUG)
# que muestran la posición, orientación y tipo de gesto detectado.
#
# El archivo temporal se crea en la carpeta TEMP del sistema operativo 
# y se actualiza constantemente con el último gesto reconocido.
# ==============================================================

import sys, os, time
import numpy as np

# --------------------------------------------------------------
# CONFIGURACIÓN DEL ENTORNO Y API DE LEAP MOTION
# --------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# --------------------------------------------------------------
# CONFIGURACIÓN DE ARCHIVO TEMPORAL (Windows)
# --------------------------------------------------------------
TEMP_FILE_PATH = os.path.join(os.environ['TEMP'], 'leap_motion_command.txt')

# --------------------------------------------------------------
# FUNCIÓN AUXILIAR: distancia entre dos puntos 3D
# --------------------------------------------------------------
def distancia(v1, v2):
    """Calcula la distancia euclidiana entre dos vectores 3D."""
    return np.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2)

# --------------------------------------------------------------
# CLASE PRINCIPAL: detección y envío de gestos
# --------------------------------------------------------------
class GestureAndSender:
    """Detecta gestos de la mano y los guarda en un archivo temporal."""
    def __init__(self):
        self.ultimo_gesto = ""
        self.ultimo_tiempo = 0
        self.frame_count = 0

    def enviar_gesto(self, gesto):
        """Escribe el gesto en el archivo temporal (modo comunicación indirecta)."""
        if not gesto:
            return

        current_time = time.time()
        # Evita escribir repetidamente el mismo gesto si no ha cambiado
        if gesto == self.ultimo_gesto and current_time - self.ultimo_tiempo < 0.1:
            return

        self.ultimo_gesto = gesto
        self.ultimo_tiempo = current_time

        try:
            with open(TEMP_FILE_PATH, 'w') as f:
                f.write(gesto)
            print(f"✓ ENVIADO: {gesto}")
        except Exception as e:
            print(f"Error escribiendo archivo: {e}")

    def on_event(self, event):
        """Procesa cada evento de rastreo del Leap Motion (con mensajes DEBUG)."""
        self.frame_count += 1

        if not isinstance(event, events.TrackingEvent):
            return

        if self.frame_count % 30 == 0:
            print(f"Frame {self.frame_count}: {len(event.hands)} manos detectadas")

        gesto_derecha = None
        mano_izquierda_parar = False

        for hand in event.hands:
            try:
                palma = hand.palm.position
                normal = hand.palm.normal

                if self.frame_count % 30 == 0:
                    print(f"  Mano {hand.type}: pos({palma.x:.1f}, {palma.y:.1f}, {palma.z:.1f})")

                # Cálculo de distancias a las puntas de los dedos
                distancias = []
                for d in hand.digits:
                    if len(d.bones) >= 4:
                        punta = d.bones[3].next_joint
                        distancias.append(distancia(palma, punta))

                if not distancias:
                    continue

                promedio = np.mean(distancias)

                if self.frame_count % 30 == 0:
                    print(f"    Distancia promedio: {promedio:.1f}")

                # Mano izquierda: comando de parada
                if hand.type == enums.HandType.Left:
                    if promedio > 70:
                        mano_izquierda_parar = True
                        if self.frame_count % 30 == 0:
                            print("    ↳ MANO IZQUIERDA: PARAR")

                # Mano derecha: control de movimiento
                elif hand.type == enums.HandType.Right:
                    if promedio > 70:
                        gesto = "abierta"
                        if self.frame_count % 30 == 0:
                            print("    ↳ MANO DERECHA: ABIERTA")
                    elif promedio < 40:
                        gesto = "cerrada"
                        if self.frame_count % 30 == 0:
                            print("    ↳ MANO DERECHA: CERRADA")
                    else:
                        continue

                    # Detección de orientación lateral (izquierda/derecha)
                    if abs(normal.x) > 0.4:
                        if normal.x < 0:
                            gesto += "_derecha"
                            if self.frame_count % 30 == 0:
                                print("    ↳ DIRECCIÓN: DERECHA")
                        else:
                            gesto += "_izquierda"
                            if self.frame_count % 30 == 0:
                                print("    ↳ DIRECCIÓN: IZQUIERDA")

                    gesto_derecha = gesto

            except Exception as e:
                print(f"Error procesando mano: {e}")

        # Decidir qué gesto enviar
        if mano_izquierda_parar:
            self.enviar_gesto("parar")
        elif gesto_derecha:
            self.enviar_gesto(gesto_derecha)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------
def main():
    print("=== Leap Motion Controller (Modo DEBUG) ===")
    print("✓ Iniciando...")

    # Limpia el archivo previo (si existía)
    try:
        if os.path.exists(TEMP_FILE_PATH):
            os.remove(TEMP_FILE_PATH)
    except:
        pass

    conn = connection.Connection()
    listener = GestureAndSender()
    conn.add_listener(listener)

    try:
        with conn.open():
            print("✓ Conexión establecida")
            print("✓ Moviendo manos frente al sensor...")
            try:
                while True:
                    time.sleep(0.01)
            except KeyboardInterrupt:
                print("\n✓ Finalizado por el usuario")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        try:
            if os.path.exists(TEMP_FILE_PATH):
                os.remove(TEMP_FILE_PATH)
        except:
            pass

# --------------------------------------------------------------
# EJECUCIÓN DIRECTA
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
