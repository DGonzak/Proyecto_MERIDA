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



import os
from platformdirs import user_documents_path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

from Pantallas.Pantalla_Principal import Pantalla_Principal
from Pantallas.Clases_Pantalla_Administrativa.Vista_BaseDeDatos import Vista_Base_De_Datos
from Pantallas.Clases_Pantalla_Administrativa.Vista_AjustesEstilo import Vista_AjustesEstilo

from Lib_Extra.Rutas_Gestion import inicializar_carpetas, get_recursos_dir, get_data_dir,get_cache_dir
from Lib_Extra.Funciones_extras import escribir_log, leer_archivo_recurrente

from BDs_Functions.Constructor_BDs import crear_BDs_Constructor
from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions

# ==========================================================
# Ventana Splash con progreso
# ==========================================================
class Splash(Gtk.Window):
    def __init__(self, app):
        super().__init__(title="Cargando MERIDA", application=app)
        self.set_default_size(900, 300)
        self.set_resizable(False)
        
        # Logo
        self.LOGO_COMPLETO = os.path.join(
            get_recursos_dir(), "Imágenes", "Logos_MERIDA_Completo_Sin-Fondo_02.svg"
        )

        #Cargar o leer configuración inicial guardada
        self.Dict_ConfigInicial = leer_archivo_recurrente("Dict_Config_Inicial.json", "json")

        # Estructura principal
        self.box_pr = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15,
            margin_top=20,
            margin_bottom=20,
            margin_start=20,
            margin_end=20,
        )
        self.set_child(self.box_pr)

        # Logo
        self.box_logo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        logo = Gtk.Picture.new_for_filename(self.LOGO_COMPLETO)
        logo.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
        logo.set_size_request(300, 200)
        self.box_logo.append(logo)

        # Info
        self.box_infor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.label_estado = Gtk.Label(label="Iniciando...")
        self.label_estado.set_xalign(0)

        #Barra de progreso
        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)

        #Spinner
        self.Spinner_infor = Gtk.Spinner()


        self.TextView_Infor_Cons = Gtk.TextView()
        self.TextView_Infor_Cons.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.TextView_Infor_Cons.set_editable(False)
        self.TextView_Infor_Cons.set_focusable(False)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(self.TextView_Infor_Cons)
        scroll.set_size_request(150, 150)
        scroll.set_vexpand(True)

        self.box_infor.append(self.label_estado)
        self.box_infor.append(self.Spinner_infor)
        self.box_infor.append(self.progress)
        self.box_infor.append(scroll)

        # Añadir a la ventana principal
        self.box_pr.append(self.box_logo)
        self.box_pr.append(self.box_infor)

        # Lista de pasos con funciones
        self.pasos = [
            ("Inicializando carpetas...", self.verificar_carpetas),
            ("Verificando recursos...", self.verificar_recursos),
            ("Finalizando...", self.finalizar),
        ]
        self.paso_actual = 0

        #Se crea el archivo log para registrar en el log de inicio (Startup)
        #log_startup contiene la ruta del archivo
        self.log_startup = escribir_log("===Inicio de Sesión MERIDA===", categoria="startup")

        self.Vista_Ajustes_de_Estilo = Vista_AjustesEstilo()
        self.Vista_Ajustes_de_Estilo.Aplicar_Tema_SUP()
        
        # Lanzar el primer paso después de 200ms para no bloquear el inicio (problema con gtk)
        GLib.timeout_add(200, self.ejecutar_siguiente_paso, app)

    # ==========================================================
    # CONTROL DE MENSAJES
    # ==========================================================
    def control_mensajes_infor_C(self, mensaje_label=None, mensaje_textview=None):
        """Muestra mensajes en el label y/o en el TextView del Splash."""
        if mensaje_label is not None:
            self.label_estado.set_text(mensaje_label)

        if mensaje_textview is not None:
            buffer_tv = self.TextView_Infor_Cons.get_buffer()
            texto_actual = buffer_tv.get_text(
                buffer_tv.get_start_iter(), buffer_tv.get_end_iter(), True
            )
            nuevo_texto = texto_actual + mensaje_textview + "\n"
            buffer_tv.set_text(nuevo_texto)

            #Guardar en log startup
            escribir_log(mensaje_textview, categoria="startup", log_file=self.log_startup)

    # ==========================================================
    # FUNCIONES DE VERIFICACIÓN
    # ==========================================================
    def verificar_carpetas(self, app=None):
        #==========================================================
        #Carpetas principales (críticas para que el programa inicie)
        #===========================================================
        self.control_mensajes_infor_C(None, "Revisando existencia de carpetas principales para MERIDA...")

        resultados = inicializar_carpetas()
        for ruta, estado, error in resultados:
            if error:
                self.control_mensajes_infor_C(
                    None, f" [ERROR] Se ha detectado un error en {ruta}: {error}"
                )
            else:
                self.control_mensajes_infor_C(
                    None, f"[OK] Carpeta {ruta} verificada ({estado})"
                )

        #=======================================================
        #Carpetas secundarias (predeterminada, resguardos, etc)
        #===========================================================
        self.control_mensajes_infor_C(None, "Revisando carpetas secundarias para MERIDA...")

        #------------------Carpeta de Resguardos de BDs-----------------------------------
        dir_bdsResguardos = os.path.join(get_data_dir(), "BDs", "Resguardos_BD")
        self.control_mensajes_infor_C(
            None, f"Verificando carpetas de respaldos predeterminados en {dir_bdsResguardos}")

        if not os.path.exists(dir_bdsResguardos):
            self.control_mensajes_infor_C(
                None,
                "[INFO] No se ha detectado carpeta de respaldos. Creando carpeta de respaldos...")
            os.makedirs(dir_bdsResguardos, exist_ok=True)
            self.control_mensajes_infor_C(None, "[OK] Creación exitosa de la carpeta de respaldos.")
        else:
            self.control_mensajes_infor_C(
                None, "[OK] Se ha detectado la carpeta de respaldos. Verificación exitosa.")
        #--------------------------Carpeta de Archivos Temporales------------------------

        dir_ArchTmp = os.path.join(get_cache_dir(), "Archivos_Temporales")
        self.control_mensajes_infor_C(
            None, f"Verificando carpetas de archivos temporales en {dir_ArchTmp}")

        if not os.path.exists(dir_ArchTmp):
            self.control_mensajes_infor_C(
                None,
                "[INFO] No se ha detectado carpeta de archivos temporales. Creando carpeta de archivos temporales...")
            os.makedirs(dir_ArchTmp, exist_ok=True)
            self.control_mensajes_infor_C(
                None,
                "[OK] Creación exitosa de la carpeta de archivos temporales.")
        else:
            self.control_mensajes_infor_C(
                None,
                "[OK] Se ha detectado la carpeta de archivos temporales. Verificación exitosa.")
        #-------------------------Carpeta de Iconos de MERIDA----------------------------
        dir_Iconos = os.path.join(get_data_dir(), "Iconos_MERIDA")
        self.control_mensajes_infor_C(
            None, f"Verificando carpeta de iconos de MERIDA en {dir_Iconos}")
        
        if not os.path.exists(dir_Iconos):
            self.control_mensajes_infor_C(
                None,
                "[INFO] No se ha detectado carpeta de iconos. Creando carpeta de iconos...")
            os.makedirs(dir_Iconos, exist_ok=True)
            self.control_mensajes_infor_C(None, "[OK] Creación exitosa de la carpeta de iconos.")
        else:
            self.control_mensajes_infor_C(
                None, "[OK] Se ha detectado la carpeta de iconos. Verificación exitosa.")
        #-------------------------Carpeta Predeterminada de Guardado----------------------
        self.RUTA_PREDETERMINADA = os.path.join(user_documents_path(), "MERIDA")
        self.control_mensajes_infor_C(
            None, f"Verificando carpeta predeterminada de guardado en {self.RUTA_PREDETERMINADA}")

        if self.Dict_ConfigInicial is None:
            # No existe archivo de config → primer inicio
            self.control_mensajes_infor_C(
                None, "[INFO] No se detectó configuración inicial. Primer inicio confirmado. Creando carpeta predeterminada...")
            
            os.makedirs(self.RUTA_PREDETERMINADA, exist_ok=True)
            
            self.control_mensajes_infor_C(
                None, "[OK] Carpeta predeterminada creada exitosamente en primer inicio.")

        else:
            # Existe archivo, revisar flag
            Si_PrimerInicio = self.Dict_ConfigInicial.get("Prm_Inicio", False)

            if Si_PrimerInicio:
                self.control_mensajes_infor_C(
                    None, "[INFO] Configuración indica primer inicio. Creando carpeta predeterminada...")
                os.makedirs(self.RUTA_PREDETERMINADA, exist_ok=True)
                self.control_mensajes_infor_C(
                    None, "[OK] Carpeta predeterminada creada exitosamente.")
            else:
                self.control_mensajes_infor_C(
                    None, "[OK] No es el primer inicio. Carpeta predeterminada no requiere modificaciones.")

        return True

    def verificar_recursos(self, app=None):
        self.control_mensajes_infor_C(None, "Verificando recursos y bases de datos...")

        dir_bds = os.path.join(get_data_dir(), "BDs")
        list_archivos_bds_a_buscar = [
            "BD_ComTecl",
            "BD_Informadora",
            "BD_RecentArch",
            "BD_TAGS",
        ]

        lista_bds_a_construir = []
        for bd in list_archivos_bds_a_buscar:
            ruta_espec_de_archivo = os.path.join(dir_bds, f"{bd}.sqlite")

            if not os.path.exists(ruta_espec_de_archivo):
                self.control_mensajes_infor_C(None, f"[ERROR] BD faltante: {bd}")
                lista_bds_a_construir.append(bd)
            else:
                self.control_mensajes_infor_C(None, f"[OK] BD encontrada: {bd}")

        # Si faltan, reconstruir
        if lista_bds_a_construir:
            self.control_mensajes_infor_C(
                None, f"Reconstruyendo BDs: {', '.join(lista_bds_a_construir)}"
            )
            try:
                crear_BDs_Constructor(lista_bds_a_construir)
                self.control_mensajes_infor_C(None, "[OK] BDs reconstruidas correctamente.")
            except Exception as e:
                self.control_mensajes_infor_C(None, f"[ERROR] Falló la construcción de BDs: {e}")
                return False

        # Ahora asegurar predeterminados (siempre, tanto si se crearon como si ya estaban)
        try:
            self.control_mensajes_infor_C(
                None, "Insertando valores predeterminados en las bases de datos..."
            )
            #Instanciamos la clase y llamamos a la función
            self.Vista_Base_De_Datos = Vista_Base_De_Datos()
            self.Vista_Base_De_Datos.minifunción_asegur_preder()

            #Hacemos lo mismo pero para las combinaciones de teclas
            self.BD_ComTecl_Functions = BD_ComTecl_Functions()
            self.BD_ComTecl_Functions.asegurar_entradas_preder()

            self.control_mensajes_infor_C(None, "[OK] Valores predeterminados asegurados.")
        except Exception as e:
            self.control_mensajes_infor_C(None, f"[ERROR] Falló al asegurar predeterminados: {e}")
            return False

        return True

    def finalizar(self, app=None):
        self.control_mensajes_infor_C("Iniciando aplicación principal...", None)
        self.destroy()
        ventana = Pantalla_Principal(application=app)
        ventana.present()
        return False

    # ==========================================================
    # GESTIÓN DE PASOS
    # ==========================================================
    def ejecutar_siguiente_paso(self, app):
        self.Spinner_infor.start()

        if self.paso_actual < len(self.pasos):
            texto, funcion = self.pasos[self.paso_actual]
            self.control_mensajes_infor_C(mensaje_label=texto)

            self.progress.set_fraction((self.paso_actual + 1) / len(self.pasos))
            self.progress.set_text(f"{self.paso_actual + 1} / {len(self.pasos)}")

            # Ejecutar función asociada
            if app is not None:
                funcion(app)
            else:
                funcion()

            self.paso_actual += 1
            # Esperar N segundos antes del siguiente paso
            GLib.timeout_add_seconds(1, self.ejecutar_siguiente_paso, app)
        self.Spinner_infor.stop()
        return False


# ==========================================================
# Aplicación principal
# ==========================================================
class MERIDA(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.dgonzakLA.MERIDA")

    def do_activate(self):
        splash = Splash(self)
        splash.present()


if __name__ == "__main__":
    app = MERIDA()
    app.run()

