import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import signal
import sys

ventana = tk.Tk()
ventana.title("Control de Robots con Leap Motion")
ventana.configure(bg="#79BC90")
ventana.attributes("-fullscreen", True)

ruta_base = os.path.dirname(os.path.abspath(__file__))
carpeta_imagenes = os.path.join(ruta_base, "imagenes")

procesos_activos = []

def ejecutar_script(nombre_script):
    ruta_script = os.path.join(ruta_base, nombre_script)
    print(f"Iniciando: {ruta_script}")
    proceso = subprocess.Popen([sys.executable, ruta_script])
    procesos_activos.append(proceso)

def cerrar_aplicacion():
    print("Cerrando aplicación...")
    for proceso in procesos_activos:
        try:
            proceso.terminate()
        except Exception:
            pass
    ventana.destroy()
    sys.exit(0)

def minimizar_ventana():
    ventana.iconify()

def iniciar_robot_con_nombre(nombre_robot, script):
    ejecutar_script(script)

robots = {
    "Mano animatrónica":        ("mano_animatronica_serial.py",  "mano_animatronica.png"),
    "Pololu":                   ("pololu_fisico.py",             "pololu.png"),
    "Mano Simulada":            ("mano_simulacion_matlab.py",    "simulacion_mano.png"),
    "Robot Sawyer":             ("sawyer_simulacion.py",         "max_arm_simulacion.png"),
    "Esfera Virtual":           ("esfera_virtual.py",            "lector_de_gestos.png"),
    "Pololu webots":            ("pololu_webots.py",             "pololu_webots.png")
}

# Logo
try:
    logo_path = os.path.join(carpeta_imagenes, "logo_uvg.png")
    logo_img = Image.open(logo_path).resize((100, 100))
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(ventana, image=logo_photo, bg="#79BC90")
    logo_label.image = logo_photo
    logo_label.place(x=20, y=20)
except Exception as e:
    print("Error cargando el logo:", e)

# Título
titulo = tk.Label(
    ventana,
    text="Selecciona el sistema que deseas controlar",
    font=("Helvetica", 30, "bold"),
    fg="white",
    bg="#79BC90"
)
titulo.pack(pady=(80, 30))

robots_items = list(robots.items())

# === 3 arriba, 3 abajo ===
fila1 = robots_items[:3]
fila2 = robots_items[3:]

def crear_boton(nombre, script, imagen_archivo, parent):
    try:
        imagen_path = os.path.join(carpeta_imagenes, imagen_archivo)
        imagen = Image.open(imagen_path).resize((220, 220))
        imagen_tk = ImageTk.PhotoImage(imagen)

        marco = tk.Frame(parent, bg="#79BC90", highlightthickness=0)
        marco.pack(side="left", padx=40, pady=20)

        boton = tk.Label(marco, image=imagen_tk, bg="#79BC90", cursor="hand2", bd=4, relief="flat")
        boton.image = imagen_tk
        boton.pack()

        # Eventos hover/click
        boton.bind("<Button-1>", lambda e, n=nombre, s=script: iniciar_robot_con_nombre(n, s))
        boton.bind("<Enter>", lambda e: boton.config(highlightbackground="white", highlightcolor="white", highlightthickness=4))
        boton.bind("<Leave>", lambda e: boton.config(highlightthickness=0))

        # (Opcional) Nombre debajo de la imagen
        lbl = tk.Label(marco, text=nombre, bg="#79BC90", fg="white", font=("Helvetica", 17, "bold"))
        lbl.pack(pady=(6, 0))
    except Exception as e:
        print(f"Error cargando imagen para {nombre}:", e)

# Fila 1 (3 imágenes)
frame1 = tk.Frame(ventana, bg="#79BC90")
frame1.pack()
for nombre, (script, imagen) in fila1:
    crear_boton(nombre, script, imagen, frame1)

# Fila 2 (3 imágenes)
frame2 = tk.Frame(ventana, bg="#79BC90")
frame2.pack()
for nombre, (script, imagen) in fila2:
    crear_boton(nombre, script, imagen, frame2)

# Frame para botones de control (abajo)
control_frame = tk.Frame(ventana, bg="#79BC90")
control_frame.pack(side="bottom", fill="x", pady=20)

# Botón salir (derecha)
boton_salir = tk.Button(
    control_frame, text="Salir", command=cerrar_aplicacion,
    font=("Helvetica", 12, "bold"), bg="red", fg="white",
    width=12, height=2
)
boton_salir.pack(side="right", padx=30)

# Botón minimizar (derecha)
boton_minimizar = tk.Button(
    control_frame, text="Minimizar", command=minimizar_ventana,
    font=("Helvetica", 12, "bold"), bg="black", fg="white",
    width=12, height=2
)
boton_minimizar.pack(side="right", padx=40)

# Ctrl+C para cerrar
def cerrar_por_ctrl_c(sig, frame):
    cerrar_aplicacion()

signal.signal(signal.SIGINT, cerrar_por_ctrl_c)

ventana.mainloop()
