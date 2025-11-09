# Proyecto de Graduación – Control e Integración Multiplataforma de Sistemas Robóticos

Este repositorio reúne todos los códigos, simulaciones y herramientas desarrolladas durante el proyecto de graduación de **Marcela Padilla Micheo** en la **Universidad del Valle de Guatemala**.  
El trabajo integra el control de múltiples robots y simulaciones, conectados mediante interfaces gestuales, Robotis, MATLAB y Python.

---

## Descripción general

El proyecto busca demostrar la integración simultánea de varios sistemas robóticos físicos y simulados, permitiendo su control a través de una **interfaz** basada en el sensor **Leap Motion Gemini v5**.  
Cada módulo está diseñado para servir como material educativo en talleres STEM.

El sistema completo incluye:

- **Pololu físico y simulado (Webots)**
- **Mano simulada en MATLAB**
- **Mano animatrónica**
- **Robot Sawyer simulado**
- **Agente Puntual**
- **Interfaces de comunicación (UDP, Serial, TCP/IP y archivos temporales)**

---

## Estructura del repositorio

| Carpeta / Archivo | Descripción |
|--------------------|-------------|
| **esfera_virtual/** | Simulación 3D del movimiento de una agente virtual controlada mediante gestos en Matlab. |
| **leapc-python-bindings-main/** | SDK adaptado del Leap Motion Gemini con ejemplos de control gestual para distintos robots. Incluye subcarpeta `examples/` con todos los scripts de integración de los códigos de Python. |
| **mano_simulada/matlab/** | Scripts MATLAB para la simulación de la mano virtual. |
| **pololu/** | Código MATLAB para controlar el robot Pololu 3Pi físico y su versión en Webots mediante comunicación UDP. |
| **robot_sawyer/** | Simulación del robot Sawyer en MATLAB. |
| **robotat_3pi_esp32_base/** | Código base para el agente Pololu con ESP32-S3. Incluye firmware y configuración de comunicación. |
| **final_animatronica_openCM.ino** | Firmware en C++ para la mano animatrónica en Robotis, que interpreta los comandos seriales enviados desde Python. |


---

## Lenguajes y plataformas utilizadas

- **Python 3.9+** (control gestual y comunicación)
- **MATLAB R2023a** (simulación y control robótico)
- **C/C++** (firmware de control en Robotis OpenCM y TinyS3)
- **Webots R2023b** (simulación física de robots)
- **Robotis Dynamixel SDK**
- **Leap Motion SDK Gemini v5**

---

## Comunicación entre módulos

| Tipo de Comunicación | Aplicación | Descripción |
|----------------------|-------------|-------------|
| **UDP** | Leap Motion -> MATLAB / Webots | Envío en tiempo real de gestos para controlar robots simulados. |
| **Serial (USB)** | Leap Motion ↔ Mano Animatrónica (OpenCM) | Control de servos Dynamixel mediante buffer de 10 bytes. |
| **TCP/IP** | Pololu 3Pi ↔ ESP32-S3 | Control directo del agente físico mediante comandos CBOR. |
| **Archivos temporales** | Leap Motion ↔ MATLAB (modo debug) | Comunicación simple por archivo de texto para pruebas locales. |

---

## Principales scripts y su función

| Script | Descripción |
|---------|--------------|
| **interfaz.py** | Interfaz principal que permite seleccionar y controlar los diferentes robots. |
| **mano_animatronica_serial.py** | Envía los movimientos detectados por Leap Motion al firmware de la mano animatrónica. |
| **Pololu3Pi.py** | Control del robot Pololu físico mediante TCP/IP. |
| **animatronica.py** | Detección de gestos y envío de comandos en modo demostrativo. |
| **mano_simulacion_matlab.m** | Simulación completa de la mano controlada por gestos. |
| **robot_sawyer_simulacion.m** | Script de control y simulación del robot Sawyer en MATLAB. |

---

## Metodología general

1. **Captura gestual:** Se utilizan los datos del Leap Motion para identificar apertura, cierre y orientación de las manos.  
2. **Procesamiento:** Los gestos se interpretan como comandos de movimiento.  
3. **Comunicación:** Los comandos se envían mediante el protocolo correspondiente a cada sistema (UDP, Serial, TCP o Archivos Temporales).  
4. **Ejecución:** Los robots o simulaciones reaccionan en tiempo real, replicando los movimientos del usuario.

---

## Resultados obtenidos

- Integración simultánea de seis sistemas robóticos en un mismo entorno.  
- Interfaz gestual fluida y precisa basada en distancia euclidiana y orientación de la palma.  
- Movimiento coordinado de una mano animatrónica con servos Dynamixel controlada por gestos.  
- Validación de funcionamiento tanto en entornos simulados (Webots, MATLAB) como físicos.  

---

## Créditos

Proyecto desarrollado por **Marcela Padilla Micheo**  
Universidad del Valle de Guatemala  
Trabajo de Graduación – Ingeniería Mecatrónica  
2025

---

