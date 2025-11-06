# gestor_s3_completo.py
import boto3
from botocore.exceptions import ClientError
import credencialesAWS
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from datetime import datetime
import subprocess

import os
# Carpeta actual
ruta_actual = os.getcwd()
ruta_prueba = os.path.join(ruta_actual,"AWS\proyecto mpi", "prueba.py")

def get_s3_client():
    return credencialesAWS.getCredentials()

def listar_buckets():
    #Devuelve una lista con los nombres de los buckets.
    s3 = get_s3_client()
    try:
        response = s3.list_buckets()
        return [bucket["Name"] for bucket in response["Buckets"]]
    except ClientError as e:
        messagebox.showerror("Error", f"No se pudieron listar los buckets:\n{e}")
        return []

def bucket_exists(s3, bucket_name):
    #Verifica si un bucket existe.
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False

def create_folders(s3, bucket_name):
    #Crea carpetas vacías raw/ y curated/ si no existen.
    for folder in ["raw/", "curated/"]:
        try:
            s3.put_object(Bucket=bucket_name, Key=folder)
        except ClientError as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta {folder}: {e}")
            return False
    return True

def create_or_select_bucket():
    #Selecciona un bucket existente o crea uno nuevo.
    bucket_name = bucket_var.get().strip().lower()
    region = region_var.get()
    if not bucket_name:
        messagebox.showwarning("Atención", "Por favor selecciona o ingresa un nombre de bucket.")
        return

    s3 = get_s3_client()

    if bucket_exists(s3, bucket_name):
        messagebox.showinfo("Bucket existente", f"Usando bucket '{bucket_name}'.")
    else:
        try:
            
            s3.create_bucket(Bucket=bucket_name)

            # if region == "us-east-1":
            #     s3.create_bucket(Bucket=bucket_name)
            # else:
            #     s3.create_bucket(
            #         Bucket=bucket_name,
            #         CreateBucketConfiguration={'LocationConstraint': region}
            #     )
            messagebox.showinfo("Bucket creado", f"Se creó el bucket '{bucket_name}' correctamente.")
        except ClientError as e:
            messagebox.showerror("Error", f"No se pudo crear el bucket:\n{e}")
            return

    # Crear carpetas base
    if create_folders(s3, bucket_name):
        messagebox.showinfo("Creacion de carpetas","Se crearon las carpetas raw/ y curated.")
        upload_file(bucket_name)

# def upload_file(bucket_name):
#     #Sube un archivo a la carpeta elegida dentro del bucket.
#     folder = folder_var.get()
#     if folder not in ["raw", "curated"]:
#         messagebox.showwarning("Atención", "Selecciona una carpeta destino (raw o curated).")
#         return

#     filetoup = filedialog.askopenfilename(title="Selecciona un archivo para subir")
#     if not filetoup:
#         return

#     s3 = get_s3_client()
#     filename = os.path.basename(filetoup)
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     key = f"{folder}/{timestamp}/{filename}"

#     try:
#         s3.upload_file(filetoup, bucket_name, key)
#         messagebox.showinfo("Éxito", f"Archivo '{filename}' subido correctamente a:\n{bucket_name}/{key}")
#     except ClientError as e:
#         messagebox.showerror("Error", f"No se pudo subir el archivo:\n{e}")


def upload_file(bucket_name):
    # Sube un archivo a la carpeta elegida dentro del bucket.
    folder = folder_var.get()
    if folder not in ["raw", "curated"]:
        messagebox.showwarning("Atención", "Selecciona una carpeta destino (raw o curated).")
        return

    filetoup = filedialog.askopenfilename(title="Selecciona un archivo para subir")
    if not filetoup:
        return

    s3 = get_s3_client()
    filename = os.path.basename(filetoup)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    key = f"{folder}/{timestamp}/{filename}"

    try:
        s3.upload_file(filetoup, bucket_name, key)
        messagebox.showinfo("Éxito", f"Archivo '{filename}' subido correctamente a:\n{bucket_name}/{key}")
        
        # Preguntar si quiere abrir el dashboard
        abrir = messagebox.askyesno("Abrir dashboard", "¿Deseas abrir el dashboard ahora?")
        if abrir:
            subprocess.Popen(["streamlit", "run", ruta_prueba], shell=True)
            
    except ClientError as e:
        messagebox.showerror("Error", f"No se pudo subir el archivo:\n{e}")

def actualizar_buckets():
    #Actualiza la lista de buckets mostrada en el combobox.
    buckets = listar_buckets()
    bucket_combo["values"] = buckets
    if buckets:
        bucket_combo.current(0)

# ---------------- INTERFAZ ----------------
app = ttk.Window(themename="flatly")
app.title("Gestor de Buckets S3 Completo")
app.geometry("520x360")

ttk.Label(app, text="Gestor de Buckets S3", font=("Segoe UI", 16, "bold")).pack(pady=10)

frame = ttk.Frame(app)
frame.pack(pady=10)

# Buckets
ttk.Label(frame, text="Buckets disponibles:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
bucket_var = ttk.StringVar()
bucket_combo = ttk.Combobox(frame, textvariable=bucket_var, width=30)
bucket_combo.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(frame, text="Actualizar lista", bootstyle=INFO, command=actualizar_buckets).grid(row=0, column=2, padx=5, pady=5)

# Región
ttk.Label(frame, text="Región (para crear nuevo):").grid(row=1, column=0, padx=5, pady=5, sticky=E)
region_var = ttk.StringVar(value="us-east-1")
region_combo = ttk.Combobox(frame, textvariable=region_var, values=[
    "us-east-1", "us-west-1", "us-west-2", "eu-west-1", "sa-east-1"
], state="readonly", width=28)
region_combo.grid(row=1, column=1, padx=5, pady=5)

# Carpeta destino
ttk.Label(frame, text="Subir a carpeta:").grid(row=2, column=0, padx=5, pady=5, sticky=E)
folder_var = ttk.StringVar(value="raw")
folder_combo = ttk.Combobox(frame, textvariable=folder_var, values=["raw", "curated"], state="readonly", width=28)
folder_combo.grid(row=2, column=1, padx=5, pady=5)

# Botón principal
ttk.Button(app, text="Usar o crear bucket y subir archivo", bootstyle=SUCCESS, command=create_or_select_bucket).pack(pady=20)

ttk.Label(app, text="Selecciona un bucket existente o escribe un nuevo nombre.\n"
                    "Se crearán carpetas raw/ y curated si no existen.", font=("Segoe UI", 9)).pack()

ttk.Label(app, text="Desarrollado con boto3 + ttkbootstrap", font=("Segoe UI", 8)).pack(side="bottom", pady=5)

# Llenar lista inicial
actualizar_buckets()

app.mainloop()

import prueba 

