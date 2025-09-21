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
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Pango, GLib, GdkPixbuf, Gio, GObject, Adw

from functools import partial
import re
import os
import zipfile
import json
from platformdirs import user_documents_path


from Pantallas.Clases_Pantalla_Principal.Panel_lateral_Derecha.Arbol_de_Archivos_Recientes import Pestana_Recientes
from Pantallas.Clases_Pantalla_Principal.Panel_lateral_Derecha.Arbol_de_Archivos_Etiquetas import Pestana_ArbolArch_Etiquetas
from Pantallas.Clases_Pantalla_Principal.Panel_lateral_Derecha.Tablero_de_Notificaciones import Pestana_Notificaciones
from Pantallas.Clases_Pantalla_Principal.Panel_lateral_Izquierda.Pestana_NotasTex import Pestana_Notas_Tex
from Pantallas.Clases_Pantalla_Principal.Espacio_Central.Editor_Central import Vista_Editor_Central

from Pantallas.Pantalla_de_listas import pantalla_listas
from Pantallas.Pantalla_Acerca_de import Pantalla_AcercaDe

from Pantallas.Pantalla_administrativa import pantalla_admins
from Pantallas.Clases_Pantalla_Administrativa.Vista_BaseDeDatos import Vista_Base_De_Datos
from Pantallas.Clases_Pantalla_Administrativa.Vista_AjustesEstilo import Vista_AjustesEstilo

from Lib_Extra.Funciones_extras import Reempla_espacios_nombre, mostrar_vent_IEO, aplicar_estilos_css, control_label_estado, Restaurar_espacios_nombre,leer_archivo_recurrente,filtrar_archivos_por_extension_BD,crear_archivos_recurrentes
from Lib_Extra.Rutas_Gestion import get_data_dir,get_recursos_dir
from Lib_Extra.Gestion_Dict_EDITOR import Gestor_Variable_ActuEtiquetas

from BDs_Functions.Models_BD import BD_Tags_General, BD_Comb_Teclas, BD_Recient_Arch
from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions
from BDs_Functions.BD_TAGS_Funct import BD_TAGS_Functions
from BDs_Functions.BD_RecentArch_Funct import BD_Recient_Arch_Functions
from BDs_Functions.BD_Utilidades_Generales import BD_UtilidadesGenerales
from BDs_Functions.BD_Informadora_Funct import BD_Informadora_Functions

