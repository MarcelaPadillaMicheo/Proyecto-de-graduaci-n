# ==============================================================
# Programa desarrollado por M.Sc. Miguel Zea
# Clase de comunicación TCP para el robot Pololu 3Pi+
# ==============================================================
# Esta clase implementa una interfaz de comunicación directa con el robot 
# Pololu 3Pi+ a través del protocolo TCP/IP. 
# Permite conectarse al agente físico, enviar velocidades de rueda 
# (en rpm), y detener el movimiento del robot de forma segura. 
# ==============================================================

import socket
import struct
from typing import Optional


class Pololu3Pi:
    DEFAULT_PORT = 9090           # Puerto TCP por defecto
    MAX_RPM = 400.0               # Límite superior de velocidad
    MIN_RPM = -400.0              # Límite inferior de velocidad

    def __init__(self, timeout: float = 2.0) -> None:
        """Inicializa el objeto Pololu3Pi sin conexión activa."""
        self.id: Optional[int] = None
        self.ip: Optional[str] = None
        self.port: int = self.DEFAULT_PORT
        self._sock: Optional[socket.socket] = None
        self._timeout = float(timeout)

    # ----------------------------------------------------------
    # GESTIÓN DE CONEXIÓN
    # ----------------------------------------------------------
    def connect(self, agent_id: Optional[int] = None, ip: Optional[str] = None) -> None:
        """
        Establece conexión TCP con el robot.

        Opciones:
          - Especificar agent_id (0–19) para construir la IP automáticamente.
          - O bien especificar la IP directamente.

        Lanza:
            ValueError si los parámetros son inválidos.
            OSError si la conexión falla.
        """
        if ip is not None:
            # IP proporcionada directamente
            self.ip = ip
        elif agent_id is not None:
            agent_id = int(round(agent_id))
            if agent_id < 0 or agent_id > 19:
                raise ValueError("Invalid agent ID. Allowed IDs: 0–19.")
            base = "192.168.50.1" if agent_id > 9 else "192.168.50.10"
            self.ip = f"{base}{agent_id}"
            self.id = agent_id
        else:
            raise ValueError("Must provide either agent_id or ip to connect().")

        # Crear y conectar socket TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self._timeout)
        try:
            s.connect((self.ip, self.port))
        except OSError:
            s.close()
            raise OSError(f"ERROR: Could not connect to the robot at {self.ip}:{self.port}")

        self._sock = s

    def disconnect(self) -> None:
        """Detiene el robot y cierra la conexión TCP de forma segura."""
        try:
            self.force_stop()
        except Exception:
            pass
        finally:
            if self._sock is not None:
                try:
                    self._sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self._sock.close()
                self._sock = None

    def __enter__(self):
        """Permite uso con contexto 'with'."""
        if self._sock is None:
            raise RuntimeError("Call connect() before entering context.")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()
        return False

    # ----------------------------------------------------------
    # COMANDOS DE MOVIMIENTO
    # ----------------------------------------------------------
    def set_wheel_velocities(self, dphiL_rpm: float, dphiR_rpm: float) -> None:
        """
        Envía velocidades de rueda izquierda y derecha (en rpm).

        - Limita automáticamente los valores a ±400 rpm.
        - Usa codificación CBOR mínima para envío binario.
        """
        if self._sock is None:
            raise RuntimeError("Not connected. Call connect() first.")

        L, R = float(dphiL_rpm), float(dphiR_rpm)

        # Saturación de límites
        if L > self.MAX_RPM:
            print(f"Warning: Left wheel speed saturated to {self.MAX_RPM} rpm")
            L = self.MAX_RPM
        if R > self.MAX_RPM:
            print(f"Warning: Right wheel speed saturated to {self.MAX_RPM} rpm")
            R = self.MAX_RPM
        if L < self.MIN_RPM:
            print(f"Warning: Left wheel speed saturated to {self.MIN_RPM} rpm")
            L = self.MIN_RPM
        if R < self.MIN_RPM:
            print(f"Warning: Right wheel speed saturated to {self.MIN_RPM} rpm")
            R = self.MIN_RPM

        payload = self._encode_cbor_wheel_cmd(L, R)
        self._sendall(payload)

    def force_stop(self) -> None:
        """Envía un comando de parada inmediata (velocidades = 0)."""
        if self._sock is None:
            return
        payload = self._encode_cbor_wheel_cmd(0.0, 0.0)
        self._sendall(payload)

    # ----------------------------------------------------------
    # FUNCIONES INTERNAS
    # ----------------------------------------------------------
    @staticmethod
    def _encode_cbor_wheel_cmd(left_rpm: float, right_rpm: float) -> bytes:
        """
        Codifica las velocidades en formato CBOR mínimo (array de dos floats).
        Estructura binaria: 0x82 [0xFA float(L)] [0xFA float(R)]
        """
        return b"".join([
            b"\x82",                                 # Encabezado CBOR para array de 2 elementos
            b"\xFA", struct.pack(">f", float(left_rpm)),
            b"\xFA", struct.pack(">f", float(right_rpm)),
        ])

    def _sendall(self, data: bytes) -> None:
        """Envía un bloque de datos binarios al robot."""
        try:
            self._sock.sendall(data)  # type: ignore
        except OSError as e:
            raise OSError(f"TCP send failed: {e}")
