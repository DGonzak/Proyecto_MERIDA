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
from gi.repository import Gtk, GObject, Gio

import os

from Lib_Extra.Funciones_extras import mostrar_vent_IEO


from BDs_Functions.BD_TAGS_Funct import BD_TAGS_Functions
from BDs_Functions.Models_BD import BD_Tags_General


class TagRecord(GObject.Object):
    id = GObject.Property(type=int)
    nombre = GObject.Property(type=str)
    ruta = GObject.Property(type=str)

    def __init__(self, id=0, nombre="", ruta=""):
        super().__init__()
        self.id = id
        self.nombre = nombre
        self.ruta = ruta

class pantalla_listas(Gtk.Window):
    def __init__(self):
        super().__init__(title="Listas de la Base de Datos")
        self.set_default_size(600, 400)

        self.BD_TAGS_Functions = BD_TAGS_Functions()

        self.modelo = Gio.ListStore(item_type=TagRecord)

        self.seleccion = Gtk.SingleSelection(model=self.modelo)
        self.columnview = Gtk.ColumnView(model=self.seleccion)
        self.crear_columnas()

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.columnview)

        btn_crear = Gtk.Button(label="Crear")
        btn_crear.connect("clicked", self.registrar_nuevas_direcciones)

        btn_eliminar = Gtk.Button(label="Eliminar")
        btn_eliminar.connect("clicked", self.eliminar_entradas)

        botones = Gtk.Box(spacing=6)
        botones.append(btn_crear)
        botones.append(btn_eliminar)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.append(scrolled)
        vbox.append(botones)
        self.set_child(vbox)

        self.cargar_datos()


    def crear_columnas(self):
        columnas = [("ID", "id"), ("Etiqueta", "nombre"), ("Dirección de Carpeta", "ruta")]

        for titulo, propiedad in columnas:
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup_label)
            factory.connect("bind", self.bind_label, propiedad)
            columna = Gtk.ColumnViewColumn(title=titulo, factory=factory)
            self.columnview.append_column(columna)



    def bind_label(self):
        """
        Crea y configura las columnas visibles de un `Gtk.ColumnView`, en este caso, de
        la tabla que se usará para las listas.

        Las columnas se definen con títulos estáticos y se vinculan con 
        propiedades específicas del modelo de datos (`id`, `nombre`, `ruta`).
        Para cada columna se utiliza una `SignalListItemFactory` que define
        cómo renderizar los valores.

        Este método debe llamarse una vez para inicializar las columnas del
        `Gtk.ColumnView` con el formato correcto.

        Esta función es llamada por: __init__
        """
        columnas = [("ID", "id"), ("Etiqueta", "nombre"), ("Dirección de Carpeta", "ruta")]
        for titulo, propiedad in columnas:
            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup_label)
            factory.connect("bind", self.bind_label, propiedad)
            columna = Gtk.ColumnViewColumn(title=titulo, factory=factory)
            self.columnview.append_column(columna)

    def setup_label(self, factory, list_item):
        """
        Configura un `Gtk.Label` como hijo del `Gtk.ListItem`.

        Este método se usa como callback del evento `setup` de una `SignalListItemFactory`.

        Parameters
        ----------
        factory : Gtk.SignalListItemFactory
            La fábrica que generó el evento.
        list_item : Gtk.ListItem
            El item visual de la lista que necesita ser configurado.

        Esta función es llamada por: crear_columnas
        """
        label = Gtk.Label(xalign=0)
        list_item.set_child(label)

    def bind_label(self, factory, list_item, propiedad):
        """
        Asocia un valor del modelo de datos a un `Gtk.Label` del `Gtk.ListItem`.

        Este método se usa como callback del evento `bind` de una `SignalListItemFactory`.
        Se obtiene el valor desde un atributo específico del objeto (`TagRecord`) 
        y se muestra como texto en la etiqueta.

        Parameters
        ----------
        factory : Gtk.SignalListItemFactory
            La fábrica que generó el evento.
        list_item : Gtk.ListItem
            El item visual de la lista a ser enlazado.
        propiedad : str
            El nombre del atributo del objeto que se mostrará en la etiqueta.


        Esta función es llamada por: crear_columnas
        """
        record = list_item.get_item()
        label = list_item.get_child()
        valor = getattr(record, propiedad)
        label.set_text(str(valor))

    def cargar_datos(self):
        """
        Carga y muestra los registros actuales en el modelo del `ColumnView`, es decir,
        la tabla de listas.

        Este método limpia el modelo actual y luego carga los registros
        más recientes desde la base de datos `BD_TAGS_Functions`, invirtiendo
        el orden de los datos para que los últimos aparezcan primero.

        Los datos cargados son instancias de `TagRecord`.

        Esta función es llamada por: eliminar_entradas; on_dialog_response; __init__
        """
        while self.modelo.get_n_items() > 0:
            self.modelo.remove(0)

        datos = self.BD_TAGS_Functions.obtener_registros()
        datos.reverse()
        for id_, nombre, ruta in datos:
            record = TagRecord(id=id_, nombre=nombre, ruta=ruta)
            self.modelo.append(record)

    def registrar_nuevas_direcciones(self, widget):
        """
        Despliega un diálogo para registrar una nueva etiqueta y su ruta de carpeta.

        El usuario debe ingresar una etiqueta y la ruta correspondiente. También puede
        usar un botón para seleccionar la carpeta desde un diálogo de archivos.

        El resultado se valida y, si es correcto, se guarda en la base de datos tras 
        una verificación de existencia del directorio.
        
        Parameters
        ----------
        widget : Gtk.Widget
            El botón u objeto que activó esta función.

        Esta función es llamada por: __init__
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Añadir nueva dirección de carpeta"
        )

        content_area = dialog.get_content_area()
        
        label_Ingr1 = Gtk.Label(label="Ingrese el nombre de la etiqueta y la ruta de la carpeta")
        label_Ingr1.set_wrap(True)

        self.entry_etiqueta = Gtk.Entry(placeholder_text="Etiqueta")
        self.entry_ruta = Gtk.Entry(placeholder_text="Ruta de carpeta")

        self.boton_seleccionar_archivo = Gtk.Button.new_with_label("Seleccionar carpeta")
        self.boton_seleccionar_archivo.connect("clicked", self.dialog_select_Carpeta)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_vexpand(True)

        box.append(label_Ingr1)
        box.append(self.entry_etiqueta)
        box.append(self.entry_ruta)
        box.append(self.boton_seleccionar_archivo)

        content_area.append(box)

        dialog.connect("response", self.on_dialog_response, self.entry_etiqueta, self.entry_ruta)
        dialog.present()

    def on_dialog_response(self, dialog, response, entry_etiqueta, entry_ruta):
        """
        Procesa la respuesta del diálogo de registro de etiquetas.

        Si el usuario acepta y proporciona datos válidos, se verifica si la
        etiqueta es única y si la ruta es válida. Luego se registra en la
        base de datos o se informa al usuario sobre los errores encontrados.

        Parameters
        ----------
        dialog : Gtk.MessageDialog
            El diálogo que produjo la respuesta.
        response : Gtk.ResponseType
            Tipo de respuesta del usuario (e.g., OK, CANCEL).
        entry_etiqueta : Gtk.Entry
            Entrada de texto para el nombre de la etiqueta.
        entry_ruta : Gtk.Entry
            Entrada de texto para la ruta de la carpeta.


        Esta función es llamada por: registrar_nuevas_direcciones
        """
        
        if response == Gtk.ResponseType.OK:
            
            etiqueta = entry_etiqueta.get_text().strip()
            ruta = entry_ruta.get_text().strip()
            
            if etiqueta and ruta:

                if self.BD_TAGS_Functions.validar_unico(etiqueta) is None:

                    #Uso de callbacks
                    def continuar_registro():
                        nuevo = BD_Tags_General()
                        nuevo.Nombre_etiqueta = etiqueta
                        nuevo.Ruta_carpeta = ruta
                        
                        self.BD_TAGS_Functions.registrar_nuevas_listas(nuevo)
                        self.cargar_datos()

                    def cancelar_registro():

                        mostrar_vent_IEO(
                            self,
                            "Ruta no válida",
                            "No se registró la etiqueta porque la carpeta no existe.",
                            Gtk.MessageType.INFO,
                            1,
                            "Aceptar",
                            None,
                            None)
                    self.verificar_o_crear_ruta(ruta, continuar_registro, cancelar_registro)

                else:
                    mostrar_vent_IEO(
                        self,
                        "Error: Etiqueta duplicada",
                        "El nombre de la etiqueta ya está registrado.",
                        Gtk.MessageType.ERROR,
                        1,
                        "Aceptar",
                        None,
                        None)
                        
            else:
                mostrar_vent_IEO(
                    self,
                    "Campos vacíos",
                    "Uno o más campos están vacíos.",
                    Gtk.MessageType.ERROR,
                    1,
                    "Aceptar",
                    None,
                    None)

        dialog.destroy()

    def eliminar_entradas(self, widget):
        """
        Elimina la entrada seleccionada del modelo y la base de datos.

        Si hay un elemento seleccionado actualmente, se elimina su registro
        de la base de datos utilizando su ID y luego se actualiza la vista.

        Parameters
        ----------
        widget : Gtk.Widget
            El botón u objeto que activó esta función.

        Esta función en llamada por: __init__
        """
        record = self.seleccion.get_selected_item()
        if record:
            self.BD_TAGS_Functions.eliminar_registros(record.id)
            self.cargar_datos()


    def verificar_o_crear_ruta(self, ruta_get: str, callback_si_existe: callable, callback_cancelado: callable):
        """
        Verifica si la ruta proporcionada existe en el sistema de archivos. 
        Si no existe, solicita al usuario confirmación para crearla. 
        Ejecuta una de las funciones de callback según el resultado.

        Parámetros:
            ruta_get (str): Ruta a verificar.
            callback_si_existe (callable): Función que se ejecuta si la ruta existe o 
            se crea exitosamente.
            callback_cancelado (callable): Función que se ejecuta si la ruta no existe 
            y el usuario decide no crearla.

        Comportamiento:
            - Si la ruta ya existe, se llama inmediatamente a `callback_si_existe`.
            - Si no existe, se presenta un diálogo para preguntar si se desea crear la 
                carpeta.
            - Si el usuario acepta, se intenta crear la carpeta:
                - Si se crea con éxito, se llama a `callback_si_existe`.
                - Si ocurre un error, se muestra un mensaje de error y se llama a `callback_cancelado`.
            - Si el usuario cancela, se llama directamente a `callback_cancelado`.
        
        Esta función es llamada por: on_dialog_response

        """
        if os.path.isdir(ruta_get):
            callback_si_existe()
            return  # La ruta ya existe

        # Crear un diálogo modal de confirmación
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text="Error de Creación",
        )

        content_area = dialog.get_content_area()

        label1 = Gtk.Label(label="La ruta ingresada no existe.")
        label1.set_wrap(True)

        label2 = Gtk.Label(label="¿Desea crear la carpeta de la ruta?\n\n" + ruta_get)
        label2.set_wrap(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_vexpand(True)
        vbox.set_hexpand(True)

        vbox.append(label1)
        vbox.append(label2)

        content_area.append(vbox)


        dialog.add_button("Sí, crear ruta", Gtk.ResponseType.OK)
        dialog.add_button("No, no crear ruta", Gtk.ResponseType.CANCEL)

        # Almacenar la ruta y los callbacks como atributos del diálogo
        dialog.ruta_get = ruta_get
        dialog.callback_si_existe = callback_si_existe
        dialog.callback_cancelado = callback_cancelado

        dialog.connect("response", self.on_dialog_response_YN)
        dialog.present()


    def on_dialog_response_YN(self, dialog, response):
        """
        Maneja la respuesta del usuario al diálogo que pregunta si desea crear una 
        ruta inexistente.

        Parámetros:
            dialog (Gtk.MessageDialog): El diálogo que emitió la respuesta.
            response (Gtk.ResponseType): Código de respuesta del usuario (OK o CANCEL).

        Comportamiento:
            - Si el usuario acepta (OK), intenta crear la carpeta con `os.makedirs`.
                - Si tiene éxito, ejecuta el callback `dialog.callback_si_existe`.
                - Si falla, muestra un mensaje de error y ejecuta `dialog.callback_cancelado`.
            - Si el usuario cancela, ejecuta directamente `dialog.callback_cancelado`.
            - En ambos casos, destruye el diálogo tras procesar la respuesta.
        
        Esta función es llamada por: verificar_o_crear_ruta

        """

        ruta_a_usar = dialog.ruta_get

        if response == Gtk.ResponseType.OK:
            try:
                os.makedirs(ruta_a_usar, exist_ok=True)
                dialog.callback_si_existe()

            except Exception as e:
                # Mostrar error si no se pudo crear la carpeta
                mostrar_vent_IEO(
                    dialog.get_transient_for(),
                    "Error de Creación",
                    f"No se pudo crear la ruta acordada.\nDetalles:{e}",
                    Gtk.MessageType.ERROR,
                    1,
                    "Aceptar",
                    None,
                    None
                )
                dialog.callback_cancelado()
                
        else:
            dialog.callback_cancelado()

        dialog.destroy()

    def dialog_select_Carpeta(self, widget=None):
        """
        Abre un diálogo Gtk.FileChooserDialog que permite al usuario seleccionar 
        una carpeta del sistema de archivos.

        Parámetros:
            widget (Gtk.Widget, opcional): El widget que disparó la acción 
            (puede ser None).

        Comportamiento:
            - Muestra un diálogo modal con botones "Seleccionar" y "Cancelar".
            - El resultado del diálogo es manejado por `self.on_Carpeta_Escogida`.
        
        Esta función es llamada por: registrar_nuevas_direcciones

        """
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar una carpeta",
            transient_for=self,
            modal=True,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            )

        dialog.add_button("Seleccionar", Gtk.ResponseType.OK)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)

        dialog.connect("response", self.on_Carpeta_Escogida)
        dialog.present()

    def on_Carpeta_Escogida(self, dialog, response):

        """
        Maneja la respuesta del usuario al seleccionar una carpeta en el diálogo de 
        selección.

        Parámetros:
            dialog (Gtk.FileChooserDialog): El diálogo que emitió la respuesta.
            response (Gtk.ResponseType): Código de respuesta del usuario (OK o CANCEL).

        Comportamiento:
            - Si el usuario presiona "Seleccionar" (OK) y elige una carpeta válida,
              actualiza el campo de entrada `self.entry_ruta` con la ruta seleccionada.
            - Cierra el diálogo en cualquier caso.
        """

        if response == Gtk.ResponseType.OK:
            file_get = dialog.get_file()

            if file_get:
                self.entry_ruta.set_text(file_get.get_path())
        dialog.destroy()