class Pantalla_Principal(Gtk.ApplicationWindow):
    """
    Clase que contiene el contenido principal del editor MERIDA. A partir de ella se
    extraen las demás ventanas. 

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("MERIDA") 

        #=======================================================
        #INICIALIZADORES
        #====================================================
        self.BD_TAGS_Functions = BD_TAGS_Functions()
        self.BD_ComTecl_Functions = BD_ComTecl_Functions()
        self.BD_Recient_Arch_Functions = BD_Recient_Arch_Functions()
        self.BD_Utilidades_Generales = BD_UtilidadesGenerales()
        self.BD_Informadora_Functions = BD_Informadora_Functions()
        
        self.Vista_Editor_Central = Vista_Editor_Central(self)
        self.Vista_BaseDeDatos = Vista_Base_De_Datos()
        self.Vista_Ajustes_de_Estilo = Vista_AjustesEstilo()

        """Se pasa self a la Pestana_Recientes para que esta pueda tener acceso a las 
        funciones de la ventana principal. No funciona al reves, solo de Pestana_Recientes 
        a Pantalla_Principal, es decir, la pantalla principal no tiene acceso a las funciones 
        de Pestana Recientes.""" 
        self.Pestana_Notas_Tex_get = Pestana_Notas_Tex(self) 
        self.Pestana_Recientes_get = Pestana_Recientes(self) 
        self.Pestana_ArbolArch_Etiquetas_get = Pestana_ArbolArch_Etiquetas(self)
        self.Pestana_de_Notificaciones_get = Pestana_Notificaciones()

        self. Gestor_Variable_ActuEtiquetas = Gestor_Variable_ActuEtiquetas()
        
        ruta_estilos = os.path.join(get_recursos_dir(), "Estilo_CSS", "estilo_base.css")
        aplicar_estilos_css(ruta_css=ruta_estilos)

        #=====================================================
        # Configuración de la ventana (tamaño, etc)
        #=====================================================
        # Leemos el diccionario de configuración
        self.dict_config_VentYPaneds_GET = leer_archivo_recurrente(
            "Configuracion_de_VentanaYPaneds.json", "json"
        )

        # Si existe configuración guardada
        if self.dict_config_VentYPaneds_GET:
            estado_max = self.dict_config_VentYPaneds_GET.get("estado_VentMaximizada", False)

            if estado_max:
                # Abrimos maximizada
                self.maximize()
            else:
                # Recuperamos tamaño almacenado o valores por defecto
                ancho_vent = self.dict_config_VentYPaneds_GET.get("ancho_ventana", 1000)
                alto_vent = self.dict_config_VentYPaneds_GET.get("alto_ventana", 800)
                self.set_default_size(ancho_vent, alto_vent)

        # Si no existe configuración guardada, aplicamos valores por defecto (maximizada)
        else:
            self.maximize()


        
        

        #--------Tema------------------------
        self.Vista_Ajustes_de_Estilo.Aplicar_Tema_SUP()
        self.sync_theme()
        self.style_manager.connect("notify::dark", self.sync_theme)
        
        #==================================================
        #Contenedores
        #================================================

        # --------------------Contenedores Principales-----------------------
        self.Overlay_Present = Gtk.Overlay()

        self.VBox_Principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Superior
        self.hbox_SuperiorSec = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Central
        self.hbox_CentralSec = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.hbox_CentralSec.set_hexpand(True)
        
        # Inferior
        self.hbox_InferiorSec = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.hbox_InferiorSec.set_hexpand(True)
        


        # ------------------------- CONTENEDORES SECUNDARIOS --------------------
        # Paned izquierda (barra lateral izquierda + editor central)
        self.Paned_Panel_Izquierda_Exterior = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        #Paned Derecha (barra lateral derecha + navegación)
        self.Paned_Panel_Derecha_Interior = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        
        espaciador_Superior = Gtk.Box()
        espaciador_Superior.set_hexpand(True)

        boton_SUP_Árbol = Gtk.Button(label="☰")
        boton_SUP_Árbol.connect("clicked", self.Mostrar_Ocultar_BarraÁrbol)

        #===========================================
        #Extras
        #=========================================
        espaciador_Superior = Gtk.Box()
        espaciador_Superior.set_hexpand(True)
        boton_SUP_Árbol = Gtk.Button(label="☰")
        boton_SUP_Árbol.connect("clicked", self.Mostrar_Ocultar_BarraÁrbol)
        

        self.RUTA_PREDETERMINADA = os.path.join(user_documents_path(), "MERIDA")
        self.BD_TAGS_Functions.asegurar_etiqueta_predeterminada(self, self.RUTA_PREDETERMINADA)
        self.Vista_BaseDeDatos.mostrar_pantalla_de_recuperacion_ReconstBDs(self)

        #=============================================
        #Controladores
        #==============================================
        self.barra_lateral_SUP_Visible = True
        self.lista_notas_SUP = []
        self.Contenido_Modificado_SUP = False
        self.Ignorar_Cambios = False

        #=============================================
        #FIN
        #===========================================
        
        #====================Orden de Empaquetado======================

        #SUPERIOR
        self.hbox_SuperiorSec.append(self.crear_barraMenú())
        self.hbox_SuperiorSec.append(espaciador_Superior)
        self.hbox_SuperiorSec.append(boton_SUP_Árbol)
        

        #CENTRAL

        # El paned exterior: barra izquierda ↔ paned interior
        self.Paned_Panel_Izquierda_Exterior.set_start_child(self.crear_barraLateral_Izquierda())
        self.Paned_Panel_Izquierda_Exterior.set_end_child(self.Paned_Panel_Derecha_Interior)

        # El paned interior: editor central ↔ barra derecha
        self.Paned_Panel_Derecha_Interior.set_start_child(self.Vista_Editor_Central)
        self.Paned_Panel_Derecha_Interior.set_end_child(self.crear_barraLateral_Derecha())

        self.hbox_CentralSec.append(self.Paned_Panel_Izquierda_Exterior)

        #INFERIOR
        self.hbox_InferiorSec.append(self.crear_espacio_inferior())

        #BOX PRINCIPAL
        self.VBox_Principal.append(self.hbox_SuperiorSec)
        self.VBox_Principal.append(self.hbox_CentralSec)
        self.VBox_Principal.append(self.hbox_InferiorSec)

        #Incorporación del Box Principal al overlay de presentación
        self.Overlay_Present.set_child(self.VBox_Principal)

        #INCORPORACIÓN A LA VENTANA
        self.set_child(self.Overlay_Present)


        # ==================== AJUSTES DEL INIT ===================
        
        self.loading_overlay = None

        self.mostrar_overlay("Configurando interfaz...", "MERIDA")

        for text_view in (
            self.Vista_Editor_Central.text_view_titulo,
            self.Vista_Editor_Central.text_view_etiquetas,
            self.Vista_Editor_Central.text_view_cuerpo):
            
            buffer = text_view.get_buffer()
            buffer.connect("changed", self.marcar_contenido_modificado)

        
        self.registrar_atajos_globales()
        self.Verificar_Respaldo_Automático()
        
        #Se pone el foco cuando "gtk" este "listo"
        self.Vista_Editor_Central.text_view_titulo.grab_focus()

        self.connect("map", self.aplicar_posicion_paned)
        self.connect("close-request", self.on_quit)
    #==================================================
    #Funciones
    #===============================================
    
    #-------Funciones relacionadas a la organización y creación de widgets---------------

    def aplicar_posicion_paned(self, *args):
        """
        Aplica la posición guardada de los paneds cuando ya tienen ancho real.
        Usa un pequeño polling con GLib.timeout_add hasta que los paneds tengan
        un allocated_width razonable, o hasta agotar reintentos.
        """
        config = self.dict_config_VentYPaneds_GET or {}
        fracI = config.get("posicion_paned_izquierdo", 0.2)
        fracD = config.get("posicion_paned_derecho", 0.2)

        MAX_ATTEMPTS = 40        # cuántas veces reintentamos
        INTERVAL_MS = 25         # cada cuántos ms reintentamos
        MIN_VALID_WIDTH = 30     # umbral para considerar ancho 'válido' (px)

        state = {"attempts": 0}

        def _try_apply():
            state["attempts"] += 1

            wI = self.Paned_Panel_Izquierda_Exterior.get_allocated_width()
            wD = self.Paned_Panel_Derecha_Interior.get_allocated_width()

            # Si ambos paneds tienen ancho válido aplicamos y terminamos
            if wI and wD and wI >= MIN_VALID_WIDTH and wD >= MIN_VALID_WIDTH:
                posI = int(wI * fracI)
                posD = int(wD * fracD)
                try:
                    self.Paned_Panel_Izquierda_Exterior.set_position(posI)
                    self.Paned_Panel_Derecha_Interior.set_position(posD)

                except Exception as e:
                    # en caso extremo, todavía seguimos (no fatal)
                    print("Error al set_position:", e)

                #Cuando termine de posicionar, se quita el overlay
                #Nota: Esto solo se ejecutará si hubo un CAMBIO en la posición de los paneds
                self.ocultar_overlay()
                return False  # cancelar el timeout
            

            # Si agotamos intentos, aplicamos fallback prudente y terminamos
            if state["attempts"] >= MAX_ATTEMPTS:
                # Aplicar posiciones si hay algo de ancho, si no usar defaults
                if wI and wI > 0:
                    self.Paned_Panel_Izquierda_Exterior.set_position(int(wI * fracI))
                else:
                    self.Paned_Panel_Izquierda_Exterior.set_position(130)

                if wD and wD > 0:
                    self.Paned_Panel_Derecha_Interior.set_position(int(wD * fracD))
                else:
                    self.Paned_Panel_Derecha_Interior.set_position(450)
                
                #Se retira el overlay
                #Nota: Esto se ejecuta si los paneds no sufrieron cambios por el usuario.
                self.ocultar_overlay()
                return False

            # Repetir el chequeo tras INTERVAL_MS milisegundos
            return True

        # Lanza el reintento periódico (se cancelará cuando _try_apply devuelva False)
        GLib.timeout_add(INTERVAL_MS, _try_apply)

    def crear_barraMenú(self):
        """
        Función encargada de "crear" la barra del menú.

        """
        # ---------------------------ACCIONES------------------------------------------
        acciones = {
            "abrir": self.abrir_archivo_md,
            "guardar": self.guardar_archivo_md,
            "salir": self.on_quit,
            "preferencias": self.abrir_ajustes,
            "listas": self.abrir_listas,
            "acerca": self.abrir_Acercade,
            "nuevo": self.limpiar_todo,
        }

        for nombre, callback in acciones.items():
            accion = Gio.SimpleAction.new(nombre, None)
            accion.connect("activate", callback)
            self.add_action(accion)

        # ---------------------------MENÚS------------------------------------------
        menu = Gio.Menu()

        # Menú "Archivo"
        menu_archivo = Gio.Menu()
        menu_archivo.append("Abrir", "win.abrir")
        menu_archivo.append("Nuevo", "win.nuevo")
        menu_archivo.append("Guardar", "win.guardar")
        menu_archivo.append("Salir de la Aplicación", "win.salir")
        menu.append_submenu("Archivo", menu_archivo)

        # Menú "Administrar"
        menu_admin = Gio.Menu()
        menu_admin.append("Preferencias", "win.preferencias")
        menu_admin.append("Ver listas", "win.listas")
        menu.append_submenu("Administrar", menu_admin)

        # Menú "Ayuda"
        menu_ayuda = Gio.Menu()
        menu_ayuda.append("Acerca de...", "win.acerca")
        menu.append_submenu("Ayuda", menu_ayuda)

        # ---------------------------BOTÓN DE MENÚ------------------------------------------
        boton_menu = Gtk.MenuButton(icon_name="open-menu-symbolic")
        popover = Gtk.PopoverMenu.new_from_model(menu)
        boton_menu.set_popover(popover)

        # ---------------------------AGREGAR A LA INTERFAZ-----------------------------------
        return boton_menu

    def crear_barraLateral_Izquierda(self):
        """
        Función encargada de "crear" la barra lateral izquierda. Esta recibe los contenedores
        (Gtk.Box) importados desde otro archivo. Esto permite manejar de mejor manera
        los contenidos a crear. 

        """
        #------------------Contenedores-------------------------
        self.vbox_Izquierda = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.Notebook_Izquierda = Gtk.Notebook()

        scroll_NotebookI = Gtk.ScrolledWindow()
        scroll_NotebookI.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_NotebookI.set_child(self.Notebook_Izquierda)
        scroll_NotebookI.set_vexpand(True) 
        # ----------------Barra Lateral Izquierda------------------------------------

        self.Notebook_Izquierda.append_page(self.Pestana_Notas_Tex_get, Gtk.Label(label="Notas"))
        
        self.vbox_Izquierda.append(scroll_NotebookI)

        return self.vbox_Izquierda

    def crear_espacio_inferior(self):
        #--------Contenedores----------
        hbox_espacio_Inferior = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Estado inferior
        self.progress_bar = Gtk.ProgressBar()

        #expandir horizontalmente la barra de estado
        self.progress_bar.set_hexpand(True)

        self.status_label = Gtk.Label(label="Estado: Esperando acción.")
        self.status_label.set_halign(Gtk.Align.END)

        hbox_espacio_Inferior.append(self.progress_bar)
        hbox_espacio_Inferior.append(self.status_label)

        return hbox_espacio_Inferior

    def crear_barraLateral_Derecha(self):
        """
        Crea y configura la barra lateral derecha del editor, que contiene un Gtk.Notebook
        con dos pestañas: "Recientes" y "Archivos".

        - La primera pestaña contiene archivos abiertos recientemente.
        - La segunda pestaña muestra un árbol de archivos por carpetas (usando TreeListModel y ListView).
        - Finalmente, el notebook se añade al contenedor vertical `vbox_Derecha`.

        Esta función no retorna ningún valor, y modifica los atributos del objeto `self`.
        Al igual que otras funciones, sus componentes son importados desde archivos externos.
        """

        #-----------------Contenedores-----------------------
        self.vbox_Derecha = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.Notebook_Derecha = Gtk.Notebook()

        scroll_NotebookD = Gtk.ScrolledWindow()
        scroll_NotebookD.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_NotebookD.set_child(self.Notebook_Derecha)
        scroll_NotebookD.set_vexpand(True)

        ## === PESTAÑA 1: ARCHIVOS RECIENTES (Desde BD_RecentArch)
        self.Notebook_Derecha.append_page(self.Pestana_Recientes_get, Gtk.Label(label="Recientes"))

        ## ==== PESTAÑA 2: ARCHIVOS POR CARPETAS (TreeListModel + ListView) ====
        self.Notebook_Derecha.append_page(self.Pestana_ArbolArch_Etiquetas_get, Gtk.Label(label="Archivos"))

        ##==== PESTAÑA 3: TABLERO DE NOTIFICACIONES =====
        self.Notebook_Derecha.append_page(self.Pestana_de_Notificaciones_get, Gtk.Label(label="Avisos"))


        self.vbox_Derecha.append(scroll_NotebookD)
        return self.vbox_Derecha

    def mostrar_overlay(self, mensaje="Cargando...", logo_texto="MERIDA"):
        """
        Muestra un overlay de carga sobre toda la ventana principal.
        """
        # Si ya existe, lo quitamos primero
        if self.loading_overlay:
            self.Overlay_Present.remove_overlay(self.loading_overlay)

        # Contenedor principal del overlay
        overlay_box = Gtk.Overlay()
        overlay_box.set_hexpand(True)
        overlay_box.set_vexpand(True)

        css_provider_Unic = Gtk.CssProvider()
        css_provider_Unic.load_from_data(b"""
        label.title_LOGO {
            font-size: 20pt;
            color: #ffffff;
        }

        """)

        # ========================
        # Caja superior con Logo
        # ========================
        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        logo_box.set_valign(Gtk.Align.START)   # Arriba
        logo_box.set_halign(Gtk.Align.FILL)    # Que se estire horizontalmente
        logo_box.set_hexpand(True)             # Expansión horizontal
        logo_box.get_style_context().add_class("Present_Boxs_Over")

        logo_lbl = Gtk.Label(label=logo_texto)
        logo_lbl.set_halign(Gtk.Align.CENTER)  # El texto se centra dentro del box
        logo_box.append(logo_lbl)

        style_context1 = logo_lbl.get_style_context()
        style_context1.add_provider(css_provider_Unic, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context1.add_class("title_LOGO")


        overlay_box.add_overlay(logo_box)


        # ========================
        # Imagen de fondo a pantalla completa
        # ========================

        ubicacion_IMG_Preder = os.path.join(get_recursos_dir(), "Imágenes", "Logos_MERIDA_SOLO_Con-Fondo_03.svg")

        dict_Estilo_Config = leer_archivo_recurrente("dict_Confg_Estilo.json", "json")

        # Extensiones válidas
        extensiones_validas = (".png", ".jpg", ".jpeg")

        if dict_Estilo_Config:
            ruta_img = dict_Estilo_Config.get("Ruta_IMGFONDO_1", ubicacion_IMG_Preder)
            
            # Comprobar si el archivo existe y su extensión es válida
            if os.path.isfile(ruta_img) and ruta_img.lower().endswith(extensiones_validas):
                dato_img = ruta_img
            else:
                dato_img = ubicacion_IMG_Preder
        else:
            dato_img = ubicacion_IMG_Preder


        IMG_FONDO = Gtk.Picture.new_for_filename(dato_img)
        IMG_FONDO.set_content_fit(Gtk.ContentFit.FILL)
        IMG_FONDO.set_hexpand(True)
        IMG_FONDO.set_vexpand(True)
        IMG_FONDO.set_opacity(1.0)

        overlay_box.set_child(IMG_FONDO)


        # ========================
        # Caja inferior con mensaje
        # ========================
        msg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        msg_box.set_valign(Gtk.Align.END)     # Abajo
        msg_box.set_halign(Gtk.Align.FILL)    # Que se estire horizontalmente
        msg_box.set_hexpand(True)             # Expansión horizontal
        msg_box.get_style_context().add_class("Present_Boxs_Over")

        mensaje_lbl = Gtk.Label(label=mensaje)
        mensaje_lbl.set_halign(Gtk.Align.START)  # Texto a la izquierda
        msg_box.append(mensaje_lbl)

        overlay_box.add_overlay(msg_box)

        # Añadir al Overlay principal
        self.Overlay_Present.add_overlay(overlay_box)
        self.loading_overlay = overlay_box

    def ocultar_overlay(self):
        """
        Elimina el overlay si existe.
        """
        if self.loading_overlay:
            self.Overlay_Present.remove_overlay(self.loading_overlay)
            self.loading_overlay = None


    #--------Funciones relacionadas a Acciones de la interfaz---------------------
    def Mostrar_Ocultar_BarraÁrbol(self, widget=None, *args):
        """
        Muestra u oculta las barras laterales izquierda y derecha del editor,
        alternando su visibilidad cada vez que se invoca esta función.

        - Si las barras están visibles (`barra_lateral_SUP_Visible` es True), se ocultan.
        - Si están ocultas, se muestran nuevamente.
        
        Parámetros:
        - widget: Widget que puede haber activado esta acción (opcional).
        - *args: Argumentos adicionales que pueden ser pasados por señales (no utilizados).

        Esta función modifica el estado booleano `barra_lateral_SUP_Visible` 
        y actualiza la visibilidad de `vbox_Izquierda` y `vbox_Derecha`.

        Esta función es llamada por: "mostrar/ocultar_barra_lateral" (usado para el mapa 
        de funciones de la función de atajos de teclado), boton_SUP_Árbol (botón en la
        parte superior)
        """
        if self.barra_lateral_SUP_Visible:
            self.vbox_Derecha.hide()
            self.vbox_Izquierda.hide()
            self.barra_lateral_SUP_Visible = False
        else:
            self.vbox_Derecha.show()
            self.vbox_Izquierda.show()
            self.barra_lateral_SUP_Visible = True
    
    def abrir_ajustes(self, widget=None, *args):
        """
        Abre la ventana de configuración administrativa del programa.

        Esta función es llamada por: crear_barraMenú
        """
        self.ventana_administrativa = pantalla_admins(self)
        self.ventana_administrativa.present()

    def abrir_listas(self, widget=None, *args):
        """
        Abre la ventana que muestra las listas predefinidas del sistema 
        (como etiquetas, rutas, etc.).

        Esta función es llamada por: crear_barraMenú

        """
        ventana_listas = pantalla_listas()
        ventana_listas.present()
    
    def abrir_Acercade(self, widget=None, *args):
        """
        Abre la ventana 'Acerca de', que muestra información sobre el programa y su 
        autoría.

        Esta función es llamada por: crear_barraMenú
        """
        ventana_AcercaDe = Pantalla_AcercaDe(parent=self)
        ventana_AcercaDe.present()

    def limpiar_todo(self, widget=None, *args):

        """
        Limpia todos los campos (título, etiquetas, cuerpo y notasTex) del programa 
        si el usuario lo confirma.

        Verifica si hay contenido no guardado antes de proceder. Si el usuario acepta 
        continuar sin guardar, se borran los datos.

        Esta función es llamada por: crear_barraMenú
        """

        Campos_Principales_Rev = [
            self.Vista_Editor_Central.text_view_titulo,
            self.Vista_Editor_Central.text_view_etiquetas,
            self.Vista_Editor_Central.text_view_cuerpo,
        ]
        """Any devuelve true si al menos uno, de los elementos de la lista es verdadero (esta con texto)
        y devuelve false si todos los elementos son falsos (estan vacios) o la lista como tal está vacía."""
        contenido_en_campos_rev = any(self.verificar_contenido_Textview(Campos) for Campos in Campos_Principales_Rev)

        #Se verifica el contenido en las notastext
        contenido_enNotas_rev = any(self.verificar_contenido_Textview(nota) for nota in self.lista_notas_SUP)

        #Verificación
        if contenido_en_campos_rev or contenido_enNotas_rev:

            self.Ignorar_Cambios = True

            if not self.confirmar_guardado_pendiente():
                #Si el usuario oprime "cancelar" será false, e ingresará al return.
                #Si el usuario oprime "Continuar" será True
                return

            self.Vaciar_Campos_SUP()


        self.Ignorar_Cambios = False
        self.Contenido_Modificado_SUP = False #para asegurarse una sincronización con las partes
        control_label_estado(self.status_label, "Limpiados todos los campos.")#Se notifica el exito

    def Vaciar_Campos_SUP(self):
        """
        Vacía el contenido de los campos principales (título, etiquetas, cuerpo) y 
        elimina todas las notasTex.

        Esta función es llamada por: limpiar_todo
        """
        # Vaciar campos principales

        for campo in [self.Vista_Editor_Central.text_view_titulo, self.Vista_Editor_Central.text_view_etiquetas, self.Vista_Editor_Central.text_view_cuerpo]:
            buffer = campo.get_buffer()
            buffer.set_text("")

        # Vaciar (eliminar) las notas
        self.Pestana_Notas_Tex_get.eliminar_todas_las_notastex()

    #-------Funciones relacionadas al manejo de archivos (MERIDA)--------------------
    def abrir_archivo_ArbolArch(self, ruta_archivo_get):
        """
        Abre un archivo seleccionado desde la vista de árbol de archivos (Archivos por carpetas).
        Solo se permiten archivos con extensión `.merida`, propia del programa.

        Proceso:
        - Establece la bandera `Ignorar_Cambios` en `True` temporalmente para evitar 
          conflictos durante la carga.
        - Verifica si hay cambios pendientes por guardar antes de continuar.
        - Si el archivo existe y es compatible:
            - Guarda la ruta y nombre del archivo como atributos internos.
            - Restaura el nombre original sin guiones bajos.
            - Llama a la función encargada de abrir el archivo `.merida`.
        - En caso de error o extensión no válida, se muestra una ventana de advertencia 
          o error usando `mostrar_vent_IEO`, importada desde un archivo externo.
        - Restaura los estados de control (`Ignorar_Cambios` y `Contenido_Modificado_SUP`).
        - Actualiza el estado del label inferior con "Documento cargado".

        Parámetros:
        - ruta_archivo_get (str): Ruta absoluta del archivo seleccionado.

        Esta función no retorna valores. Puede mostrar mensajes de error y modificar
        atributos internos relacionados al archivo actual.

        Esta función es llamada por: _on_archivo_seleccionado(ubicado en el archivo 
        Arbol_de_archivos_recientes.py y Arbol_de_Archivos-Etiquetas.py respectivamente) 
        """

        self.Ignorar_Cambios = True


        if not self.confirmar_guardado_pendiente():
            return

        if os.path.isfile(ruta_archivo_get):
            extension_archivo = os.path.splitext(ruta_archivo_get)[1].lower()

            if extension_archivo == ".merida":

                try:
                    self.archivo_actual = ruta_archivo_get
                    
                    self.Nombre_Tit = os.path.basename(ruta_archivo_get)
                    self.Nombre_Tit_solo = os.path.splitext(self.Nombre_Tit)[0]
                    self.Nombre_Tit_SinGui = Restaurar_espacios_nombre(self.Nombre_Tit_solo)
                
                    self.abrir_archivo_merida()
                except Exception as e:
                    mostrar_vent_IEO(
                        self,
                        "Error desconocido",
                        f"Ocurrió un error inesperado.\nDetalles: {str(e)}",
                        Gtk.MessageType.ERROR,
                        1, None, None, None
                    )
            else:
                mostrar_vent_IEO(
                    self,
                    "Archivo no compatible",
                    "Solo se pueden abrir archivos con extensión .merida.",
                    Gtk.MessageType.ERROR,
                    1, None, None, None
                )


        self.Ignorar_Cambios = False
        self.Contenido_Modificado_SUP = False

        control_label_estado(self.status_label, "Documento cargado")

    def abrir_archivo_md(self, widget=None, *args):
        """
        Muestra un diálogo para abrir archivos con extensión `.merida`, 
        valida su extensión y delega la carga del contenido al método correspondiente.
        También maneja errores de formato o tipo de archivo.

        Desactiva temporalmente el control de cambios durante la carga mediante self.Ignorar_Cambios= True/False.
        para que no haya errores de carga de archivo.

        Esta función es llamada por: crear_barraMenú; registrar_atajos_globales

        """
        self.Ignorar_Cambios = True

        if not self.confirmar_guardado_pendiente():
            return

        ventana_seleccion = Gtk.FileChooserDialog(
            title="Abrir archivo Merida",
            action=Gtk.FileChooserAction.OPEN
        )
        ventana_seleccion.set_transient_for(self)
        ventana_seleccion.set_modal(True)

        ventana_seleccion.add_button("_Cancelar", Gtk.ResponseType.CANCEL)
        ventana_seleccion.add_button("_Abrir", Gtk.ResponseType.OK)

        filtro_md = Gtk.FileFilter()
        filtro_md.set_name("Archivos Merida")
        filtro_md.add_pattern("*.merida")
        ventana_seleccion.add_filter(filtro_md)

        def on_response(dialog, response_id):
            """
            Procesa la respuesta del diálogo de selección:
            - Verifica extensión del archivo
            - Llama a `abrir_archivo_merida()` si es válido
            - Muestra errores si es inválido

            Esta subfunción es llamada por: abrir_archivo_md
            """
            if response_id == Gtk.ResponseType.OK:
                self.archivo_actual = dialog.get_file().get_path()

                self.Nombre_Tit = os.path.basename(self.archivo_actual)
                self.Nombre_Tit_solo = os.path.splitext(self.Nombre_Tit)[0]
                self.Nombre_Tit_SinGui = Restaurar_espacios_nombre(self.Nombre_Tit_solo)
                
                extension = os.path.splitext(self.archivo_actual)[1].lower()

                try:
                    if extension == ".merida":
                        self.abrir_archivo_merida()
                    else:
                        mostrar_vent_IEO(
                            self,
                            "Error de Cargado",
                            "El archivo seleccionado no es compatible con el programa.\nSolo se aceptan archivos .merida.",
                            Gtk.MessageType.ERROR,
                            1,
                            None, None, None
                        )
                except Exception as e:
                    mostrar_vent_IEO(
                        self,
                        "Error Desconocido",
                        f"Ocurrió un error inesperado.\nDetalles: {e}",
                        Gtk.MessageType.ERROR,
                        1,
                        None, None, None
                    )

            dialog.destroy()
            self.Ignorar_Cambios = False
            self.Contenido_Modificado_SUP = False
            control_label_estado(self.status_label, "Documento cargado")

        ventana_seleccion.connect("response", on_response)
        ventana_seleccion.present()

    def abrir_archivo_merida(self):
        """
        Carga un archivo `.merida` (que no es más que un archivo ZIP) extrayendo y 
        mostrando el contenido de:
        - contenido.md: texto principal, extraido desde textview_cuerpo.
        - etiquetas.txt: etiquetas asociadas al archivo, extraidas desde textview_etiquetas
        - notas.json (opcional): notas adicionales que se colocan en notasTex, es decir,
          en la barra lateral izquierda.

        También maneja errores relacionados con formato ZIP o codificación.

        Esta función es llamada por: abrir_archivo_ArbolArch; on_response(subfunción de
        abrir_archivo_md)
        """

        try:
            with zipfile.ZipFile(self.archivo_actual, "r") as archivo_zip:
                archivos = archivo_zip.namelist()

                if "contenido.md" in archivos and "etiquetas.txt" in archivos:
                    with archivo_zip.open("contenido.md") as f:
                        contenido_SUP = f.read().decode("utf-8")
                    with archivo_zip.open("etiquetas.txt") as f:
                        etiquetas_cont_SUP = f.read().decode("utf-8")

                    self.Pestana_Notas_Tex_get.eliminar_todas_las_notastex()

                    if "notas.json" in archivos:
                        with archivo_zip.open("notas.json") as f:
                            textos = json.load(f)

                        for _, texto in textos.items():
                            self.Pestana_Notas_Tex_get.Crear_NotasTex()
                            buffer = self.lista_notas_SUP[-1].get_buffer()
                            buffer.set_text(texto)

                    self.actualizar_cargado_textviews(contenido_SUP, etiquetas_cont_SUP)

                else:
                    mostrar_vent_IEO(
                        self,
                        "Error de Archivo",
                        "El archivo .merida no contiene los archivos requeridos (contenido.md y etiquetas.txt).",
                        Gtk.MessageType.ERROR,
                        1,
                        None, None, None
                    )

        except zipfile.BadZipFile:
            mostrar_vent_IEO(
                self,
                "Error de Formato",
                "El archivo seleccionado no es un archivo ZIP válido.",
                Gtk.MessageType.ERROR,
                1,
                None, None, None
            )

        except UnicodeDecodeError:
            mostrar_vent_IEO(
                self,
                "Error de Decodificación",
                "El archivo contiene caracteres no válidos o está en una codificación incompatible.",
                Gtk.MessageType.ERROR,
                1,
                None, None, None
            )

    def guardar_archivo_md(self, widget=None, *args):
        
        """
        Guarda el contenido actual en un archivo `.merida` comprimido (ZIP), incluyendo 
        título, etiquetas, cuerpo del texto y notas auxiliares. 

        Muestra, además,mensajes de advertencia o error si hay campos importantes vacíos. 
        Utiliza una barra de progreso durante el guardado para mostrar el progreso.

        Esta función es llamada por: crear_barraMenú; registrar_atajos_globales
        """
        #Obtener el contenido de los diferentes textviews
        contenido_cuerpo = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_cuerpo)
        
        contenido_etiquetas = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_etiquetas).strip()
        
        ext_contenido = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_titulo)
        
        ext_contenido2 = Reempla_espacios_nombre(ext_contenido)
        
        contenido_Te_Etiquetas = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_etiquetas)

        if not self.verificar_contenido_Textview(self.Vista_Editor_Central.text_view_titulo):
            mostrar_vent_IEO(
                self,
                "Error de Guardado",
                "No se ha podido guardar el archivo.\nRazón: No se ha detectado un título.",
                Gtk.MessageType.ERROR,
                1, None, None, None
            )
            return

        if not contenido_etiquetas:
            respuesta = mostrar_vent_IEO(
                self,
                "Advertencia",
                "No se ha detectado etiquetas en el documento.\n ¿Desea continuar sin etiquetas?",
                Gtk.MessageType.WARNING,
                2,
                "Continuar", "Cancelar", None
            )
            if respuesta != Gtk.ResponseType.OK:
                return
            else:
                buffer_etiquetas_PREDER = self.Vista_Editor_Central.text_view_etiquetas.get_buffer()
                buffer_etiquetas_PREDER.set_text("[_Etiqueta Predeterminada_]")
                contenido_Te_Etiquetas = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_etiquetas)
                self.verificar_etiquetas()

        if not self.verificar_contenido_Textview(self.Vista_Editor_Central.text_view_cuerpo):
            mostrar_vent_IEO(
                self,
                "Error de Guardado",
                "No se ha podido guardar el archivo.\nRazón: No se ha detectado contenido en el documento.",
                Gtk.MessageType.ERROR,
                1, None, None, None
            )
            return

        # Para validar el color de las etiquetas
        ver_color = self.Controlador_Guardado()


        if ver_color:
            contenido_notastext_get = self.guardar_notastex_en_json()
            self.status_label.set_text("Guardando archivo...")
            self.progress_bar.set_fraction(0.0)
            self.progress_bar.set_visible(True)

            GLib.timeout_add(500, lambda: actualizar_progreso(0.2))
            GLib.timeout_add(1000, lambda: actualizar_progreso(0.4))
            GLib.timeout_add(1500, lambda: actualizar_progreso(0.6))
            GLib.timeout_add(2000, lambda: actualizar_progreso(0.8))
            GLib.timeout_add(2500, lambda: finalizar_guardado())

            GLib.idle_add(lambda: self.compresión_de_archivos(
                ext_contenido2,
                contenido_cuerpo,
                contenido_Te_Etiquetas,
                contenido_notastext_get
            ))

        def actualizar_progreso(valor):
            """Actualiza visualmente la barra de progreso con un valor entre 0.0 y 1.0."""
            self.progress_bar.set_fraction(valor)
            return False

        def finalizar_guardado():
            """
            Finaliza el proceso de guardado, muestra las rutas en que se guardó el 
            archivo mediante el status_label y actualiza la barra de progreso al 100%.
            
            """
            ruta_guardado = os.path.abspath(ext_contenido2 + ".merida")
            Nombre_Archivo = ext_contenido2 + ".merida"
            Rutas_labels = []

            dict_etiquetas_SUP_get = self.Gestor_Variable_ActuEtiquetas.obtener_todas()

            for etiqueta, ruta_base in dict_etiquetas_SUP_get.items():
                ruta_completa = os.path.join(ruta_base, Nombre_Archivo)
                Rutas_labels.append(f"Ubicación: {ruta_completa}")

            mensaje_rutas = "\n".join(Rutas_labels)
            
            self.status_label.set_text(
                f"Arhivo:{Nombre_Archivo} guardado con exito.\n{mensaje_rutas}")

            self.progress_bar.set_fraction(1.0)
            
            GLib.timeout_add(100, lambda: self.progress_bar.set_visible(False))
            GLib.timeout_add(5000, lambda: restaurar_estado())
            
            #Se notifica para marcar contenido modificado
            self.Contenido_Modificado_SUP = False
            
            return False

        def restaurar_estado():
            """
            Restaura el estado visual de la barra de progreso y 
            el estado general tras el guardado.
            
            """
            self.status_label.set_text("Estado: Esperando acción.")
            self.progress_bar.set_fraction(0.0)
            self.progress_bar.set_visible(True)
            
            #Para evitar llamados infinitos.
            return False

    def compresión_de_archivos(self, nombre_archivo, contenido_archivo, contenido_etiquetas, contenido_notastext):
        """
        Comprime los contenidos del documento actual en un archivo `.merida`.

        Esta función genera un archivo ZIP personalizado que incluye tres archivos: 
        "contenido.md", "etiquetas.txt" y "notas.json". Luego guarda dicho archivo ZIP 
        en todas las rutas asociadas a las etiquetas válidas. Al finalizar, elimina los 
        archivos temporales creados en el proceso.

        Args:
            -nombre_archivo (str): Nombre base del archivo ".merida" a crear.
            -contenido_archivo (str): Contenido principal del documento en formato 
            Markdown.

            -contenido_etiquetas (str): Texto con las etiquetas en su formato original.
            -contenido_notastext (dict): Diccionario con las notas o metadatos 
            adicionales a guardar en JSON.

        Returns:
            bool: Siempre retorna `False` para que GLib.idle_add no ejecute la 
            función repetidamente.

        Esta función es llamada: guardar_archivo_md
        """

        #Nombre del zip (extensión personalizada)
        Nombre_zip = f"{nombre_archivo}.merida"

        
        #Lista con los archivos a comprimir y luego a eliminar
        List_arch = ["contenido.md", "etiquetas.txt", "notas.json"]

        #Ciclo for para iterar sobre las etiquetas y sus rutas de guardado
        dict_etiquetas_SUP_get = self.Gestor_Variable_ActuEtiquetas.obtener_todas()

        for etiqueta, ruta_base in dict_etiquetas_SUP_get.items():

            #se une las rutas de guardado obtenidas con el nombre del archivo zip al final
            ruta_completa = os.path.join(ruta_base, Nombre_zip)

            try:

                #Crear un Zip con los archivos internos
                with zipfile.ZipFile(ruta_completa, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
                    with open("contenido.md", "w") as archivo_md:
                        archivo_md.write(contenido_archivo)

                    with open("etiquetas.txt", "w") as etiquetas_txt:
                        etiquetas_txt.write(contenido_etiquetas)
                    
                    with open("notas.json", "w", encoding="utf-8") as notas_json:
                        json.dump(contenido_notastext, notas_json, ensure_ascii=False, indent=4)
                    
                    for archivo in List_arch:
                        archivo_zip.write(archivo)
            
            except Exception as e:
                mostrar_vent_IEO(
                    self,
                    "Error de Guardado",
                    f"No se ha podido guardar el archivo.\n Error de guardado en {ruta_completa}\nPara {etiqueta}: {e}",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None,
                    None)
        
                
        for archivo in List_arch:
            
            if os.path.exists(archivo): #Verificar que existe. De lo contrario, lanzará un error.
                os.remove(archivo)
        """Se debe retornar False para que la función se llamé una sola vez. Si no se hace,
        GLib.idle_add llamará a la función repetidas veces."""
        return False 

    def guardar_notastex_en_json(self):
        """
        Guarda el contenido de las notasTex como un diccionario para su posterior 
        exportación a JSON.

        Retorna:
            dict: Diccionario con las notas en el formato: 
                {"nota_1": texto1, "nota_2": texto2, ...}

        Esta función es llamada por: guardar_archivo_md
        """

        notas_texto = {}

        for i, textview in enumerate(self.lista_notas_SUP, start=1): #start indica que la enumaración sea 1

            buffer = textview.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()

            texto = buffer.get_text(start_iter, end_iter, True)

            notas_texto[f"nota_{i}"] = texto
        return notas_texto

    #-------Funciones relacionadas a una clase específica----------------------

    #De: Editor_Central------------------------
    def actualizar_cargado_textviews(self, contenido, etiquetas):
        """
        Carga el contenido del cuerpo y las etiquetas en sus respectivos TextViews,
        y aplica el estilo de título al campo de título utilizando el nombre del archivo.
        
        Esta función es llamada por: abrir_archivo_merida
        """

        buffer_titulo = self.Vista_Editor_Central.text_view_titulo.get_buffer()
        buffer_titulo.set_text(self.Nombre_Tit_SinGui)
        
        start, end = buffer_titulo.get_bounds()
        buffer_titulo.apply_tag_by_name("título_docu", start, end)

        self.Vista_Editor_Central.text_view_etiquetas.get_buffer().set_text(etiquetas)
        self.Vista_Editor_Central.text_view_cuerpo.get_buffer().set_text(contenido)

        self.verificar_etiquetas()

    def verificar_etiquetas(self):
        """
        Busca y valida las etiquetas en el campo correspondiente.

        Recorre el texto del TextView de etiquetas y encuentra patrones entre corchetes
        con guiones bajos. Luego, consulta cada etiqueta en la base de datos y aplica 
        un estilo de color: verde si la etiqueta existe, rojo si no existe.

        No retorna nada, pero actualiza visualmente el campo de etiquetas y el 
        diccionario de etiquetas válidas.

        Esta función es llamada por:on_focus_out, guardar_archivo_md, actualizar_cargado_textviews,
        actualizar_textview_etiquetas
        """

        texto = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_etiquetas)
        etiquetas = re.findall(r'\[(.*?)\]', texto)


        if not etiquetas:
            return

        for match in re.finditer(r"\[_([^_]+)_\]", texto):
            etiqueta = match.group(1)
            existe = self.consultar_bd(etiqueta)
            start = match.start()
            end = match.end()

            buffer = self.Vista_Editor_Central.text_view_etiquetas.get_buffer()
            start_iter = buffer.get_iter_at_offset(start)
            end_iter = buffer.get_iter_at_offset(end)
            buffer.remove_all_tags(start_iter, end_iter)

            tag = "VerdeTag" if existe else "RojoTag"
            buffer.apply_tag_by_name(tag, start_iter, end_iter)

    def Controlador_Guardado(self):
        """
        Controla el proceso de guardado, evaluando si existen etiquetas sin ruta definida 
        (etiquetas en rojo). En caso de detectarlas, ofrece al usuario la opción de
        crear rutas antes de continuar con el guardado.

        Flujo:
        - Obtiene un diccionario de etiquetas y sus colores con `identificar_colores_etiquetas`.
        - Si alguna etiqueta está en rojo, se muestra una ventana de confirmación:
            - Si el usuario elige crear rutas, se abre la pantalla de listas.
            - Si decide continuar sin crear rutas, se permite el guardado.
        - Si no hay etiquetas en rojo, el guardado se permite directamente.

        Retorna:
        - `True` si se permite el guardado (sin etiquetas rojas o con confirmación del usuario).
        - `False` si se cancela el proceso (por defecto o por cierre de ventana).

        Esta función es llamada por: guardar_archivo_md
        """
        contr_color = False

        # Se identifican los colores de las etiquetas
        dic_etiquetas_con_color = self.identificar_colores_etiquetas()


        if "rojo" in dic_etiquetas_con_color.values():
            respuesta = mostrar_vent_IEO(
                self,
                "Error de Guardado",
                "Se ha detectado etiquetas en rojo.\n¿Desea crear rutas para dichas etiquetas?",
                Gtk.MessageType.QUESTION,
                2,
                "Sí, crear ruta.",
                "No, guardar de todos modos.",
                None
            )

            if respuesta == Gtk.ResponseType.OK:
                ventana_listas = pantalla_listas()
                ventana_listas.present()

                #Usar close-request en lugar de "destroy". Parece funcionar mejor.
                ventana_listas.connect("close-request", self.actualizar_textview_etiquetas)
            else:
                
                """Se comprueba, además, que si existe una etiqueta en verde, solo se 
                <<pase>> la confirmación del controlador (contr_color) y no se añade 
                nada más, ya que se usará unicamente las etiquetas en verde. Caso contrario
                se inserta la etiqueta predeterminada."""
                if any(color == "verde" for color in dic_etiquetas_con_color.values()):


                    contr_color = True

                else:

                    buffer_etiquetas_PREDER = self.Vista_Editor_Central.text_view_etiquetas.get_buffer()
                    buffer_etiquetas_PREDER.set_text("[_Etiqueta Predeterminada_]")
                    self.verificar_etiquetas()

                    contr_color = True
        else:
            contr_color = True

        return contr_color

    def identificar_colores_etiquetas (self):

        """
        Recorre todas las etiquetas del TextView de etiquetas y determina su color 
        de marcado (verde o rojo).

        Retorna:
            dict: Un diccionario con las etiquetas encontradas como claves y su 
            color correspondiente como valor ('verde' o 'rojo').

        Esta función es llamada por: Controlador_Guardado
        """

        buffer = self.Vista_Editor_Central.text_view_etiquetas.get_buffer()
        texto = self.obtener_texto_Textview(self.Vista_Editor_Central.text_view_etiquetas)
        
        etiquetas = re.finditer(r"\[_([^_]+)_\]", texto)  # Encuentra todas las etiquetas

        #Se crea el diccionario que almacenará el texto y su color
        etiquetas_colores_dic = {}


        for match in etiquetas:
            etiqueta = match.group(1)  # Extrae el contenido de la etiqueta

            start = match.start()
            end = match.end()

            start_iter = buffer.get_iter_at_offset(start)
            end_iter = buffer.get_iter_at_offset(end)

            # Verificar si tiene la etiqueta "VerdeTag"
            tags_en_rango = start_iter.get_tags()

            es_verde = any(tag.get_property("name") == "VerdeTag" for tag in tags_en_rango)
            
            if es_verde:
                
                etiquetas_colores_dic[etiqueta] = "verde"
                
            else: #Si no es verde, obligatoriamente estará en rojo
                
                etiquetas_colores_dic[etiqueta] = "rojo"

        #se devuelve el diccionario que contiene todas las etiquetas del ciclo for.
        return etiquetas_colores_dic

    def on_focus_out_get(self, controller, *args):
        """
        Se ejecuta cuando un TextView pierde el foco. Según esto, se pueden realizar
        diversas acciones. Hasta el momento, se tienen inscritas las siguientes:

        1. Restaurar el estilo visual del widget a su estado normal (NORMAL)
        2. Limpia el contenido del diccionario de las etiquetas para luego llamar
        a la función de verificación. Esto asegura que el diccionario siempre esté 
        actualizado según las últimas etiquetas registradas en el textview de las etiquetas
        ya que verificar_etiquetas se encarga de "extraer" y "rellenar" nuevamente el 
        dicccionario de las etiquetas. 
        3. Actualizar la base de datos de archivos recientes, y actualizar visualmente el 
        árbol lateral derecho (cambiar de página).

        Args:
            controller: Controlador de eventos asociado al foco.
            *args: Argumentos adicionales no utilizados.

        """

        widget = controller.get_widget()
        if widget:
            context = widget.get_style_context()
            context.set_state(Gtk.StateFlags.NORMAL)
            

            self.Gestor_Variable_ActuEtiquetas.limpiar_contenido()
            
            self.verificar_etiquetas()

            dict_etiquetas_SUP_get = self.Gestor_Variable_ActuEtiquetas.obtener_todas()
            self.Registrar_ArchRecientes(dict_etiquetas_SUP_get)

            self.Pestana_ArbolArch_Etiquetas_get.actualizar_arbol_desde_principal(diccionario_rutas_get=dict_etiquetas_SUP_get)

            self.Notebook_Derecha.set_current_page(1)


    #De: Pestana_NotasTex---------------------------------------
    def conectar_cambios_NotasTex(self, textview):

        """
        Conecta señales 'changed' de un TextView de notasTex para aplicar formateo 
        y marcar contenido como modificado.

        Esta función es para evitar multiples señales por conexión repetida (por ejemplo
        al copiar notas o recargar las mismas). Esta función centraliza eso, evitando que
        pase,creo.

        Args:
            textview (Gtk.TextView): El widget al que se le conectarán las señales.

        Esta función es llamada por: Crear_NotasTex(desde Pestana_NotasTex.py)
        """



        buffer = textview.get_buffer()
        
        #Se copia el self.formatear_texto_en_cambio_cuerpo ya que, en esencia, es el mismo comportamiento
        buffer.connect("changed", self.Vista_Editor_Central.formatear_texto_en_cambio_cuerpo)
        
        #se marca cualquier cambio mediante la función marcar contenido.
        buffer.connect("changed", self.marcar_contenido_modificado)

    #--------Funciones Útiles---------------------------------------------
    def obtener_texto_Textview(self, textview):
        """
        Obtiene el texto completo de un widget `Gtk.TextView`.

        Parámetros:
        - textview (Gtk.TextView): El widget del cual se desea obtener el contenido.

        Retorna:
        - str: Texto plano extraído desde el principio hasta el final del buffer asociado.

        Esta función es llamada por: identificar_colores_etiquetas; verificar_etiquetas; 
        guardar_archivo_md
        """
        buffer = textview.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
    
    def actualizar_textview_etiquetas(self, widget):
        """
        Actualiza el contenido del TextView de etiquetas después de cerrar la ventana 
        de edición de listas.

        Este método es usado como "callback" cuando se destruye la ventana de etiquetas,
        para sincronizar los cambios realizados.

        Parámetros:
        - widget: Referencia al widget que disparó el evento de cierre (usualmente `pantalla_listas`).

        No retorna ningún valor. Llama internamente a `verificar_etiquetas`.

        Esta función es llamada por: Controlador_Guardado
        """

        self.verificar_etiquetas()

        #Close-request necesita una "confirmación", por ello se debe enviar un False.
        #True: detiene el cierre de la ventana (se cancela).False: permite que la ventana se cierre.
        return False

    def verificar_contenido_Textview(self, textview):
        """
        Verifica si un widget `Gtk.TextView` contiene texto no vacío.

        Parámetros:
        - textview (Gtk.TextView): El widget a evaluar.

        Retorna:
        - bool: `True` si el contenido no está vacío (ignorando espacios en blanco con strip),
                `False` si el buffer está vacío o solo contiene espacios.

        Esta función es llamada por: limpiar_todo; guardar_archivo_md
        """

        buffer = textview.get_buffer()
        start, end = buffer.get_bounds()
        contenido = buffer.get_text(start, end, True)
        
        return bool(contenido.strip())

    def marcar_contenido_modificado(self, buffer):
        """
        Marca el documento como modificado al detectar un cambio en el buffer, a menos 
        que esté activado Ignorar_Cambios.
        
        Cambia también el estado del label inferior (status_label) para informar al usuario.
        
        Esta función es llamada por: conectar_cambios_NotasTex; __init__ 

        """
        if self.Ignorar_Cambios:
            # Si el controlador es true, el contenido no será marcado como modificado
            return

        # Función para "marcar", según sea llamada, como contenido modificado
        self.Contenido_Modificado_SUP = True 
        
        # El label se cambia cada vez que se llama
        control_label_estado(self.status_label, "Documento modificado. No guardado.")

    def confirmar_guardado_pendiente(self):
        """
        Muestra un diálogo de confirmación si existen cambios no guardados antes de 
        ejecutar una acción destructiva.

        Retorna:
            bool: True si el usuario acepta continuar, False si desea cancelar.

        Esta función es llamada por: limpiar_todo; on_quit; abrir_archivo_md; abrir_archivo_ArbolArch

        """

        # Función para confirmar el guardado según la variable Contenido_Modificado_SUP

        if self.Contenido_Modificado_SUP:  # Si la variable es True, entrará.
            respuesta = mostrar_vent_IEO(
                self,
                "Cambios No Guardados",
                "Hay cambios sin guardar.\n¿Desea continuar sin guardar?",
                Gtk.MessageType.WARNING,
                2,
                "Continuar", "Cancelar", None)
            # Retornamos la respuesta únicamente si es ok como True, de lo contrario devolverá False.
            return respuesta == Gtk.ResponseType.OK
        return True

    #-----------------Funciones relacionadas a las Bases de Datos---------------
    def consultar_bd(self, etiqueta):
        """
        Consulta si una etiqueta existe en la base de datos.

        Utiliza una función externa "obtener_registro_NombEtiq" para buscar una etiqueta
        en la base de datos. Si se encuentra, actualiza el diccionario 
        "Lista_Etiquetas_SUP".

        Args:
            etiqueta (str): Nombre de la etiqueta a buscar.

        Returns:
            str or None: Ruta asociada a la etiqueta si existe, o None si no se encuentra.
        
        Esta función es llamada por: verificar_etiquetas

        """

        existe = None
        
        Registro_get2 = self.BD_TAGS_Functions.obtener_registro_NombEtiq(etiqueta)
        
        if Registro_get2 != "No encontrado":
            existe = Registro_get2
            
            self.Gestor_Variable_ActuEtiquetas.agregar_contenido(etiqueta, Registro_get2)
            
       
        return existe

    def Registrar_ArchRecientes(self, lista_get_SUP):

        """
        Registra rutas de archivos recientes en la base de datos si no están duplicadas.

        Args:
            lista_get_SUP (dict): Diccionario con claves como nombres de etiquetas y 
            valores como rutas de carpetas.

        Esta función es llamada por: on_focus_out
        """

        if lista_get_SUP: #Verificar que el diccionario tenga algo. Si tiene, es true.
            for clave, valor in lista_get_SUP.items():

                if self.BD_Recient_Arch_Functions.validar_unico(clave) is None:
                    
                    Registro_nuevo = BD_Recient_Arch()
                    Registro_nuevo.RA_Nombre_Etiqueta = clave
                    Registro_nuevo.RA_Ruta_Carpeta = valor

                    self.BD_Recient_Arch_Functions.registrar_nuevas_listas(Registro_nuevo)

    #------------Funciones relacionadas al programa-------------------

    def sync_theme(self, *_):
        self.style_manager = Adw.StyleManager.get_default()
        ctx = self.get_style_context()
        if self.style_manager.get_dark():
            ctx.add_class("dark")
            ctx.remove_class("light")
        else:
            ctx.add_class("light")
            ctx.remove_class("dark")

    def registrar_atajos_globales(self):
        """
        Registra los atajos de teclado globales definidos por el usuario a partir 
        de una base de datos.

        Reemplaza cualquier controlador de atajos anterior y vincula acciones como 
        guardar, abrir y mostrar/ocultar componentes.

        Esta función es llamada por: __init__
        
        """
        # Quitar controlador anterior si existe
        if hasattr(self, "shortcut_controller") and self.shortcut_controller is not None:
            self.remove_controller(self.shortcut_controller)

        # Crear nuevo controlador
        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)

        # Asegúrate de añadirlo a la ventana principal
        self.add_controller(self.shortcut_controller)

        # Mapa de funciones por nombre de acción
        mapa_funciones = {
            "guardar": self.guardar_archivo_md,
            "abrir": self.abrir_archivo_md,
            "mostrar/ocultar_barra_lateral": self.Mostrar_Ocultar_BarraÁrbol,
            "crear_nuevas_notastex": self.Pestana_Notas_Tex_get.Crear_NotasTex,
            "crear_nuevo_archivo": self.limpiar_todo
        }

        # Obtener los atajos registrados
        lista_regist_ComTecl2 = self.BD_ComTecl_Functions.obtener_registros(modo="diccionario")

        # Acción de atajo con retorno explícito para evitar bloqueos
        def _accion_con_atajo(*args, funcion=None):
            if funcion:
                funcion()
            return True
        
        for registro in lista_regist_ComTecl2.values():
            nombre = registro["nombre"].lower()
            atajo = registro["atajo"]

            if nombre in mapa_funciones:
                trigger = Gtk.ShortcutTrigger.parse_string(atajo)

                if trigger is not None:
                    action = Gtk.CallbackAction.new(partial(_accion_con_atajo, funcion=mapa_funciones[nombre]))
                    shortcut = Gtk.Shortcut.new(trigger, action)
                    self.shortcut_controller.add_shortcut(shortcut)

    def Verificar_Respaldo_Automático(self):
        """
        Verifica si es el "momento" para realizar respaldos de las bases de datos.
        Si al menos una base requiere respaldo, se muestra una ventana con información del proceso.
        """

        def controlar_mensaje_A(mensaje_label, mensaje_textview):
            if mensaje_label is not None:
                label_estado.set_text(mensaje_label)
            if mensaje_textview is not None:
                buffer = textview_infor.get_buffer()
                iter_final = buffer.get_end_iter()
                buffer.insert(iter_final, mensaje_textview + "\n")

        def mostrar_ventana_de_respaldo(parent):
            Vent_Info_Respald = Gtk.MessageDialog(
                transient_for=parent,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.NONE,
                text="Respaldo Automático"
            )

            Vent_Info_Respald.set_default_size(700, 400)
            content_area = Vent_Info_Respald.get_content_area()

            spinner_respald = Gtk.Spinner()
            spinner_respald.start()

            label_estado = Gtk.Label(label="Esperando instrucciones...")

            textview_Infor_A = Gtk.TextView(vexpand=True, hexpand=True)
            textview_Infor_A.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            textview_Infor_A.set_editable(False)
            textview_Infor_A.set_focusable(False)

            scroll_infor = Gtk.ScrolledWindow()
            scroll_infor.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll_infor.set_child(textview_Infor_A)
            scroll_infor.set_vexpand(True)
            scroll_infor.set_hexpand(True)

            box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            box_pr.append(spinner_respald)
            box_pr.append(label_estado)
            box_pr.append(scroll_infor)

            content_area.append(box_pr)

            Vent_Info_Respald.show()
            return Vent_Info_Respald, label_estado, textview_Infor_A, spinner_respald

        def eliminar_archivos_antiguos(controlar_mensaje_A):
            controlar_mensaje_A("Iniciando limpieza de respaldos", "Eliminando archivos más antiguos...")
            datos_dict_Spinns = leer_archivo_recurrente("Archivo_Recurrente_Spinn.json", "json")
            N_Archivos_Mantener = datos_dict_Spinns["Número_Arch_a_Mantener"]

            #Ruta usada para bds del sistema
            ruta_resguardos_bd_Sistema = os.path.join(get_data_dir(),"Resguardos_BD")

            lista_sqlite, lista_sql = filtrar_archivos_por_extension_BD(ruta_resguardos_bd_Sistema)

            estado_sqlite, error_sqlite, estado_sql, error_sql = self.BD_Utilidades_Generales.Eliminar_ArchivosRes_Antiguos(lista_sqlite,lista_sql,N_Archivos_Mantener)


            if estado_sqlite is None and estado_sql is None:
                #Si el estado es none, no se cumple la condición de eliminación.
                controlar_mensaje_A(
                    None,
                    f"[INFO] La cantidad de archivos de respaldo encontrados no cumple la condición para la eliminación:<<Mantener {N_Archivos_Mantener} archivos más recientes.")
                controlar_mensaje_A(None, "No se ha eliminado ningún archivo de respaldo.")
                return

            elif error_sqlite is None and error_sql is None:
                # No hubo errores → mostrar estados si no son None
                if estado_sqlite is not None:
                    controlar_mensaje_A("Limpieza SQLite completada", f"{estado_sqlite}")
                if estado_sql is not None:
                    controlar_mensaje_A("Limpieza SQL completada", f"{estado_sql}")
            else:
                # Mostrar mensajes de error si existen
                if error_sqlite is not None:
                    controlar_mensaje_A("Error en limpieza SQLite", f"{error_sqlite}")
                if error_sql is not None:
                    controlar_mensaje_A("Error en limpieza SQL", f"{error_sql}")

            controlar_mensaje_A(None, "Limpieza de archivos completada.")

        dict_estados_unificados_bds = self.BD_Utilidades_Generales.Verificar_Intervalo_RespalAutomic()

        ventana_mostrada = False
        ventana = None
        label_estado = None
        textview_infor = None
        spinner = None
        respaldo_realizado = False

        # Verificación de archivos de restauración existentes
        if not dict_estados_unificados_bds:  
            descripcion_get = """No se han detectado archivos de respaldo de bases de datos
            en la carpeta predeterminada de resguardos. Se recomienda ampliamente crearlos. Para ello, puede ir a la sección correspondiente en la ventana de preferencias del
            programa, sección bases de datos. 

            Así mismo, se recomienda ajustar (y guardar) la configuración para los respaldos
            automáticos. Más información respecto a este tema puede encontrarse en el manual de
            usuario del programa MERIDA."""

            self.Pestana_de_Notificaciones_get.agregar_aviso(
                "Sistema",
                "No se han detectado respaldos en la carpeta de resguardos",
                descripcion_get)

            self.Notebook_Derecha.set_current_page(2)#2 es la pestaña de avisos

            return  # Sale de la función para no continuar con el resto del flujo


        # Si SÍ hay respaldos previos, seguimos como siempre
        for nombre_bd, estado in dict_estados_unificados_bds.items():
            if  estado["estado_sqlite"] or  estado["estado_sql"]:
                if not ventana_mostrada:
                    ventana, label_estado, textview_infor, spinner = mostrar_ventana_de_respaldo(self)
                    controlar_mensaje_A("Iniciando respaldo", "Recolectando datos...")
                    ventana_mostrada = True

                controlar_mensaje_A(f"Respaldo para {nombre_bd}", f"Iniciando respaldo de {nombre_bd}...")

                id_bd = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_bd)
                origen_bd = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_bd, "origen")
                ruta_respald_bd = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_bd, "ubicacion_respaldo")
                ruta_respald_bd_ab = os.path.dirname(ruta_respald_bd)
                ruta_archivo_bd = self.BD_Informadora_Functions.Obtener_Ruta_BD(id_get=id_bd)

                self.BD_Utilidades_Generales.respaldar_base_de_datos(
                    nombre_bd,
                    origen_bd,
                    ruta_respald_bd_ab,
                    ruta_archivo_bd
                )

                controlar_mensaje_A(None, f"Respaldo de {nombre_bd} finalizado.")
                respaldo_realizado = True

        if respaldo_realizado:
            eliminar_archivos_antiguos(controlar_mensaje_A)

        if ventana_mostrada:
            label_estado.set_text("Respaldo automático completado.\\Ya puede cerrar esta ventana.")
            spinner.stop()

    def on_quit(self, window=None, *args):
        """
        Función que se ejecuta siempre al cerrarse el programa. Tiene una variedad de
        procesos que sigue antes de permitir al programa cerrar. 

        Procesos:
            -Verifica si hay o no cambios en el documento mediante lo que devuelva la función
            de: self.confirmar_guardado_pendiente().
            -Cambia las variables de ignorar cambios y contenido modificado para 
            asegurarse su "estado" al inicio siguiente
            -Obtiene los datos de ancho y alto de la ventana para luego poder restaurarlos
            en el siguiente arranque
            -Obtiene la posición de los paneds y el "width" de los mismos para poder 
            restaurarlos en el siguiente arranque. Sin estos datos, los paneds se posicionaran
            de forma extraña.
            -Guarda la posición de la ventana y de los paneds en un diccionario. Ese diccionario
            es "exportado" como archivo recurrente para luego ser utilizado al inicio del siguiente
            arranque
            -Guarda datos relacionados a la "Configuración Inicial" del programa. Esto 
            significa que estos datos son usada para aplicar configuraciones iniciales, sin
            embargo, en este caso, sirve para cambiar la señal se primer arranque a True,
            ya que esto será utilizado para otras funciones. Si se desea, puede cambiarse
            esta función por "añadir_a_archivo_recurrente" y así, añadir información.


            -Por último, finaliza la aplicación.

        """

        #--------------------Guardado Pendiente---------------
        if not self.confirmar_guardado_pendiente():
            return True

        self.Ignorar_Cambios = False
        self.Contenido_Modificado_SUP = False

        #-----------------------Confg de Ventana y Paneds------------------------
        estado_VentMaximizada = self.is_maximized()
        ancho_vent, alto_vent = self.get_default_size()
        
        ancho_real_VentPanedI = self.Paned_Panel_Izquierda_Exterior.get_allocated_width()
        ancho_real_VentPanedD = self.Paned_Panel_Derecha_Interior.get_allocated_width()

        position_panedI = self.Paned_Panel_Izquierda_Exterior.get_position()
        position_panedD = self.Paned_Panel_Derecha_Interior.get_position()

        # Si ancho real es cero o muy pequeño, no sobreescribimos la fracción guardada.
        if ancho_real_VentPanedI and ancho_real_VentPanedI > 10:
            fracI = position_panedI / ancho_real_VentPanedI
        else:
            fracI = self.dict_config_VentYPaneds_GET.get("posicion_paned_izquierdo", 0.2)

        if ancho_real_VentPanedD and ancho_real_VentPanedD > 10:
            fracD = position_panedD / ancho_real_VentPanedD
        else:
            fracD = self.dict_config_VentYPaneds_GET.get("posicion_paned_derecho", 0.2)

        
        dict_config_VentYPaneds = {
            "estado_VentMaximizada": estado_VentMaximizada,
            "ancho_ventana": ancho_vent,
            "alto_ventana": alto_vent,
            "posicion_paned_izquierdo": fracI,
            "posicion_paned_derecho": fracD
        }



        crear_archivos_recurrentes(
            "Configuracion_de_VentanaYPaneds.json",
            "json",
            dict_config_VentYPaneds
        )

        #=======================================================
        #Creación del Archivo Recurrente de configuración inicial
        #(Usado para verificaciones si no existe)
        #======================================================
        
        dict_Config_Inicial = {
            "Prm_Inicio": False #Señal de primer arranque(False: ya no es el primer inicio)

        }

        crear_archivos_recurrentes(
            "Dict_Config_Inicial.json",
            "json",
            dict_Config_Inicial
            )


        #---------------------Finalización-------------------------------------
        app = self.get_application()
        if app:
            app.quit()

        return False
     


