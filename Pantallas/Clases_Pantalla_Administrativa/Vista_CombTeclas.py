import gi
import re
import json



gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio

from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions
from BDs_Functions.Models_BD import BD_Comb_Teclas

from Lib_Extra.Funciones_extras import mostrar_vent_IEO

# Modelo de datos moderno
class CombinacionTecla(GObject.Object):
    id = GObject.Property(type=str)
    nombre = GObject.Property(type=str)
    atajo = GObject.Property(type=str)
    descripcion = GObject.Property(type=str)

    def __init__(self, id="", nombre="", atajo="", descripcion=""):
        super().__init__()
        self.id = id
        self.nombre = nombre
        self.atajo = atajo
        self.descripcion = descripcion


class Vista_Combinacion_Teclas(Gtk.Box):
    def __init__(self, Pantalla_principal_SUP):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_vexpand(True)

        #-----------------Iniciadores de clase (instancias)---------------
        self.BD_ComTecl_Functions = BD_ComTecl_Functions()

        self.Pantalla_principal = Pantalla_principal_SUP

        # Modelo con ListStore moderno
        self.modelo = Gio.ListStore(item_type=CombinacionTecla)

        self.seleccion = Gtk.SingleSelection(model=self.modelo)
        self.columnview = Gtk.ColumnView(model=self.seleccion)
        self.crear_columnas()

        self.seleccion.connect("notify::selected-item", self.Columnview_obt_selección)

        scroll_comteclas = Gtk.ScrolledWindow()
        scroll_comteclas.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_comteclas.set_child(self.columnview)
        scroll_comteclas.set_vexpand(True)


        boton_box = Gtk.Box(spacing=6)
        self.btn_modificar = Gtk.Button(label="Modificar")
        self.btn_modificar.set_sensitive(False)
        self.btn_modificar.connect("clicked", self.modificar_CombTeclas)
        
        boton_box.append(self.btn_modificar)

        self.append(scroll_comteclas)
        self.append(boton_box)

        self.cargar_datos_comteclas()

    def Columnview_obt_selección(self, seleccion, _):
        """
        Habilita o deshabilita el botón de modificación según la selección actual en 
        el ColumnView.

        Parámetros:
            seleccion (Gtk.SingleSelection): Objeto de selección asociado al ColumnView.
            _ : Parámetro ignorado, usado para conexión de señal.

        Comportamiento:
            - Si hay un elemento seleccionado, habilita el botón de modificación (`btn_modificar`).
            - Si no hay selección, el botón se desactiva.
        
        Esta función es llamada por: __init__
        """
        self.btn_modificar.set_sensitive(bool(seleccion.get_selected_item()))

    def crear_columnas(self):
        """
        Crea y añade columnas al Gtk.ColumnView para mostrar datos de combinaciones 
        de teclas.

        Columnas creadas:
            - ID: Identificador único de la entrada.
            - Nombre: Nombre descriptivo de la acción.
            - Combinación de Teclas: Atajo asignado.
            - Descripción de Acción: Descripción explicativa de la acción.

        Cada columna se vincula a una propiedad del modelo y utiliza un 
        Gtk.SignalListItemFactory con funciones `setup_label` y `bind_label` para 
        renderizar los valores.
        
        Esta función es llamada por: __init__ 
        """
        columnas = [
            ("ID", "id"),
            ("Nombre", "nombre"),
            ("Combinación de Teclas", "atajo"),
            ("Descripción de Acción", "descripcion"),
        ]
        for titulo, propiedad in columnas:
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup_label)
            factory.connect("bind", self.bind_label, propiedad)
            columna = Gtk.ColumnViewColumn(title=titulo, factory=factory)
            self.columnview.append_column(columna)

    def setup_label(self, factory, list_item):
        """
        Configura el widget hijo de cada celda de la columna como un Gtk.Label.

        Parámetros:
            factory (Gtk.SignalListItemFactory): Fábrica de ítems del ColumnView.
            list_item (Gtk.ListItem): Elemento de la lista al que se le asigna un Gtk.Label como hijo.
        
        Esta función es llamada por: crear_columnas
        """
        label = Gtk.Label(xalign=0)
        list_item.set_child(label)

    def bind_label(self, factory, list_item, propiedad):
        """
        Enlaza el texto del Gtk.Label con la propiedad correspondiente del modelo.

        Parámetros:
            factory (Gtk.SignalListItemFactory): Fábrica de ítems.
            list_item (Gtk.ListItem): Ítem de la lista que contiene el Gtk.Label.
            propiedad (str): Nombre de la propiedad del objeto que se mostrará en la celda.
        
        Esta función es llamada por: crear_columnas
        """
        item = list_item.get_item()
        label = list_item.get_child()
        valor = getattr(item, propiedad)
        label.set_text(str(valor))

    def cargar_datos_comteclas(self):
        """
        Carga todos los registros de combinaciones de teclas desde la base de datos y 
        los muestra en el modelo del ColumnView.

        Comportamiento:
            - Limpia el modelo actual (`self.modelo`).
            - Obtiene los registros usando `obtener_registros(modo="lista")`.
            - Agrega cada combinación de teclas al modelo usando la clase `CombinacionTecla`.
        
        Esta función es llamada por: on_vent_mod_Dialog_response; __init__
        """
        datos = self.BD_ComTecl_Functions.obtener_registros(modo="lista")
        while self.modelo.get_n_items() > 0:
            self.modelo.remove(0)

        for id_, nombre, atajo, descripcion in datos:
            self.modelo.append(CombinacionTecla(id=id_, nombre=nombre, atajo=atajo, descripcion=descripcion))

    def obtener_ID_Busc(self):
        """
        Obtiene el ID de la combinación actualmente seleccionada en el ColumnView.

        Retorna:
            int | None: El ID del ítem seleccionado, o None si no hay selección.
        
        Esta función es llamada por: modificar_CombTeclas
        """
        item = self.seleccion.get_selected_item()
        if item:
            return item.id
        return None



    def modificar_CombTeclas(self, widget=None, *args):
        """
        Muestra un diálogo que permite modificar el atajo de una combinación de teclas 
        seleccionada.

        Comportamiento:
            - Recupera el ID de la entrada seleccionada.
            - Obtiene los datos actuales del atajo desde la base de datos.
            - Presenta un diálogo con la información actual y una entrada para modificar 
            el atajo.
            - Conecta la respuesta del usuario a `on_vent_mod_Dialog_response`.

        Parámetros:
            widget (Gtk.Widget, opcional): El widget que disparó la acción.
            *args: Argumentos adicionales ignorados.
        
        Esta función es llamada por: __init__
        """

        id_get = self.obtener_ID_Busc()

        self.datos_dicc_get = self.BD_ComTecl_Functions.obtener_registros_ID(id_get)

        vent_mod_Dialog = Gtk.MessageDialog(
            transient_for=self.get_root(), #para conectar a la ventana, no al box
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Modificar una combinación de teclas"
        )
        
        content_are = vent_mod_Dialog.get_content_area()

        label_tit_1 = Gtk.Label(label="Modifique la combinación de teclas y confirme los cambios")
        label_tit_1.set_wrap(True)

        
        # Etiqueta: Nombre de la combinación
        Label_Nombre = Gtk.Label()
        Label_Nombre.set_markup(f"<b>Nombre:</b> {self.datos_dicc_get['nombre']}")
        Label_Nombre.set_xalign(0)

        # Entrada para el atajo de teclado
        Entry_Combtec = Gtk.Entry()
        Entry_Combtec.set_placeholder_text("Combinación de Teclas")
        Entry_Combtec.set_text(self.datos_dicc_get['atajo'])

        # Etiqueta: Descripción
        Label_Descrip = Gtk.Label()
        Label_Descrip.set_markup(f"<b>Descripción:</b> {self.datos_dicc_get['descripción']}")
        Label_Descrip.set_xalign(0)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_vexpand(True)


        # Añadir los widgets a la caja de contenido
        vbox.append(label_tit_1)
        vbox.append(Label_Nombre)
        vbox.append(Entry_Combtec)
        vbox.append(Label_Descrip)

        content_are.append(vbox)


        vent_mod_Dialog.connect("response", self.on_vent_mod_Dialog_response,Entry_Combtec, id_get)
        vent_mod_Dialog.present()



    def on_vent_mod_Dialog_response(self, dialog, respuesta_get, Entry_Combtec_get, id_get_get):
        """
        Procesa la respuesta del usuario al diálogo de modificación del atajo.

        Parámetros:
            dialog (Gtk.MessageDialog): Diálogo que fue mostrado.
            respuesta_get (Gtk.ResponseType): Respuesta del usuario (OK o CANCEL).
            Entry_Combtec_get (Gtk.Entry): Campo de entrada donde el usuario escribió el nuevo atajo.
            id_get_get (int): ID del registro que se desea modificar.

        Comportamiento:
            - Si el usuario acepta (OK):
                - Verifica que el nuevo atajo no esté vacío ni sea igual al anterior.
                - Valida el formato del atajo usando `validar_formato_atajo`.
                - Verifica que el atajo no esté duplicado.
                - Si es válido, modifica el registro en la base de datos y recarga los datos.
                - Vuelve a registrar los atajos globales desde la ventana principal.
                - Si ocurre algún error, muestra un mensaje adecuado.
            - Finalmente, destruye el diálogo.
        
        Esta función es llamada por: modificar_CombTeclas
        """
        Ejemplo_comb1 = "<Control>A"
        Ejemplo_comb2 = "<Shift><Alt>S"
        Ejemplo_comb3 = "<Control><Alt>Delete"
        Ejemplo_comb4 = "<super><meta>Tab"
        Ejemplo_comb5 = "<ctrl><shift><alt>F12"


        if respuesta_get == Gtk.ResponseType.OK:

            try:
                nuevo_atajo = Entry_Combtec_get.get_text().strip()
                atajo_actual = self.datos_dicc_get['atajo']

                if nuevo_atajo == atajo_actual:
                    dialog.destroy()
                    return

                if not nuevo_atajo:
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Error de Guardado",
                        "Es posible que haya espacios no permitidos o campos vacios.\nPor favor, vuelva a intentarlo.",
                        Gtk.MessageType.ERROR,
                        1,
                        None,
                        None)
                    dialog.destroy()
                    return

                if not self.validar_formato_atajo(nuevo_atajo):
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Error de Formato",
                        f"El atajo ingresdo no sigue el formato establecido.\nEjemplos de formato (según GTK):\n{Ejemplo_comb1}\n{Ejemplo_comb2}\n{Ejemplo_comb3}\n{Ejemplo_comb4}\n{Ejemplo_comb5}",
                        Gtk.MessageType.ERROR,
                        1,
                        None,
                        None)
                    dialog.destroy()
                    return

                Verificación_Único = self.BD_ComTecl_Functions.validar_unica_ComTec(nuevo_atajo)

                if Verificación_Único is None:

                    self.BD_ComTecl_Functions.modificar_registros(
                        ID_GET_MOD=id_get_get,
                        nuevo_atajo_get=nuevo_atajo)

                    self.cargar_datos_comteclas()

                    """La siguiente linea funciona gracias a pasar la llave de la
                    pantalla principal. Esta llave lleva siendo transportada desde
                    el archivo de Pantalla Administrativa. Esta representada por el 
                    nombre Pantalla_principal_SUP en señal de que, en realidad,
                    la llave proviene de una pantalla mucho más elevada que la que
                    donde se encuentra la instancia principal. Es decir, más arriba 
                    que la de Vista_CombTeclas. """
                    self.Pantalla_principal.registrar_atajos_globales()

                else:
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Error de Guardado",
                        "El atajo ingresado ya está registrado.\nPor favor, vuelva a intentarlo.",
                        Gtk.MessageType.ERROR,
                        1,
                        None,
                        None)
            except Exception as e:
                mostrar_vent_IEO(
                    self.get_root(),
                    "Error desconocido",
                    f"Ha ocurrido un error inesperado.\nDetalles:{e}",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

        dialog.destroy()


    def validar_formato_atajo(self, atajo: str) -> bool:
        """
        Valida que un atajo de teclado cumpla con el formato requerido por GTK.

        Este método comprueba que una cadena que representa una combinación de teclas
        siga el patrón general de uno o más modificadores encerrados entre signos 
        angulares (por ejemplo, `<Ctrl><Alt>`) seguidos de una tecla final válida.

        La validación incluye:
        - Sintaxis general: el atajo debe coincidir con la expresión `<Mod><Mod>...TeclaFinal`.
        - Validación de modificadores: todos los modificadores deben estar en la lista 
          de modificadores aceptados (`Ctrl`, `Alt`, `Shift`, etc.).
        - Validación de la tecla final: debe ser una letra, un número, o teclas especiales 
          como `F1–F12`, `Escape`, `Tab`, etc.

        Este método se utiliza antes de guardar o modificar combinaciones de teclas
        en el sistema para evitar errores o entradas inválidas que no puedan ser registradas
        por GTK.

        Args:
            atajo (str): La combinación de teclas a validar, en formato GTK (ej. "<Ctrl><Alt>S").

        Returns:
            bool: True si el formato es válido, False si no lo es.

        Esta función es llamada por: on_vent_mod_Dialog_response
        """

        # Lista de modificadores válidos (usados para la validación)
        modificadores_validos = ["Ctrl", "Control", "Alt", "Shift", "Super", "Meta", "Hyper"]

        # Verifica que el atajo siga el patrón general: uno o más <Mod> seguido de UNA tecla
        match = re.fullmatch(r'(<\w+>)+(\w+)$', atajo)
        if not match:
            return False

        # Extraer modificadores que tengan <Mod>
        modificadores = re.findall(r'<(\w+)>', atajo)

        # Verificar que todos los modificadores sean válidos (con la lista de modificadores validos)
        for mod in modificadores:
            if mod.capitalize() not in modificadores_validos:#con capitaliza se aceptan: SHIFT o Shift
                return False

        # Extraer la tecla final
        tecla_final = re.sub(r'(<\w+>)', '', atajo)

        # Validar que la tecla final sea solo una letra, dígito o tecla especial válida
        # Por ahora, permitimos una letra (a-zA-Z), una cifra (0-9), o teclas como F1-F12, Escape, Tab, etc.
        tecla_valida = re.fullmatch(r'[A-Za-z0-9]|F[1-9]|F1[0-2]|Tab|Escape|Return|Space|BackSpace', tecla_final)
        if not tecla_valida:
            return False

        return True