import os
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


class Pestana_ArbolArch_Etiquetas(Gtk.Box):
    def __init__(self, Pantalla_Principal):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        #------------------------Iniciadores de Clases (Instancias)-------------
        self.Pantalla_Principal = Pantalla_Principal

        #-----------------------Controladores----------------------


        #-------------------Contenedores-------------------------------
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.box_btn = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        #-----------------Árbol de Archivos de Etiquetas---------------------------
        self.listbox_ArbArch_Etiquetas = Gtk.ListBox()
        


        #----------------------Scroll--------------------------------------
        self.Scroll_Etique = Gtk.ScrolledWindow()
        self.Scroll_Etique.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.Scroll_Etique.set_child(self.vbox)
        self.Scroll_Etique.set_vexpand(True)
        


        #------------------------Botones--------------------------------
        self.btn_Actualizar_ArbArch_Etiquetas = Gtk.Button(label="Actualizar Árbol de Archivos")
        self.btn_Actualizar_ArbArch_Etiquetas.connect("clicked", self.actualizar_arbol_desde_principal)
        


        #-------------------------Posicionamiento de Widgets---------------
        self.vbox.append(self.listbox_ArbArch_Etiquetas)
        self.box_btn.append(self.btn_Actualizar_ArbArch_Etiquetas)

        self.append(self.Scroll_Etique)
        self.append(self.box_btn)
    def crear_ÁrbolArch_Etiquetas(self, diccionario_rutas):

        """
        Construye dinámicamente el árbol visual de archivos y carpetas organizados por 
        etiquetas.

        Esta función crea una estructura expandible de carpetas (expander) y archivos
        (listas internas) dentro de un Gtk.ListBox principal, a partir de un diccionario
        que asocia nombres de etiquetas o categorías con rutas de directorios en el sistema
        de archivos.

        Cada carpeta mostrada puede expandirse para revelar archivos y subdirectorios.
        Los archivos individuales son interactivos y están conectados a una función que
        permite abrirlos cuando son seleccionados.

        Este método se utiliza para visualizar de forma clara y jerárquica los archivos
        etiquetados, permitiendo una navegación rápida desde la interfaz lateral del 
        programa.

        Args:
            diccionario_rutas (dict): Diccionario que asocia nombres de etiquetas o 
                                      categorías (str) con rutas absolutas (str) en 
                                      el sistema de archivos.
        """
        # Limpia el contenido actual
        self.listbox_ArbArch_Etiquetas.remove_all()
        # Ordena las claves alfabéticamente
        for nombre_carpeta in sorted(diccionario_rutas.keys(), key=str.lower):
            ruta = diccionario_rutas[nombre_carpeta]

            # Crea el expander con el nombre de la carpeta
            expander = Gtk.Expander(label=f"📁 {nombre_carpeta}")

            # Lista interna para los archivos
            lista_interna = Gtk.ListBox()
            lista_interna.set_selection_mode(Gtk.SelectionMode.SINGLE)
            lista_interna.connect("row-activated", self._on_archivo_seleccionado, ruta)

            if os.path.isdir(ruta):
                for archivo in sorted(os.listdir(ruta), key=str.lower):
                    ruta_archivo = os.path.join(ruta, archivo)
                    if os.path.isfile(ruta_archivo):
                        fila = Gtk.Label(label=f"📄 {archivo}", xalign=0)
                        lista_interna.append(fila)
                    elif os.path.isdir(ruta_archivo):
                        fila = Gtk.Label(label=f"📁 {archivo}/", xalign=0)
                        lista_interna.append(fila)

            expander.set_child(lista_interna)

            # Inserta en el listbox principal
            fila_expander = Gtk.ListBoxRow()
            fila_expander.set_child(expander)
            self.listbox_ArbArch_Etiquetas.append(fila_expander)

    def actualizar_arbol_desde_principal(self, widget=None, diccionario_rutas_get=None):
        """
        Actualiza el árbol de etiquetas usando el diccionario "guardado" de Gestion_Dict_EDITOR.
        Esta función es llamada desde la pantalla principal y necesita como argumento
        el diccionario a usar. 

        Nota: si se llama desde otro lugar, se debe aclarar la variable. De lo contrario
        se usará None y no se actualizará el árbol. Ejemplo:
        self.actualizar_arbol_desde_principal(diccionario_rutas_get=diccionario) Correcto
        self.actualizar_arbol_desde_principal(diccionario) Incorrecto (se usará None)
        """
        if diccionario_rutas_get is not None:
            self.crear_ÁrbolArch_Etiquetas(diccionario_rutas_get)

    def _on_archivo_seleccionado(self, listbox, row, ruta_carpeta):
        """
        Abre un archivo seleccionado desde el árbol lateral de etiquetas.

        Esta función se conecta al evento `row-activated` del Gtk.ListBox que contiene 
        los archivos. Extrae el nombre del archivo seleccionado 
        (eliminando íconos decorativos) y construye la ruta completa usando el directorio asociado.

        Posteriormente, delega la apertura del archivo al método correspondiente de la
        pantalla principal del editor (`abrir_archivo_ArbolArch`).

        Args:
            listbox (Gtk.ListBox): El contenedor de filas que generó el evento.
            row (Gtk.ListBoxRow): La fila activada que contiene el nombre del archivo.
            ruta_carpeta (str): Ruta base del directorio que contiene los archivos mostrados en esa lista.
        """
        nombre_archivo = row.get_child().get_text()
        # Quitar íconos y espacios
        if nombre_archivo.startswith("📄 ") or nombre_archivo.startswith("📁 "):
            nombre_archivo = nombre_archivo[2:].strip()
        if nombre_archivo.endswith("/"):
            nombre_archivo = nombre_archivo[:-1]

        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)

        self.Pantalla_Principal.abrir_archivo_ArbolArch(ruta_completa)
