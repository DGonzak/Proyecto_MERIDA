import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw

from Lib_Extra.Funciones_extras import crear_archivos_recurrentes, leer_archivo_recurrente
from Pantallas.Clases_Pantalla_Principal.Espacio_Central.Editor_Central import Vista_Editor_Central
from Lib_Extra.Rutas_Gestion import get_recursos_dir

class Vista_AjustesEstilo (Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_vexpand(True)



        titulo_AjusEstilo = Gtk.Label(label="Ajustes de Estilo")
        titulo_AjusEstilo.set_xalign(0)

        titulo_SelectTema = Gtk.Label(label="Selección de Tema")
        titulo_SelectTema.set_xalign(0)


        titulo_SelectImg = Gtk.Label(label="Selección de Fondo de Pantalla")
        titulo_SelectImg.set_xalign(0)

        titulo_SelectImg2 = Gtk.Label(label="Imagen de Fondo para <<Pantalla de Carga>>")
        titulo_SelectImg2.set_xalign(0)

        self.label_estado_estilo = Gtk.Label(label="No se ha detectado cambios.")
        self.label_estado_estilo.set_xalign(0)

        boton_guardar_config_Estilo = Gtk.Button(label="Guardar Configuración de Estilo")
        boton_guardar_config_Estilo.connect("clicked", self.guardar_configuracion_Estilo)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        label.title {
            font-weight: bold;
            font-size: 20pt;
        }

        label.title2 {
            font-weight: bold;
            font-size: 14pt;
        }

        label.title3 {

            font-weight: bold;
            font-size: 12pt;
        }

        """)

        style_context1 = titulo_AjusEstilo.get_style_context()
        style_context1.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context1.add_class("title")

        style_context2 = titulo_SelectTema.get_style_context()
        style_context2.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context2.add_class("title2")

        style_context3 = titulo_SelectImg.get_style_context()
        style_context3.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context3.add_class("title2")

        style_context3_1 = titulo_SelectImg2.get_style_context()
        style_context3_1.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context3_1.add_class("title3")

        #============================
        #Posicionamiento de widgets
        #==============================

        self.append(titulo_AjusEstilo)

        self.append(titulo_SelectTema)
        self.append(self.Seleccionar_Tema())

        self.append(titulo_SelectImg)
        self.append(titulo_SelectImg2)
        self.append(self.Seleccionar_FondosPanta())

        self.append(self.label_estado_estilo)
        self.append(boton_guardar_config_Estilo)


    #================================
    #Funciones
    #==================================

    def marcar_cambios(self, con_cambios):
        if con_cambios:
            self.label_estado_estilo.set_text("⚠ Cambios No Guardados.")
        else:
            self.label_estado_estilo.set_text("✓ Cambios guardados")

    def Seleccionar_Tema(self):
        """
        Muestra y posiciona todos los widgets relacionados a la selección del tema.
        """
        # Esta es una función auxiliar que se llama para sincronizar los widgets
        def sincronizar_widgets(widget=None, *args):
            # Si la casilla está marcada, ambos switches deben desactivarse y deshabilitarse.
            if self.casilla_Sistem.get_active():
                self.Switch_oscuro.set_sensitive(False)
                self.Switch_oscuro.set_active(False)
                self.Switch_Claro.set_sensitive(False)
                self.Switch_Claro.set_active(False)
                self.restablecer_tema_del_sistema()
                #self.Aplicar_CambiosTema_A_Esp_Widgets()
                self.marcar_cambios(True)
            else:
                # Si la casilla se desmarca, ambos switches deben activarse (habilitarse).
                self.Switch_oscuro.set_sensitive(True)
                self.Switch_Claro.set_sensitive(True)
                self.marcar_cambios(True)

        # Esta es la lógica para gestionar la exclusividad de los switches
        def manejar_switches(switch, state):
            if self.casilla_Sistem.get_active():
                # Si la casilla está marcada, no hacemos nada y cancelamos la acción del switch.
                # Esto evita que el usuario cambie el switch mientras la casilla está activa.
                return True

            #Lógica de exclusión mutua para los switches (no pueden activarse ambos)
            if switch == self.Switch_oscuro:
                if state:
                    self.forzar_tema_oscuro()
                    #self.Aplicar_CambiosTema_A_Esp_Widgets()
                    self.Switch_Claro.set_active(False)
                    self.marcar_cambios(True)
                else:
                    self.forzar_tema_claro()
                    #self.Aplicar_CambiosTema_A_Esp_Widgets()
                    self.Switch_Claro.set_active(True) # Para asegurar que siempre uno está activo
                    self.marcar_cambios(True)
            elif switch == self.Switch_Claro:
                if state:
                    self.forzar_tema_claro()
                    #self.Aplicar_CambiosTema_A_Esp_Widgets()
                    self.Switch_oscuro.set_active(False)
                    self.marcar_cambios(True)
                else:
                    self.forzar_tema_oscuro()
                    #self.Aplicar_CambiosTema_A_Esp_Widgets()
                    self.Switch_oscuro.set_active(True) # Para asegurar que siempre uno está activo
                    self.marcar_cambios(True)
            # Desactivamos la casilla del sistema si un switch es manipulado
            self.casilla_Sistem.set_active(False)
            return False # Permitimos que el estado del switch cambie

        box_tem = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(15)

        label_tit = Gtk.Label()
        label_tit.set_markup("<b>Aplicar tema:</b>")
        label_tit.set_xalign(0)

        label_claro = Gtk.Label(label="Claro")
        self.Switch_Claro = Gtk.Switch()
        self.Switch_Claro.connect("state-set", manejar_switches)

        label_oscuro = Gtk.Label(label="Oscuro")
        self.Switch_oscuro = Gtk.Switch()
        self.Switch_oscuro.connect("state-set", manejar_switches)

        self.casilla_Sistem = Gtk.CheckButton.new_with_label("Usar tema según la preferencia del sistema")
        self.casilla_Sistem.connect("toggled", sincronizar_widgets)

        # Posicionamiento de los widgets en el grid
        grid.attach(label_claro, 0, 0, 1, 1) #Columna 0, Fila, 1, 1x1
        grid.attach(self.Switch_Claro, 1, 0, 1, 1) #Columna 1, Fila 0, 1x1

        grid.attach(label_oscuro, 0, 1, 1, 1) #Columna 0, Fila 1, 1x1
        grid.attach(self.Switch_oscuro, 1, 1, 1,1) #Columna 1, Fila 1, 1x1

        grid.attach(self.casilla_Sistem, 0, 2, 7, 1) #Columna 0, Fila 2, 7x1

        box_tem.append(label_tit)
        box_tem.append(grid)

        # Sincronización inicial al crear los widgets
        sincronizar_widgets()

        #Recuperación de estados desde archivo
        datos1 = leer_archivo_recurrente("dict_Confg_Estilo.json", "json")

        if datos1:
            tema_oscuro = datos1.get("estado_tema_oscuro", False)
            tema_claro = datos1.get("estado_tema_claro", False)
            tema_SSistema = datos1.get("estado_casilla_Sitem", False)

            if tema_oscuro and not tema_claro and not tema_SSistema:
                self.Switch_oscuro.set_active(True)
                self.Switch_Claro.set_active(False)
                self.casilla_Sistem.set_active(False)
    
                self.Switch_oscuro.set_sensitive(True)
                self.Switch_Claro.set_sensitive(True)

            elif tema_claro and not tema_oscuro and not tema_SSistema:
                self.Switch_Claro.set_active(True)
                self.Switch_oscuro.set_active(False)
                self.casilla_Sistem.set_active(False)
                
                self.Switch_oscuro.set_sensitive(True)
                self.Switch_Claro.set_sensitive(True)

            elif tema_SSistema and not tema_oscuro and not tema_claro:
                self.casilla_Sistem.set_active(True)
                self.Switch_Claro.set_active(False)
                self.Switch_oscuro.set_active(False)
                
                #deshabilitamos los switches cuando la casilla del sistema está marcada
                self.Switch_Claro.set_sensitive(False)
                self.Switch_oscuro.set_sensitive(False)

        
        return box_tem

    def obtener_estado_temas(self):
        """
        Función que solo obtiene el estado de los widgets.
        """
        est_casilla = self.casilla_Sistem.get_active()
        est_switch_oscuro = self.Switch_oscuro.get_active()
        est_switch_claro = self.Switch_Claro.get_active()

        if est_casilla:
            
            est_switch_oscuro = False
            est_switch_claro = False

        

        return est_casilla, est_switch_oscuro, est_switch_claro

    def guardar_configuracion_Estilo(self, widget=None):
        """
        Guarda los estados de los widgets en un diccionario.
        """
        est_casilla, est_switch_oscuro, est_switch_claro = self.obtener_estado_temas()

        ruta_FondoImg_1 = self.Entry_Ruta1.get_text().strip()


        dict_Confg_Estilo = {
            "estado_casilla_Sitem": est_casilla,
            "estado_tema_oscuro": est_switch_oscuro,
            "estado_tema_claro": est_switch_claro,
            "Ruta_IMGFONDO_1": ruta_FondoImg_1
        }

        crear_archivos_recurrentes("dict_Confg_Estilo.json", "json", dict_Confg_Estilo)
        self.marcar_cambios(False)
        
    def forzar_tema_oscuro(self):
        """
        Función que fuerza el tema oscuro en toda la aplicación.
        """
        style_manager = Adw.StyleManager.get_default()
        # Establece el esquema de color a oscuro.
        style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

    def forzar_tema_claro(self):
        """
        Función que fuerza el tema claro en toda la aplicación.
        """
        style_manager = Adw.StyleManager.get_default()
        # Establece el esquema de color a claro.
        style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)

    def restablecer_tema_del_sistema(self):
        """
        Función que restablece el tema a la preferencia del sistema.
        """
        style_manager = Adw.StyleManager.get_default()
        # Restablece el esquema de color a la preferencia por defecto del sistema.
        style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def Aplicar_Tema_SUP(self):
        datos1 = leer_archivo_recurrente("dict_Confg_Estilo.json", "json")

        if datos1:
            tema_oscuro = datos1.get("estado_tema_oscuro", False)
            tema_claro = datos1.get("estado_tema_claro", False)
            tema_SSistema = datos1.get("estado_casilla_Sitem", False)

            if tema_oscuro and not tema_claro and not tema_SSistema:
                self.forzar_tema_oscuro()
                
    
            elif tema_claro and not tema_oscuro and not tema_SSistema:
                self.forzar_tema_claro()
                
                
            elif tema_SSistema and not tema_oscuro and not tema_claro:
                self.restablecer_tema_del_sistema()
                

            


    def Seleccionar_FondosPanta(self):
        """
        Muestra y posiciona los widgets encargados de seleccionar una imagen para ser
        usada en distintas partes del programa
        """

        box_SelcImg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_SelcImg.set_hexpand(True)

        label_nomb1 = Gtk.Label(label="Seleccionar imagen: ")

        self.Entry_Ruta1 = Gtk.Entry()
        self.Entry_Ruta1.set_editable(False)
        self.Entry_Ruta1.set_hexpand(True)


        ubicacion_preder_IMG = os.path.join(get_recursos_dir(), "Imágenes", "Logos_MERIDA_SOLO_Con-Fondo_03.svg")

        dict_Estilo_Config = leer_archivo_recurrente("dict_Confg_Estilo.json", "json")
        if dict_Estilo_Config:
            dato_img = dict_Estilo_Config.get("Ruta_IMGFONDO_1", ubicacion_preder_IMG)
        
        else:
            dato_img = ubicacion_preder_IMG


        self.Entry_Ruta1.set_text(dato_img)


        boton_select1 = Gtk.Button(label="...")
        boton_select1.connect("clicked", self.dialog_select_ArchImg)


        box_SelcImg.append(label_nomb1)
        box_SelcImg.append(self.Entry_Ruta1)
        box_SelcImg.append(boton_select1)

        return box_SelcImg

    def dialog_select_ArchImg(self, widget=None):
        """
        Abre un diálogo Gtk.FileChooserDialog que permite al usuario seleccionar 
        un archivo de imagen. 

        Parámetros:
            widget (Gtk.Widget, opcional): El widget que disparó la acción 
            (puede ser None).

        """
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar una carpeta",
            transient_for=self.get_root(),
            modal=True,
            action=Gtk.FileChooserAction.OPEN,
            )

        #Creación de filtros para archivos de imagen
        filtro_png = Gtk.FileFilter()
        filtro_png.set_name("Archivos PNG (*.png)")
        filtro_png.add_pattern("*.png")
        dialog.add_filter(filtro_png)

        filtro_jpg = Gtk.FileFilter()
        filtro_jpg.set_name("Archivos JPG y JPEG (*.jpg, *.jpeg)")
        filtro_jpg.add_pattern("*.jpg")
        filtro_jpg.add_pattern("*.jpeg")
        dialog.add_filter(filtro_jpg)

        dialog.add_button("Seleccionar", Gtk.ResponseType.OK)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)

        dialog.connect("response", self.on_Archivo_Seleccionado)
        dialog.present()

    def on_Archivo_Seleccionado(self, dialog, response):

        """
        Maneja la respuesta del usuario al seleccionar un archivo de imagen. 

        Proceso:
            1. Obtiene la ruta del archivo
            2. La inserta directamente en self.Entry1 (o cualquier entry correspondiente)
            3. Marca cambios para señalar guardado
            4. Destruye el dialogo.

        
        """

        if response == Gtk.ResponseType.OK:
            file_get = dialog.get_file()

            if file_get:
                self.Entry_Ruta1.set_text(file_get.get_path())
                self.marcar_cambios(True)


        dialog.destroy()