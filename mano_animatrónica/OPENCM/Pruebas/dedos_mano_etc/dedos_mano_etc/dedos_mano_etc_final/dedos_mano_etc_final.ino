#include <math.h>

// ===== IDs =====
#define AX_ANTE       1
#define AX_MUNE_DES   2
#define AX_MUNE_EXT   3
#define XL_PULG       4
#define XL_PULG_META  6
#define XL_INDI       5
#define XL_MEDI       7
#define XL_ANUL       8
#define XL_MENI       9

// ===== Variables objetivo =====
int ANTE = 0, MUNE_DES = 0, MUNE_EXT = 0;
int PULG = 0, PULG_META = 0, INDI = 0, MEDI = 0, ANUL = 0, MENI = 0;

// ===== Control Table =====
// AX-12A
#define AX_TORQUE_ENABLE   24
#define AX_TORQUE_LIMIT    34
#define P_GOAL_POSITION    30
#define P_GOAL_SPEED       32

// XL-320 (control table v2)
#define XL_TORQUE_ENABLE   24
#define DXL_BUS_SERIAL1    1

Dynamixel SERVO(DXL_BUS_SERIAL1);

// ===== Utilidad de mapeo =====
inline int map_u8_to_xl_pos(int u8)
{
  // 0..255 → 200..800
  int v = 200 + (u8 * 600) / 255;
  if (v < 200) v = 200;
  if (v > 800) v = 800;
  return v;
}

void setup() {
  // 1 Mbps (index 3 en Robotis lib)
  SERVO.begin(3);

  // ===== AX-12A (Packet 1) =====
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeByte(AX_ANTE,     AX_TORQUE_ENABLE, 1);
  SERVO.writeByte(AX_MUNE_DES, AX_TORQUE_ENABLE, 1);
  SERVO.writeByte(AX_MUNE_EXT, AX_TORQUE_ENABLE, 1);

  // Velocidad y torque limit altos para pruebas
  SERVO.writeWord(BROADCAST_ID, P_GOAL_SPEED, 600);
  SERVO.writeWord(BROADCAST_ID, AX_TORQUE_LIMIT, 1023);

  // Posición neutral inicial (aprox. mapeo de 127)
  ANTE     = constrain(int(3.41 * 127 + 79), 0, 1023);
  MUNE_DES = ANTE;
  MUNE_EXT = ANTE;

  // ===== XL-320 (Packet 2) =====
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.jointMode(XL_PULG);
  SERVO.jointMode(XL_PULG_META);
  SERVO.jointMode(XL_INDI);
  SERVO.jointMode(XL_MEDI);
  SERVO.jointMode(XL_ANUL);
  SERVO.jointMode(XL_MENI);

  SERVO.writeByte(XL_PULG,      XL_TORQUE_ENABLE, 1);
  SERVO.writeByte(XL_PULG_META, XL_TORQUE_ENABLE, 1);
  SERVO.writeByte(XL_INDI,      XL_TORQUE_ENABLE, 1);
  SERVO.writeByte(XL_MEDI,      XL_TORQUE_ENABLE, 1);
  SERVO.writeByte(XL_ANUL,      XL_TORQUE_ENABLE, 1);
  SERVO.writeByte(XL_MENI,      XL_TORQUE_ENABLE, 1);

  // Posición inicial segura (media)
  PULG = PULG_META = INDI = MEDI = ANUL = MENI = 500;

  // Inicializa puerto serie USB
  SerialUSB.begin();
  delay(1000);
}

void loop() {
  // ===== LECTURA USB =====
  static byte buffer[10];

  if (SerialUSB.available() >= 10) {
    for (int i = 0; i < 10; i++) {
      buffer[i] = SerialUSB.read();
    }

    if (buffer[0] == 255) { // encabezado válido
      // AX (0..1023)
      ANTE     = constrain(int(3.41 * buffer[1] + 79), 0, 1023);
      MUNE_DES = constrain(int(3.41 * buffer[2] + 79), 0, 1023);
      MUNE_EXT = constrain(int(3.41 * buffer[3] + 79), 0, 1023);

      // XL (200..800)
      PULG      = map_u8_to_xl_pos(buffer[4]);
      PULG_META = map_u8_to_xl_pos(buffer[5]);
      INDI      = map_u8_to_xl_pos(buffer[6]);
      MEDI      = map_u8_to_xl_pos(buffer[7]);
      ANUL      = map_u8_to_xl_pos(buffer[8]);
      MENI      = map_u8_to_xl_pos(buffer[9]);
    }
  }

  // ===== AX-12A (packet 1) =====
  word AX_Sincrono[9] = {
    AX_ANTE,     (word)round(ANTE),     600,
    AX_MUNE_DES, (word)round(MUNE_DES), 600,
    AX_MUNE_EXT, (word)round(MUNE_EXT), 600
  };
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.syncWrite(P_GOAL_POSITION, 2, AX_Sincrono, 9);

  // ===== XL-320 (packet 2) =====
  word XL_Sincrono1[9] = {
    XL_PULG,      (word)round(PULG),      600,
    XL_PULG_META, (word)round(PULG_META), 600,
    XL_INDI,      (word)round(INDI),      600
  };
  word XL_Sincrono2[9] = {
    XL_MEDI, (word)round(MEDI), 600,
    XL_ANUL, (word)round(ANUL), 600,
    XL_MENI, (word)round(MENI), 600
  };

  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sincrono1, 9);
  SERVO.syncWrite(P_GOAL_POSITION, 2, XL_Sincrono2, 9);

  delay(30);  // más reactivo
}

