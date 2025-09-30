import os
import json
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk
from datetime import datetime

from Lib_Extra.Rutas_Gestion import get_config_dir, get_cache_dir, get_log_dir,get_recursos_dir

#Ruta para la creación de la carpeta de archivos temporales
CARPETA_ARCHIVOS_TMP_SUP = os.path.join(get_cache_dir(), "Archivos_Temporales")

#Ruta para la creación de la carpeta de archivos recurrentes
CARPETA_ARCHIVOS_RECURRENTES_SUP = os.path.join(get_config_dir(), "Archivos_Recurrentes")

# ============================================
# Funciones referentes a: Utilidades Varias
# ============================================

def Reempla_espacios_nombre(nombre_a_cambiar):
    """
    Reemplaza los espacios en blanco en un nombre por guiones bajos (_).

    Útil para crear nombres de archivos o identificadores compatibles
    con sistemas que no permiten espacios.

    Args:
        nombre_a_cambiar (str): Texto original que contiene espacios.

    Returns:
        str: Texto con los espacios reemplazados por guiones bajos.
    """
    return "_".join(nombre_a_cambiar.split())

def Restaurar_espacios_nombre(nombre_con_guiones):
    """
    Restaura los espacios en blanco en un nombre que usa guiones bajos (_).

    Reemplaza los guiones bajos por espacios, útil para mostrar nombres
    previamente codificados en la interfaz.

    Args:
        nombre_con_guiones (str): Texto con guiones bajos en lugar de espacios.

    Returns:
        str: Texto con espacios restaurados.
    """
    return " ".join(nombre_con_guiones.split("_"))

def mostrar_vent_IEO(parent, titulo_vendialog, mensaje_del_vendialog, tipo_mensaje: Gtk.MessageType, cont_boton, texto_boton1=None, texto_boton2=None, texto_boton3=None):
    """
    Muestra una ventana de diálogo interactiva con un mensaje y botones personalizados.

    Esta función permite mostrar un Gtk.MessageDialog modal y configurable
    (tipo de mensaje, número de botones, textos), y espera la respuesta del usuario.

    Nota importante: el argumento `parent` debe ser una ventana (`Gtk.Window`).
    Si no conoces el contenedor raíz, puedes usar `self.get_root()` para obtenerlo.

    Args:
        parent (Gtk.Window): Ventana que actúa como padre del diálogo.
        
        titulo_vendialog (str): Título principal del diálogo.
        
        mensaje_del_vendialog (str): Texto secundario o informativo.
        
        tipo_mensaje (Gtk.MessageType): Tipo del mensaje 
                                        (INFO, WARNING, QUESTION, ERROR, etc.).
        
        cont_boton (int): Cantidad de botones (1, 2 o 3).
        
        texto_boton1 (str, opcional): Texto del primer botón.
        
        texto_boton2 (str, opcional): Texto del segundo botón.
        
        texto_boton3 (str, opcional): Texto del tercer botón.

    Returns:
        Gtk.ResponseType: Respuesta del botón presionado por el usuario.
    """




    """Notas: Para evitar errores en el transient_for, recuerda que ahí se debe pasar
    una ventana (Gtk.Window), no son válidos los contenedores (Gtk.Box, etc) o 
    widgets similares. Puedes pasarle directamente la referencia, o si no la conoces,
    puedes usar directamente: self.get_root() que obtiene la raíz (window) del contenedor."""


    dialog = Gtk.MessageDialog(
        transient_for=parent,
        modal=True,
        message_type=tipo_mensaje,
        buttons=Gtk.ButtonsType.NONE,
        text=titulo_vendialog
    )

    content_area = dialog.get_content_area()
    label_sec = Gtk.Label(label=mensaje_del_vendialog)
    label_sec.set_wrap(True)

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
    box.set_vexpand(True)
    box.append(label_sec)
    content_area.append(box)

    # Botones según cantidad indicada
    if cont_boton == 1:
        dialog.add_button(texto_boton1 or "Aceptar", Gtk.ResponseType.OK)
    elif cont_boton == 2:
        dialog.add_button(texto_boton1 or "Aceptar", Gtk.ResponseType.OK)
        dialog.add_button(texto_boton2 or "Cancelar", Gtk.ResponseType.CANCEL)
    elif cont_boton == 3:
        dialog.add_button(texto_boton1 or "Sí", Gtk.ResponseType.YES)
        dialog.add_button(texto_boton2 or "No", Gtk.ResponseType.NO)
        dialog.add_button(texto_boton3 or "Cancelar", Gtk.ResponseType.CANCEL)

    loop = GLib.MainLoop()
    response_holder = {"response": None}

    def on_response(dlg, response_id):
        response_holder["response"] = response_id
        dlg.destroy()
        loop.quit()

    dialog.connect("response", on_response)
    dialog.show()
    loop.run()

    return response_holder["response"]

