// ==============================================================
// Programa desarrollado por Marcela Padilla
// Control de mano animatrónica con servomotores Dynamixel (AX y XL)
// ==============================================================
// Este código permite recibir comandos desde un computador (por puerto USB)
// y mover de forma suave una mano robótica compuesta por servos Dynamixel.
//
// El sistema recibe paquetes de 10 bytes desde un script en Python,
// que representa las posiciones del antebrazo, muñeca y dedos,
// los interpreta y genera movimientos progresivos (interpolados) 
// para cada articulación.
//
// Estructura del paquete recibido (10 bytes):
// [255, ante, mune_des, mune_ext, pulg, pulg_meta, indi, medi, anul, meni]
//
// Los tres primeros bytes (1–3) representan articulaciones AX,
// y los restantes (4–9) son dedos controlados por servos XL.
// ==============================================================

#include <math.h>
#include <stdint.h>

// --------------------------------------------------------------
// Definición de IDs de los servos Dynamixel
// --------------------------------------------------------------
#define AX_ANTE       1   // Servo del antebrazo
#define AX_MUNE_DES   2   // Servo de desviación de muñeca
#define AX_MUNE_EXT   3   // Servo de extensión de muñeca
#define XL_PULG       4   // Servo del pulgar
#define XL_PULG_META  6   // Servo metacarpiano del pulgar
#define XL_INDI       5   // Servo del índice
#define XL_MEDI       7   // Servo del medio
#define XL_ANUL       8   // Servo del anular
#define XL_MENI       9   // Servo del meñique

// --------------------------------------------------------------
// Direcciones de control en la memoria de los servos
// --------------------------------------------------------------
#define AX_TORQUE_ENABLE   24
#define AX_TORQUE_LIMIT    34
#define P_GOAL_POSITION    30
#define P_GOAL_SPEED       32
#define XL_TORQUE_ENABLE   24
#define DXL_BUS_SERIAL1    1

// Instancia del bus Dynamixel
Dynamixel SERVO(DXL_BUS_SERIAL1);

// --------------------------------------------------------------
// Límites de movimiento (posiciones abiertas/cerradas)
// --------------------------------------------------------------
#define POS_ABIERTO_XL  200
#define POS_CERRADO_XL  800
#define POS_ABIERTO_AX  200
#define POS_CERRADO_AX  800

// --------------------------------------------------------------
// Variables de posición actuales e inicialización
// --------------------------------------------------------------
int ANTE = 512, MUNE_DES = 512, MUNE_EXT = 512;
int PULG = POS_ABIERTO_XL, PULG_META = POS_ABIERTO_XL;
int INDI = POS_ABIERTO_XL, MEDI = POS_ABIERTO_XL, ANUL = POS_ABIERTO_XL, MENI = POS_ABIERTO_XL;

// Variables objetivo
int target_ANTE, target_MUNE_DES, target_MUNE_EXT;
int target_PULG, target_PULG_META, target_INDI, target_MEDI, target_ANUL, target_MENI;

// --------------------------------------------------------------
// FUNCIÓN DE CONFIGURACIÓN
// --------------------------------------------------------------
void setup() {
  SERVO.begin(3);           // Inicializa el bus Dynamixel
  SerialUSB.begin();        // Comunicación USB
  delay(1000);

  // === Configuración de los servos AX (tipo 1) ===
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeByte(AX_ANTE, AX_TORQUE_ENABLE, 1);
  SERVO.writeByte(AX_MUNE_DES, AX_TORQUE_ENABLE, 1);
  SERVO.writeByte(AX_MUNE_EXT, AX_TORQUE_ENABLE, 1);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 150);   // velocidad base
  SERVO.writeWord(BROADCAST_ID, AX_TORQUE_LIMIT, 1023);

  // === Configuración de los servos XL (tipo 2) ===
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  uint8_t ids[] = {XL_PULG, XL_PULG_META, XL_INDI, XL_MEDI, XL_ANUL, XL_MENI};
  for (int i = 0; i < 6; i++) {
    SERVO.jointMode(ids[i]);                // modo conjunto
    SERVO.writeByte(ids[i], XL_TORQUE_ENABLE, 1);  // habilitar torque
  }
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 150);

  SerialUSB.println("Mano lista. Movimiento suave habilitado.");
}

