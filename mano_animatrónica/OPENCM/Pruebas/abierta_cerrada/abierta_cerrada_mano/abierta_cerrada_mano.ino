#include <math.h>

// IDs
#define AX_ANTE       1
#define AX_MUNE_DES   2
#define AX_MUNE_EXT   3
#define XL_PULG       4
#define XL_PULG_META  6
#define XL_INDI       5
#define XL_MEDI       7  
#define XL_ANUL       8
#define XL_MENI       9

// Registro
#define P_GOAL_POSITION 30
#define P_GOAL_SPEED    32

#define DXL_BUS_SERIAL1 1
Dynamixel SERVO(DXL_BUS_SERIAL1);

// Posiciones
int ANTE = 512, MUNE_DES = 512, MUNE_EXT = 512;
int PULG = 500, PULG_META = 500, INDI = 500, MEDI = 500, ANUL = 500, MENI = 500;

void setup() {
  SerialUSB.begin();
  SERVO.begin(3);

  // AX protocolo 1.0
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);

  // XL protocolo 2.0
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 100);

  SerialUSB.println("Presiona 'e' para abrir, 'z' para cerrar la mano.");
}

void loop() {
  if (SerialUSB.available()) {
    char cmd = SerialUSB.read();

    switch (cmd) {
      case 'e':  // Abrir
        ANTE = MUNE_DES = MUNE_EXT = 512;
        PULG = 250;
        PULG_META = 250;
        INDI = 300;
        MEDI = 300;
        ANUL = 300;
        MENI = 300;
        break;

      case 'z':  // Cerrar
        ANTE = MUNE_DES = MUNE_EXT = 512;
        PULG = 700;
        PULG_META = 700;
        INDI = 750;
        MEDI = 750;
        ANUL = 750;
        MENI = 750;
        break;

      default:
        return;
    }

    // Enviar a AX
    word AX_Sync[9] = {
      AX_ANTE, round(ANTE), 100,
      AX_MUNE_DES, round(MUNE_DES), 100,
      AX_MUNE_EXT, round(MUNE_EXT), 100
    };
    SERVO.setPacketType(DXL_PACKET_TYPE1);
    SERVO.syncWrite(P_GOAL_POSITION, 2, AX_Sync, 9);

    // Enviar a XL
    word XL_Sync1[9] = {
      XL_PULG, round(PULG), 100,
      XL_PULG_META, round(PULG_META), 100,
      XL_INDI, round(INDI), 100
    };
    word XL_Sync2[9] = {
      XL_MEDI, round(MEDI), 100,
      XL_ANUL, round(ANUL), 100,
      XL_MENI, round(MENI), 100
    };
    SERVO.setPacketType(DXL_PACKET_TYPE2);
    SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sync1, 9);
    SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sync2, 9);
  }
}

