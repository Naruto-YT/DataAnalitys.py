import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import re

# Rutas de los archivos de chat
ruta_dorado1 = r"C: WhatsApp con FBI.txt"    #Aqui tienen que poner la rutas de acceso del archivo txt, en mi caso eran dos archivos, uno donde exportaba mi nombre registrado y el otro donde no salia mi nombre pero era el mismo grupo 
ruta_dorado2 = r"C:WhatsApp Chat with FBI.txt"

# Leer archivos de texto
def leer_archivo_chat(ruta):
    with open(ruta, encoding='utf-8', errors='ignore') as f:
        return f.readlines()

chat_dorado1 = leer_archivo_chat(ruta_dorado1)
chat_dorado2 = leer_archivo_chat(ruta_dorado2)

# Procesar chat
def procesar_chat(chat_lines, usuarios_interesados_regex, nombre_predeterminado=None):
    registros = []
    patron_usuario = re.compile(usuarios_interesados_regex, re.IGNORECASE)
    patron_media_omitted = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} [ap]m - ‎: <Media omitted>")
    
    for line in chat_lines:
        try:
            if ' - ' in line:
                fecha_str, resto = line.split(' - ', 1)
                # Probar múltiples formatos de fecha
                formatos_fecha = ["%d/%m/%Y, %I:%M %p", "%d/%m/%y, %I:%M %p"]
                fecha = None
                for formato in formatos_fecha:
                    try:
                        fecha = datetime.strptime(fecha_str.strip(), formato)
                        break
                    except ValueError:
                        continue
                if fecha:
                    if patron_media_omitted.match(line.strip()):
                        usuario = nombre_predeterminado if nombre_predeterminado else "Desconocido"
                    elif ': ' in resto:
                        usuario, _ = resto.split(': ', 1)
                    else:
                        usuario = nombre_predeterminado if nombre_predeterminado else "Desconocido"
                    
                    if patron_usuario.match(usuario.strip()) or usuario == nombre_predeterminado:
                        registros.append({"Fecha": fecha, "Usuario": usuario.strip()})
        except ValueError:
            continue
    return pd.DataFrame(registros)

usuarios_dorado2 = ["Brianna T.E", "Yahir T.E", "Yanesis T.E", "Ricardo T.E", "Christian T.E", "Marina T.E", "Carlos T.E", "Stephanie T.E", "Emiliano T.E", "Christie T.E", "Indira T.E"]

# Procesar chats
df_dorado1 = procesar_chat(chat_dorado1, r"hermogenes")
df_dorado2 = procesar_chat(chat_dorado2, "|".join(map(re.escape, usuarios_dorado2)), nombre_predeterminado="Hermogenes T.E")

# Mostrar información de depuración
print("Primeros registros de df_dorado1:")
print(df_dorado1.head())
print("Primeros registros de df_dorado2:")
print(df_dorado2.head())

if df_dorado1.empty:
    print("Advertencia: No se encontraron registros para hermogenes en dorado1.")
if df_dorado2.empty:
    print("Advertencia: No se encontraron registros para los usuarios en dorado2.")

# Combinar los datos
df = pd.concat([df_dorado1, df_dorado2])

if df.empty:
    print("Advertencia: No se encontraron datos combinados.")
else:
    df['Día'] = df['Fecha'].dt.day

    # Filtrar por semanas
    semanas = {
        "13-17 enero": (13, 17),
        "20-24 enero": (20, 24),
        "27-31 enero": (27, 31)
    }

    colores_usuarios = {usuario: color for usuario, color in zip(df['Usuario'].unique(), plt.cm.tab20.colors)}

    for semana, (inicio, fin) in semanas.items():
        df_semana = df[(df['Día'] >= inicio) & (df['Día'] <= fin)]
        plt.figure(figsize=(10, 5))

        # Calcular actividad por usuario y ordenar por cantidad
        actividad_usuarios = (
            df_semana.groupby('Usuario').size().sort_values(ascending=False)
        )

        for usuario in actividad_usuarios.index:
            actividad = df_semana[df_semana['Usuario'] == usuario].groupby('Día').size()
            label_usuario = f"{usuario} ({actividad.sum()} mensajes)"
            plt.plot(actividad.index, actividad.values, marker='o', label=label_usuario, color=colores_usuarios[usuario])

        plt.title(f"Evolución de Actividad: {semana}")
        plt.xlabel("Día")
        plt.ylabel("Cantidad de Mensajes")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
