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
        
        #-------------------Inserción a la ventana-------------------
        box_sup.append(self.Entry_Busqueda)
        
        box_cent.append(self.Label_Sin_Modulos)

        box_infer.append(self.boton_instalar)
        box_pr.append(box_sup)
        box_pr.append(box_cent)
        box_pr.append(box_infer)

        self.set_child(box_pr)


