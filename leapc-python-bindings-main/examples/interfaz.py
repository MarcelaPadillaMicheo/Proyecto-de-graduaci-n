# ==============================================================
# Programa desarrollado por Marcela Padilla
# Interfaz gráfica principal para control de robots con Leap Motion
# ==============================================================
# Esta aplicación implementa una interfaz gráfica (GUI) en Python 
# mediante Tkinter que permite seleccionar y ejecutar distintos sistemas 
# robóticos controlados con gestos detectados por el sensor Leap Motion.
#
# Cada botón en el menú principal lanza un script asociado (ya sea de MATLAB 
# o Python) que controla uno de los robots disponibles:
# - Pololu físico y su menú de talleres
# - Pololu simulado en Webots
# - Mano animatrónica
# - Mano simulada
# - Agente puntual
# - Robot Sawyer
#
# La interfaz está diseñada a pantalla completa, muestra imágenes 
# ilustrativas y permite iniciar, detener y finalizar los programas 
# de forma segura.
# ==============================================================

import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import signal
import sys

# --------------------------------------------------------------
# CONFIGURACIÓN INICIAL DE LA VENTANA
# --------------------------------------------------------------
ventana = tk.Tk()
ventana.title("Control de Robots con Leap Motion")
ventana.configure(bg="#79BC90")
ventana.attributes("-fullscreen", True)

# Directorios base
ruta_base = os.path.dirname(os.path.abspath(__file__))
carpeta_imagenes = os.path.join(ruta_base, "imagenes")

procesos_activos = []  # Lista de procesos en ejecución

# --------------------------------------------------------------
# FUNCIONES BÁSICAS DE CONTROL
# --------------------------------------------------------------
def ejecutar_script(nombre_script):
    """Ejecuta el script correspondiente al robot seleccionado."""
    ruta_script = os.path.join(ruta_base, nombre_script)
    print(f"Iniciando: {ruta_script}")
    proceso = subprocess.Popen([sys.executable, ruta_script])
    procesos_activos.append(proceso)
    mostrar_estado_ejecucion(proceso, nombre_script)

def detener_proceso(proceso):
    """Detiene el proceso activo del robot y regresa al menú principal."""
    try:
        proceso.terminate()
        print("Programa detenido.")
    except Exception:
        pass
    crear_pantalla_principal()

def cerrar_aplicacion():
    """Cierra todos los procesos activos y la aplicación."""
    print("Cerrando aplicación...")
    for proceso in procesos_activos:
        try:
            proceso.terminate()
        except Exception:
            pass
    ventana.destroy()
    sys.exit(0)

def minimizar_ventana():
    """Minimiza la ventana principal."""
    ventana.iconify()

# --------------------------------------------------------------
# INTERFAZ PRINCIPAL Y LIMPIEZA DE FRAMES
# --------------------------------------------------------------
frame_principal = tk.Frame(ventana, bg="#79BC90")
frame_principal.pack(fill="both", expand=True)

def limpiar_frame():
    """Elimina todos los elementos gráficos del frame principal."""
    for widget in frame_principal.winfo_children():
        widget.destroy()

# --------------------------------------------------------------
# ESTADO DE EJECUCIÓN
# --------------------------------------------------------------
def mostrar_estado_ejecucion(proceso, nombre_script):
    """Muestra una pantalla de 'código en ejecución' con opción de detenerlo."""
    limpiar_frame()

    lbl = tk.Label(
        frame_principal,
        text="Código del robot corriendo",
        font=("Helvetica", 28, "bold"),
        fg="red", bg="#79BC90"
    )
    lbl.pack(pady=60)

    # Muestra imagen guía del Pololu si es el script correspondiente
    if "pololu_fisico.py" in nombre_script:
        try:
            img_path = os.path.join(carpeta_imagenes, "Pololu_guia.png")
            img = Image.open(img_path).resize((900, 500))
            img_tk = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(frame_principal, image=img_tk, bg="#79BC90")
            lbl_img.image = img_tk
            lbl_img.pack(pady=20)
        except Exception as e:
            print("Error cargando la imagen Pololu_guia.png:", e)

    boton_detener = tk.Button(
        frame_principal,
        text="Detener programa",
        font=("Helvetica", 16, "bold"),
        bg="red", fg="white",
        width=18, height=2,
        command=lambda: detener_proceso(proceso)
    )
    boton_detener.pack(pady=40)

    agregar_botones_inferiores()

