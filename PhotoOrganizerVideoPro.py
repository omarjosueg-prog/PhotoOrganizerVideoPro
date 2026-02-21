import os
import shutil
import hashlib
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador Multimedia Pro - Monitor en Tiempo Real")
        self.root.geometry("700x400") # Ventana más grande para ver las rutas
        self.root.resizable(True, True)

        # Etiquetas de encabezado
        tk.Label(root, text="Monitor de Organización Multimedia", font=("Arial", 14, "bold")).pack(pady=10)

        # Panel de información de rutas
        self.frame_info = tk.Frame(root, padx=20)
        self.frame_info.pack(fill="x")

        tk.Label(self.frame_info, text="Origen:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.origen_label = tk.Label(self.frame_info, text="-", fg="gray", wraplength=650, justify="left")
        self.origen_label.pack(anchor="w", pady=(0, 10))

        tk.Label(self.frame_info, text="Destino:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.destino_label = tk.Label(self.frame_info, text="-", fg="green", wraplength=650, justify="left")
        self.destino_label.pack(anchor="w", pady=(0, 10))

        # Barra de progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=20)

        self.status_file = tk.Label(root, text="Esperando selección de carpetas...", font=("Arial", 9, "italic"))
        self.status_file.pack(pady=5)

        self.btn_inicio = tk.Button(root, text="Iniciar Organización", command=self.iniciar_proceso, 
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=30, pady=10)
        self.btn_inicio.pack(pady=20)

    def obtener_huella(self, ruta):
        hash_md5 = hashlib.md5()
        try:
            with open(ruta, "rb") as f:
                for trozo in iter(lambda: f.read(4096), b""):
                    hash_md5.update(trozo)
            return hash_md5.hexdigest()
        except: return None

    def iniciar_proceso(self):
        origen = filedialog.askdirectory(title="Selecciona Carpeta de Origen")
        if not origen: return
        
        destino = filedialog.askdirectory(title="Selecciona Carpeta de Destino")
        if not destino: return

        por_mes = messagebox.askyesno("Configuración", "¿Deseas organizar por AÑO y MES?")

        ext_fotos = ('.jpg', '.jpeg', '.png', '.gif', '.heic', '.webp', '.tiff', '.bmp')
        ext_videos = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp', '.m4v')
        todas_las_exts = ext_fotos + ext_videos
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        archivos_a_procesar = []
        for root, dirs, files in os.walk(origen):
            if os.path.abspath(destino) in os.path.abspath(root): continue
            for f in files:
                if f.lower().endswith(todas_las_exts):
                    archivos_a_procesar.append(os.path.join(root, f))
        
        if not archivos_a_procesar:
            messagebox.showinfo("Aviso", "No hay archivos para mover.")
            return

        self.progress["maximum"] = len(archivos_a_procesar)
        self.progress["value"] = 0
        self.btn_inicio.config(state="disabled")

        huellas = set()
        movidos = 0

        for ruta_full in archivos_a_procesar:
            nombre = os.path.basename(ruta_full)
            
            # ACTUALIZACIÓN DE LA INTERFAZ
            self.origen_label.config(text=ruta_full)
            self.status_file.config(text=f"Procesando: {nombre}")
            self.root.update()

            huella = self.obtener_huella(ruta_full)
            if not huella:
                self.progress["value"] += 1
                continue

            if huella in huellas:
                # Caso de duplicado
                ruta_final_dir = os.path.join(destino, "Duplicados_Detectados")
            else:
                huellas.add(huella)
                try:
                    fecha = datetime.datetime.fromtimestamp(os.path.getmtime(ruta_full))
                    anio = str(fecha.year)
                    ruta_base = os.path.join(destino, anio, f"{anio}-{meses[fecha.month-1]}") if por_mes else os.path.join(destino, anio)
                    
                    # Subcarpeta para videos
                    if nombre.lower().endswith(ext_videos):
                        ruta_final_dir = os.path.join(ruta_base, "Videos")
                    else:
                        ruta_final_dir = ruta_base
                except:
                    ruta_final_dir = os.path.join(destino, "Error_Fecha")

            # Mostrar destino en la interfaz antes de mover
            dest_completo = os.path.join(ruta_final_dir, nombre)
            self.destino_label.config(text=dest_completo)
            self.root.update()

            # Movimiento real
            os.makedirs(ruta_final_dir, exist_ok=True)
            try:
                shutil.move(ruta_full, dest_completo)
                movidos += 1
            except Exception as e:
                print(f"Error al mover: {e}")

            self.progress["value"] += 1

        self.btn_inicio.config(state="normal")
        messagebox.showinfo("Finalizado", f"Se han organizado {movidos} archivos con éxito.")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = OrganizadorApp(ventana)
    ventana.mainloop()