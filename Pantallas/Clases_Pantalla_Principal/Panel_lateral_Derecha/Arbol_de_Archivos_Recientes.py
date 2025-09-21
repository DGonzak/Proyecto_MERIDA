import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

import os
import asyncio

from BDs_Functions.BD_RecentArch_Funct import BD_Recient_Arch_Functions
from Lib_Extra.Funciones_extras import mostrar_vent_IEO

class Pestana_Recientes(Gtk.Box):
    def __init__(self, Pantalla_Principal):#Se recibe la referencia de la pantalla principal (self)
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        #---------------------Iniciadores de Clase (Instancias)------------

        #Se instancia, y ya se tiene acceso a las funciones de la pantalla principal
        self.Pantalla_Principal = Pantalla_Principal

        self.BD_Recient_Arch_Functions = BD_Recient_Arch_Functions()

        #-----------------------Contenedores------------------------
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.box_btn = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        #------------------------Árbol de Recientes--------------
        # ListBox para mostrar carpetas y sus archivos
        self.listbox = Gtk.ListBox()
        

        #----------------------Scroll------------------
        self.Scroll_Recent = Gtk.ScrolledWindow()
        self.Scroll_Recent.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.Scroll_Recent.set_child(self.vbox)
        self.Scroll_Recent.set_vexpand(True)

        # Botón para limpiar
        self.boton_limpiar = Gtk.Button(label="Limpiar Recientes")
        self.boton_limpiar.connect("clicked",self.Eliminar_Recientes_ArbRecent)
        
        #------------------------Posicionamiento de los widgets-----------------
        self.vbox.append(self.listbox)
        self.box_btn.append(self.boton_limpiar)

        self.append(self.Scroll_Recent)
        self.append(self.box_btn)

        self.actualizar_árbolArch_recent()

    def actualizar_árbolArch_recent(self):
        """
        Reconstruye y actualiza visualmente la pestaña de archivos recientes.

        Esta función obtiene los registros de archivos recientes desde la base de 
        datos interna, los ordena por fecha de registro (del más reciente al más antiguo), y crea un árbol
        visual de accesos rápidos. Cada entrada está agrupada por su etiqueta 
        correspondiente.

        Dentro de cada grupo (Gtk.Expander), se listan los archivos presentes en la 
        carpeta asociada al registro, y se conecta cada fila a una función que permite 
        abrir el archivo cuando se selecciona.

        Esta pestaña permite al usuario acceder rápidamente a los documentos usados 
        recientemente, organizados por etiquetas y accesibles desde la interfaz.

        No recibe parámetros y debe ser invocada cuando se quiera refrescar la 
        vista de archivos recientes.
        """
        self.listbox.remove_all()
        registros = self.BD_Recient_Arch_Functions.obtener_registros(modo="diccionario")

        registros_ordenados = sorted(registros.values(), key=lambda x: x["Fecha_de_Registro"], reverse=True)

        for datos in registros_ordenados:
            ruta_carpeta = datos["RA_Ruta_Carpeta"]
            etiqueta = datos["RA_Nombre_Etiqueta"]
            if not ruta_carpeta or not os.path.exists(ruta_carpeta):
                continue

            expander = Gtk.Expander(label=etiqueta)

            listbox_archivos = Gtk.ListBox()
            listbox_archivos.set_selection_mode(Gtk.SelectionMode.SINGLE)
            listbox_archivos.connect("row-activated", self._on_archivo_seleccionado, ruta_carpeta)

            for archivo in os.listdir(ruta_carpeta):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    row = Gtk.ListBoxRow()
                    label = Gtk.Label(label=archivo, xalign=0)
                    row.set_child(label)
                    listbox_archivos.append(row)

            expander.set_child(listbox_archivos)
            self.listbox.append(expander)

    def _on_archivo_seleccionado(self, listbox, row, ruta_carpeta):
        """
        Abre un archivo desde la pestaña de archivos recientes al hacer clic en su fila.

        Esta función se conecta al evento `row-activated` del Gtk.ListBox. Cuando el 
        usuario selecciona un archivo, se obtiene su nombre desde el Gtk.Label, se 
        construye su ruta completa y se solicita su apertura mediante el método `abrir_archivo_ArbolArch` de
        la pantalla principal.

        Args:
            listbox (Gtk.ListBox): Contenedor que contiene las filas de archivos.
            row (Gtk.ListBoxRow): Fila seleccionada que contiene la etiqueta del archivo.
            ruta_carpeta (str): Ruta base donde se encuentra el archivo mostrado en la lista.
        """
        nombre_archivo = row.get_child().get_text()
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)

        self.Pantalla_Principal.abrir_archivo_ArbolArch(ruta_completa)

    def Eliminar_Recientes_ArbRecent(self, widget=None):
        """
        Elimina todos los registros de archivos recientes tras una confirmación del 
        usuario.

        Esta función muestra un cuadro de diálogo de advertencia solicitando 
        confirmación para eliminar todos los archivos recientes. Si el usuario acepta, 
        se eliminan los registros desde la base de datos interna (`BD_Recient_Arch_Functions`) y se actualiza visualmente
        la pestaña de archivos recientes.

        Esta acción es irreversible y debe ejecutarse con precaución.

        Args:
            widget (Gtk.Widget, opcional): Widget que puede haber activado la acción 
            (no utilizado).
        """
 
        """Nota: Se necesita pasar la ventana madre para el dialog, por ello se señala
        mediante self.Pantalla_principal_Editor esto."""
        response = mostrar_vent_IEO(
            self.Pantalla_Principal,
            "Advertencia",
            "¿Está seguro de eliminar los archivos recientes?\nEsto no se puede deshacer.",
            Gtk.MessageType.QUESTION,
            2,
            "Sí",
            "No",
            None
        )

        if response == Gtk.ResponseType.OK:
            self.BD_Recient_Arch_Functions.eliminar_todos_registros()
            self.actualizar_árbolArch_recent()

