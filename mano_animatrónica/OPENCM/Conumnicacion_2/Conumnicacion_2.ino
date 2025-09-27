//INCLCUYE MATH PARA FUNCIONES
#include<math.h>

//DEFINE EL NOMBRE Y ID DE LOS MOTORES
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





//DEFINICIONES DE REGISTROS DE POS Y VEL
#define P_GOAL_POSITION    30
#define P_GOAL_SPEED       32

//DEFINE E INICIA BUS SERIAL USART1 PARA SERVOS
#define DXL_BUS_SERIAL1 1
Dynamixel SERVO(DXL_BUS_SERIAL1);


//INICIALIZACION 
void setup(){
  
  //INICIA COMUNICACION A 1Mbps
  SERVO.begin(3);
  
  //DEFINE LOS DOS PROTOCOLOS
  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.writeWord( BROADCAST_ID,   P_GOAL_POSITION,  512 );
  SERVO.writeWord( BROADCAST_ID,   P_GOAL_SPEED,     50 );
  
  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.jointMode(1);
  SERVO.writeWord( BROADCAST_ID,   P_GOAL_POSITION,    0 );
  SERVO.writeWord( BROADCAST_ID,   P_GOAL_SPEED,     50 );
  
  ANTE = 3.41*(127)+79;
  MUNE_DES   = 3.41*(127)+79;
  MUNE_EXT   = 3.41*(127)+79;  
      
      
      //seg.circular = radio*angulo_max_servo
      //angulo_max_servo = seg.circular/radio 
      //angulo_max_servo = 22.5/30 = 0.75 rad -> 43 grad
    
      // (max_data/max_angulo)*(angulo_max_servo/ang_maz_dedo)*(angulo centrado en 127 - 127)
      //(600/90)*(buffer -127)
      // (6.6)*(buffer -127)
      
      //MAPEO A ANGULOS DEL SERVO SEGUN DEDUCCION ANTERIOR
//  PULG       = 6*(170)-127; //dos articulaciones
//  PULG_META  = 6*(160-127);
//  
//  INDI       = 7.5*(190-127)+50; 
//  MEDI       = 7*(127-127);  
//  ANUL       = 7*(190-127);
//  MENI       = 7*(190-127);
  
  PULG       = 6*(127)-127; //dos articulaciones
  PULG_META  = 6*(127-127);
  
  INDI       = 7.5*(127-127)+50; 
  MEDI       = 7*(127-127);  
  ANUL       = 7*(127-127);
  MENI       = 7*(127-127);
  
  //INCIALIZAA CON POS 0 Y VEL 0 TODOS LOS SERVOS
  //CONECTADOS EN EL MISMO BUS


  //INICIALIZA LA INTERRUPCION POR COMUNICACION SERIAL USB
  SerialUSB.attachInterrupt(usbInterrupt);
  
  delay(5000);
}
//FIN DE LA INICIALIZACION

//INICIA INTERRUPCION
void usbInterrupt(byte* buffer, byte nCount){
  //BANDERA DE INICIO DE TRANSMISION DE DATOS
  if (buffer[0] == 255){

    // (max_data/max_angulo)*(angulo centrado en 127 - 127)+(medio_data)
    // (1023/300)*(buffer -127)+ (512)
    // 3.41* buffer - 78.93

    //MAPEO A ANGULOS DEL SERVO SEGUN DEDUCCION ANTERIOR
    ANTE       = 3.41*(buffer[1])+79;
    MUNE_DES   = 3.41*(buffer[2])+79;
    MUNE_EXT   = 3.41*(buffer[3])+79;  
    
    
    //seg.circular = radio*angulo_max_servo
    //angulo_max_servo = seg.circular/radio 
    //angulo_max_servo = 22.5/30 = 0.75 rad -> 43 grad
  
    // (max_data/max_angulo)*(angulo_max_servo/ang_maz_dedo)*(angulo centrado en 127 - 127)
    //(600/90)*(buffer -127)
    // (6.6)*(buffer -127)
    
    //MAPEO A ANGULOS DEL SERVO SEGUN DEDUCCION ANTERIOR
    PULG       = 6*(buffer[4])-127; //dos articulaciones
    PULG_META  = 6*(buffer[5]-127);
    INDI       = 7.5*(buffer[6]-127)+50; 
    MEDI       = 7*(buffer[7]-127);  
    ANUL       = 7*(buffer[8]-127);
    MENI       = 7*(buffer[9]-127);
  }

}
//FIN DE INTERRUPCION

// Código de Prueba para analizar ángulos

    // (max_data/max_angulo)*(angulo centrado en 127 - 127)+(medio_data)
    // (1023/300)*(buffer -127)+ (512)
    // 3.41* buffer - 78.93

//MAPEO A ANGULOS DEL SERVO SEGUN DEDUCCION ANTERIOR


// Fin de setup

//INICIO DE LOOP
void loop(){
  

  //CREACIÓN DE LISTA PARA AX-12A
  word AX_Sincrono[9]=
  { 
    AX_ANTE,     round(ANTE),      120, 
    AX_MUNE_DES, round(MUNE_DES),  120, 
    AX_MUNE_EXT, round(MUNE_EXT),  120  }; 

  SERVO.setPacketType(DXL_PACKET_TYPE1);
  SERVO.syncWrite(30,2,AX_Sincrono,9);

    //CREACIÓN DE LISTA PARA XL-320
  word XL_Sincrono1[9]=
  { XL_PULG,       round(PULG),        200, 
    XL_PULG_META,  round(PULG_META),   200, 
    XL_INDI,       round(INDI),        200  }; 

  word XL_Sincrono2[9]=
  { XL_MEDI,   round(MEDI),  200, 
    XL_ANUL,   round(ANUL),  200,
    XL_MENI,   round(MENI),  200  }; 


  SERVO.setPacketType(DXL_PACKET_TYPE2);
  SERVO.syncWrite(30,2,XL_Sincrono1,9);
  SERVO.syncWrite(30,2,XL_Sincrono2,9);

  delay(100);

}
//FIN DE LOOP