def aplicar_estilos_css(ruta_css="estilos.css"):
    """
    Carga y aplica un archivo CSS a toda la interfaz de GTK.

    Utiliza `Gtk.CssProvider` para cargar reglas de estilo desde un
    archivo externo y aplicarlas al contexto global de la interfaz.

    Args:
        ruta_css (str): Ruta al archivo CSS a cargar. Por defecto, "estilos.css".

    Nota:
        Si ocurre un error al cargar el archivo, se imprime un mensaje de error
        y no se aplica ningún estilo.
    """
    css_provider = Gtk.CssProvider()
    try:
        css_provider.load_from_path(ruta_css)
    except Exception as e:
        print(f"No se pudo cargar el archivo CSS: {e}")
        return

    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display,
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

def control_label_estado(label_SUP_Get, texto_1, segundos=5):

    """
    Cambia temporalmente el texto de un Gtk.Label y lo restaura luego de unos segundos.

    Se utiliza para mostrar mensajes breves de estado (como confirmaciones de acción)
    y luego restaurar un mensaje por defecto.

    Args:
        label_SUP_Get (Gtk.Label): Label al que se desea cambiar el texto.
        texto_1 (str): Texto temporal que se mostrará en el label.
        segundos (int, opcional): Tiempo en segundos antes de restaurar el texto (por defecto 5).

    Ejemplo de uso:
        control_label_estado(mi_label, "Nota guardada correctamente", 3)
    """

    label_SUP_Get.set_text(texto_1)

    def restaurar_texto():
        label_SUP_Get.set_text("Estado: Esperando acción.")
        return False  # No repetir el callback

    # Ejecutar `restaurar_texto` después de X segundos (convertido a milisegundos)
    GLib.timeout_add(segundos * 1000, restaurar_texto)

def obtener_ruta_icono_Preder():
    """"
    Devuelve la ruta absoluta del icono predeterminado si no el icono propio 
    no existe o no se puede cargar. Debe ser llamado manualmente."""

    ruta_Icono_Preder = os.path.join(get_recursos_dir(), "Imágenes", "Logo_MERIDA_Solo_Sin-Fondo_02.svg")
    
    return ruta_Icono_Preder
# ============================================
# Funciones referentes a: Archivos Temporales
# ============================================

def guardar_archivo_tmp(nombre_archivo_get, contenido_archivo_get):
    """
    Guarda contenido en un archivo temporal dentro de la carpeta Archivo_tmp.
    Crea la carpeta si no existe.

    Devuelve error (si existe) y el estado.
    """

    #Se asegura de que la carpeta exista
    os.makedirs(CARPETA_ARCHIVOS_TMP_SUP, exist_ok=True)

    error = None
    estado = False

    ruta_archivo = os.path.join(CARPETA_ARCHIVOS_TMP_SUP, nombre_archivo_get)

    try:
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            archivo.write(contenido_archivo_get)
        estado = True

        return estado, error

    except Exception as e:
        error = e

        return estado, error

def leer_archivo_tmp(nombre_archivo_get):
    """
    Lee el contenido de un archivo temporal. Devuelve None si no existe.
    """

    error = None

    ruta_archivo = os.path.join(CARPETA_ARCHIVOS_TMP_SUP, nombre_archivo_get)

    if os.path.isfile(ruta_archivo):
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                archivo_get = archivo.read().strip()

            return archivo_get

        except Exception as e:
            print(f"Ha ocurrido un problema al leer el archivo temporal <<{nombre_archivo_get}>>: {e}")
            return None
    else:
        return None

