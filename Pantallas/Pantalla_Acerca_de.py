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
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GdkPixbuf

from Lib_Extra.Rutas_Gestion import get_recursos_dir

class Pantalla_AcercaDe(Gtk.Dialog):
    def __init__(self, parent=None):
        super().__init__(title="Acerca de", transient_for=parent, modal=True)
        self.set_default_size(700, 650)

        self.VERSIÓN_PROGRAM = "1.0"
        self.SOBRE_VERSIÓN = "Editor Merida"
        self.SOBRE_PROGRAM = "Hecho con amor."
        self.SOBRE_TECNO = "Gtk+4 y Python 3"

        self.LOGO_COMPLETO = os.path.join(get_recursos_dir(), "Imágenes", "Logos_MERIDA_Completo_Sin-Fondo_02.svg") 

        self.CREDITOS_SUP = {
            "DGonzak": "dgonzak4@gmail.com",
        }

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        self.crear_vista_principal()
        self.crear_vista_creditos()
        self.crear_botones()

        caja = self.get_content_area()
        caja.append(self.stack)
        caja.append(self.vbox_Botons)

        self.set_default_response(Gtk.ResponseType.CLOSE)
        self.add_button("Cerrar", Gtk.ResponseType.CLOSE)
        self.connect("response", lambda d, r: d.destroy())
        self.show()

    def crear_vista_principal(self):
        vbox_Principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox_Principal.set_margin_top(10)
        vbox_Principal.set_margin_bottom(10)
        vbox_Principal.set_margin_start(10)
        vbox_Principal.set_margin_end(10)
        vbox_Principal.set_vexpand(True)
        vbox_Principal.set_hexpand(True)

        vbox_imagen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_imagen.set_vexpand(True)
        vbox_imagen.set_hexpand(True)

        Titulo_SUP = Gtk.Label(label="<span size='large'><b>SOBRE ESTE SOFTWARE</b></span>")
        Titulo_SUP.set_use_markup(True)

        logo = Gtk.Picture.new_for_filename(self.LOGO_COMPLETO)
        logo.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
        logo.set_size_request(200,200)
        
        #Textview para "Sobre este programa"
        TextView_Infor_SobrProgram = Gtk.TextView()
        TextView_Infor_SobrProgram.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        TextView_Infor_SobrProgram.set_editable(False)
        TextView_Infor_SobrProgram.set_focusable(False)

        #CSS para fondo o estilo
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        textview.background {
            background-color: #242323;
        }


        """)

        
        style_context_infor = TextView_Infor_SobrProgram.get_style_context()
        style_context_infor.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context_infor.add_class("background")



        #Cargar texto al textview    
        try:
            with open(os.path.join(get_recursos_dir(), "Texto", "explicacion_Sobr_Program_Vent_Ayuda.txt")) as txt1:

                contenido_txt1 = txt1.read()
        except Exception as e:
            contenido_txt1 = "Archivo de explicacion no encontrado\nExplicación de emergencia: MERIDA: una herramienta flexible para la creación literaria y académica."

        TextView_Infor_SobrProgram.get_buffer().set_text(contenido_txt1)

        #Posicionamiento de widgets

        vbox_imagen.append(logo)

        vbox_Principal.append(Titulo_SUP)
        vbox_Principal.append(vbox_imagen)
        vbox_Principal.append(self.crear_seccion("SOBRE EL PROGRAMA"))
        vbox_Principal.append(TextView_Infor_SobrProgram)
        vbox_Principal.append(self.crear_seccion("VERSIÓN", self.VERSIÓN_PROGRAM))
        vbox_Principal.append(self.crear_seccion("SOBRE ESTA VERSIÓN", f"Esta versión contiene: {self.SOBRE_VERSIÓN}"))
        vbox_Principal.append(self.crear_seccion("TECNOLOGÍAS USADAS", self.SOBRE_TECNO))

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(vbox_Principal)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self.stack.add_named(scroll, "principal")

    def crear_vista_creditos(self):
        vbox_creditos = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox_creditos.set_margin_top(15)
        vbox_creditos.set_margin_bottom(15)
        vbox_creditos.set_margin_start(15)
        vbox_creditos.set_margin_end(15)

        titulo = Gtk.Label(label="<span size='large'><b>Créditos</b></span>")
        titulo.set_use_markup(True)
        vbox_creditos.append(titulo)

        subtitulo = Gtk.Label(label="<b>Desarrolladores y colaboradores:</b>")
        subtitulo.set_use_markup(True)
        subtitulo.set_margin_top(10)
        subtitulo.set_margin_bottom(10)
        vbox_creditos.append(subtitulo)

        for nombre, correo in self.CREDITOS_SUP.items():
            caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            caja.set_margin_bottom(10)
            caja.set_margin_start(20)
            caja.set_margin_end(20)

            etiqueta = Gtk.Label(label=f"<b>{nombre}</b>")
            etiqueta.set_use_markup(True)
            etiqueta.set_xalign(0)
            caja.append(etiqueta)

            entrada = Gtk.Entry()
            entrada.set_text(correo)
            entrada.set_editable(False)
            entrada.set_focusable(False)
            entrada.set_css_classes(["flat"])
            entrada.set_alignment(0.0)
            entrada.set_margin_top(2)
            caja.append(entrada)

            vbox_creditos.append(caja)

        vbox_creditos.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        scroll_creditos = Gtk.ScrolledWindow()
        scroll_creditos.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_creditos.set_child(vbox_creditos)
        scroll_creditos.set_vexpand(True)
        scroll_creditos.set_hexpand(True)

        self.stack.add_named(scroll_creditos, "creditos")

    def crear_botones(self):
        self.vbox_Botons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.vbox_Botons.set_margin_top(10)

        btn_anterior = Gtk.Button(label="← Principal")
        btn_anterior.connect("clicked", lambda b: self.stack.set_visible_child_name("principal"))
        self.vbox_Botons.append(btn_anterior)

        btn_siguiente = Gtk.Button(label="Créditos →")
        btn_siguiente.connect("clicked", lambda b: self.stack.set_visible_child_name("creditos"))
        self.vbox_Botons.append(btn_siguiente)

    def crear_seccion(self, titulo, contenido=None):
        caja = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        etiqueta_titulo = Gtk.Label(label=f"<b>{titulo}</b>")
        etiqueta_titulo.set_use_markup(True)
        etiqueta_titulo.set_xalign(0)

        if contenido:

            etiqueta_contenido = Gtk.Label(label=contenido)
            etiqueta_contenido.set_xalign(0)
            caja.append(etiqueta_titulo)
            caja.append(etiqueta_contenido)
            return caja
        
        else:
            caja.append(etiqueta_titulo)
            return caja


