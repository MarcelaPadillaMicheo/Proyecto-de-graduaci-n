#include <math.h>

// IDs de motores
#define AX_ANTE       1
#define AX_MUNE_DES   2
#define AX_MUNE_EXT   3
#define XL_PULG       4
#define XL_PULG_META  6
#define XL_INDI       5
#define XL_MEDI       7  
#define XL_ANUL       8
#define XL_MENI       9

// Registro de posición y velocidad
#define P_GOAL_POSITION    30
#define P_GOAL_SPEED       32

// Bus serial
#define DXL_BUS_SERIAL1 1
Dynamixel SERVO(DXL_BUS_SERIAL1);

// Variables de posición
int ANTE = 512;
int MUNE_DES = 512;
int MUNE_EXT = 512;
int PULG       = 500;
int PULG_META  = 500;
int INDI       = 500;
int MEDI       = 500;
int ANUL       = 500;
int MENI       = 500;

void setup() {
  SerialUSB.begin();
  SERVO.begin(3);  // 1 Mbps

  // Inicializar AX con protocolo 1.0
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_POSITION, 512); // Neutro

  // Inicializar XL con protocolo 2.0
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_POSITION, 500); // Semi abierto
}

void loop() {
  if (SerialUSB.available()) {
    char cmd = SerialUSB.read();

    // Configuración de posiciones según gesto
    switch (cmd) {
      case 'a':  // Mano abierta
        ANTE = 512;
        MUNE_DES = 200;
        MUNE_EXT = 50;

        PULG = 50;
        PULG_META = 50;
        INDI =  50;
        MEDI =  50;
        ANUL =  50;
        MENI =  50;
        break;

      case 's':  // Mano cerrada
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 700;

        PULG = 700;
        PULG_META = 700;
        INDI = 700;
        MEDI = 700;
        ANUL = 700;
        MENI = 700;
        break;

      default:
        return;
    }

    // === Mover AX ===
    word AX_Sincrono[9] = {
      AX_ANTE, round(ANTE), 100,
      AX_MUNE_DES, round(MUNE_DES), 100,
      AX_MUNE_EXT, round(MUNE_EXT), 100
    };
    SERVO.setPacketType(DXL_PACKET_TYPE1);
    SERVO.syncWrite(P_GOAL_POSITION, 2, AX_Sincrono, 9);

    // === Mover XL ===
    SERVO.setPacketType(DXL_PACKET_TYPE2);
    SERVO.writeWord(XL_PULG,      P_GOAL_POSITION, PULG);
    SERVO.writeWord(XL_PULG_META, P_GOAL_POSITION, PULG_META);
    SERVO.writeWord(XL_INDI,      P_GOAL_POSITION, INDI);
    SERVO.writeWord(XL_MEDI,      P_GOAL_POSITION, MEDI);
    SERVO.writeWord(XL_ANUL,      P_GOAL_POSITION, ANUL);
    SERVO.writeWord(XL_MENI,      P_GOAL_POSITION, MENI);
  }
}

