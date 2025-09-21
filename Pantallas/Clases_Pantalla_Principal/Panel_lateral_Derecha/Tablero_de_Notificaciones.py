
import textwrap
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from datetime import datetime

class Pestana_Notificaciones(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        #=========Creación de contenedores==============
        self.box_ContAvisos = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Label inicial (cuando no hay avisos)
        self.label_sin_avisos = Gtk.Label(label="Sin avisos")
        
        # ListBox para avisos
        self.listbox_avisos = Gtk.ListBox()

        self.box_btns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        scroll_ContAvisos = Gtk.ScrolledWindow()
        scroll_ContAvisos.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_ContAvisos.set_child(self.box_ContAvisos)
        scroll_ContAvisos.set_vexpand(True)

        #========================
        #Botones
        #======================
        btn_limpiar_Y_Actualir = Gtk.Button(label="Limpiar tablero")
        btn_limpiar_Y_Actualir.connect("clicked", self.limpiar_avisos)

        #=============================
        #Posicionamiento de widgets
        #===============================
        self.box_ContAvisos.append(self.label_sin_avisos)
        self.box_ContAvisos.append(self.listbox_avisos)

        self.box_btns.append(btn_limpiar_Y_Actualir)

        self.append(scroll_ContAvisos)
        self.append(self.box_btns)

    #============================
    # Funciones auxiliares
    #============================

    def agregar_aviso(self, origen, titulo, descripcion):
        """Agrega un aviso con los datos indicados y hora actual"""
        
        if self.label_sin_avisos.get_parent():
            self.box_ContAvisos.remove(self.label_sin_avisos)

        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        box_aviso = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box_aviso.set_margin_start(10)
        box_aviso.set_margin_end(10)
        box_aviso.set_margin_top(5)
        box_aviso.set_margin_bottom(5)

        lbl_origen = Gtk.Label(xalign=0)
        lbl_origen.set_markup(f"<b>Desde</b>: {origen}")
        lbl_origen.set_wrap(True)

        lbl_titulo = Gtk.Label(xalign=0)
        lbl_titulo.set_markup(f"<b>{titulo}</b>")
        lbl_titulo.set_wrap(True)

        # --- Mejoras para TextView ---
        textview_desc = Gtk.TextView()
        textview_desc.set_wrap_mode(Gtk.WrapMode.WORD)   # corte respetando palabras
        textview_desc.set_editable(False)
        textview_desc.set_cursor_visible(False)
        textview_desc.set_left_margin(10)
        textview_desc.set_right_margin(10)
        textview_desc.set_top_margin(5)
        textview_desc.set_bottom_margin(5)

        buffer_desc = textview_desc.get_buffer()
        tag_table = buffer_desc.get_tag_table()

        tag_left = Gtk.TextTag.new("left")
        tag_left.set_property("justification", Gtk.Justification.LEFT)
        tag_left.set_property("pixels-above-lines", 2)
        tag_left.set_property("pixels-below-lines", 2)
        tag_table.add(tag_left)

        # Normalizar texto para evitar espacios raros
        descripcion = textwrap.dedent(descripcion).strip()

        buffer_desc.set_text(descripcion)
        start_iter = buffer_desc.get_start_iter()
        end_iter = buffer_desc.get_end_iter()
        buffer_desc.apply_tag(tag_left, start_iter, end_iter)
        # --- Fin mejoras ---

        lbl_hora = Gtk.Label(xalign=0)
        lbl_hora.set_markup(f"<b>Hora</b>: {hora_actual}")
        lbl_hora.set_wrap(True)

        box_aviso.append(lbl_origen)
        box_aviso.append(lbl_titulo)
        box_aviso.append(textview_desc)
        box_aviso.append(lbl_hora)

        row = Gtk.ListBoxRow()
        row.set_child(box_aviso)
        self.listbox_avisos.append(row)



    def limpiar_avisos(self, button):
        """Elimina todos los avisos de la listbox"""
        child = self.listbox_avisos.get_first_child()
        while child:
            siguiente = child.get_next_sibling()
            self.listbox_avisos.remove(child)
            child = siguiente

        # Restaurar label "Sin avisos"
        if not self.label_sin_avisos.get_parent():
            self.box_ContAvisos.prepend(self.label_sin_avisos)