def borrar_archivo_tmp(nombre_archivo_get):
    ruta_archivo = os.path.join(CARPETA_ARCHIVOS_TMP_SUP, nombre_archivo_get)
    
    estado = False
    error = None

    if os.path.isfile(ruta_archivo):
        try:
            os.remove(ruta_archivo)
            
            estado = True
            return estado, error

        except Exception as e:
            
            error = e

    return estado, error

# ============================================
# Funciones referentes a: Bases de datos
# ============================================
def obtener_archivo_mas_reciente_ResplArch(lista_archivos):
    def extraer_fecha(nombre_archivo):
        try:
            fecha_str = nombre_archivo.split("_respaldo_")[1].replace(".sqlite", "").replace(".sql", "")
            return datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M")
        except Exception:
            return datetime.min  # Si hay error, se considera como el más antiguo
    return max(lista_archivos, key=extraer_fecha, default=None)

def obtener_archivo_mas_antiguo_ResplArch(lista_archivos):
    def extraer_fecha(nombre_archivo):
        try:
            fecha_str = nombre_archivo.split("_respaldo_")[1].replace(".sqlite", "").replace(".sql", "")
            return datetime.strptime(fecha_str, "%Y-%m-%d_%H-%M")
        except Exception:
            return datetime.max  # Si hay error, se considera como el más reciente
    return min(lista_archivos, key=extraer_fecha, default=None)

def filtrar_archivos_por_extension_BD(ruta_base):
    lista_sqlite = []
    lista_sql = []

    for carpeta_actual, subcarpetas, archivos in os.walk(ruta_base):
        for archivo in archivos:
            ruta_completa = os.path.join(carpeta_actual, archivo)
            if archivo.endswith(".sqlite"):
                lista_sqlite.append(ruta_completa)
            elif archivo.endswith(".sql"):
                lista_sql.append(ruta_completa)

    return lista_sqlite, lista_sql

# ============================================
# Funciones referentes a: Archivos Recurrentes
# ============================================

def crear_archivos_recurrentes(nombre_archivo, tipo_archivo, contenido_archivo):
    """
    Crea un archivo recurrente en la carpeta designada.
    Soporta tipo "json" y "txt".

    Retorna:
        (estado: bool, error: str | None)
    """
    try:
        # Asegurar que la carpeta exista
        os.makedirs(CARPETA_ARCHIVOS_RECURRENTES_SUP, exist_ok=True)

        # Definir ruta completa del archivo
        ruta = os.path.join(CARPETA_ARCHIVOS_RECURRENTES_SUP, nombre_archivo)

        # Escribir el archivo
        if tipo_archivo == "json":
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(contenido_archivo, archivo, indent=4, ensure_ascii=False)

        elif tipo_archivo == "txt":
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(contenido_archivo)

        else:
            return False, f"Tipo de archivo no soportado: {tipo_archivo}"

        return True, None

    except Exception as e:
        return False, str(e)

def leer_archivo_recurrente(nombre_archivo, tipo_archivo):
    """
    Lee un archivo recurrente desde la carpeta designada.
    Retorna el contenido si se encuentra y es válido, o None si no existe o está dañado.
    """
    try:
        ruta = os.path.join(CARPETA_ARCHIVOS_RECURRENTES_SUP, nombre_archivo)

        if not os.path.isfile(ruta):
            return None

        if tipo_archivo == "json":
            with open(ruta, "r", encoding="utf-8") as archivo:
                return json.load(archivo)

        elif tipo_archivo == "txt":
            with open(ruta, "r", encoding="utf-8") as archivo:
                return archivo.read()

        else:
            return None  # Tipo no soportado

    except Exception:
        return None

def eliminar_archivo_recurrente(nombre_archivo):
    """
    Elimina un archivo recurrente de la carpeta designada.
    
    Retorna:
        (estado: bool, error: str | None)
    """
    try:
        ruta = os.path.join(CARPETA_ARCHIVOS_RECURRENTES_SUP, nombre_archivo)

        if os.path.isfile(ruta):
            os.remove(ruta)
            return True, None
        else:
            return False, "Archivo no encontrado"

    except Exception as e:
        return False, str(e)