// --------------------------------------------------------------
// FUNCIÓN DE MOVIMIENTO SUAVE
// --------------------------------------------------------------
void moveSmooth(int &current, int target, int step) {
  // Interpolación simple para suavizar el movimiento hacia el objetivo
  if (abs(target - current) < step) current = target;
  else if (current < target) current += step;
  else current -= step;
}

// --------------------------------------------------------------
// BUCLE PRINCIPAL
// --------------------------------------------------------------
void loop() {
  static byte buffer[10];   // Almacena los datos recibidos del host

  // ----------------------------------------------------------
  // LECTURA DE COMANDOS DESDE EL PUERTO USB
  // ----------------------------------------------------------
  if (SerialUSB.available() >= 10) {
    for (int i = 0; i < 10; i++) buffer[i] = SerialUSB.read();

    // Verifica byte de inicio
    if (buffer[0] == 255) {
      // Mapea los 3 primeros valores (antebrazo y muñeca)
      target_ANTE     = map(buffer[1], 0, 255, POS_ABIERTO_AX, POS_CERRADO_AX);
      target_MUNE_DES = map(buffer[2], 0, 255, POS_ABIERTO_AX, POS_CERRADO_AX);
      target_MUNE_EXT = map(buffer[3], 0, 255, POS_ABIERTO_AX, POS_CERRADO_AX);

      // Detección binaria de dedos (0 = cerrado, distinto = abierto)
      target_PULG      = (buffer[4] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
      target_PULG_META = (buffer[5] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
      target_INDI      = (buffer[6] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
      target_MEDI      = (buffer[7] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
      target_ANUL      = (buffer[8] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
      target_MENI      = (buffer[9] == 0) ? POS_CERRADO_XL : POS_ABIERTO_XL;
    }
  }

  // ----------------------------------------------------------
  // MOVIMIENTO SUAVIZADO DE CADA ARTICULACIÓN
  // ----------------------------------------------------------
  int stepAX = 10;  // tamaño del paso para servos AX (más grande = más rápido)
  int stepXL = 8;   // tamaño del paso para servos XL

  moveSmooth(ANTE, target_ANTE, stepAX);
  moveSmooth(MUNE_DES, target_MUNE_DES, stepAX);
  moveSmooth(MUNE_EXT, target_MUNE_EXT, stepAX);
  moveSmooth(PULG, target_PULG, stepXL);
  moveSmooth(PULG_META, target_PULG_META, stepXL);
  moveSmooth(INDI, target_INDI, stepXL);
  moveSmooth(MEDI, target_MEDI, stepXL);
  moveSmooth(ANUL, target_ANUL, stepXL);
  moveSmooth(MENI, target_MENI, stepXL);

  // ----------------------------------------------------------
  // ENVÍO DE POSICIONES A LOS SERVOMOTORES
  // ----------------------------------------------------------
  // --- Servos AX (antebrazo y muñeca) ---
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  word AX_Sync[9] = {
    AX_ANTE, ANTE, 150,
    AX_MUNE_DES, MUNE_DES, 150,
    AX_MUNE_EXT, MUNE_EXT, 150
  };
  SERVO.syncWrite(P_GOAL_POSITION, 2, AX_Sync, 9);

  // --- Servos XL (dedos) ---
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  word XL_Sync1[9] = {
    XL_PULG, PULG, 150,
    XL_PULG_META, PULG_META, 150,
    XL_INDI, INDI, 150
  };
  word XL_Sync2[9] = {
    XL_MEDI, MEDI, 150,
    XL_ANUL, ANUL, 150,
    XL_MENI, MENI, 150
  };
  SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sync1, 9);
  SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sync2, 9);

  // Pequeña pausa para control de frecuencia (~50 Hz)
  delay(20);
}


