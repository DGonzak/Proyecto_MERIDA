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
import re
import json

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Pango

from Pantallas.Clases_Pantalla_Administrativa.Vista_AjustesGenerales import Vista_AjustesGenerales
from Pantallas.Clases_Pantalla_Administrativa.Vista_CombTeclas import Vista_Combinacion_Teclas
from Pantallas.Clases_Pantalla_Administrativa.Vista_BaseDeDatos import Vista_Base_De_Datos
from Pantallas.Clases_Pantalla_Administrativa.Vista_AjustesEstilo import Vista_AjustesEstilo

from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions
from BDs_Functions.Models_BD import BD_Comb_Teclas


class pantalla_admins(Gtk.Window):
    def __init__(self, Pantalla_principal):
        super().__init__(title="Ajustes")
        
        self.maximize()

        self.Pantalla_principal = Pantalla_principal
        self.BD_ComTecl_Functions = BD_ComTecl_Functions()

        box_principal = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.set_child(box_principal)

        Lista_Lateral = Gtk.ListBox()
        Lista_Lateral.set_selection_mode(Gtk.SelectionMode.NONE)

        item_ajustes = Gtk.ListBoxRow()
        Boton_Ajustes = Gtk.Button(label="Ajustes Generales")
        Boton_Ajustes.connect("clicked", self.cambiar_página, "ajustes_generales")
        item_ajustes.set_child(Boton_Ajustes)

        item_combteclas = Gtk.ListBoxRow()
        Boton_ComTeclas = Gtk.Button(label="Combinaciones de Teclas")
        Boton_ComTeclas.connect("clicked", self.cambiar_página, "combinacion_teclas")
        item_combteclas.set_child(Boton_ComTeclas)

        item_AjusEstilo = Gtk.ListBoxRow()
        Boton_AjusEstilo = Gtk.Button(label="Ajustes de Estilo")
        Boton_AjusEstilo.connect("clicked", self.cambiar_página, "ajustes_estilo")
        item_AjusEstilo.set_child(Boton_AjusEstilo)

        item_BaseDatos = Gtk.ListBoxRow()
        Boton_BaseDatos = Gtk.Button(label="Bases de Datos")
        Boton_BaseDatos.connect("clicked", self.cambiar_página, "bases_de_datos")
        item_BaseDatos.set_child(Boton_BaseDatos)

        Lista_Lateral.append(item_ajustes)
        Lista_Lateral.append(item_combteclas)
        Lista_Lateral.append(item_AjusEstilo)
        Lista_Lateral.append(item_BaseDatos)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)


        vista_comteclas = Vista_Combinacion_Teclas(Pantalla_principal)
        vista_AjustesGenerales = Vista_AjustesGenerales(Pantalla_principal)
        Vista_Ajustes_Estilo = Vista_AjustesEstilo()
        Vista_BaseDeDatos = Vista_Base_De_Datos()

        #Scroll
        #Scroll para ajustes generales
        scroll_AjustGenerales = Gtk.ScrolledWindow()
        scroll_AjustGenerales.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_AjustGenerales.set_child(vista_AjustesGenerales)
        scroll_AjustGenerales.set_vexpand(True)
        scroll_AjustGenerales.set_hexpand(True)

        #Scroll para ajustes de estilo
        scroll_AjustEstilo = Gtk.ScrolledWindow()
        scroll_AjustEstilo.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_AjustEstilo.set_child(Vista_Ajustes_Estilo)
        scroll_AjustEstilo.set_vexpand(True)
        scroll_AjustEstilo.set_hexpand(True)


        # Aqui se integran las importaciones
        self.stack.add_titled(scroll_AjustGenerales, "ajustes_generales", "Ajustes Generales")
        self.stack.add_titled(vista_comteclas, "combinacion_teclas", "Combinaciones de Teclas")
        self.stack.add_titled(scroll_AjustEstilo, "ajustes_estilo", "Ajustes de Estilo")
        self.stack.add_titled(Vista_BaseDeDatos, "bases_de_datos", "Bases de Datos")

        box_principal.append(Lista_Lateral)
        box_principal.append(self.stack)

        self.show()

    def cambiar_página(self, boton, nombre_página):
        self.stack.set_visible_child_name(nombre_página)






 
