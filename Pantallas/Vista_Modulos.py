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
from Lib_Extra.Rutas_Gestion import get_recursos_dir

class pantalla_modulos(Gtk.Window):
    def __init__(self):
        super().__init__(title="Gestión de Módulos y Complementos")
        self.set_default_size(1000, 800)
    
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
        Vent_IntallModul.set_default_size(900, 600)
        content_area = Vent_IntallModul.get_content_area()
        
        box_pr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box_ajustes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        textview_regist =Gtk.TextView()
        textview_regist.set_editable(False)
        textview_regist.set_focusable(False)
        textview_regist.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview_regist.set_vexpand(True)
        textview_regist.set_hexpand(True)

        ruta_archivo_explicacion = os.path.join(get_recursos_dir(), "Texto", "explicacion_InstalModMeri_1.txt")
        
        try:
            with open(ruta_archivo_explicacion) as txt1:

                contenido_txt1 = txt1.read()
        except Exception as e:
            contenido_txt1 = "Archivo de explicacion no encontrado. Error: " + str(e)


        textview_regist.get_buffer().set_text(contenido_txt1)
        
        
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_child(textview_regist)
        scroll_window.set_vexpand(True)
        scroll_window.set_hexpand(True)

        btn_busArch = Gtk.Button(label="Instalar desde archivo")
        btn_busArch.set_tooltip_text("Seleccionar un archivo .modmeri para instalar un módulo o complemento")

        btn_busCarpet = Gtk.Button(label="Instalar desde carpeta")
        btn_busCarpet.set_tooltip_text("Seleccionar una carpeta que contenga módulos o complementos .modmeri")

        box_pr.append(scroll_window)
        box_pr.append(box_ajustes)

        box_ajustes.append(btn_busArch)
        box_ajustes.append(btn_busCarpet)

        content_area.append(box_pr)

        Vent_IntallModul.show()

    def seleccionar_modulo_ArchCarpet(self, ArchCarpet):
        """
        Abre una ventana de selección de archivo o carpeta, según el parámetro recibido.

        Args:
            ArchCarpet (str): "Archivo" para seleccionar un archivo, "Carpeta" para seleccionar una carpeta.
        """

        ventana_seleccion = Gtk.FileChooserDialog(
            title="Abrir archivo de módulo",
            action=Gtk.FileChooserAction.OPEN
        )
        ventana_seleccion.set_transient_for(self)
        ventana_seleccion.set_modal(True)

        ventana_seleccion.add_button("_Cancelar", Gtk.ResponseType.CANCEL)
        ventana_seleccion.add_button("_Abrir", Gtk.ResponseType.OK)

        filtro_md = Gtk.FileFilter()
        filtro_md.set_name("Archivos de módulo MERIDA (.modmeri)")
        filtro_md.add_pattern("*.modmeri")
        ventana_seleccion.add_filter(filtro_md)
    
        def on_response_ArchCarpet(dialog, response_id):
            """
            Maneja la respuesta del diálogo de selección de archivo o carpeta de la función:
            seleccionar_modulo_ArchCarpet. Devuelve la ruta del archivo o carpeta seleccionado.

            Args:
                dialog (Gtk.FileChooserDialog): El diálogo de selección.
                response_id (int): El ID de la respuesta del diálogo.
            """
            if response_id == Gtk.ResponseType.OK:
                archivo_seleccionado = dialog.get_filename()
                print("Archivo seleccionado: " + archivo_seleccionado)
    
            elif response_id == Gtk.ResponseType.CANCEL:
                print("Selección cancelada")
            
            dialog.destroy()