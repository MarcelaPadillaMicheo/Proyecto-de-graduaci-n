import sys, os, time
import numpy as np

# Ruta al API de Leap Motion Gemini
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'leapc-python-api', 'src')))
from leap import connection, events, enums

# Configuración para Windows - usamos archivo temporal
TEMP_FILE_PATH = os.path.join(os.environ['TEMP'], 'leap_motion_command.txt')

def distancia(v1, v2):
    return np.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2)

class GestureAndSender:
    def __init__(self):
        self.ultimo_gesto = ""
        self.ultimo_tiempo = 0
        self.frame_count = 0
        
    def enviar_gesto(self, gesto):
        """Enviar gesto escribiendo en archivo temporal"""
        if not gesto:
            return
            
        current_time = time.time()
        
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
        """Manejador de eventos con DEBUG"""
        self.frame_count += 1
        
        if not isinstance(event, events.TrackingEvent):
            return
            
        if self.frame_count % 30 == 0:  # Mostrar cada 30 frames
            print(f"Frame {self.frame_count}: {len(event.hands)} manos detectadas")
        
        gesto_derecha = None
        mano_izquierda_parar = False
        
        for hand in event.hands:
            try:
                palma = hand.palm.position
                normal = hand.palm.normal
                
                if self.frame_count % 30 == 0:
                    print(f"  Mano {hand.type}: pos({palma.x:.1f}, {palma.y:.1f}, {palma.z:.1f})")
                
                # Calcular distancia a puntas de dedos
                distancias = []
                for d in hand.digits:
                    if len(d.bones) >= 4:
                        punta = d.bones[3].next_joint
                        dist = distancia(palma, punta)
                        distancias.append(dist)
                
                if not distancias:
                    continue
                    
                promedio = np.mean(distancias)
                
                if self.frame_count % 30 == 0:
                    print(f"    Distancia promedio: {promedio:.1f}")
                
                if hand.type == enums.HandType.Left:
                    if promedio > 70:
                        mano_izquierda_parar = True
                        if self.frame_count % 30 == 0:
                            print("    ↳ MANO IZQUIERDA: PARAR")
                        
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
                    
                    # Detectar dirección
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

def main():
    print("=== Leap Motion Controller (Modo DEBUG) ===")
    print("✓ Iniciando...")
    
    # Limpiar archivo al inicio
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
                print("\n✓ Finalizado")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        try:
            if os.path.exists(TEMP_FILE_PATH):
                os.remove(TEMP_FILE_PATH)
        except:
            pass

if __name__ == "__main__":
    main()