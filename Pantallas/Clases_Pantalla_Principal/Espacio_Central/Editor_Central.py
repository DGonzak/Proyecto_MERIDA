import os
import re


import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw

from Lib_Extra.Rutas_Gestion import get_data_dir,get_recursos_dir
from Lib_Extra.Tags_Formato import crear_tags_Formato_Titulo, crear_tags_Formato_Etiquetas, crear_tags_Formato_Cuerpo


class Vista_Editor_Central(Gtk.Box):
    def __init__ (self, Pantalla_Principal=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        #=============================
        #Iniciadores de clases
        #============================
        self.Pantalla_Principal = Pantalla_Principal


        #========================================
        #Interfaz del EDITOR
        #========================================
        self.set_vexpand(True)
        self.set_hexpand(True)

        # Título
        self.text_view_titulo = Gtk.TextView()
        self.text_view_titulo.set_wrap_mode(Gtk.WrapMode.NONE)
        self.text_view_titulo.set_editable(True)
        self.text_view_titulo.set_size_request(-1, 30)  # Solo altura
        self.text_view_titulo.get_buffer().connect("changed", self.formatear_texto_en_titulo)
        
        # Controlador de teclado para text_view_titulo
        controller_titulo = Gtk.EventControllerKey()
        controller_titulo.connect("key-pressed", self.limitar_a_una_linea, "titulo")
        self.text_view_titulo.add_controller(controller_titulo)


        self.text_view_titulo.set_margin_top(5)
        self.text_view_titulo.set_margin_bottom(5)
        self.text_view_titulo.set_margin_start(15)
        self.text_view_titulo.set_margin_end(15)
        self.text_view_titulo.get_style_context().add_class("textview_Princi-focus")

        # Etiquetas
        self.text_view_etiquetas = Gtk.TextView()
        self.text_view_etiquetas.set_wrap_mode(Gtk.WrapMode.NONE)
        self.text_view_etiquetas.set_editable(True)
        self.text_view_etiquetas.set_size_request(-1, 40)
        
        # Controlador de foco
        focus_controller_etiquetas = Gtk.EventControllerFocus()
        
        #entra en el foco
        focus_controller_etiquetas.connect("enter", self.on_focus_in)
        
        #sale del foco
        focus_controller_etiquetas.connect("leave", self.on_focus_out)
       
        self.text_view_etiquetas.add_controller(focus_controller_etiquetas)

        # Controlador de teclado para text_view_etiquetas
        controller_etiquetas = Gtk.EventControllerKey()
        controller_etiquetas.connect("key-pressed", self.limitar_a_una_linea, "etiqueta")
        self.text_view_etiquetas.add_controller(controller_etiquetas)

        self.text_view_etiquetas.set_margin_start(15)
        self.text_view_etiquetas.set_margin_end(15)
        self.text_view_etiquetas.get_style_context().add_class("textview_Princi-focus")

        # Cuerpo
        self.text_view_cuerpo = Gtk.TextView()
        self.text_view_cuerpo.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view_cuerpo.set_editable(True)
        self.text_view_cuerpo.get_buffer().connect("changed", self.formatear_texto_en_cambio_cuerpo)

        # Controlador de teclado para textview cuerpo
        controller_cuerpo = Gtk.EventControllerKey()
        controller_cuerpo.connect("key-pressed", self.limitar_a_una_linea, "cuerpo")
        self.text_view_cuerpo.add_controller(controller_cuerpo)

        self.text_view_cuerpo.set_margin_top(10)
        self.text_view_cuerpo.set_margin_bottom(10)
        self.text_view_cuerpo.set_margin_start(15)
        self.text_view_cuerpo.set_margin_end(15)
        self.text_view_cuerpo.get_style_context().add_class("textview_Princi-focus")


        Overlay_Cuerpo = self.imagen_de_fondo_Textview(self.text_view_cuerpo)


        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_child(Overlay_Cuerpo)
        scroll_window.set_vexpand(True)

        # Agregamos al contenedor vertical principal
        self.append(self.text_view_titulo)
        self.append(self.text_view_etiquetas)
        self.append(scroll_window)

        # Formato y base de datos
        crear_tags_Formato_Titulo(self.text_view_titulo)
        crear_tags_Formato_Etiquetas(self.text_view_etiquetas)
        crear_tags_Formato_Cuerpo(self.text_view_cuerpo)

        #self.Aplicar_CambiosTema_A_Esp_Widgets2()

    #===========================================
    #Funciones
    #============================================
    def formatear_texto_en_titulo(self, buffer_titulo):
        """
        Aplica el estilo 'título_docu' a todo el texto presente en 
        el buffer del título.

        Esta función es llamada por:crear_Editor_Central 
        """
        start, end = buffer_titulo.get_bounds()
        buffer_titulo.apply_tag_by_name("título_docu", start, end)

    def limitar_a_una_linea(self, controller, keyval, keycode, state, tipo):
        """
        Restringe el campo a una sola línea y gestiona el comportamiento de 
        Enter y Shift+Enter para cambiar el enfoque entre los campos de texto 
        (título, etiquetas y cuerpo).

        Args:
            controller: Controlador del evento de teclado.
            
            keyval: Valor de la tecla presionada.
            
            keycode: Código de la tecla presionada.
            
            state: Estado de las teclas modificadoras (como Shift).
            
            tipo (str): Tipo de campo ('titulo', 'etiqueta', 'cuerpo') 
            donde se aplica la restricción.

        Returns:
            bool: True si se bloquea el salto de línea, False si se permite.

        Esta función es llamada por: crear_Editor_Central
        """
        widget = controller.get_widget()
        buffer_ = widget.get_buffer()
        start_iter = buffer_.get_start_iter()
        end_iter = buffer_.get_end_iter()
        text = buffer_.get_text(start_iter, end_iter, True)

        # Reemplaza saltos de línea pegados desde el portapapeles (solo para campos de una línea)
        if tipo in ("titulo", "etiqueta") and "\n" in text:
            text = text.replace("\n", " ")
            buffer_.set_text(text)

        is_enter = keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)
        is_shift = state & Gdk.ModifierType.SHIFT_MASK

        if is_enter:
            if is_shift:
                # Shift+Enter: campo anterior
                if tipo == "etiqueta":
                    self.text_view_titulo.grab_focus()
                    return True  # Bloquea salto de línea
                elif tipo == "cuerpo":
                    self.text_view_etiquetas.grab_focus()
                    return True  # Bloquea salto de línea
            else:
                # Enter normal: campo siguiente, excepto en el último (cuerpo)
                if tipo == "titulo":
                    self.text_view_etiquetas.grab_focus()
                    return True  # Bloquea salto de línea
                elif tipo == "etiqueta":
                    self.text_view_cuerpo.grab_focus()
                    return True  # Bloquea salto de línea
                # Si es "cuerpo", no se bloquea: se permite salto de línea

        return False  # Permite otros caracteres o salto de línea en cuerpo

    def on_focus_in(self, controller, *args):
        """
        Se ejecuta cuando un TextView gana el foco. Según esto, se puede realizar
        diversas acciones. Actualmente se tienen las siguientes inscritas:

        1. Cambiar el estado visual del widget enfocado (FOCUSED)
        2. Remover todas las etiquetas de estilo del buffer correspondiente, para ayudar
        en lo visual y en lo práctico al momento de escribir.
        
        Args:
            controller: Controlador de eventos asociado al foco.
            *args: Argumentos adicionales no utilizados.

        Esta función es llamada por: crear_Editor_Central
        """

        widget = controller.get_widget()
        if widget:
            context = widget.get_style_context()
            context.set_state(Gtk.StateFlags.FOCUSED)

            buffer = widget.get_buffer()
            start, end = buffer.get_bounds()
            buffer.remove_all_tags(start, end)

    def on_focus_out(self, controller, *args):
        self.Pantalla_Principal.on_focus_out_get(controller, *args)

    def formatear_texto_en_cambio_cuerpo(self, buffer_cuerpo):
        """
        Elimina todos los estilos del cuerpo de texto y aplica nuevos estilos en 
        función del contenido, utilizando marcas de Markdown y encabezados como 
        '#', '##', etc. Esta función se llama cada vez que "cambia" el texto del cuerpo.

        Esta función es llamada por: crear_Editor_Central; conectar_cambios_NotasTex
        """
        start, end = buffer_cuerpo.get_bounds()
        buffer_cuerpo.remove_all_tags(start, end)
        text_cuerpo = buffer_cuerpo.get_text(start, end, include_hidden_chars=False)
        self.aplicar_estilos_cuerpo(buffer_cuerpo, text_cuerpo)

    def imagen_de_fondo_Textview(self, textview):
        """
        Devuelve un Gtk.Overlay que contiene un TextView y un logo SVG como fondo
        que desaparece cuando el TextView contiene texto.
        """
        overlay = Gtk.Overlay()

        ubicacion_SVGs = os.path.join(get_recursos_dir(), "Imágenes")
        ruta_logo = os.path.join(ubicacion_SVGs, "Logos_MERIDA_Completo_Sin-Fondo_02.svg")

        # Carga y escalado del SVG con Picture
        logo  = Gtk.Picture.new_for_filename(ruta_logo)
        logo.set_content_fit(Gtk.ContentFit.SCALE_DOWN) #mantiene proporcion
        logo.set_halign(Gtk.Align.CENTER)
        logo.set_valign(Gtk.Align.CENTER)
        logo.set_opacity(0.30)
        logo.set_size_request(300, 300)

        # Hacemos que el logo no intercepte eventos
        logo.set_can_target(False)

        # Añadir widgets al overlay
        overlay.set_child(textview)     # el TextView es el hijo principal
        overlay.add_overlay(logo)       # encima, el logo

        # Señal: mostrar/ocultar logo según haya o no texto
        buffer_01 = textview.get_buffer()

        def cambiar_segun_texto(buffer, logo):
            start, end = buffer.get_bounds()
            texto = buffer.get_text(start, end, True)
            logo.set_visible(len(texto.strip()) == 0)

        buffer_01.connect("changed", cambiar_segun_texto, logo)

        # Inicializar visibilidad
        cambiar_segun_texto(buffer_01, logo)

        return overlay

    def aplicar_estilos_cuerpo(self, buffer_cuerpo, text_cuerpo):
        """Aplica estilos personalizados al texto del cuerpo de acuerdo a marcas 
        de Markdown como encabezados (nivel 1 a 4), negrita (**texto**) y 
        cursiva (*texto*).

        Args:
            buffer_cuerpo: El Gtk.TextBuffer del cuerpo del documento.
            text_cuerpo: Texto plano del cuerpo sobre el que se aplican los estilos.

        Esta función es llamada por: formatear_texto_en_cambio_cuerpo
        """
        lines = text_cuerpo.split("\n")
        offset = 0

        for line in lines:
            line_length = len(line)

            def aplicar_tag(tag_name):
                """
                Aplica un tag de estilo a una línea específica del texto.
                """
                start_iter = buffer_cuerpo.get_iter_at_offset(offset)
                end_iter = buffer_cuerpo.get_iter_at_offset(offset + line_length)
                buffer_cuerpo.apply_tag_by_name(tag_name, start_iter, end_iter)

            if line.startswith("# "):
                aplicar_tag("título_cuer")
            elif line.startswith("## "):
                aplicar_tag("sub2título")
            elif line.startswith("### "):
                aplicar_tag("sub3título")
            elif line.startswith("#### "):
                aplicar_tag("sub4título")

            for start, end in self.find_markdown_pattern(r"\*\*(.*?)\*\*", line):
                buffer_cuerpo.apply_tag_by_name(
                    "Negrita",
                    buffer_cuerpo.get_iter_at_offset(offset + start),
                    buffer_cuerpo.get_iter_at_offset(offset + end)
                )

            for start, end in self.find_markdown_pattern(r"\*(.*?)\*", line):
                buffer_cuerpo.apply_tag_by_name(
                    "Cursiva",
                    buffer_cuerpo.get_iter_at_offset(offset + start),
                    buffer_cuerpo.get_iter_at_offset(offset + end)
                )

            offset += line_length + 1

    def find_markdown_pattern(self, pattern, text):
        """
        Busca y devuelve las posiciones de coincidencias para un patrón 
        de Markdown dentro del texto.

        Args:
            pattern (str): Expresión regular que representa la sintaxis Markdown 
            (como negrita o cursiva).

            text (str): Texto en el que se buscarán coincidencias.

        Returns:
            list: Lista de tuplas (inicio, fin) de cada coincidencia encontrada 
            en el grupo 1.

        Esta función es llamada por: aplicar_estilos_cuerpo
        """
        matches = re.finditer(pattern, text)
        return [(m.start(1), m.end(1)) for m in matches]
