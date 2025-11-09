# ==============================================================
# Programa desarrollado por Marcela Padilla
# Control de mano animatrónica con Leap Motion y comunicación serial
# ==============================================================
# Este script utiliza el sensor Leap Motion (SDK Gemini v5) para capturar 
# el movimiento y orientación de la mano derecha del usuario, 
# y envía los datos a una mano animatrónica a través de comunicación serial.
#
# La posición y orientación de la palma se traducen en valores 
# para los servos del antebrazo y muñeca (inclinación, extensión, desviación),
# mientras que la apertura de los dedos se interpreta de forma binaria (abierto/cerrado).
# Los datos se envían en un paquete de 10 bytes al microcontrolador (TinyS3 / OpenCM).
# ==============================================================

import sys, os, time, serial, math
import numpy as np

# --------------------------------------------------------------
# CONFIGURACIÓN DEL API DE LEAP MOTION
# --------------------------------------------------------------
# Se agrega la ruta del SDK Gemini para importar el módulo `leap`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# --------------------------------------------------------------
# CONFIGURACIÓN DEL PUERTO SERIAL
# --------------------------------------------------------------
# Define el puerto y la velocidad de comunicación con la mano animatrónica
SERIAL_PORT = 'COM7'
BAUD_RATE = 1000000  # velocidad alta (1 Mbps)

# Intentar abrir el puerto serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Puerto serial abierto: {SERIAL_PORT}")
except Exception as e:
    print(f"Error abriendo puerto serial: {e}")
    ser = None

# --------------------------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------------------------
def distancia(v1, v2):
    """Calcula la distancia euclidiana entre dos puntos del Leap Motion."""
    return np.linalg.norm([v1.x - v2.x, v1.y - v2.y, v1.z - v2.z])

def map_val(v, in_min, in_max, out_min, out_max):
    """Realiza un mapeo lineal del rango [in_min, in_max] a [out_min, out_max], con saturación."""
    return int(np.clip(np.interp(v, [in_min, in_max], [out_min, out_max]), out_min, out_max))

# --------------------------------------------------------------
# CLASE PRINCIPAL: PROCESAMIENTO Y ENVÍO DE DATOS
# --------------------------------------------------------------
class LeapSender:
    """Clase que interpreta los movimientos de la mano y envía un buffer serial."""
    def __init__(self):
        self.last_sent_time = 0       # tiempo del último envío
        self.last_buffer = [0] * 10   # último paquete enviado (para evitar repeticiones)

    def send_buffer(self, buffer):
        """Envía el buffer al microcontrolador si hubo un cambio y pasa el intervalo mínimo."""
        if ser:
            now = time.time()
            # Evitar enviar paquetes idénticos con alta frecuencia (menor carga serial)
            if buffer != self.last_buffer and now - self.last_sent_time > 0.08:
                ser.write(bytearray(buffer))
                self.last_sent_time = now
                self.last_buffer = buffer.copy()
                print(" Buffer enviado:", buffer)

    def on_event(self, event):
        """Procesa cada evento del Leap Motion."""
        if isinstance(event, events.TrackingEvent):
            # Analiza cada mano detectada (usamos solo la derecha)
            for hand in event.hands:
                if hand.type == enums.HandType.Right:
                    palma = hand.palm.position
                    normal = hand.palm.normal
                    direction = hand.palm.direction

                    # ----------------------------------------------------------
                    # MOVIMIENTOS DE ANTEBRAZO Y MUÑECA
                    # ----------------------------------------------------------
                    # - direction.y → inclinación del antebrazo
                    # - normal.z → desviación de muñeca (adelante/atrás)
                    # - normal.x → extensión de muñeca (izquierda/derecha)
                    ante = map_val(direction.y, -0.7, 0.7, 0, 255)
                    mune_des = map_val(normal.z, -0.7, 0.7, 0, 255)
                    mune_ext = map_val(normal.x, -0.8, 0.8, 0, 255)

                    # ----------------------------------------------------------
                    # DETECCIÓN BINARIA DE DEDOS
                    # ----------------------------------------------------------
                    # Cada dedo se considera “abierto” si la distancia entre la palma
                    # y la punta supera el umbral definido.
                    puntas = [d.bones[3].next_joint for d in hand.digits]
                    distancias = [distancia(palma, p) for p in puntas]

                    umbral = 45  # milímetros (ajustable)
                    dedos_abiertos = [1 if d > umbral else 0 for d in distancias]

                    # Asignación: [pulgar, índice, medio, anular, meñique]
                    pulg = dedos_abiertos[0]
                    pulg_meta = dedos_abiertos[0]  # meta: articulación adicional del pulgar
                    indi, medi, anul, meni = dedos_abiertos[1:5]

                    # Escalar a 8 bits (0/255) para compatibilidad con el firmware
                    dedos_byte = [x * 255 for x in [pulg, pulg_meta, indi, medi, anul, meni]]

                    # ----------------------------------------------------------
                    # CONSTRUCCIÓN DEL BUFFER A ENVIAR
                    # ----------------------------------------------------------
                    # Estructura:
                    # [255, ante, muñeca_desv, muñeca_ext, pulgar, pulgar_meta, índice, medio, anular, meñique]
                    buffer = [
                        255,                # byte de inicio
                        ante,               # antebrazo
                        mune_des,           # muñeca (desviación)
                        mune_ext,           # muñeca (extensión)
                        *dedos_byte         # valores de dedos (0 o 255)
                    ]

                    # Mensaje informativo
                    print(f"ÁNGULOS → ANTE:{ante:3d}  M_DES:{mune_des:3d}  M_EXT:{mune_ext:3d} | "
                          f"DEDO(bin) → P:{pulg} I:{indi} M:{medi} A:{anul} Me:{meni}")

                    # Enviar al microcontrolador
                    self.send_buffer(buffer)

# --------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------
def main():
    print(" Conectando con Leap Motion...")
    conn = connection.Connection()
    listener = LeapSender()
    conn.add_listener(listener)

    with conn.open():
        print("Conexión establecida. Detectando movimientos y dedos binarios... (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(0.01)
        except KeyboardInterrupt:
            # Cierre seguro del puerto serial
            if ser:
                ser.close()
            print("Programa finalizado.")

# --------------------------------------------------------------
# EJECUCIÓN DIRECTA
# --------------------------------------------------------------
if __name__ == "__main__":
    main()

