import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import signal
from PIL import Image, ImageTk

# Variable global para el proceso activo
proceso_gestos = None

def ejecutar_script(nombre_archivo):
    global proceso_gestos

    # Usar Python del entorno virtual
    python_path = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    
    if proceso_gestos:
        proceso_gestos.terminate()
    
    try:
        ruta = os.path.join(os.getcwd(), "examples", nombre_archivo)
        print(f"Iniciando: {ruta}")
        proceso_gestos = subprocess.Popen([python_path, ruta], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar el script:\n{e}")

def iniciar_robot_con_nombre(nombre, script):
    messagebox.showinfo("Robot seleccionado", f"Iniciando {nombre}...")
    ejecutar_script(script)

def cerrar_app(event=None):
    global proceso_gestos
    print("Cerrando aplicación...")
    if proceso_gestos:
        proceso_gestos.terminate()
    ventana.destroy()

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Control de Robots con Leap Motion")
ventana.configure(bg="#1e1e2f")
ventana.resizable(True, True)
ventana.bind('<Control-c>', cerrar_app)
ventana.protocol("WM_DELETE_WINDOW", cerrar_app)
ventana.state("zoomed")  # Pantalla completa

# Logo UVG en esquina superior izquierda
try:
    img_path = os.path.join(os.getcwd(), "examples", "logo_robotica.png")
    imagen = Image.open(img_path)
    imagen = imagen.resize((100, 100))
    img_tk = ImageTk.PhotoImage(imagen)
    panel_img = tk.Label(ventana, image=img_tk, bg="#1e1e2f")
    panel_img.place(relx=0.02, rely=0.03)
except Exception as e:
    print("No se encontró la imagen:", e)

# Título
etiqueta = tk.Label(
    ventana,
    text="Selecciona el sistema que deseas controlar:",
    font=("Helvetica", 18, "bold"),
    bg="#1e1e2f",
    fg="white"
)
etiqueta.place(relx=0.3, rely=0.03)

# Diccionario de robots
robots = {
    "Mano\nanimatrónica": "dedos_mano_etc_serial.py",
    "Pololu": "gestos_basicos.py",
    "Mano\nSimulada": "mano_simulacion_matlab.py",
    "MaxArm": "max_arm_simulacion.py",
    "Gestos\n(lector de sensor)": "gestos_basicos.py"
}

# Crear botones grandes y cuadrados (160x160)
for i, (nombre, script) in enumerate(robots.items()):
    btn = tk.Button(
        ventana,
        text=nombre,
        command=lambda n=nombre, s=script: iniciar_robot_con_nombre(n.replace("\n", " "), s),
        bg="#d32f2f",
        fg="white",
        activebackground="#b71c1c",
        activeforeground="white",
        font=("Helvetica", 11, "bold"),
        relief="flat",
        bd=0
    )
    # Posición: 3 por fila
    col = i % 3
    row = i // 3
    relx = 0.17 + col * 0.28
    rely = 0.2 + row * 0.4
    btn.place(relx=relx, rely=rely, width=160, height=160)

# Botón Salir
boton_salir = tk.Button(
    ventana,
    text="Salir",
    command=cerrar_app,
    bg="#555555",
    fg="white",
    activebackground="#333333",
    activeforeground="white",
    font=("Helvetica", 10, "bold"),
    relief="flat",
    bd=0,
    width=10,
    height=2
)
boton_salir.place(relx=0.85, rely=0.88)

# Footer
footer = tk.Label(
    ventana,
    text="Desarrollado por Marcela Padilla",
    font=("Helvetica", 10),
    bg="#1e1e2f",
    fg="gray"
)
footer.place(relx=0.02, rely=0.95)

# Ejecutar GUI
ventana.mainloop()
