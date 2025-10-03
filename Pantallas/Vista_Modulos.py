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
from packaging import version
from datetime import datetime

from Lib_Extra.Rutas_Gestion import get_recursos_dir, get_data_dir
from Lib_Extra.Funciones_extras import escribir_log,obtener_ruta_icono_Preder,formatear_y_convertir_fecha

from BDs_Functions.Models_BD import BD_Moduls
from BDs_Functions.BD_Moduls_Funct import BD_Moduls_Functions

from Recursos.__MERIDA_METADATOS__ import MERIDA_Metadata
class pantalla_modulos(Gtk.Window):
    def __init__(self):
        super().__init__(title="Gestión de Módulos y Complementos")
        self.set_default_size(1000, 800)

        #==================INSTANCIAS DE CLASES==================
        self.BD_Moduls_Functions = BD_Moduls_Functions()
        self.MERIDA_METADATA = MERIDA_Metadata()


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
        
        self.Label_Sin_Modulos = Gtk.Label(label="Aún no hay módulos o complementos instalados.")

        self.FlowBox_Modulos = Gtk.FlowBox()
        self.FlowBox_Modulos.set_valign(Gtk.Align.START)
        self.FlowBox_Modulos.set_max_children_per_line(4)
        self.FlowBox_Modulos.set_selection_mode(Gtk.SelectionMode.NONE)

        dict_modulos_regist = self.BD_Moduls_Functions.obtener_datos_simples_Registros()
        
        if dict_modulos_regist:
            for id_modulo, datos in dict_modulos_regist.items():
                icono1 = self.crear_entrada_modulo(
                    icono_path=datos["icono"],
                    nombre_modulo=datos["nombre_modulo"],
                    version_modulo=datos["version"],
                    id_modulo = id_modulo)
                
                self.FlowBox_Modulos.append(icono1)

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

        if dict_modulos_regist:
            box_cent.append(self.FlowBox_Modulos)
        else:
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
        """
        # Limpieza del textview de registro
        self.textview_regist.get_buffer().set_text("")

        # Import dinámico para verificar dependencias externas
        try:
            #Se intenta, en primer lugar, con importlib.metadata (Python 3.8+)
            from importlib.metadata import version as _pkg_version, PackageNotFoundError
            _can_check_deps = True
        except Exception:
            try:
                #Si falla, se intenta con importlib_metadata (backport para Python <3.8) si esta instalado.
                from importlib_metadata import version as _pkg_version, PackageNotFoundError
                _can_check_deps = True
            except Exception:
                _pkg_version = None
                PackageNotFoundError = None
                _can_check_deps = False

        # Validar ruta proporcionada
        if not ruta_modulo:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Error de instalación de módulo",
                mensaje_textview="[ERROR] No se proporcionó ninguna ruta. Instalación cancelada."
            )
            return

        # Buscar rutas válidas (.modmeri)
        rutas_validas = self.descubrir_rutas_modmeri(ruta_modulo)
        
        if not rutas_validas:
            self.control_mensajes_Textview_Regist_A(
                mensaje_label="Error de instalación de módulo",
                mensaje_textview="[ERROR] No se encontraron archivos .modmeri en la ruta proporcionada."
            )
            return

        # Carpeta de instalación de módulos
        carpeta_modulos = os.path.join(get_data_dir(), "modulos")
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

                    # Verificar JSON de instalación
                    if "Instruc_Install.json" not in archivos_zip:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación de módulo",
                            mensaje_textview=f"[ERROR] El módulo {ruta} no contiene Instruc_Install.json. Instalación cancelada."
                        )
                        return

                    # Leer JSON
                    datos = json.load(archivo_zip.open("Instruc_Install.json"))

                    if not self.validar_datos_json(datos):
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación de módulo",
                            mensaje_textview=f"[ERROR] El JSON de {ruta} no contiene los campos requeridos. Instalación cancelada."
                        )
                        return

                    # Validar versión de MERIDA
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label="Verificando compatibilidad",
                        mensaje_textview="[INFO] Verificando versión mínima requerida de MERIDA..."
                    )
                    if not self.verificar_version_merida(datos, version.parse(self.MERIDA_METADATA.VERSION_DEL_PROGRAMA)):
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación de módulo",
                            mensaje_textview=(
                                f"[ERROR] El módulo {datos.get('Nombre_del_Modulo','<sin nombre>')} "
                                f"requiere MERIDA >= {datos.get('Version_Minima_MERIDA','1.0.0')}. "
                                f"Su versión actual es {self.MERIDA_METADATA.VERSION_DEL_PROGRAMA}. Instalación cancelada."
                            )
                        )
                        return

                    # Revisar dependencias
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview="[INFO] Verificando dependencias del módulo..."
                    )
                    deps_resultados = self.verificar_dependencias(datos, _can_check_deps, _pkg_version, PackageNotFoundError)
                    for dep, estado, info in deps_resultados:
                        if estado == "INSTALADO":
                            self.control_mensajes_Textview_Regist_A(None, f"[DEPENDENCIA] {dep} — INSTALADO (v{info})")
                        elif estado == "NO INSTALADO":
                            self.control_mensajes_Textview_Regist_A(None, f"[DEPENDENCIA] {dep} — NO INSTALADO")
                        else:
                            self.control_mensajes_Textview_Regist_A(None, f"[DEPENDENCIA] {dep} — DESCONOCIDO ({info})")

                    # Crear carpeta del módulo
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label="Procesando instalación de módulo",
                        mensaje_textview=f"[INFO] Creando carpeta para el módulo {datos['id']}..."
                    )
                    ruta_carpeta_modulo = os.path.join(carpeta_modulos, datos['id'])
                    os.makedirs(ruta_carpeta_modulo, exist_ok=True)

                    # Instalar archivo principal
                    self.control_mensajes_Textview_Regist_A(    
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Instalando archivo principal {datos['Archivo_Principal']} en {ruta_carpeta_modulo}..."
                    )
                    destino_py = self.instalar_archivo_principal(archivo_zip, datos, ruta_carpeta_modulo)
                    if not destino_py:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error",
                            mensaje_textview=f"[ERROR] El módulo {datos['id']} no tiene archivo principal válido. Instalación cancelada."
                        )
                        return
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[OK] Archivo principal instalado en {destino_py}."
                    )
                    # Instalar icono
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Instalando icono del módulo..."
                    )
                    destino_iconos = os.path.join(get_data_dir(), "Iconos_MERIDA")
                    icono_ubicacion = self.instalar_icono(archivo_zip, datos, destino_iconos)
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[OK] Icono instalado en {icono_ubicacion}."
                    )

                    # Instalar recursos extra
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Instalando recursos extras del módulo..."
                    )
                    recursos_path = self.instalar_recursos_extra(archivo_zip, datos, ruta_carpeta_modulo)
                    if recursos_path:
                        self.control_mensajes_Textview_Regist_A(None, f"[OK] Recursos extra copiados en {recursos_path}")
                    else:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label=None,
                            mensaje_textview=f"[INFO] No se requieren recursos extras."
                        )
                    # Registrar en la base de datos
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label=None,
                        mensaje_textview=f"[INFO] Registrando módulo en la base de datos..."
                    )
                    ok_registro = self.registrar_modulo(datos, destino_py, icono_ubicacion)
                    if not ok_registro:
                        self.control_mensajes_Textview_Regist_A(
                            mensaje_label="Error de instalación",
                            mensaje_textview=f"[ERROR] Ya existe un módulo con el ID {datos['id']} en la base de datos. Instalación cancelada."
                        )
                        return

                    # Instalación completada
                    self.control_mensajes_Textview_Regist_A(
                        mensaje_label="Instalación completada",
                        mensaje_textview=f"[OK] Instalación de {datos.get('Nombre_del_Modulo','<sin nombre>')} finalizada."
                    )

            except zipfile.BadZipFile:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error",
                    mensaje_textview=f"[ERROR] El archivo {ruta} no es un ZIP válido."
                )
            except json.JSONDecodeError:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error",
                    mensaje_textview=f"[ERROR] El archivo Instruc_Install.json en {ruta} no es válido (JSON mal formado)."
                )
            except Exception as e:
                self.control_mensajes_Textview_Regist_A(
                    mensaje_label="Error inesperado",
                    mensaje_textview=f"[ERROR] Ocurrió un error inesperado al procesar {ruta}: {e}"
                )

    def descubrir_rutas_modmeri(self,ruta_modulo):
        """
        Descubre los archivos .modmeri en la ruta dada.
        Retorna lista de rutas válidas o [] si no se encuentra nada.
        """
        rutas_validas = []

        if os.path.isdir(ruta_modulo):
            for archivo in os.listdir(ruta_modulo):
                if archivo.endswith(".modmeri"):
                    rutas_validas.append(os.path.join(ruta_modulo, archivo))

        elif os.path.isfile(ruta_modulo) and ruta_modulo.endswith(".modmeri"):
            rutas_validas.append(ruta_modulo)

        return rutas_validas

    def validar_datos_json(self, datos):
        """
        Valida que el JSON tenga los campos mínimos requeridos.
        Retorna True si es válido, False si falta algún campo.
        """
        campos_requeridos = [
            "id",
            "Archivo_Principal",
            "Nombre_del_Modulo",
            "version",
            "Version_Minima_MERIDA",
            "Autor_del_Modulo",
            "Correo_Electronico_del_Autor", 
        ]
        
        
        for campo in campos_requeridos:
            if campo not in datos or not datos[campo]:
                return False
        
        return True

    def verificar_version_merida(self, datos, version_actual_merida):
        """
        Compara la versión mínima requerida con la versión actual de MERIDA.
        Retorna True si es compatible, False si no.
        """
        version_requerida = version.parse(datos.get("Version_Minima_MERIDA", "1.0.0"))
        
        if version_actual_merida < version_requerida:
            return False
        
        return True

    def verificar_dependencias(self, datos, can_check_deps, _pkg_version, PackageNotFoundError):
        """
        Verifica las dependencias declaradas en el JSON.
        Retorna una lista de resultados en la forma:
        [("nombre_paquete", "INSTALADO"/"NO INSTALADO"/"DESCONOCIDO", "versión o error")]
        """
        resultados = []
        deps_field = datos.get("Dependencias", None)
        deps_list = []

        if deps_field:
            if isinstance(deps_field, list):
                deps_list = [str(d).strip() for d in deps_field if str(d).strip()]
            elif isinstance(deps_field, str):
                if deps_field.strip().lower() not in ("ninguno", "none", ""):
                    deps_list = [d.strip() for d in deps_field.split(",") if d.strip()]

        for dep in deps_list:
            estado, info = "DESCONOCIDO", ""
            if can_check_deps and _pkg_version is not None:
                import re
                m = re.split(r"(==|>=|<=|>|<)", dep, maxsplit=1)
                pkg_name = m[0].strip()
                try:
                    installed_ver = _pkg_version(pkg_name)
                    estado, info = "INSTALADO", installed_ver
                except PackageNotFoundError:
                    estado, info = "NO INSTALADO", ""
                except Exception as e:
                    estado, info = "DESCONOCIDO", str(e)
            resultados.append((dep, estado, info))

        return resultados

    def instalar_archivo_principal(self, archivo_zip, datos, ruta_destino):
        """
        Copia el archivo principal del módulo en la carpeta de destino.
        Retorna la ruta al archivo copiado o None si falla.
        """
        archivo_principal = datos.get("Archivo_Principal")
        if not archivo_principal or archivo_principal not in archivo_zip.namelist():
            return None

        destino_py = os.path.join(ruta_destino, f"{datos['id']}.py")
        try:
            with archivo_zip.open(archivo_principal) as src, open(destino_py, "wb") as dst:
                shutil.copyfileobj(src, dst)
            return destino_py
        except Exception:
            return None

    def instalar_icono(self, archivo_zip, datos, ruta_iconos):
        """
        Copia el icono del módulo a la carpeta de iconos de MERIDA.
        - Si no existe, retorna el icono predeterminado.
        - Si falla la copia, también retorna el icono predeterminado.
        Retorna la ruta final al icono.
        """
        ruta_icono_final_preder = obtener_ruta_icono_Preder()
        icono_arch = datos.get("icono")
        if not icono_arch or icono_arch not in archivo_zip.namelist():
            
            return ruta_icono_final_preder

        os.makedirs(ruta_iconos, exist_ok=True)
        nombre_icono_final = f"{datos['id']}.svg"
        ruta_icono_final = os.path.join(ruta_iconos, nombre_icono_final)

        try:
            with archivo_zip.open(icono_arch) as src, open(ruta_icono_final, "wb") as dst:
                shutil.copyfileobj(src, dst)
            return ruta_icono_final
        
        except Exception:
            return ruta_icono_final_preder
                                
    def instalar_recursos_extra(self, archivo_zip, datos, ruta_modulo_individual):
        """
        Extrae recursos extra desde el ZIP si existen en carpeta 'recursos/'.
        Retorna la ruta de la carpeta de recursos creada o None si no había recursos.
        """
        recursos_extras = datos.get("Recursos_extras")
        if not recursos_extras or str(recursos_extras).strip().lower() in ("ninguno", "none", ""):
            return None

        carpeta_recursos = os.path.join(ruta_modulo_individual, "recursos")
        os.makedirs(carpeta_recursos, exist_ok=True)

        for recurso in archivo_zip.namelist():
            if recurso.startswith("recursos/"):
                archivo_zip.extract(recurso, carpeta_recursos)

        return carpeta_recursos

    def registrar_modulo(self, datos, destino_py, icono_ubicacion):
        """
        Registra el módulo en la base de datos.
        Retorna True si se registró con éxito, False si ya existía.
        """
        if self.BD_Moduls_Functions.validar_unico("Identificador_Modulo", datos['id']) is not None:
            return False

        Registro_nuevo = BD_Moduls()
        Registro_nuevo.Nombre_Modulo = datos.get('Nombre_del_Modulo', '<sin nombre>')
        Registro_nuevo.Identificador_Modulo = datos['id']
        Registro_nuevo.Version_Modulo = datos.get('version', '<sin versión>')
        Registro_nuevo.Autor_Modulo = datos.get('Autor_del_Modulo', '<sin autor>')
        Registro_nuevo.CorreoElectronico_Autor = datos.get('Correo_Electronico_del_Autor', '<sin correo>')
        Registro_nuevo.Descripcion_Modulo = datos.get('descripcion', '<sin descripción>')
        Registro_nuevo.Arch_Principal_Ejecucion = datos.get('Archivo_Principal', '<sin archivo>')
        Registro_nuevo.Arch_Icono_Ubicacion = icono_ubicacion
        Registro_nuevo.Recursos_Adicionales = datos.get('Recursos_extras', '<sin recursos>')
        Registro_nuevo.Dependencias_Especiales = datos.get('Dependencias', '<sin dependencias>')
        Registro_nuevo.Estado_Modulo = True
        Registro_nuevo.Ubicacion_Modulo = destino_py

        self.BD_Moduls_Functions.registrar_nuevas_listas(Registro_nuevo)
        return True
 
    def crear_entrada_modulo(self, icono_path, nombre_modulo, version_modulo, id_modulo):
        """
        Crea un widget "visual" para representar un módulo instalado.
        Se compone de :
            1. Icono del módulo
            2. Nombre del módulo
            3. Versión del módulo
    
        El widget, al ser presionado, mostrará más detalles del módulo en una ventana aparte.
        Para mostrar dicha ventana, se usa como argumento el id_modulo, para realizar consultas
        a la base de datos.
        """

        btn_CR_Modulo = Gtk.Button()
        btn_CR_Modulo.set_hexpand(False)
        btn_CR_Modulo.set_vexpand(False)

        box_most = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box_text = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        box_image = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_image.set_halign(Gtk.Align.CENTER)
        box_image.set_hexpand(True)
        box_image.set_vexpand(True)

        #logo / icono
        if icono_path and os.path.exists(icono_path):
            logo = Gtk.Picture.new_for_filename(icono_path)
        else:
            logo = Gtk.Picture.new_for_filename(obtener_ruta_icono_Preder())

        logo.set_content_fit(Gtk.ContentFit.CONTAIN)
        logo.set_size_request(64, 64)  # tamaño fijo recomendado

        # Nombre del módulo y Version (texto)
        label_nombre = Gtk.Label()
        label_nombre.set_markup(f"<b>{nombre_modulo}</b>")
        label_nombre.set_xalign(0)

        label_version = Gtk.Label(label=f"v{version_modulo}")
        label_version.set_xalign(0)
        label_version.add_css_class("dim-label")  # estilo grisado de GTK


        btn_CR_Modulo.connect("clicked", self.mostrar_detalles_modulo, id_modulo)

        #Organización de widgets
        box_image.append(logo)

        box_text.append(label_nombre)
        box_text.append(label_version)

        box_most.append(box_image)
        box_most.append(box_text)

        btn_CR_Modulo.set_child(box_most)

        return btn_CR_Modulo

    def mostrar_detalles_modulo(self, widget=None, id_modulo=None):
        """
        Muestra una ventana con los detalles completos del módulo seleccionado.
        """
        datos_modulo = self.BD_Moduls_Functions.obtener_registro_ID(id_modulo)
        
        Vent_ModulInfor = Gtk.Dialog(
            title="Detalles del Módulo MERIDA",
            transient_for=self.get_root(),
            modal=True,
        )
        Vent_ModulInfor.set_default_size(1000, 400)
        
        #=======Contenedores================
        content_area = Vent_ModulInfor.get_content_area()

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(6)

        box_pr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        vbox_grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        vbox_btn = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)


        #==========Extras===================
        fecha_cruda = datos_modulo.get("fecha_instalacion")
        if fecha_cruda:
            # Usamos la función de conversión centralizada
            fecha_transformada = formatear_y_convertir_fecha(str(fecha_cruda))
        else:
            fecha_transformada = "Sin datos"


        # Transformar estado booleano
        estado_bool = datos_modulo.get("estado_modulo", False)
        estado_transformado = "Instalado" if estado_bool else "Sin Uso"

        def configurar_entry():
            return {
                "hexpand": True,
                "editable": False,
                "focusable": False
            }


        #======Widget======
        #Etiquetas
        label_nombre = Gtk.Label(label="Nombre del Módulo:", xalign=1.0)
        label_identificador = Gtk.Label(label="Identificador del Módulo:", xalign=1.0)
        label_version = Gtk.Label(label="Versión del Módulo:", xalign=1.0)
        label_autor = Gtk.Label(label="Autor del Módulo:", xalign=1.0)
        label_correoAutor = Gtk.Label(label="Correo electrónico del autor:", xalign=1.0)
        label_descripcion = Gtk.Label(label="Descripción del Módulo:", xalign=1.0)
        label_archPrincipal = Gtk.Label(label="Archivo Principal de Ejecución:", xalign=1.0)
        label_archIconoUbi = Gtk.Label(label="Ubicación del Icono del Módulo:", xalign=1.0)
        label_RecursAdic = Gtk.Label(label="Recursos Adicionales del Módulo:", xalign=1.0)
        label_DepenEspec = Gtk.Label(label="Dependencias Especiales del Módulo:", xalign=1.0)
        label_EstadoModul = Gtk.Label(label="Estado del Módulo:", xalign=1.0)
        label_fechaInstall = Gtk.Label(label="Fecha de Instalación:", xalign=1.0)
        label_ubiModulo = Gtk.Label(label="Ubicación del Módulo:", xalign=1.0)

        #Entrys
        Entry_nombre = Gtk.Entry(**configurar_entry())
        Entry_nombre.set_text(datos_modulo.get("nombre_modulo", "<sin-nombre>"))

        Entry_identificador = Gtk.Entry(**configurar_entry())
        Entry_identificador.set_text(datos_modulo.get("identificador_modulo", "<sin-identificador>"))

        Entry_version = Gtk.Entry(**configurar_entry())
        Entry_version.set_text(datos_modulo.get("version_modulo", "<sin-version>"))

        Entry_autor = Gtk.Entry(**configurar_entry())
        Entry_autor.set_text(datos_modulo.get("autor_modulo", "<sin-autor>"))

        Entry_correoAutor = Gtk.Entry(**configurar_entry())
        Entry_correoAutor.set_text(datos_modulo.get("correo_autor", "<sin-correo>"))

        TextView_Descripcion = Gtk.TextView(hexpand=True, vexpand=True)
        TextView_Descripcion.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        TextView_Descripcion.set_editable(False)
        TextView_Descripcion.set_focusable(False)
        TextView_Descripcion.get_buffer().set_text(datos_modulo.get("descripcion_modulo", "<sin-descripcion>"))

        Entry_ArchPrincipal = Gtk.Entry(**configurar_entry())
        Entry_ArchPrincipal.set_text(datos_modulo.get("arch_principal_ejecucion", "<sin-ArchPrincipal>"))

        Entry_ArchIconoUbi = Gtk.Entry(**configurar_entry())
        Entry_ArchIconoUbi.set_text(datos_modulo.get("arch_icono_ubi", "<sin-archiconoubi>"))

        Entry_RecursAdic = Gtk.Entry(**configurar_entry())
        Entry_RecursAdic.set_text(datos_modulo.get("recursos_adicionales", "<sin-datos>"))

        Entry_DepenEspec = Gtk.Entry(**configurar_entry())
        Entry_DepenEspec.set_text(datos_modulo.get("dependencias_especiales", "<sin-datos>"))

        Entry_EstadoModul = Gtk.Entry(**configurar_entry())
        Entry_EstadoModul.set_text(estado_transformado)

        Entry_FechaInstall = Gtk.Entry(**configurar_entry())
        Entry_FechaInstall.set_text(fecha_transformada)

        Entry_UbiModulo = Gtk.Entry(**configurar_entry())
        Entry_UbiModulo.set_text(datos_modulo.get("ubicacion_modulo", "<sin-datos>"))
        
        #Botones
        btn_desinstalarModul = Gtk.Button(label="Desinstalar Módulo")



        #=======Posicionamiento de Wigets===========
        Para_Pos = [
            (label_nombre, Entry_nombre),
            (label_identificador, Entry_identificador),
            (label_version, Entry_version),
            (label_autor, Entry_autor),
            (label_correoAutor, Entry_correoAutor),
            (label_descripcion, TextView_Descripcion),
            (label_archPrincipal, Entry_ArchPrincipal),
            (label_archIconoUbi, Entry_ArchIconoUbi),
            (label_RecursAdic, Entry_RecursAdic),
            (label_EstadoModul, Entry_EstadoModul),
            (label_DepenEspec, Entry_DepenEspec),
            (label_fechaInstall, Entry_FechaInstall),
            (label_ubiModulo, Entry_UbiModulo)
        ]

        for i, (etiqueta, contenido) in enumerate(Para_Pos):
            grid.attach(etiqueta, 0, i, 1, 1) #col, fila, with, height
            grid.attach(contenido, 1, i, 1, 1) #col1, fila i, ocupa 1x1


        vbox_btn.append(btn_desinstalarModul)

        vbox_grid.append(grid)

        box_pr.append(vbox_grid)
        box_pr.append(vbox_btn)

        content_area.append(box_pr)
        Vent_ModulInfor.show()