import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
import os

from Lib_Extra.Tags_Formato import crear_tags_Formato_NotasText
from Lib_Extra.Funciones_extras import aplicar_estilos_css, control_label_estado
from Lib_Extra.Rutas_Gestion import get_recursos_dir



class Pestana_Notas_Tex(Gtk.Box):
    def __init__(self, Pantalla_Principal):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_vexpand(True)

        #---------------------Iniciadores de Clase/Funciones (instancias)----------------
        self.Pantalla_Principal = Pantalla_Principal


        ruta_estilos = os.path.join(get_recursos_dir(), "Estilo_CSS", "estilo_base.css")
        aplicar_estilos_css(ruta_css=ruta_estilos)

        #---------------------Contenedores----------------------------------
        ###Contenedor (Cuarto) Pestaña Notebook Izquierda (Textviews de las notas)
        self.vbox_CuartPestNotas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        #-------------------------Scroll------------------------------------
        self.Scroll_NotasTex = Gtk.ScrolledWindow()
        self.Scroll_NotasTex.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.Scroll_NotasTex.set_child(self.vbox_CuartPestNotas)
        self.Scroll_NotasTex.set_vexpand(True)


        #-----------------------Botones------------------------
        #Boton para crear NotasTex
        self.btn_gen_Notastex = Gtk.Button(label="Crear nota")
        self.btn_gen_Notastex.connect("clicked", self.Crear_NotasTex)


        #-------------------Empaquetar----------------------------------------
        self.append(self.Scroll_NotasTex)
        self.append(self.btn_gen_Notastex)


    def Crear_NotasTex(self, widget=None, *args):
        """
        Crea y agrega una nueva nota textual (NotasTex) editable en la interfaz gráfica.

        Esta función construye un contenedor horizontal que incluye un Gtk.TextView
        para ingresar texto (la nota) y un botón para eliminarla. Aplica estilos 
        específicos a los widgets, configura el TextView para que sea editable y 
        expandible horizontalmente, y lo vincula al sistema de control de cambios de 
        la pantalla principal.

        Además, el TextView se agrega a la lista de notas de la pantalla principal 
        para su gestión posterior y se enfoca automáticamente al ser creado.

        Args:
            widget (Gtk.Widget, opcional): Widget que puede haber activado la acción.
            *args: Argumentos adicionales (no utilizados directamente).
        """

        Contenedor_Princi = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        contenedor_nota = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        contenedor_nota.get_style_context().add_class("nota-contenedor")

        nueva_nota_textview = Gtk.TextView()
        nueva_nota_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        nueva_nota_textview.set_size_request(-1, 100)

        nueva_nota_textview.get_style_context().add_class("nota-textview")

        crear_tags_Formato_NotasText(nueva_nota_textview)
        nueva_nota_textview.set_editable(True)
        nueva_nota_textview.set_hexpand(True)


        self.Pantalla_Principal.conectar_cambios_NotasTex(nueva_nota_textview)
        self.Pantalla_Principal.lista_notas_SUP.append(nueva_nota_textview)

        Contenedor_Buti = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        btn_eliminar_notatex = Gtk.Button(label="x")
        btn_eliminar_notatex.connect("clicked", self.Eliminar_Notatex_IndividualmenteBTN, Contenedor_Princi)

        Contenedor_Buti.append(btn_eliminar_notatex)
        contenedor_nota.append(nueva_nota_textview)
        contenedor_nota.append(Contenedor_Buti)

        Contenedor_Princi.append(contenedor_nota)

        self.vbox_CuartPestNotas.append(Contenedor_Princi)


        nueva_nota_textview.grab_focus()

    def Eliminar_Notatex_IndividualmenteBTN(self, widget=None, contenedor_principal=None):
        """
        Elimina una nota textual individual (NotasTex) del contenedor visual y de la 
        lista de control.

        Primero solicita confirmación de guardado pendiente. Luego, identifica el 
        Gtk.TextView asociado al contenedor principal recibido, lo remueve de la lista 
        interna de notas (`lista_notas_SUP`) y elimina su contenedor de la interfaz.

        Finalmente, muestra un mensaje en la barra de estado informando que la nota 
        fue eliminada.

        Args:
            widget (Gtk.Widget, opcional): Botón que activó la acción.
            contenedor_principal (Gtk.Widget): Contenedor principal de la nota a 
            eliminar.
        """
        if not self.Pantalla_Principal.confirmar_guardado_pendiente():
            return

        notatex_a_eliminar = None

        def buscar_textview(widget):
            nonlocal notatex_a_eliminar
            if isinstance(widget, Gtk.TextView):
                notatex_a_eliminar = widget
            elif isinstance(widget, Gtk.Widget):
                child = widget.get_first_child()
                while child:
                    buscar_textview(child)
                    child = child.get_next_sibling()

        buscar_textview(contenedor_principal)

        if notatex_a_eliminar and notatex_a_eliminar in self.Pantalla_Principal.lista_notas_SUP:
            self.Pantalla_Principal.lista_notas_SUP.remove(notatex_a_eliminar)

        self.vbox_CuartPestNotas.remove(contenedor_principal)
        control_label_estado(
            self.Pantalla_Principal.status_label,
            "Nota eliminada.")

    def eliminar_todas_las_notastex(self):
        """
        Elimina todas las notas textuales (NotasTex) de la interfaz y borra su 
        referencia interna.

        Esta función recorre todos los hijos del contenedor principal 
        (`vbox_CuartPestNotas`) y los elimina de la interfaz gráfica. También limpia 
        completamente la lista interna de notas (`lista_notas_SUP`) mantenida en la pantalla principal.

        Útil para reiniciar el área de notas o limpiar el estado general del módulo.
        """
        child = self.vbox_CuartPestNotas.get_first_child()
        while child:
            siguiente = child.get_next_sibling()
            self.vbox_CuartPestNotas.remove(child)
            child = siguiente

        self.Pantalla_Principal.lista_notas_SUP.clear()