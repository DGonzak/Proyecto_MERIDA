# MERIDA Editor - Un software para escritores literarios y académicos
# Copyright (C) 2025 DGonzak
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import os
import zipfile
import json
import shutil

from Lib_Extra.Rutas_Gestion import get_recursos_dir, get_data_dir
from Lib_Extra.Funciones_extras import escribir_log

from BDs_Functions.Models_BD import BD_Moduls
from BDs_Functions.BD_Moduls_Funct import BD_Moduls_Functions


class pantalla_modulos(Gtk.Window):
    def __init__(self):
        super().__init__(title="Gestión de Módulos y Complementos")
        self.set_default_size(1000, 800)

        #==================INSTANCIAS DE CLASES==================
        self.BD_Moduls_Functions = BD_Moduls_Functions()



        #==================ORGANIZACIÓN Y CREACIÓN DE WIDGETS==================
        #---------------------Contenedores---------------------
        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        box_sup = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_cent = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_cent.set_vexpand(True)
        box_cent.set_hexpand(True)
        box_infer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        #---------------------Widgets---------------------
        #Entry de busqueda
        self.Entry_Busqueda = Gtk.SearchEntry()
        self.Entry_Busqueda.set_placeholder_text("Buscar módulos...")
        self.Entry_Busqueda.set_hexpand(True)

        #Espacio central para mostrar los módulos
        #Aún no se desarrolló
        self.Label_Sin_Modulos = Gtk.Label(label="Aún no hay módulos o complementos instalados.")


        #Botones inferiores
        self.boton_instalar = Gtk.Button(label="Instalar módulo")
        self.boton_instalar.set_tooltip_text(
            "Instalar un nuevo módulo o complemento desde un archivo .modmeri")
        self.boton_instalar.connect("clicked", self.instalar_modulo_Interfaz)
        #---------------------Extras-------------------------
        #Creación del log a utilizar para guardar los registros de instalación de módulos
        self.intall_log_modul = escribir_log("=== Inicio del log de instalación de módulos ===", categoria="módulos")

        
        #-------------------Inserción a la ventana-------------------
        box_sup.append(self.Entry_Busqueda)
        
        box_cent.append(self.Label_Sin_Modulos)

        box_infer.append(self.boton_instalar)
        box_pr.append(box_sup)
        box_pr.append(box_cent)
        box_pr.append(box_infer)

        self.set_child(box_pr)


    def instalar_modulo_Interfaz(self, widget=None):
        """
        Muestra la interfaz para instalar un nuevo módulo o complemento.
        1. Abre la ventana de instalación de módulo.
        2. Permite seleccionar un archivo o carpeta de módulos.
        """
        #Ventana de instalación
        Vent_IntallModul = Gtk.Dialog(
            title="Instalar nuevo módulo o complemento",
            transient_for=self.get_root(),
            modal=True,
        )
        Vent_IntallModul.set_default_size(1000, 600)
        content_area = Vent_IntallModul.get_content_area()
        
        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_ajustes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_infor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.label_infor_estado = Gtk.Label(label="Esperando instrucciones...")

        self.textview_regist =Gtk.TextView()
        self.textview_regist.set_editable(False)
        self.textview_regist.set_focusable(False)
        self.textview_regist.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview_regist.set_vexpand(True)
        self.textview_regist.set_hexpand(True)

        ruta_archivo_explicacion = os.path.join(get_recursos_dir(), "Texto", "explicacion_InstalModMeri_1.txt")
        
        try:
            with open(ruta_archivo_explicacion) as txt1:

                contenido_txt1 = txt1.read()
        except Exception as e:
            contenido_txt1 = "Archivo de explicacion no encontrado. Error: " + str(e)


        self.textview_regist.get_buffer().set_text(contenido_txt1)
        
        
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_child(self.textview_regist)
        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)

        btn_busArch = Gtk.Button(label="Instalar desde archivo")
        btn_busArch.set_tooltip_text("Seleccionar un archivo .modmeri para instalar un módulo o complemento")
        btn_busArch.connect("clicked", self.seleccionar_modulo_ArchCarpet, "Archivo")

        btn_busCarpet = Gtk.Button(label="Instalar desde carpeta")
        btn_busCarpet.set_tooltip_text("Seleccionar una carpeta que contenga módulos o complementos .modmeri")
        btn_busCarpet.connect("clicked", self.seleccionar_modulo_ArchCarpet, "Carpeta")
        box_pr.append(self.label_infor_estado)
        box_pr.append(box_infor)

        box_infor.append(scroll_window)
        box_infor.append(box_ajustes)

        box_ajustes.append(btn_busArch)
        box_ajustes.append(btn_busCarpet)

        content_area.append(box_pr)

        Vent_IntallModul.show()

    def control_mensajes_Textview_Regist_A(self, mensaje_label=None, mensaje_textview=None):
        """Muestra y controla los mensajes en la interfaz de instalación de módulos."""
        if mensaje_label is not None:
            self.label_infor_estado.set_text(mensaje_label)

        if mensaje_textview is not None:
            buffer_tv = self.textview_regist.get_buffer()
            texto_actual = buffer_tv.get_text(
                buffer_tv.get_start_iter(), buffer_tv.get_end_iter(), True
            )
            nuevo_texto = texto_actual + mensaje_textview + "\n"
            buffer_tv.set_text(nuevo_texto)

            #Guardar en log startup
            escribir_log(mensaje_textview, categoria="módulos", log_file=self.intall_log_modul)

    def seleccionar_modulo_ArchCarpet(self, widget=None, tipo=None):
        """
        Abre un diálogo para seleccionar un archivo (.modmeri) o una carpeta de módulos.

        Args:
            tipo (str): "Archivo" para seleccionar un archivo .modmeri, "Carpeta" para seleccionar un directorio.
        """
        # Definir configuración según tipo
        if tipo not in ["Archivo", "Carpeta"]:
            raise ValueError("El argumento 'tipo' debe ser 'Archivo' o 'Carpeta'.")

        titulo = "Abrir archivo de módulo" if tipo == "Archivo" else "Seleccionar carpeta de módulos"
        accion = Gtk.FileChooserAction.OPEN if tipo == "Archivo" else Gtk.FileChooserAction.SELECT_FOLDER
        boton_aceptar = "_Abrir" if tipo == "Archivo" else "_Seleccionar"

        # Crear diálogo
        ventana_seleccion = Gtk.FileChooserDialog(
            title=titulo,
            action=accion
        )
        ventana_seleccion.set_transient_for(self)
        ventana_seleccion.set_modal(True)

        ventana_seleccion.add_button("_Cancelar", Gtk.ResponseType.CANCEL)
        ventana_seleccion.add_button(boton_aceptar, Gtk.ResponseType.OK)

        # Si es selección de archivo, aplicar filtro
        if tipo == "Archivo":
            filtro_md = Gtk.FileFilter()
            filtro_md.set_name("Archivos de módulo MERIDA (.modmeri)")
            filtro_md.add_pattern("*.modmeri")
            ventana_seleccion.add_filter(filtro_md)

        
        def on_response_ArchCarpet(dialog, response_id, tipo):
            if response_id == Gtk.ResponseType.OK:

                if tipo == "Archivo":
                    ruta_seleccionada = dialog.get_file().get_path()
                    print(f"{'Archivo' if tipo == 'Archivo' else 'Carpeta'} seleccionado: {ruta_seleccionada}")
                    self.Instalar_Modulo_Accion(ruta_seleccionada)
                elif tipo == "Carpeta":
                    ruta_seleccionada = dialog.get_file().get_path()
                    print(f"{'Archivo' if tipo == 'Archivo' else 'Carpeta'} seleccionado: {ruta_seleccionada}")
                    self.Instalar_Modulo_Accion(ruta_seleccionada)
            dialog.destroy()

        ventana_seleccion.connect("response", on_response_ArchCarpet, tipo)
        ventana_seleccion.present()

    def Instalar_Modulo_Accion(self, ruta_modulo=None):
        """
        Realiza la instalación de módulos desde la ruta proporcionada.
        1. Verifica si la ruta es carpeta o archivo.
            - Si es carpeta: busca todos los archivos con extensión .modmeri y los añade a la lista.
            - Si es archivo: lo añade directamente a la lista si es .modmeri.
        2. Para cada archivo válido, revisa que:
            - El ZIP contenga 'Instruc_Install.json' y un archivo .py principal.
            - Los datos del JSON sean compatibles (nombre, id, versión).
        3. Copia el .py y recursos extra a la carpeta ~/.local/share/MERIDA/modulos/
        Además:
        - Muestra mensajes de registro en self.control_mensajes_Textview_Regist_A
        - Verifica dependencias indicadas en Instruc_Install.json y las informa
        """
        #Limpieza del textview
        self.textview_regist.get_buffer().set_text("")

        # Intento de importar importlib.metadata para revisar versiones instaladas
        try:
            from importlib.metadata import version as _pkg_version, PackageNotFoundError
            _can_check_deps = True
        except Exception:
            try:
                # fallback a importlib_metadata si está instalado
                from importlib.metadata import version as _pkg_version, PackageNotFoundError
                _can_check_deps = True
            except Exception:
                _pkg_version = None
                PackageNotFoundError = None
                _can_check_deps = False

        if not ruta_modulo:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label= "Error de instalación de módulo",
                mensaje_textview="[ERROR] No se proporcionó ninguna ruta. Instalación cancelada."
            )
            return

        rutas_validas = []

        #Verificar si es carpeta o archivo
        if os.path.isdir(ruta_modulo):
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Verificando ruta proporcionada...",
                mensaje_textview= "[INFO] Se detectó carpeta. Buscando archivos .modmeri..."
            )

            for archivo in os.listdir(ruta_modulo):
                if archivo.endswith(".modmeri"):
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview= f"[OK] Se encontró archivo: {archivo}..."
                    )
                    rutas_validas.append(os.path.join(ruta_modulo, archivo))

        elif os.path.isfile(ruta_modulo) and ruta_modulo.endswith(".modmeri"):
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Verificando ruta proporcionada...",
                mensaje_textview= f"[OK] Se detectó archivo .modmeri en {ruta_modulo}"
            )

            rutas_validas.append(ruta_modulo)

        else:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Error de instalación de módulo",
                mensaje_textview="[ERROR] La ruta proporcionada no es válida o no contiene archivos .modmeri. Instalación cancelada."
            )
            return

        if not rutas_validas:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Error de instalación de módulo",
                mensaje_textview="[ERROR] No se encontraron archivos .modmeri en la ruta proporcionada."
            )
            return

        # Carpeta de instalación de módulos (si no existe, la crea)
        carpeta_modulos = os.path.join(get_data_dir(), "modulos")
        self.control_mensajes_Textview_Regist_A(
            mensaje_label="Verificando carpeta de módulos...",
            mensaje_textview=f"[INFO] Verificando la existencia de la carpeta de módulos en {carpeta_modulos}..."
        )
        os.makedirs(carpeta_modulos, exist_ok=True)

        # Procesar cada archivo válido
        for ruta in rutas_validas:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Instalando módulo...",
                mensaje_textview=f"[INFO] Procesando módulo: {ruta}..."
            )
            try:
                with zipfile.ZipFile(ruta, 'r') as archivo_zip:
                    archivos_zip = archivo_zip.namelist()
                    
                    #Verificar que exista el JSON de instrucciones
                    if "Instruc_Install.json" not in archivos_zip:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación de módulo",
                            mensaje_textview=f"[ERROR] El módulo {ruta} no contiene Instruc_Install.json. Instalación cancelada."
                        )
                        return

                    # Leer y analizar el JSON
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Leyendo instrucciones de instalación desde Instruc_Install.json..."
                    )
                    with archivo_zip.open("Instruc_Install.json") as json_file:
                        datos = json.load(json_file)

                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[OK] Instrucciones de instalación leídas para {datos.get('Nombre_del_Modulo','<sin nombre>')} v{datos.get('version','?')}."
                    )

                    # ===== Verificación y mensajes sobre DEPENDENCIAS =====
                    deps_field = datos.get("Dependencias", None)
                    deps_list = []

                    # Normalizar dependencias a lista (acepta lista o string separado por comas)
                    if deps_field:
                        if isinstance(deps_field, list):
                            deps_list = [str(d).strip() for d in deps_field if str(d).strip()]
                        elif isinstance(deps_field, str):
                            if deps_field.strip().lower() not in ("ninguno", "none", ""):
                                # dividir por comas si es string
                                deps_list = [d.strip() for d in deps_field.split(",") if d.strip()]

                    if deps_list:
                        # Mensaje de sugerencia general
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label=None,
                            mensaje_textview=f"[SUGERENCIA] Detectado dependencias requeridas para el módulo {datos.get('Nombre_del_Modulo','<sin nombre>')}. Se recomienda verificar su existencia e instalarlos si no existen en su sistema."
                        )

                        # Mensaje que lista las dependencias tal como se especificaron
                        deps_formatted = ", ".join(deps_list)
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label=None,
                            mensaje_textview=f"[DEPENDENCIAS] Detectado las siguientes dependencias: {deps_formatted}"
                        )

                        # Intentar verificar si están instaladas y mostrar estado individual
                        if _can_check_deps and _pkg_version is not None:
                            for dep in deps_list:
                                # Extraer nombre base antes de cualquier operador (==,>=,<=,>,<)
                                import re
                                m = re.split(r"(==|>=|<=|>|<)", dep, maxsplit=1)
                                pkg_name = m[0].strip()
                                try:
                                    installed_ver = _pkg_version(pkg_name)
                                    self.control_mensajes_Textview_Regist_A(
                                        mensaje_label=None,
                                        mensaje_textview=f"[DEPENDENCIA] {pkg_name} — INSTALADO (versión: {installed_ver})"
                                    )
                                except PackageNotFoundError:
                                    self.control_mensajes_Textview_Regist_A(
                                        mensaje_label=None,
                                        mensaje_textview=f"[DEPENDENCIA] {pkg_name} — NO INSTALADO"
                                    )
                                except Exception as e_chk:
                                    self.control_mensajes_Textview_Regist_A(
                                        mensaje_label=None,
                                        mensaje_textview=f"[DEPENDENCIA] {pkg_name} — Estado desconocido. Error al comprobar: {e_chk}"
                                    )
                        else:
                            # No se puede comprobar programáticamente (informar)
                            self.control_mensajes_Textview_Regist_A(
                                mensaje_label=None,
                                mensaje_textview=f"[INFO] No fue posible comprobar automáticamente las dependencias en este entorno (importlib.metadata no disponible). Verifique manualmente: {deps_formatted}"
                            )
                    # ===== fin bloque dependencias =====

                    #Verificar que el archivo principal exista
                    archivo_principal = datos.get("Archivo_Principal")
                    if archivo_principal not in archivos_zip:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación de módulo",
                            mensaje_textview=f"[ERROR] El módulo {datos.get('Nombre_del_Modulo','<sin nombre>')} no contiene el archivo principal {archivo_principal}. Instalación cancelada."
                        )
                        return

                    #Copiar archivo principal a carpeta de módulos
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Copiando archivo principal {archivo_principal} a la carpeta de módulos...(se usará el id como nombre del archivo .py)"
                    )
                    destino_py = os.path.join(carpeta_modulos, f"{datos['id']}.py")
                    with archivo_zip.open(archivo_principal) as src, open(destino_py, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[OK] Archivo principal copiado a {destino_py} como {datos['id']}.py"
                    )

                    #Si hay recursos extra, extraerlos a carpeta específica
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Verificando y copiando recursos extra si existen..."
                    )
                    recursos_extras = datos.get("Recursos_extras")
                    # Se considera "Ninguno" como ausencia de recursos (tal como en tu ejemplo)
                    if recursos_extras and str(recursos_extras).strip().lower() != "ninguno":
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label=None,
                            mensaje_textview=f"[INFO] Recursos extra detectados. Copiando a carpeta específica..."
                        )
                        carpeta_recursos = os.path.join(carpeta_modulos, datos['id'])
                        os.makedirs(carpeta_recursos, exist_ok=True)

                        for recurso in archivos_zip:
                            # Se asume que los recursos van dentro de una carpeta 'recursos/' dentro del ZIP
                            if recurso.startswith("recursos/"):
                                archivo_zip.extract(recurso, carpeta_recursos)
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label=None,
                            mensaje_textview=f"[OK] Recursos extra copiados en {carpeta_recursos}."
                        )

                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label="Instalación completada con éxito",
                        mensaje_textview=f"[OK] Instalación de {datos.get('Nombre_del_Modulo','<sin nombre>')} completada."
                    )

            except zipfile.BadZipFile:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error de instalación de módulo",
                    mensaje_textview=f"[ERROR] El archivo {ruta} no es un ZIP válido. Instalación cancelada."
                )
            except json.JSONDecodeError:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error de instalación de módulo",
                    mensaje_textview=f"[ERROR] El archivo Instruc_Install.json en {ruta} no es un JSON válido. Instalación cancelada."
                )
            except Exception as e:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error de instalación de módulo",
                    mensaje_textview=f"[ERROR] Ocurrió un error inesperado al procesar {ruta}. Instalación cancelada. Detalles: {e}"
                )

