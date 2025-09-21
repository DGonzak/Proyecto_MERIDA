import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango

def crear_tags_Formato_NotasText(get_buffer):
    buffer_cuerpo = get_buffer.get_buffer()
    tag_table_cuerpo = buffer_cuerpo.get_tag_table()

    tag_titulo_cuerpo = Gtk.TextTag.new("título_cuer")
    tag_titulo_cuerpo.set_property("weight", Pango.Weight.BOLD)
    tag_titulo_cuerpo.set_property("scale", 1.5)
    tag_table_cuerpo.add(tag_titulo_cuerpo)

    tag_sub2titulo = Gtk.TextTag.new("sub2título")
    tag_sub2titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub2titulo.set_property("scale", 1.2)
    tag_table_cuerpo.add(tag_sub2titulo)

    tag_sub3titulo = Gtk.TextTag.new("sub3título")
    tag_sub3titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub3titulo.set_property("scale", 1.0)
    tag_table_cuerpo.add(tag_sub3titulo)

    tag_sub4titulo = Gtk.TextTag.new("sub4título")
    tag_sub4titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub4titulo.set_property("scale", 1.0)
    tag_sub4titulo.set_property("style", Pango.Style.ITALIC)
    tag_table_cuerpo.add(tag_sub4titulo)

    tag_negrita = Gtk.TextTag.new("Negrita")
    tag_negrita.set_property("weight", Pango.Weight.BOLD)
    tag_table_cuerpo.add(tag_negrita)

    tag_cursiva = Gtk.TextTag.new("Cursiva")
    tag_cursiva.set_property("style", Pango.Style.ITALIC)
    tag_table_cuerpo.add(tag_cursiva)

def crear_tags_Formato_Titulo(get_buffer):
    buffer_titulo = get_buffer.get_buffer()
    tag_table_titulo = buffer_titulo.get_tag_table()
    tag_titulo_titulo = Gtk.TextTag.new("título_docu")
    tag_titulo_titulo.set_property("weight", Pango.Weight.BOLD)
    tag_titulo_titulo.set_property("scale", 2.0)
    tag_table_titulo.add(tag_titulo_titulo)

def crear_tags_Formato_Etiquetas(get_buffer):
    buffer_etiquetas = get_buffer.get_buffer()
    tag_table_etiquetas = buffer_etiquetas.get_tag_table()

    tag_color_verdetag = Gtk.TextTag.new("VerdeTag")
    tag_color_verdetag.set_property("foreground", "green")
    tag_color_verdetag.set_property("weight", Pango.Weight.BOLD)
    tag_table_etiquetas.add(tag_color_verdetag)

    tag_color_rojotag = Gtk.TextTag.new("RojoTag")
    tag_color_rojotag.set_property("foreground", "red")
    tag_color_rojotag.set_property("weight", Pango.Weight.BOLD)
    tag_table_etiquetas.add(tag_color_rojotag)

def crear_tags_Formato_Cuerpo(get_buffer):
    buffer_cuerpo = get_buffer.get_buffer()
    tag_table_cuerpo = buffer_cuerpo.get_tag_table()

    tag_titulo_cuerpo = Gtk.TextTag.new("título_cuer")
    tag_titulo_cuerpo.set_property("weight", Pango.Weight.BOLD)
    tag_titulo_cuerpo.set_property("scale", 2.0)
    tag_table_cuerpo.add(tag_titulo_cuerpo)

    tag_sub2titulo = Gtk.TextTag.new("sub2título")
    tag_sub2titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub2titulo.set_property("scale", 1.5)
    tag_table_cuerpo.add(tag_sub2titulo)

    tag_sub3titulo = Gtk.TextTag.new("sub3título")
    tag_sub3titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub3titulo.set_property("scale", 1.2)
    tag_table_cuerpo.add(tag_sub3titulo)

    tag_sub4titulo = Gtk.TextTag.new("sub4título")
    tag_sub4titulo.set_property("weight", Pango.Weight.BOLD)
    tag_sub4titulo.set_property("scale", 1.2)
    tag_sub4titulo.set_property("style", Pango.Style.ITALIC)
    tag_table_cuerpo.add(tag_sub4titulo)

    tag_negrita = Gtk.TextTag.new("Negrita")
    tag_negrita.set_property("weight", Pango.Weight.BOLD)
    tag_table_cuerpo.add(tag_negrita)

    tag_cursiva = Gtk.TextTag.new("Cursiva")
    tag_cursiva.set_property("style", Pango.Style.ITALIC)
    tag_table_cuerpo.add(tag_cursiva)