def añadir_a_archivo_recurrente(nombre_archivo, tipo_archivo, estructura, nuevo_contenido=None, clave=None, valor=None):
    """
    Añade contenido al final de un archivo recurrente sin modificar lo existente.
    Soporta tipo "json" (lista o diccionario) y "txt".

    Args:
        nombre_archivo (str): Nombre del archivo.
        tipo_archivo (str): "json" o "txt".
        estructura (str): "lista" o "diccionario" (solo relevante si tipo_archivo == "json").
        nuevo_contenido (any): Elemento a añadir si la estructura es lista.
        clave (str): Clave a usar si la estructura es diccionario.
        valor (any): Valor a usar si la estructura es diccionario.

    Retorna:
        (estado: bool, error: str | None)
    """
    try:
        # Asegurar que la carpeta exista
        os.makedirs(CARPETA_ARCHIVOS_RECURRENTES_SUP, exist_ok=True)

        ruta = os.path.join(CARPETA_ARCHIVOS_RECURRENTES_SUP, nombre_archivo)

        # Si el archivo no existe, crear según la estructura
        if not os.path.exists(ruta):
            if tipo_archivo == "json":
                if estructura == "lista":
                    contenido = [nuevo_contenido] if nuevo_contenido is not None else []
                elif estructura == "diccionario":
                    contenido = {clave: valor} if clave is not None else {}
                else:
                    return False, f"Estructura no soportada: {estructura}"

                with open(ruta, "w", encoding="utf-8") as archivo:
                    json.dump(contenido, archivo, indent=4, ensure_ascii=False)
                return True, None

            elif tipo_archivo == "txt":
                with open(ruta, "w", encoding="utf-8") as archivo:
                    archivo.write(str(nuevo_contenido) if nuevo_contenido else "")
                return True, None

            else:
                return False, f"Tipo de archivo no soportado: {tipo_archivo}"

        # Si ya existe el archivo
        if tipo_archivo == "txt":
            with open(ruta, "a", encoding="utf-8") as archivo:
                archivo.write("\n" + str(nuevo_contenido))
            return True, None

        elif tipo_archivo == "json":
            # Leer contenido existente
            with open(ruta, "r", encoding="utf-8") as archivo:
                try:
                    contenido = json.load(archivo)
                except json.JSONDecodeError:
                    contenido = [] if estructura == "lista" else {}

            if estructura == "lista":
                if not isinstance(contenido, list):
                    return False, "El archivo JSON no es una lista. No se puede añadir."
                contenido.append(nuevo_contenido)

            elif estructura == "diccionario":
                if not isinstance(contenido, dict):
                    return False, "El archivo JSON no es un diccionario. No se puede añadir."
                if clave is None:
                    return False, "Se requiere una clave para añadir al diccionario."
                contenido[clave] = valor

            else:
                return False, f"Estructura no soportada: {estructura}"

            # Guardar de nuevo
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump(contenido, archivo, indent=4, ensure_ascii=False)

            return True, None

        else:
            return False, f"Tipo de archivo no soportado: {tipo_archivo}"

    except Exception as e:
        return False, str(e)


# ===============================
# Funciones referentes a: logs
# ===============================
def get_log_file(categoria="general", N_arch_mant=10):
    """
    Devuelve la ruta de un log nuevo para la categoría indicada.
    Crea la carpeta si no existe y rota los antiguos si es necesario.
    """
    log_dir = get_log_dir() / categoria
    log_dir.mkdir(parents=True, exist_ok=True) #Crea la carpeta si no existe en base a la categoría

    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = log_dir / f"{categoria}_{timestamp}.log"

    # Rotar: mantener solo los últimos N logs
    logs_existentes = sorted(log_dir.glob(f"{categoria}_*.log"), key=os.path.getmtime)
    if len(logs_existentes) >= N_arch_mant:
        for viejo in logs_existentes[:-N_arch_mant+1]:
            viejo.unlink()

    #Devuelve la ruta para ser utilizado en escribir_log
    return log_file

def escribir_log(message, categoria="general", log_file=None):
    """
    Escribe un mensaje en el log de la categoría indicada.
    - categoria: "startup", "general", "error", etc.
    - log_file: archivo en uso (ruta) (si no, crea uno nuevo para esta sesión).
    """
    if log_file is None:
        log_file = get_log_file(categoria)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

    return log_file