# --------------------------------------------------------------
# BOTONES INFERIORES (SALIR / MINIMIZAR)
# --------------------------------------------------------------
def agregar_botones_inferiores():
    """Agrega los botones inferiores de control general."""
    control_frame = tk.Frame(frame_principal, bg="#79BC90")
    control_frame.pack(side="bottom", fill="x", pady=20)

    boton_salir = tk.Button(
        control_frame, text="Salir", command=cerrar_aplicacion,
        font=("Helvetica", 12, "bold"), bg="red", fg="white",
        width=12, height=2
    )
    boton_salir.pack(side="right", padx=30)

    boton_minimizar = tk.Button(
        control_frame, text="Minimizar", command=minimizar_ventana,
        font=("Helvetica", 12, "bold"), bg="black", fg="white",
        width=12, height=2
    )
    boton_minimizar.pack(side="right", padx=40)

# --------------------------------------------------------------
# MENÚ PRINCIPAL
# --------------------------------------------------------------
def crear_pantalla_principal():
    """Pantalla principal del menú con todos los sistemas disponibles."""
    limpiar_frame()

    # Logo de la UVG
    try:
        logo_path = os.path.join(carpeta_imagenes, "logo_uvg.png")
        logo_img = Image.open(logo_path).resize((100, 100))
        logo_photo = ImageTk.PhotoImage(logo_img)
        logo_label = tk.Label(frame_principal, image=logo_photo, bg="#79BC90")
        logo_label.image = logo_photo
        logo_label.place(x=20, y=20)
    except Exception as e:
        print("Error cargando el logo:", e)

    # Título principal
    titulo = tk.Label(
        frame_principal,
        text="Selecciona el sistema que deseas controlar",
        font=("Helvetica", 30, "bold"),
        fg="white", bg="#79BC90"
    )
    titulo.pack(pady=(80, 30))

    robots_items = list(robots.items())
    fila1 = robots_items[:3]
    fila2 = robots_items[3:]

    # Función para crear cada botón con imagen
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

            boton.bind("<Enter>", lambda e: boton.config(highlightbackground="white", highlightcolor="white", highlightthickness=4))
            boton.bind("<Leave>", lambda e: boton.config(highlightthickness=0))
            boton.bind("<Button-1>", lambda e, n=nombre, s=script: abrir_subpantalla_robot(n, s))

            lbl = tk.Label(marco, text=nombre, bg="#79BC90", fg="white", font=("Helvetica", 17, "bold"))
            lbl.pack(pady=(6, 0))
        except Exception as e:
            print(f"Error cargando imagen para {nombre}:", e)

    # Fila 1
    frame1 = tk.Frame(frame_principal, bg="#79BC90")
    frame1.pack()
    for nombre, (script, imagen) in fila1:
        crear_boton(nombre, script, imagen, frame1)

    # Fila 2
    frame2 = tk.Frame(frame_principal, bg="#79BC90")
    frame2.pack()
    for nombre, (script, imagen) in fila2:
        crear_boton(nombre, script, imagen, frame2)

    agregar_botones_inferiores()

# --------------------------------------------------------------
# MENÚ DEL POLOLU (CON OPCIONES DE TALLER)
# --------------------------------------------------------------
def mostrar_menu_pololu(script_pololu):
    """Menú secundario para seleccionar talleres con el robot Pololu."""
    limpiar_frame()

    titulo = tk.Label(
        frame_principal,
        text="Selecciona la actividad con el Pololu",
        font=("Helvetica", 28, "bold"),
        fg="white", bg="#79BC90"
    )
    titulo.pack(pady=(60, 30))

    opciones = {
        "Carreras": "Taller_pololu_carreras.png",
        "Evadir Obstáculos": "Taller_pololu_evadir_inst.png",
        "Parquearse de retroceso": "Taller_pololu_parquearse_inst.png",
        "Trazar una forma": "Taller_pololu_trazar_inst.png"
    }

    def mostrar_instruccion(nombre_opcion, imagen_archivo):
        limpiar_frame()
        try:
            img_path = os.path.join(carpeta_imagenes, imagen_archivo)
            img = Image.open(img_path).resize((1000, 550))
            img_tk = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(frame_principal, image=img_tk, bg="#79BC90")
            lbl_img.image = img_tk
            lbl_img.pack(pady=40)
        except Exception as e:
            print(f"Error cargando {imagen_archivo}:", e)

        boton_listo = tk.Button(
            frame_principal, text="Listo", font=("Helvetica", 16, "bold"),
            bg="#005F30", fg="white", width=12, height=2,
            command=lambda: ejecutar_script(script_pololu)
        )
        boton_listo.pack(pady=10)

        boton_volver = tk.Button(
            frame_principal, text="Regresar", font=("Helvetica", 12, "bold"),
            bg="black", fg="white", width=10, command=lambda: mostrar_menu_pololu(script_pololu)
        )
        boton_volver.pack(pady=(0, 30))
        agregar_botones_inferiores()

    frame_botones = tk.Frame(frame_principal, bg="#79BC90")
    frame_botones.pack(pady=20)

    for nombre, img in opciones.items():
        btn = tk.Button(
            frame_botones,
            text=nombre,
            font=("Helvetica", 18, "bold"),
            bg="#005F30", fg="white",
            width=25, height=2,
            command=lambda n=nombre, i=img: mostrar_instruccion(n, i)
        )
        btn.pack(pady=15)

    boton_volver_menu = tk.Button(
        frame_principal, text="Volver al menú principal",
        font=("Helvetica", 12, "bold"),
        bg="black", fg="white", width=20, command=crear_pantalla_principal
    )
    boton_volver_menu.pack(pady=(40, 0))
    agregar_botones_inferiores()

