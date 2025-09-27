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

//INICIA VARIABLES DE RECEPCION
int ANTE       = 0;
int MUNE_DES   = 0;
int MUNE_EXT   = 0;
int PULG       = 0;
int PULG_META  = 0;
int INDI       = 0;
int MEDI       = 0;
int ANUL       = 0;
int MENI       = 0;
// Registro de posición y velocidad
#define P_GOAL_POSITION    30
#define P_GOAL_SPEED       32

// Bus serial
#define DXL_BUS_SERIAL1 1
Dynamixel SERVO(DXL_BUS_SERIAL1);



void setup() {
  SerialUSB.begin();
  SERVO.begin(3);  // 1 Mbps

  // Inicializar AX con protocolo 1.0
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_POSITION, 512);

  // Inicializar XL con protocolo 2.0
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_POSITION, 500);
}

void loop() {
  if (SerialUSB.available()) {
    char cmd = SerialUSB.read();


    switch (cmd) {
      case 'a':  // Número 1: solo índice
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 512;
        
        INDI = 50;
        PULG = 700;
        PULG_META = 700;
        MEDI = 700;
        ANUL = 700;
        MENI = 700;
        break;
      case 'b':  // Número 2: índice y medio
        INDI = 50;
        MEDI = 50;
        
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 512;

        PULG = 700;
        PULG_META = 700;
        ANUL = 700;
        MENI = 700;
        break;
      case 'c':  // Número 3: índice, medio, anular
        INDI = 50;
        MEDI = 50;
        ANUL = 50;
        
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 512;

        PULG = 700;
        PULG_META = 700;
        MENI = 700;
        break;
      case 'd':  // Número 4: sin pulgar
        INDI = 50;
        MEDI = 50;
        ANUL = 50;
        MENI = 50;
        
        
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 512;

        PULG = 700;
        PULG_META = 700;
        break;
      case 'e':  // Número 5: todos los dedos abiertos
        ANTE = 512;
        MUNE_DES = 512;
        MUNE_EXT = 512;

        PULG = 50;
        PULG_META = 50;
        INDI = 50;
        MEDI = 50;
        ANUL = 50;
        MENI = 50;

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