# --------------------------------------------------------------
# SUBPANTALLAS INDIVIDUALES (OTROS ROBOTS)
# --------------------------------------------------------------
def mostrar_instruccion_simple(nombre_robot, script, imagen_archivo):
    """Muestra una imagen con instrucciones y ejecuta el script asociado."""
    limpiar_frame()
    try:
        img_path = os.path.join(carpeta_imagenes, imagen_archivo)
        img = Image.open(img_path).resize((1000, 550))
        img_tk = ImageTk.PhotoImage(img)
        lbl_img = tk.Label(frame_principal, image=img_tk, bg="#79BC90")
        lbl_img.image = img_tk
        lbl_img.pack(pady=40)
    except Exception as e:
        print(f"Error cargando {imagen_archivo}:", e)

    boton_listo = tk.Button(
        frame_principal, text="Listo", font=("Helvetica", 16, "bold"),
        bg="#005F30", fg="white", width=12, height=2,
        command=lambda: ejecutar_script(script)
    )
    boton_listo.pack(pady=10)

    boton_volver = tk.Button(
        frame_principal, text="Volver al menú principal", font=("Helvetica", 12, "bold"),
        bg="black", fg="white", width=20, command=crear_pantalla_principal
    )
    boton_volver.pack(pady=(0, 30))
    agregar_botones_inferiores()

# --------------------------------------------------------------
# DICCIONARIO DE ROBOTS DISPONIBLES
# --------------------------------------------------------------
robots = {
    "Mano animatrónica": ("animatronica.py",  "mano_animatronica.png"),
    "Pololu":            ("pololu_fisico.py",           "pololu.png"),
    "Mano Simulada":     ("mano_simulacion_matlab.py",  "simulacion_mano.png"),
    "Robot Sawyer":      ("sawyer_simulacion.py",       "max_arm_simulacion.png"),
    "Agente Puntual":    ("esfera_virtual.py",          "lector_de_gestos.png"),
    "Pololu webots":     ("pololu_webots.py",           "pololu_webots.png")
}

# --------------------------------------------------------------
# FUNCIÓN PARA ABRIR SUBPANTALLAS SEGÚN EL ROBOT
# --------------------------------------------------------------
def abrir_subpantalla_robot(nombre_robot, script):
    """Determina la pantalla a mostrar según el robot seleccionado."""
    if nombre_robot == "Pololu":
        mostrar_menu_pololu(script)
    elif nombre_robot == "Robot Sawyer":
        mostrar_instruccion_simple(nombre_robot, script, "sawyer_taller.png")
    elif nombre_robot == "Pololu webots":
        mostrar_instruccion_simple(nombre_robot, script, "pololu_webots_taller.png")
    elif nombre_robot == "Mano Simulada":
        mostrar_instruccion_simple(nombre_robot, script, "mano_simulada_taller.png")
    elif nombre_robot == "Agente Puntual":
        mostrar_instruccion_simple(nombre_robot, script, "esfera_taller.png")
    elif nombre_robot == "Mano animatrónica":
        mostrar_instruccion_simple(nombre_robot, script, "mano_animatronica_taller.png")
    else:
        ejecutar_script(script)

# --------------------------------------------------------------
# EJECUCIÓN PRINCIPAL DE LA INTERFAZ
# --------------------------------------------------------------
signal.signal(signal.SIGINT, lambda sig, frame: cerrar_aplicacion())
crear_pantalla_principal()
ventana.mainloop()

