import gi
import re
import json
import os
import sys
from datetime import datetime
from platformdirs import user_documents_path


gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject, Gio, Gdk, GLib

from BDs_Functions.BD_Informadora_Funct import BD_Informadora_Functions
from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions
from BDs_Functions.BD_TAGS_Funct import BD_TAGS_Functions
from BDs_Functions.BD_RecentArch_Funct import BD_Recient_Arch_Functions
from BDs_Functions.Models_BD import BDInformadora
from BDs_Functions.Constructor_BDs import crear_BDs_Constructor
from BDs_Functions.BD_Utilidades_Generales import BD_UtilidadesGenerales


from Lib_Extra.Funciones_extras import mostrar_vent_IEO, guardar_archivo_tmp, leer_archivo_tmp, borrar_archivo_tmp, aplicar_estilos_css,obtener_archivo_mas_reciente_ResplArch, leer_archivo_recurrente
from Lib_Extra.Rutas_Gestion import get_data_dir,get_cache_dir,get_recursos_dir

class BD_Informadora_Tab(GObject.Object):
    id = GObject.Property(type=str)
    nombre = GObject.Property(type=str)
    descripcion = GObject.Property(type=str)
    estado = GObject.Property(type=str)

    def __init__(self, id="", nombre="", descripcion="",ultima_actualizacion="", estado=""):
        super().__init__()
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.ultima_actualizacion = ultima_actualizacion
        self.estado = estado


class Vista_Base_De_Datos(Gtk.Box):
    def __init__ (self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.set_vexpand(True)

        #------------Iniciadores de clases (instancias)---------------------
        self.BD_Informadora_Functions = BD_Informadora_Functions()
        self.BD_ComTecl_Functions = BD_ComTecl_Functions()
        self.BD_TAGS_Functions = BD_TAGS_Functions()
        self.BD_Recient_Arch_Functions = BD_Recient_Arch_Functions()
        self.BD_Utilidades_Generales = BD_UtilidadesGenerales()

        #--------------------Iniciadores de funciones-----------------------
        ruta_estilos = os.path.join(get_recursos_dir(), "Estilo_CSS", "estilo_base.css")
        aplicar_estilos_css(ruta_css=ruta_estilos)

        #-------------------------Variables SUP-----------------
        self.DATOS_COMPLETOS_BDINFORM_SUP = self.BD_Informadora_Functions.obtener_registros(modo="diccionario")

        self.Señal_para_Mostrar_Pantalla_Recuper = False

        self.Datos_Filtro_Get_SUP = []


        #--------------------------LISTAS----------------------
        self.Permisos_BD_Lista = [
        "lectura",
        "lectura/escritura",
        "bloqueada",
        "solo interna"]

        self.Origen_BD_Lista = [
        "sistema",
        "usuario",
        "externa",
        "extensión"]



        #-------------Tabla-----------------------------
                # Modelo con ListStore moderno
        self.modelo = Gio.ListStore(item_type=BD_Informadora_Tab)

        self.seleccion = Gtk.SingleSelection(model=self.modelo)

        self.columnview = Gtk.ColumnView(model=self.seleccion)

        gesto_click = Gtk.GestureClick.new()
        gesto_click.set_button(0) #0 es cualquier botón, creo.
        gesto_click.connect("released", self.mostrar_vent_CompletaBD)

        self.columnview.add_controller(gesto_click)

        self.crear_columnas()

        scroll_Inform = Gtk.ScrolledWindow()
        scroll_Inform.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_Inform.set_child(self.columnview)
        scroll_Inform.set_vexpand(True)
        scroll_Inform.set_hexpand(True)


        #Botones de Ajuste o Acciones
        boton_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        
        self.btn_registrarBD = Gtk.Button(label="Registrar una \nnueva base de datos")
        self.btn_registrarBD.connect("clicked", self.mostrar_vent_RegistBD)

        self.btn_reconstruir = Gtk.Button(label="Operaciones Grupales \nde bases de datos.")
        self.btn_reconstruir.set_tooltip_text("Permite aplicar funcionalidades a grupos de bases de datos filtrados según su ORIGEN")
        self.btn_reconstruir.connect("clicked", self.Mostrar_Vent_OperGrup)
        
        self.btn_actualizarV = Gtk.Button(label="Actualizar vista \nde bases de datos")
        self.btn_actualizarV.connect("clicked", self.cargar_datos_seleccionados)

        self.btn_asegurar_entPreder = Gtk.Button(label="Insertar BDs \npredeterminadas")
        self.btn_asegurar_entPreder.connect("clicked", self.minifunción_asegur_preder)

        self.btn_restaur_respald = Gtk.Button(label="Restaurar bases de datos\ndesde respaldos")
        self.btn_restaur_respald.connect("clicked", self.restaurar_bds_vent_SinInformadora)


        boton_box.append(self.btn_registrarBD)
        boton_box.append(self.btn_reconstruir)
        boton_box.append(self.btn_actualizarV)
        boton_box.append(self.btn_asegurar_entPreder)
        boton_box.append(self.btn_restaur_respald)


        self.append(scroll_Inform)
        self.append(boton_box)

        self.cargar_datos_seleccionados()


    def minifunción_asegur_preder(self, widget=None):
        """
        Asegura que las bases de datos predeterminadas estén registradas
        en la base de datos de información y actualiza sus propiedades.

        - Llama a `asegurar_bds_registro_preder()` para garantizar la existencia
          de registros predeterminados.
        - Verifica la existencia física de las bases de datos definidas en
          `rutas_relativas` y actualiza su estado y ubicación si existen.
        - Inserta la ubicación de respaldo para las bases de datos filtradas por origen "Sistema".
        - Finalmente, actualiza la vista cargando los datos seleccionados.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
        """
        self.BD_Informadora_Functions.asegurar_bds_registro_preder()

        ruta_abs_bds_N = os.path.join(get_data_dir(), "BDs")

        #Insertar origen y estado
        nombres_bds = [
            "BD_ComTecl.sqlite",
            "BD_RecentArch.sqlite",
            "BD_TAGS.sqlite",
            "BD_Informadora.sqlite"
        ]

        for nombre_bd in nombres_bds:
            ruta_absoluta = os.path.join(ruta_abs_bds_N, nombre_bd)
            existe = self.verificar_BD_Existencia(ruta_absoluta)


            nombre_archivo = os.path.basename(ruta_absoluta)
            nombre_sin_ext, _ = os.path.splitext(nombre_archivo)


            if existe:
                self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_sin_ext, "estado", True)
                self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_sin_ext, "ubicacion", ruta_absoluta)


        #Para insertar las rutas de respaldo
        if not self.Datos_Filtro_Get_SUP:
            self.Datos_Filtro_Get_SUP = self.BD_Informadora_Functions.obtener_registros_origen("Sistema")
        
        for bd in self.Datos_Filtro_Get_SUP:
            id_bd_get = bd.get("id", "Error: Sin id")

            self.insertar_ubicacion_respaldo(id_bd_get)


        self.cargar_datos_seleccionados()

    def crear_columnas(self):
        """
        Crea y añade columnas al Gtk.ColumnView para mostrar datos seleccionados de las 
        bases de datos.

        Columnas creadas:
            - ID: Identificador único de la entrada.
            - Nombre: Nombre propio de la base de datos.
            - Descripción: Descripción explicativa de la utilidad de la base de datos.
            - Ultima actualización registrada: Fecha de la ultima actualización hecha por el 
                programa o por el propio usuario.
            - Estado: Estado de la base de datos, extraido de su última revision(actualización)

        Cada columna se vincula a una propiedad del modelo y utiliza un 
        Gtk.SignalListItemFactory con funciones `setup_label` y `bind_label` para 
        renderizar los valores.
        """
        columnas = [
            ("ID", "id"),
            ("Nombre", "nombre"),
            ("Descripción", "descripcion"),
            ("Ultima actualización registrada", "ultima_actualizacion"),
            ("Estado", "estado"),
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

    def cargar_datos_seleccionados(self, widget=None):
        """
        Carga y transforma datos seleccionados del diccionario de información completa
        para mostrarlos en una tabla (ListStore). Aplica las siguientes transformaciones:
        - Convierte la fecha a formato 'DD-MM-YYYY (Hora: HHh:MMm:SSs)'
        - Convierte el estado booleano a texto: 'Existente' o 'Inexistente'
        """
        #para actualización
        self.DATOS_COMPLETOS_BDINFORM_SUP = self.BD_Informadora_Functions.obtener_registros(modo="diccionario")

        # Claves a extraer por cada registro
        datos_a_seleccionar = ["nombre", "descripcion", "ultima_actualizacion", "estado"]
        datos_seleccionados = {}

        for id_bd, datos in self.DATOS_COMPLETOS_BDINFORM_SUP.items():
            # Extraer solo las claves necesarias
            filtrado = {clave: datos[clave] for clave in datos_a_seleccionar if clave in datos}
            datos_seleccionados[id_bd] = filtrado

        # Limpiar el modelo
        while self.modelo.get_n_items() > 0:
            self.modelo.remove(0)

        # Transformar y añadir al modelo
        for id_bd, datos in datos_seleccionados.items():
            # Transformar fecha si está presente
            fecha_cruda = datos.get("ultima_actualizacion")
            if fecha_cruda:
                try:
                    fecha_obj = datetime.fromisoformat(str(fecha_cruda))
                    fecha_transformada = fecha_obj.strftime("%d-%m-%Y (Hora: %Hh:%Mm:%Ss)")
                except Exception:
                    fecha_transformada = "Fecha inválida"
            else:
                fecha_transformada = "Sin datos"

            # Transformar estado booleano
            estado_bool = datos.get("estado", False)
            estado_transformado = "Existente" if estado_bool else "Inexistente"

            # Crear objeto de fila
            item = BD_Informadora_Tab(
                id=id_bd,
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                ultima_actualizacion=fecha_transformada,
                estado=estado_transformado
            )

            self.modelo.append(item)

    def Dialogo_Form_BD(self, modo_edicion=False, btn_edicion=False):
        """
        Muestra un formulario con la información de una base de datos.

        Parámetros:
        - modo_edicion (bool): Si es True, permite editar los campos. Si es False, los campos serán solo lectura.
        """

        def iniciar_reconstrucción(widget=None):
            self.vent_General_OpcIndividual(
                funcion_a_ejecutar=self.reconstuir_BD_Individual,
                etiqueta_boton="Iniciar reconstrucción",
                nombre_tmp_Archexplic="explicacion_reconstruccion_2.txt")

        def iniciar_respaldo (widget=None):
            self.vent_General_OpcIndividual(
                funcion_a_ejecutar=self.respaldar_BD_Individual,
                etiqueta_boton="Iniciar respaldo de base de datos",
                nombre_tmp_Archexplic="explicacion_respaldo_3.txt")

        def iniciar_restauracion(widget=None):
            self.vent_General_OpcIndividual(
                funcion_a_ejecutar=self.restaurar_BD_Individual,
                etiqueta_boton="Iniciar restauración",
                nombre_tmp_Archexplic="explicacion_restauracionI_4.txt")

        def iniciar_verificación_RutaExist(widget=None):
            self.vent_General_OpcIndividual(
                funcion_a_ejecutar=self.Verificar_Rutaexistencia_BD_Invidiual,
                etiqueta_boton="Iniciar verificación",
                nombre_tmp_Archexplic="explicacion_rutaverYexis_5.txt")

        Vent_InformBD = Gtk.Dialog(
            title="Detalles de la base de datos",
            transient_for=self.get_root(),
            modal=True,
        )
        Vent_InformBD.set_default_size(1200, 600)
        content_area = Vent_InformBD.get_content_area()

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(6)

        # Helper: determinar si los widgets deben permitir edición (se usará con **funcion)
        def configurar_entry(editable=True):
            return {
                "hexpand": True,
                "editable": editable,
                "focusable": editable
            }

        # ETIQUETAS
        label_NombreBD = Gtk.Label(label="Nombre:", xalign=1.0)
        label_DescriBD = Gtk.Label(label="Descripción:", xalign=1.0, yalign=0.0)
        label_EstaBD = Gtk.Label(label="Estado:", xalign=1.0)
        label_tipoBD = Gtk.Label(label="Tipo de Base de Datos:", xalign=1.0)
        label_origenBD = Gtk.Label(label="Origen:", xalign=1.0)
        label_permisosBD = Gtk.Label(label="Permisos:", xalign=1.0)
        label_primActBD = Gtk.Label(label="Primera actualización:", xalign=1.0)
        label_ultiActBD = Gtk.Label(label="Última actualización:", xalign=1.0)
        label_ubicacionBD = Gtk.Label(label="Ubicación de la Base de Datos:", xalign=1.0)
        label_ubicacionResBD = Gtk.Label(label="Ubicación de la carpeta de respaldo de la base de datos:", xalign=1.0)

        # ENTRYS / TEXTVIEW (dependiendo del modo de edición)

        #Los dos asteriscos (**) "desempaquetan" el diccionario de configurar_entry() según
        #los valores que estos tengan. 
        self.Entry_NombreBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_NombreBD.set_tooltip_text(
            "Muestra el nombre de la base de datos")

        self.Textview_DescriBD = Gtk.TextView(hexpand=True, vexpand=True)
        self.Textview_DescriBD.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.Textview_DescriBD.set_tooltip_text(
            "Muestra la descripción de la base de datos")
        self.Textview_DescriBD.set_editable(modo_edicion)

        self.Entry_EstaBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_EstaBD.set_tooltip_text(
            "Muestra el estado reconocido de la base de datos. Puede ser: Existente o Inexistente")
        
        self.Entry_tipoBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_tipoBD.set_tooltip_text(
            "Muestra el tipo de base de datos. Puede ser: SQLite, PostgreSQL, etc.")
        
        self.Entry_orgienBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_orgienBD.set_tooltip_text(
            "Muestra el origen de la base de datos. Puede ser: Externa, Sistema, Usuario o Por Extensión.")
        
        self.Entry_permisosBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_permisosBD.set_tooltip_text(
            "Muestra los permisos registrados en la base de datos. Pueden ser: \nlectura, lectura/escritura, bloqueada o solo interna")
        
        self.Entry_primActBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_primActBD.set_tooltip_text(
            "Muestra la primera actualización registrada en la base de datos. Suele ser la fecha de registro.")

        self.Entry_ultiActBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_ultiActBD.set_tooltip_text(
            "Muestra la última actualización registrada en la base de datos. Solo en el registro (cambio de nombre, ubicación, etc)")
        
        self.Entry_ubicacionBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_ubicacionBD.set_tooltip_text(
            "Muestra la ubicación de la base de datos en el sistema de archivos.")

        self.Entry_ubicacionResBD = Gtk.Entry(**configurar_entry(modo_edicion))
        self.Entry_ubicacionResBD.set_tooltip_text(
            "Muestra la ubicación de la carpeta de respaldo (backup) de la base de datos en el sistema de archivos.\nLas carpetas solo se crean después del PRIMER respaldo.")

        # POSICIÓN
        Para_Pos = [
            (label_NombreBD, self.Entry_NombreBD),
            (label_ubicacionBD, self.Entry_ubicacionBD),
            (label_tipoBD, self.Entry_tipoBD),
            (label_EstaBD, self.Entry_EstaBD),
            (label_origenBD, self.Entry_orgienBD),
            (label_permisosBD, self.Entry_permisosBD),
            (label_DescriBD, self.Textview_DescriBD),
            (label_primActBD, self.Entry_primActBD),
            (label_ultiActBD, self.Entry_ultiActBD),
            (label_ubicacionResBD, self.Entry_ubicacionResBD)
        ]

        for i, (etiqueta, contenido) in enumerate(Para_Pos):
            grid.attach(etiqueta, 0, i, 1, 1) #col, fila, with, height
            grid.attach(contenido, 1, i, 1, 1) #col1, fila i, ocupa 1x1


        # BOTONES
        btn_reconstruitBD = Gtk.Button(label="Reconstuir base de datos")
        btn_reconstruitBD.connect("clicked", iniciar_reconstrucción)

        btn_restaurarBD = Gtk.Button(label="Restaurar base de datos")
        btn_restaurarBD.connect("clicked", iniciar_restauracion)

        btn_verExistBD = Gtk.Button(label="Verificar existencia y rutas")
        btn_verExistBD.connect("clicked", iniciar_verificación_RutaExist)

        btn_respaldarBD = Gtk.Button(label="Respaldar base de datos")
        btn_respaldarBD.connect("clicked", iniciar_respaldo)


        btn_eliminarBD = Gtk.Button(label="Eliminar base de datos")
        btn_eliminarBD.connect("clicked", self.eliminar_BD, Vent_InformBD)


        # Layout
        box_pr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        box_pr.set_margin_top(10)
        box_pr.set_margin_bottom(10)
        box_pr.set_margin_start(10)
        box_pr.set_margin_end(10)

        vbox_grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        vbox_btn = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        vbox_grid.append(grid)

        #Para decidir mostrar o no el botón de registro
        if btn_edicion:
            btn_registrarBD_op = Gtk.Button(label="Registar")
            btn_registrarBD_op.connect("clicked", self.registrar_nueva_BD)

            btn_reconstruitBD.set_sensitive(False)
            btn_eliminarBD.set_sensitive(False)
            btn_restaurarBD.set_sensitive(False)
            btn_verExistBD.set_sensitive(False)
            btn_respaldarBD.set_sensitive(False)


            #Estos campos no pueden ser editados por el usuario. Los hace el "sistema"
            self.Entry_primActBD.set_editable(False)
            self.Entry_primActBD.set_focusable(False)
            self.Entry_ultiActBD.set_editable(False)
            self.Entry_ultiActBD.set_focusable(False)
            self.Entry_EstaBD.set_editable(False)
            self.Entry_EstaBD.set_focusable(False)


            #Botones en el formulario
            btn_elegirBD = Gtk.Button(label="Seleccionar Base de Datos")
            btn_elegirBD.connect("clicked", self.Elegir_BD_vent)
            
            vbox_btn.append(btn_elegirBD)
            vbox_btn.append(btn_registrarBD_op)


        vbox_btn.append(btn_reconstruitBD)
        vbox_btn.append(btn_restaurarBD)
        vbox_btn.append(btn_verExistBD)
        vbox_btn.append(btn_respaldarBD)
        vbox_btn.append(btn_eliminarBD)

        box_pr.append(vbox_grid)
        box_pr.append(vbox_btn)

        content_area.append(box_pr)
        Vent_InformBD.show()

    def limpiar_campos_FormBD(self):
        self.Entry_NombreBD.set_text("")
        self.Textview_DescriBD.get_buffer().set_text("")
        self.Entry_EstaBD.set_text("")
        self.Entry_tipoBD.set_text("")
        self.Entry_orgienBD.set_text("")
        self.Entry_permisosBD.set_text("")
        self.Entry_primActBD.set_text("")
        self.Entry_ultiActBD.set_text("")
        self.Entry_ubicacionBD.set_text("")
        self.Entry_ubicacionResBD.set_text("")

    def mostrar_vent_CompletaBD(self, gesto_click, n_press, x, y):
        """
        Muestra un diálogo de información de base de datos al hacer clic derecho
        sobre un elemento de la lista.

        - Solo actúa cuando se detecta un clic con botón derecho (número 3).
        - Recupera el ID del elemento seleccionado y carga la información
          en la ventana de detalles correspondiente.

        Args:
            gesto_click (Gtk.GestureClick): Objeto de gesto de clic.
            n_press (int): Número de clics detectados.
            x (float): Coordenada X del clic.
            y (float): Coordenada Y del clic.
        """
        if n_press != 1:
            return

        selected_position = self.seleccion.get_selected()

        selected_item = self.seleccion.get_item(selected_position)

        if not selected_item:
            return

        #se extrae el id
        self.id_get_selected = selected_item.id

        if gesto_click.get_current_button() == 3: #Número 3 es click derecho

            self.Dialogo_Form_BD(modo_edicion=False, btn_edicion=False)
            self.cargar_datos_VenInformBD(self.id_get_selected)

    def mostrar_vent_RegistBD(self, widget=None):
        """
        Muestra una ventana para registrar una nueva base de datos,
        previa advertencia al usuario.

        - Muestra un mensaje de advertencia indicando que esta ventana
          solo permite el registro básico de la base de datos.
        - Si el usuario confirma, abre el formulario de registro de base de datos.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
        """
        text1 = "La siguiente ventana solo permite el REGISTRO de una base de datos."
        texto2 = "No añade ningún tipo de funcionalidad a la base de datos a registrar... aún."
        texto_total = text1 + "\n"+texto2
        capture_reponse = mostrar_vent_IEO(
                            self.get_root(),
                            "Advertencia",
                            texto_total,
                            Gtk.MessageType.WARNING,
                            2,
                            "Entiendo",
                            "Cancelar",
                            None
                        )

        # Se realiza una simple verificación para decidir si mostrar o no la ventana de registro.
        if capture_reponse == -5: #-5 es el ID del OK, es decir, de "Entiendo". -6 es el de "Cancelar"
            
            self.Dialogo_Form_BD(modo_edicion=True, btn_edicion=True)

    def registrar_nueva_BD(self, widget=None):
        """
        Registra una nueva base de datos en el sistema después de validar
        los campos ingresados por el usuario.

        - Valida que todos los campos obligatorios estén completos.
        - Verifica que el nombre de la base de datos sea único.
        - Comprueba que el permiso y el origen sean válidos según listas
          predefinidas.
        - Impide registrar bases de datos con origen "Sistema" por parte
          de un usuario.
        - Valida la existencia física del archivo de base de datos.
        - Crea un nuevo objeto `BDInformadora` y lo guarda en la base de datos.
        - Limpia el formulario y actualiza la vista.
        - Muestra un mensaje de confirmación o error según el caso.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.

        Returns:
            Gtk.ResponseType: Resultado de la ventana de información o error.
        """
        TX_1 = self.Entry_NombreBD.get_text().strip()
        buffer = self.Textview_DescriBD.get_buffer()
        TX_2 = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        TX_4 = self.Entry_tipoBD.get_text().strip()
        TX_5 = self.Entry_orgienBD.get_text().strip()
        TX_6 = self.Entry_permisosBD.get_text().strip()
        TX_9 = self.Entry_ubicacionBD.get_text().strip()
        TX_10 = self.Entry_ubicacionResBD.get_text().strip()


        
        try:
            # Validación de campos obligatorios
            if not all([TX_1,TX_4,TX_5,TX_6,TX_9, TX_10]):
                return mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "Se han detectado campos importantes vacíos. No se puede guardar.",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

            # Validación de nombre único
            if self.BD_Informadora_Functions.validar_unico(TX_1) is not None:
                return mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "Ya existe una base de datos registrada con el nombre ingresado.",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

            # Validación de permisos
            if not any(permiso.lower() == TX_6.lower() for permiso in self.Permisos_BD_Lista):
                return mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "No se reconoce como válido el PERMISO insertado.",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

            # Validación de origen
            if not any(origen.lower() == TX_5.lower() for origen in self.Origen_BD_Lista):
                return mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "No se reconoce como válido el ORIGEN insertado.",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

            #Validación de origen (sin Sistema)
            if TX_5.lower() == "sistema":
                return mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "Usted, como USUARIO, no puede registrar bases de datos del SISTEMA.",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)

            # Validar existencia del archivo
            existe_bd = self.verificar_BD_Existencia(TX_9)
            self.Entry_EstaBD.set_text("Existente" if existe_bd else "Inexistente")

            # Construcción del nuevo objeto de base de datos
            nueva_BD_get = BDInformadora(
                nombre=self.Entry_NombreBD.get_text(),
                descripcion=TX_2,
                tipo=self.Entry_tipoBD.get_text(),
                origen=self.Entry_orgienBD.get_text(),
                permisos=self.Entry_permisosBD.get_text(),
                ubicacion=self.Entry_ubicacionBD.get_text(),
                ubicacion_respaldo = self.Entry_ubicacionResBD.get_text(),
                estado=existe_bd
            )

            # Registro en la base de datos
            self.BD_Informadora_Functions.registrar_nuevas_BD(nueva_BD_get)

            #Limpieza de campos
            self.limpiar_campos_FormBD()
            self.Entry_NombreBD.grab_focus()

            #Actualización de la tabla
            self.cargar_datos_seleccionados()

            # Confirmación al usuario
            return mostrar_vent_IEO(
                self.get_root(),
                "Registro Exitoso",
                "El registro se ha completado sin problemas. \nEs posible que se requiera una actualización manual.",
                Gtk.MessageType.INFO,
                1,
                None,
                None)

        except Exception as e:
            return mostrar_vent_IEO(
                self.get_root(),
                "Error de Registro",
                f"Ha ocurrido un error inesperado.\nDetalles: {e}",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def Elegir_BD_vent(self, widget=None):

        """
        Abre un diálogo Gtk.FileChooserDialog que permite al usuario seleccionar 
        una carpeta del sistema de archivos.

        Parámetros:
            widget (Gtk.Widget, opcional): El widget que disparó la acción 
            (puede ser None).

        Comportamiento:
            - Muestra un diálogo modal con botones "Seleccionar" y "Cancelar".
            - El resultado del diálogo es manejado por `self.on_Carpeta_Escogida`.

        """
        dialog = Gtk.FileChooserDialog(
            title="Seleccionar una Base de Datos",
            transient_for=self.get_root(),
            modal=True,
            action=Gtk.FileChooserAction.OPEN,
            )

        dialog.add_button("Seleccionar", Gtk.ResponseType.OK)
        dialog.add_button("Cancelar", Gtk.ResponseType.CANCEL)

        filtro_dialogBD = Gtk.FileFilter()
        filtro_dialogBD.set_name("Bases de Datos (*.db, *.sqlite, *.sql)")
        filtro_dialogBD.add_pattern("*.db")
        filtro_dialogBD.add_pattern("*.sqlite")
        filtro_dialogBD.add_pattern("*.sql")

        filtro_TODOS = Gtk.FileFilter()
        filtro_TODOS.set_name("Todos los archivos")
        filtro_TODOS.add_pattern("*")

        dialog.add_filter(filtro_dialogBD)
        dialog.add_filter(filtro_TODOS)

        dialog.connect("response", self.on_BD_Escogida)
        dialog.present()

    def on_BD_Escogida(self, dialog, response):

        """
        Maneja la respuesta del usuario al seleccionar una carpeta en el diálogo de 
        selección.

        Parámetros:
            dialog (Gtk.FileChooserDialog): El diálogo que emitió la respuesta.
            response (Gtk.ResponseType): Código de respuesta del usuario (OK o CANCEL).

        Comportamiento:
            - Si el usuario presiona "Seleccionar" (OK) y elige una base de datos válida,
            la ruta del archivo se inserta en su correspondiente entry.
        """

        if response == Gtk.ResponseType.OK:
            file_get = dialog.get_file()

            if file_get:
                ruta_get = file_get.get_path()
                nombre_archivoBD = os.path.basename(ruta_get)
                nombreBD_SinExt, extensionBD = os.path.splitext(nombre_archivoBD)
                
                self.Entry_ubicacionBD.set_text(ruta_get)

                if self.Entry_NombreBD.get_text() == "":
                    self.Entry_NombreBD.set_text(nombreBD_SinExt)

                if self.Entry_tipoBD.get_text() == "":

                    if extensionBD == ".sqlite":
                        self.Entry_tipoBD.set_text("SQLite")

                    elif extensionBD == ".accdb" or extensionBD == ".mdb":
                        self.Entry_tipoBD.set_text("Microsoft Access")

                    elif extensionBD == ".db":
                        self.Entry_tipoBD.set_text("Base de Datos Genérica")

                    elif extensionBD == ".sql":
                        self.Entry_tipoBD.set_text("SQL (script)")

                    elif extensionBD == ".pgsql" or extensionBD == ".psql":
                        self.Entry_tipoBD.set_text("PostgreSQL")

                    elif extensionBD == ".mysql":
                        self.Entry_tipoBD.set_text("MySQL")

                    elif extensionBD == ".dump":
                        self.Entry_tipoBD.set_text("PostgreSQL Dump")

                    elif extensionBD in [".json", ".bson"]:
                        self.Entry_tipoBD.set_text("MongoDB / NoSQL")

                    elif extensionBD == ".xml":
                        self.Entry_tipoBD.set_text("Base de Datos XML")

                    elif extensionBD in [".ini", ".conf"]:
                        self.Entry_tipoBD.set_text("Archivo de Configuración")

                    else:
                        self.Entry_tipoBD.set_text("Tipo no reconocido")


        dialog.destroy()

    def verificar_BD_Existencia(self, ruta_a_Verificar_get):
        """
        Verifica si una base de datos existe físicamente en la ruta indicada.

        - Comprueba si el archivo especificado por `ruta_a_Verificar_get` existe en el sistema de archivos.
        - Actualiza el atributo `Estado_Existencia_BD` con el resultado.
        - Devuelve un valor booleano que indica la existencia del archivo.

        Args:
            ruta_a_Verificar_get (str): Ruta absoluta o relativa al archivo de base de datos.

        Returns:
            bool: True si el archivo existe, False en caso contrario.
        """
        self.Estado_Existencia_BD = False

        if os.path.isfile(ruta_a_Verificar_get):

            self.Estado_Existencia_BD = True

        return self.Estado_Existencia_BD

    def cargar_datos_VenInformBD(self, id_get):
        """
        Carga los datos de la base de datos según el id proporcionado en los campos del formulario.
        Transforma las fechas y el estado antes de asignarlos.
        """
        try:
            # Obtener los datos desde la base de datos
            DATO_BD_ID = self.BD_Informadora_Functions.obtener_registros_ID(id_get)


            # Diccionario de asociación entre claves del diccionario y widgets Gtk.Entry/TextView
            widgets_map = {
                "nombre": self.Entry_NombreBD,
                "descripcion": self.Textview_DescriBD,
                "tipo": self.Entry_tipoBD,
                "origen": self.Entry_orgienBD,
                "permisos": self.Entry_permisosBD,
                "ubicacion": self.Entry_ubicacionBD,
                "ubicacion_respaldo": self.Entry_ubicacionResBD
            }

            # Asignar valores simples a Entry o TextView
            for clave, widget in widgets_map.items():
                
                valor = DATO_BD_ID.get(clave, "")

                if isinstance(widget, Gtk.Entry):
                
                    widget.set_text(valor)
                
                elif isinstance(widget, Gtk.TextView):
                
                    buffer = widget.get_buffer()
                    buffer.set_text(valor)
            
            # Transformar y mostrar fechas (si existen)
            def formatear_Y_convertir_fecha(fecha_str):
                try:
                    #Convertimos de UTC a hora local (según la región)
                    region_get = leer_archivo_recurrente("Ajustes_Generales.json", "json")
                    fecha_convert, region_select= self.BD_Informadora_Functions.convertir_horaUTC_a_horalocal(fecha_str, region_get["Zona_Horaria"])



                    #Formateamos la fecha convertida
                    fecha = datetime.fromisoformat(str(fecha_convert))
                    

                    fecha2 = f"{fecha.strftime("%d-%m-%Y (Hora: %Hh:%Mm:%Ss)")}  Región: {region_select}"

                    return fecha2

                except Exception:
                    return f"Fecha inválida o Región Invalida"

            self.Entry_primActBD.set_text(formatear_Y_convertir_fecha(DATO_BD_ID.get("primera_actualizacion")))
            self.Entry_ultiActBD.set_text(formatear_Y_convertir_fecha(DATO_BD_ID.get("ultima_actualizacion")))

            # Transformar estado booleano
            estado_texto = "Existente" if DATO_BD_ID.get("estado") else "Inexistente"
            self.Entry_EstaBD.set_text(estado_texto)
        
        except Exception as e:
            mostrar_vent_IEO(
                self.get_root(),
                "Error de Cargado",
                f"No se pudo cargar los datos correctamente.\nMás detalles del error: {e}",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def eliminar_BD(self, widget=None, Vent_InformBD_get=None):
        """
        Muestra una ventana de confirmación para eliminar una base de datos.

        - Presenta dos opciones al usuario: eliminar completamente el archivo
          y su registro, o eliminar solo el registro.
        - Incluye un botón para habilitar ambas opciones como medida preventiva.
        - No realiza la eliminación directamente, sino que delega en
          `eliminar_BD_ARCHIVO` o `eliminar_BD_REGISTROS` según la elección.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
            Vent_InformBD_get (Gtk.Dialog, opcional): Ventana informativa previa
                que podría cerrarse tras la eliminación.
        """

        def habilitar_botones(widget=None):

            Btn_1.set_sensitive(True)
            Btn_2.set_sensitive(True)

        Vent_Eliminar_BD = Gtk.Dialog(
            title="¿Eliminar Base de Datos?",
            transient_for=self.get_root(),
            modal=True,
        )
        Vent_Eliminar_BD.set_default_size(400, 250)
        content_area = Vent_Eliminar_BD.get_content_area()

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box_pr.set_margin_top(20)
        box_pr.set_margin_bottom(20)
        box_pr.set_margin_start(20)
        box_pr.set_margin_end(20)

        box_label = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        Nombre_BD = self.Entry_NombreBD.get_text()
        Ruta_BD = self.Entry_ubicacionBD.get_text()

        label1 = Gtk.Label(
            label=f"¿Desea eliminar la base de datos «{Nombre_BD}»?")
        label1.set_wrap(True)
        label1.set_justify(Gtk.Justification.CENTER)
        label1.set_xalign(0.5)

        label2 = Gtk.Label(
            label=f"⚠ ADVERTENCIA: Esta acción puede eliminar el archivo:\n{Ruta_BD}")
        label2.set_wrap(True)
        label2.set_justify(Gtk.Justification.CENTER)
        label2.set_xalign(0.5)

        label3 = Gtk.Label(label="ESTA ACCIÓN NO SE PUEDE DESHACER")
        label3.get_style_context().add_class("error")
        label3.set_xalign(0.5)     

        Btn_Habili = Gtk.Button(label="Habilitar botones de opción")
        Btn_Habili.connect("clicked", habilitar_botones)

        Btn_1 = Gtk.Button(label="Eliminar Base de Datos")
        Btn_1.set_tooltip_text(
            "Esta opción ELIMINA el archivo de base de datos correspondiente al indicado en el registro.\nAdemás, elimina el REGISTRO de la base de datos.")
        Btn_1.connect("clicked", self.eliminar_BD_ARCHIVO, Vent_Eliminar_BD, Vent_InformBD_get)
        Btn_1.set_sensitive(False)

        Btn_2 = Gtk.Button(label="Eliminar solo REGISTRO")
        Btn_2.set_tooltip_text(
            "Esta opción solo elimina el REGISTRO de la base de datos. No elimina ningún archivo.")
        Btn_2.connect("clicked", self.eliminar_BD_REGISTROS, Vent_Eliminar_BD, Vent_InformBD_get)
        Btn_2.set_sensitive(False)

        box_label.append(label1)
        box_label.append(label2)
        box_label.append(label3)

        box_btn.append(Btn_1)
        box_btn.append(Btn_2)

        box_pr.append(box_label)
        box_pr.append(box_btn)
        box_pr.append(Btn_Habili)
        
        content_area.append(box_pr)

        Vent_Eliminar_BD.show()

    def eliminar_BD_REGISTROS(self, widget=None, dialog=None, Vent_InformBD_get=None):
        """
        Elimina únicamente el registro de una base de datos desde la base de datos interna del sistema.

        - Utiliza `self.BD_Informadora_Functions.eliminar_registros()` para
          borrar la entrada correspondiente.
        - Actualiza la vista para reflejar el cambio.
        - Cierra tanto la ventana de confirmación como la ventana de información asociada.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
            dialog (Gtk.Dialog, opcional): Diálogo de confirmación de eliminación.
            Vent_InformBD_get (Gtk.Dialog, opcional): Ventana de información de la base de datos.

        Raises:
            Exception: Si ocurre un error durante el proceso de eliminación.
        """
        try:
            self.BD_Informadora_Functions.eliminar_registros(self.id_get_selected)

            mostrar_vent_IEO(
                self.get_root(),
                "Eliminación exitosa",
                "La base de datos ha sido eliminada exitosamente de la base de datos.",
                Gtk.MessageType.INFO,
                1,
                None,
                None)

            #Se actualiza la tabla y luego se eliminan ambas ventanas (la de confirmación y la del formulario)
            self.cargar_datos_seleccionados()
            dialog.destroy()
            Vent_InformBD_get.destroy()

        except Exception as e:

            mostrar_vent_IEO(
                self.get_root(),
                "Error de eliminación",
                f"No se ha podido eliminar la base de datos seleccionada.\nDetalles:{e}",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def eliminar_BD_ARCHIVO(self, widget=None, dialog=None, Vent_InformBD_get=None):
        """
        Elimina físicamente el archivo de base de datos y su registro en el sistema.

        - Verifica que la base de datos esté marcada como existente y que el archivo
          realmente exista en el sistema de archivos.
        - Elimina el archivo de la ruta registrada.
        - Borra el registro correspondiente de la base de datos interna.
        - Actualiza la vista y cierra las ventanas asociadas.
        - Si el archivo no existe o el estado es "INEXISTENTE", muestra un mensaje de error.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
            dialog (Gtk.Dialog, opcional): Diálogo de confirmación de eliminación.
            Vent_InformBD_get (Gtk.Dialog, opcional): Ventana de información de la base de datos.

        Raises:
            Exception: Si ocurre un error al intentar eliminar el archivo o el registro.
        """
        ruta_BD_registrada = self.BD_Informadora_Functions.Obtener_Ruta_BD(id_get=self.id_get_selected)
        
        #Verificar el ESTADO de la base de datos seleccionada
        estado_get_BD = self.BD_Informadora_Functions.verificar_estado_BD(self.id_get_selected)

        try:

            if estado_get_BD: #Si es true (Existente)

                if not os.path.isfile(ruta_BD_registrada):
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Error de eliminación",
                        "No se encuentra el archivo o este no existe. Imposible continuar.",
                        Gtk.MessageType.ERROR,
                        1,
                        None,
                        None)
                    return

                # Se elimina el archivo de la ruta
                os.remove(ruta_BD_registrada)

                #Se elimina, además, el registro de la base de datos
                self.BD_Informadora_Functions.eliminar_registros(self.id_get_selected)

                mostrar_vent_IEO(
                    self.get_root(),
                    "Eliminación exitosa",
                    f"El archivo con nombre <<{self.Entry_NombreBD.get_text()}>> fue eliminado exitosamente.",
                    Gtk.MessageType.INFO,
                    1,
                    None,
                    None,
                    None)

                #Se actualiza la tabla y luego se eliminan ambas ventanas (la de confirmación y la del formulario)
                self.cargar_datos_seleccionados()
                dialog.destroy()
                Vent_InformBD_get.destroy()

            else: #Si es False (Inexistente)

                mostrar_vent_IEO(
                    self.get_root(),
                    "Error de eliminación",
                    f"El archivo con nombre <<{self.Entry_NombreBD.get_text()}>> no fue eliminado.\nNo es posible eliminar un archivo con estado INEXISTENTE",
                    Gtk.MessageType.ERROR,
                    1,
                    None,
                    None)
        except Exception as e:

            mostrar_vent_IEO(
                self.get_root(),
                "Error de eliminación",
                f"No se ha podido eliminar la base de datos seleccionada.\nDetalles:{e}",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def Mostrar_Vent_OperGrup(self, widget=None):
        """
        Muestra la ventana de operaciones grupales sobre bases de datos.

        - Permite al usuario filtrar bases de datos por su origen (actualmente solo "Sistema").
        - Muestra una lista de las bases de datos filtradas en un `Gtk.ListBox`.
        - Ofrece botones para reconstruir las bases de datos seleccionadas o respaldarlas.
        - Conecta la destrucción de la ventana con una función de limpieza (`limpieza_ventOperGrup`).

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
        """
        Vent_OperGrup = Gtk.Dialog(
            title="Operaciones Grupales",
            transient_for=self.get_root(),
            modal=True,
        )
        Vent_OperGrup.set_default_size(700, 600)
        content_area = Vent_OperGrup.get_content_area()

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_btn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box_2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        #Widgets Labels
        Label_FiltroSelect = Gtk.Label(label="Seleccione el ORIGEN de las bases de datos sobre las cuales trabajar:")

        #ListBox
        listbox=Gtk.ListBox(vexpand=True)
        listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_child(listbox)
        scroll_window.set_vexpand(True)


        #Widgets Entrys
        Entry_FiltroSelect = Gtk.Entry()
        Entry_FiltroSelect.set_tooltip_text(
            "Escriba el ORIGEN de la base de datos para que actue de filtro. Pueden ser: Sistema, Usuario, Externa o Por Extensión.\nADVERTENCIA: Por el momento, solo se permite Sistema.")

        """
        La siguientes lineas del Entry_FiltroSelect impiden que se inserte algo diferente
        a "Sistema", esto debido a que, al momento en que se escriben estas lineas,
        la función de reconstrucción de las bases de datos solo esta diseñada para las bases
        de datos específicas del "Sistema", y no las bases de datos del usuario; funcionalidad
        que será añadida más adelante. Una vez se haga eso, se eliminarán las dos lineas.
        """
        Entry_FiltroSelect.set_text("Sistema")
        Entry_FiltroSelect.set_editable(False)

        #Widgets Botones
        Btn_BuscarFiltro = Gtk.Button(label="Buscar bases de datos por ORIGEN")
        Btn_BuscarFiltro.connect("clicked", self.cargar_datos_filtroReconsBds, Entry_FiltroSelect, listbox)

        Btn_Reconstruir = Gtk.Button(label="Iniciar la reconstrucción de las bases de datos")
        Btn_Reconstruir.connect("clicked", self.reconstuir_BDs, listbox)

        Btn_Respaldar_BDs = Gtk.Button(label="Respaldar bases de datos")
        Btn_Respaldar_BDs.connect("clicked", self.respaldar_BDs)

        #Posicionamiento de Widgets
        box_1.append(Label_FiltroSelect)
        box_1.append(Entry_FiltroSelect)

        box_2.append(Btn_BuscarFiltro)
        box_2.append(scroll_window)

        box_btn.append(Btn_Reconstruir)
        box_btn.append(Btn_Respaldar_BDs)

        box_pr.append(box_1)
        box_pr.append(box_2)
        box_pr.append(box_btn)

        content_area.append(box_pr)

        Vent_OperGrup.connect("destroy", self.limpieza_ventOperGrup)

        Vent_OperGrup.show()

    def limpieza_ventOperGrup(self, widget=None):

        #Para limpiar la lista de filtro, y ser usada limpiamente por las funciones respectivas.
        self.Datos_Filtro_Get_SUP.clear()
    
    def cargar_datos_filtroReconsBds(self, widget=None, filtro_widget=None, listbox_wigdet=None):
        """
        Carga y muestra en un `Gtk.ListBox` las bases de datos filtradas por origen.

        - Elimina el contenido actual del listbox antes de cargar nuevos datos.
        - Valida el texto del filtro para que sea uno de los valores permitidos:
          "Sistema", "Usuario", "Externa" o "Por Extensión".
        - Recupera los registros correspondientes desde la base de datos interna
          usando `self.BD_Informadora_Functions.obtener_registros_origen()`.
        - Por cada base de datos, crea un contenedor con etiquetas para ID, nombre,
          descripción y ubicación, y lo agrega como fila al listbox.
        - Si el filtro es inválido, muestra un mensaje de error.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
            filtro_widget (Gtk.Entry): Campo de texto con el valor del filtro.
            listbox_wigdet (Gtk.ListBox): Lista en la que se mostrarán los resultados.
        """
        child = listbox_wigdet.get_first_child()
        while child:
            siguiente = child.get_next_sibling()
            listbox_wigdet.remove(child)
            child = siguiente

        texto_get = filtro_widget.get_text()

        if texto_get in ["Sistema", "Usuario", "Externa", "Por Extensión"]:
        
            self.Datos_Filtro_Get_SUP = self.BD_Informadora_Functions.obtener_registros_origen(texto_get)


            for dato in self.Datos_Filtro_Get_SUP:

                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                box.get_style_context().add_class("boxs_filtradas")

                label_id = Gtk.Label(label=f"ID:{dato["id"]}")
                label_id.set_wrap(True)
                label_id.set_xalign(0.0)

                label_nombre = Gtk.Label(label=f"Nombre:{dato["nombre"]}")
                label_nombre.set_wrap(True)
                label_nombre.set_xalign(0.0)

                label_descripcion = Gtk.Label(label=f"Descripción:{dato["descripcion"]}")
                label_descripcion.set_wrap(True)
                label_descripcion.set_xalign(0.0)

                label_ubicacionRuta = Gtk.Label(label=f"Ubicación:{dato["ubicacion"]}")
                label_ubicacionRuta.set_wrap(True)
                label_ubicacionRuta.set_xalign(0.0)

                box.append(label_id)
                box.append(label_nombre)
                box.append(label_descripcion)
                box.append(label_ubicacionRuta)


                row = Gtk.ListBoxRow()
                row.set_child(box)
                listbox_wigdet.append(row)

        else:
            mostrar_vent_IEO(
                self.get_root(),
                "Error de Verificación",
                f"No se reconoce el filtro por ORIGEN insertado ({texto_get}).\nPor favor, inserte uno válido.",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def obtener_datos_listbox(self, listbox_wigdet=None):
        """
        Extrae y devuelve el texto de las etiquetas en un `Gtk.ListBox`.

        - Itera sobre todas las filas del listbox.
        - Si una fila contiene un `Gtk.Box` con etiquetas (`Gtk.Label`), recopila
          el texto de cada una y lo agrega a una lista.
        - Devuelve los textos recopilados.

        Args:
            listbox_wigdet (Gtk.ListBox, opcional): Lista desde la que se extraerán los datos.

        Returns:
            list[str]: Lista de cadenas con los textos de las etiquetas encontradas.
        """


        # Extraer datos del listbox
        child = listbox_wigdet.get_first_child()
        fila_datos = []
        
        while child:
            contenido_fila = child.get_child()
            fila_datos = []
            if isinstance(contenido_fila, Gtk.Box):
                widget = contenido_fila.get_first_child()
                while widget:
                    if isinstance(widget, Gtk.Label):
                        fila_datos.append(widget.get_text())
                    widget = widget.get_next_sibling()

            child = child.get_next_sibling()
        
        return fila_datos

    def reconstuir_BDs(self, widget=None, listbox_wigdet=None):
        """
        Inicia el proceso de reconstrucción de bases de datos seleccionadas.

        - Presenta un diálogo de confirmación antes de iniciar.
        - Permite habilitar o cancelar la acción.
        - Si se confirma, elimina las bases de datos seleccionadas (tanto registros como archivos) 
          y las recrea usando `crear_BDs_Constructor`.
        - Posteriormente, reinicia la base de datos informadora y asegura la existencia de registros predeterminados.
        - Al finalizar, crea un archivo temporal para indicar que el programa debe reiniciarse.
        - Si no hay elementos en la lista, muestra un mensaje de error.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
            listbox_wigdet (Gtk.ListBox, opcional): Lista con las bases de datos filtradas para reconstrucción.
        """
        def habilitar_botones(widget=None):
            btn1.set_sensitive(True)

        def cerrar_dialogo(widget=None):
            Vent_Verificar_ReconstBD.destroy()

        def mostrar_mensaje(texto_get):
            label_estado.set_text(texto_get)

        def initreconstruir_bds(widget=None):
            # Limpieza visual
            for w in [box_1, box_2, btn2, btn3]:
                box_pr.remove(w)

            # Spinner y mensajes
            spinner.start()
            box_progreso = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box_progreso.append(spinner)
            box_progreso.append(label_estado)
            box_pr.append(box_progreso)

            Vent_Verificar_ReconstBD.set_default_size(500, 200)
            mostrar_mensaje("Iniciando reconstrucción de bases de datos...")

            GLib.idle_add(ejecutar_reconstruccion)

        def ejecutar_reconstruccion():

            rutas_a_eliminar = []
            nombres_para_constructor = []
            ids_para_eliminar = []

            fila_datos = self.obtener_datos_listbox(listbox_wigdet)
                
            if len(fila_datos) >= 2:
                nombre = fila_datos[1].replace("Nombre:", "").strip()
                ruta = fila_datos[3].replace("Ubicación:", "").strip()
                id_ = fila_datos[0].replace("ID:", "").strip()

                rutas_a_eliminar.append(ruta)
                nombres_para_constructor.append(nombre)
                ids_para_eliminar.append(id_)
            

            # Eliminar registros antiguos
            for ID in ids_para_eliminar:
                self.BD_Informadora_Functions.eliminar_registros(ID)


            for ruta in rutas_a_eliminar:
                if ruta == "Sin comprobar":
                    mostrar_mensaje("Se ha detectado rutas sin comprobación. Imposible eliminar.\nLa reconstrucción continuará.")

                else:
                    if os.path.isfile(ruta):
                        mostrar_mensaje(f"Eliminando archivo:\n{ruta}")
                        try:
                            os.remove(ruta)
                        except Exception as e:
                            mostrar_vent_IEO(
                                self.get_root(),
                                "Error de eliminación",
                                f"No se pudo eliminar la ruta: {ruta}\nDetalles: {e}",
                                Gtk.MessageType.ERROR,
                                1,
                                "Aceptar", None)
                            return False

            mostrar_mensaje("Recreando estructuras de base de datos...")
            estado, error = crear_BDs_Constructor(bases_a_construir=nombres_para_constructor)

            mostrar_mensaje("Reinicializando base de datos informadora...")
            estado_reconstr, error_reconstr = self.BD_Informadora_Functions.reconstruir_base_de_datos_completa()

            if not estado_reconstr:
                mostrar_mensaje(f"Error crítico: {error_reconstruccion}")
                return False

            mostrar_mensaje("Insertando valores predeterminados y verificando existencia y estado...")
            self.minifunción_asegur_preder()

            self.cargar_datos_seleccionados()


            mostrar_mensaje("¡Bases de datos reconstruidas con éxito!\nEl programa se reiniciará automáticamente en 3 segundos.")

            # Reiniciar programa 
            mostrar_mensaje("Creando archivo tmp para reinicio...")
            estado, error = guardar_archivo_tmp("estado_reinicio.tmp", "reiniciado")

            if estado:

                mostrar_mensaje("Creación de archivo tmp para reinicio exitoso. Es necesario REINICIAR el programa para completar la reconstrucción.\nCIERRE y EJECUTE nuevamente el programa.")
                spinner.stop()

            else:
                mostrar_mensaje(f"Ha ocurrido un error inesperado.\nDetalles:{error}")
            return False

        child_ver = listbox_wigdet.get_first_child()

        #Se verifica si la listbox tiene algo
        if child_ver:

            # DIÁLOGO DE CONFIRMACIÓN
            Vent_Verificar_ReconstBD = Gtk.Dialog(
                title="¿Reconstruir bases de datos?",
                transient_for=self.get_root(),
                modal=True,
            )
            Vent_Verificar_ReconstBD.set_default_size(400, 250)
            content_area = Vent_Verificar_ReconstBD.get_content_area()

            box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            content_area.append(box_pr)

            box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            label1 = Gtk.Label(label="¿Desea iniciar el proceso de reconstrucción?")
            label2 = Gtk.Label(label="⚠ Esta acción ELIMINARÁ las bases de datos seleccionadas.")
            label2.set_wrap(True)
            label3 = Gtk.Label(label="Todo contenido debe estar guardado. El programa se REINICIARÁ al finalizar el proceso.")
            label3.set_wrap(True)
            label4 = Gtk.Label(label="¿Desea continuar?")

            for l in [label1, label2, label3, label4]:
                box_1.append(l)

            box_2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            btn1 = Gtk.Button(label="Continuar", hexpand=True)
            btn1.set_sensitive(False)
            btn1.connect("clicked", initreconstruir_bds)

            btn2 = Gtk.Button(label="Cancelar")
            btn2.connect("clicked", cerrar_dialogo)

            btn3 = Gtk.Button(label="Habilitar botón de aceptación")
            btn3.connect("clicked", habilitar_botones)

            box_2.append(btn1)
            box_pr.append(box_1)
            box_pr.append(box_2)
            box_pr.append(btn3)
            box_pr.append(btn2)

            spinner = Gtk.Spinner()
            label_estado = Gtk.Label(label="Esperando acción...")
            label_estado.set_wrap(True)

            Vent_Verificar_ReconstBD.show()
        else:
            mostrar_vent_IEO(
                self.get_root(),
                "Error de reconstrucción",
                "No se detecta elementos en la lista de bases de datos filtradas.\nNo se puede continuar.",
                Gtk.MessageType.ERROR,
                1,
                None,
                None)

    def mostrar_pantalla_de_recuperacion_ReconstBDs(self, parent):
        """
        Muestra un diálogo de recuperación tras el reinicio por reconstrucción de bases de datos.

        - Lee un archivo temporal (`estado_reinicio.tmp`) para determinar si hubo un reinicio programado.
        - Si es así, presenta una pantalla que informa al usuario y restaura valores predeterminados
          en bases de datos específicas del sistema.
        - Elimina el archivo temporal al finalizar el proceso.
        - Incluye un spinner y mensajes dinámicos de estado.

        Args:
            parent (Gtk.Window): Ventana padre sobre la cual se mostrará el diálogo.
        """


        valor_leido = leer_archivo_tmp("estado_reinicio.tmp")

        spiner_res = Gtk.Spinner()

        def mostrar_mensaje_res(mensaje_get):
            label3.set_text(mensaje_get)

        def cerrar_dialogo():
            Vent_Inform_PostReinicio.destroy()

        def iniciar_restauracion():
            mostrar_mensaje_res("Restaurando valores predeterminados de <<COMBINACIONES DE TECLAS>>")
            self.BD_ComTecl_Functions.asegurar_entradas_preder()

            mostrar_mensaje_res("Restaurando valores predeterminados de <<RUTA PREDETERMINADA>>")
            RUTA_DE_FABRICA = os.path.join(user_documents_path(), "MERIDA")

            estado_y_registro = self.BD_TAGS_Functions.modificar_lista_existente(
                    filtro_etiqueta="Etiqueta Predeterminada",
                    filtro_ruta=None,
                    nueva_etiqueta="Etiqueta Predeterminada",
                    nueva_ruta=RUTA_DE_FABRICA
                    )
            spiner_res.stop()
            mostrar_mensaje_res("Todos los valores predeterminados has sido restaurados.")
            GLib.timeout_add_seconds(2, cerrar_dialogo)

        if valor_leido == "reiniciado":

            Vent_Inform_PostReinicio = Gtk.MessageDialog(
                transient_for=parent,
                modal=True,
                message_type = Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.NONE,
                text="Se ha detectado un reinicio por reconstrucción de bases de datos"
            )

            Vent_Inform_PostReinicio.set_default_size(500, 200)
            content_area = Vent_Inform_PostReinicio.get_content_area()
            
            box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

            label1 = Gtk.Label(label="Como última medida, el programa restaurará los valores predeterminados de las bases de datos seleccionadas.")
            label1.set_wrap(True)

            label2 = Gtk.Label(label="Esta función solo esta habilitada para las bases de datos del SISTEMA.")
            label2.set_wrap(True)

            spiner_res.start()

            label3 = Gtk.Label(label="Iniciando restauración de valores predeterminados")
            label3.set_wrap(True)

            box_1.append(label1)
            box_1.append(label2)
            box_1.append(spiner_res)
            box_1.append(label3)

            content_area.append(box_1)

            GLib.timeout_add_seconds(5, iniciar_restauracion)

            estado, error = borrar_archivo_tmp("estado_reinicio.tmp")

            if not estado:

                mostrar_vent_IEO(
                    parent,
                    "Error de eliminación",
                    f"No se ha podido eliminar un archivo temporal.\nDetalles:{error}",
                    Gtk.MessageType.INFO,
                    1,
                    None,
                    None)

            Vent_Inform_PostReinicio.present()

    def respaldar_BDs(self, widget=None):
        """
        Realiza el respaldo de las bases de datos listadas según el filtro actual.

        - Presenta un diálogo que muestra las bases de datos a respaldar y sus ubicaciones.
        - Inicia un respaldo paso a paso, procesando una base de datos por vez mediante 
          `self.BD_Utilidades_Generales.respaldar_base_de_datos`.
        - Muestra mensajes de progreso y finalización.
        - Si no se encuentran bases de datos para respaldar, muestra un mensaje de error.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la acción.
        """
        def mostrar_mensaje(texto):
            label_mensaje.set_text(texto)

        def iniciar_respaldo_por_pasos():
            # Paso a paso, una BD por llamada
            if iniciar_respaldo_por_pasos.indice < len(self.Datos_Filtro_Get_SUP):
                bd = self.Datos_Filtro_Get_SUP[iniciar_respaldo_por_pasos.indice]
                id_get = bd.get("id", "Sin Id")
                nombre_bd_get = bd.get("nombre", "Sin nombre")

                origen_bd_get = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_get, "origen")
                ubic_respald_bd_get_c = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_get, "ubicacion_respaldo")
                ubic_respald_bd_get = os.path.dirname(ubic_respald_bd_get_c)
                ubic_bd_get = bd.get("ubicacion", "Sin ubicación")

                mostrar_mensaje(f"Respaldando: «{nombre_bd_get}»...")
                self.BD_Utilidades_Generales.respaldar_base_de_datos(
                    nombre_bd_get, origen_bd_get, ubic_respald_bd_get, ubic_bd_get
                )

                iniciar_respaldo_por_pasos.indice += 1

                return True  # Seguir llamando hasta terminar
            else:
                mostrar_mensaje("Respaldo finalizado con éxito.")
                spinner_respald.stop()
                return False  # Detener la secuencia

        def cerrar_dialogo(widget=None):
            Vent_Respaldo_BD.destroy()

        iniciar_respaldo_por_pasos.indice = 0  # Inicializar contador

        if self.Datos_Filtro_Get_SUP:

            Vent_Respaldo_BD = Gtk.Dialog(
                title="Respaldo de Bases de Datos",
                transient_for=self.get_root(),
                modal=True,
            )
            Vent_Respaldo_BD.set_default_size(850, 480)
            content_area = Vent_Respaldo_BD.get_content_area()

            # Elementos visuales
            spinner_respald = Gtk.Spinner()
            label_mensaje = Gtk.Label(label="El respaldo comenzará en 3 segundos...")
            label_mensaje.set_wrap(True)

            box_principal = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin_top=10, margin_bottom=10, margin_start=10, margin_end=10)
            box_principal.append(spinner_respald)
            box_principal.append(label_mensaje)

            #Scroll para la ventana
            scroll_Respald = Gtk.ScrolledWindow()
            scroll_Respald.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll_Respald.set_child(box_principal)
            scroll_Respald.set_vexpand(True)
            scroll_Respald.set_hexpand(True)

            # Título 1
            label_bases = Gtk.Label()
            label_bases.set_markup("<b>Bases de datos a respaldar:</b>")
            label_bases.set_xalign(0.0)
            box_principal.append(label_bases)

            # Lista de nombres
            for bd in self.Datos_Filtro_Get_SUP:
                nombre_bd = bd.get("nombre", "Sin nombre")
                label_nombre = Gtk.Label(label=f"• {nombre_bd}")
                label_nombre.set_xalign(0.0)
                box_principal.append(label_nombre)

            box_principal.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

            # Título 2
            label_rutas = Gtk.Label()
            label_rutas.set_markup("<b>Ubicación de los respaldos:</b>")
            label_rutas.set_xalign(0.0)
            box_principal.append(label_rutas)

            # Lista de rutas
            for bd in self.Datos_Filtro_Get_SUP:
                id_get = bd.get("id", "Sin id")
                ruta = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_get, "ubicacion_respaldo")
                label_ruta = Gtk.Label(label=f"• {ruta}")
                label_ruta.set_xalign(0.0)
                box_principal.append(label_ruta)

            
            #Botones
            btn_cerrar_dialog = Gtk.Button(label="Cerrar ventana")
            btn_cerrar_dialog.connect("clicked", cerrar_dialogo)    
            
            content_area.append(scroll_Respald)
            content_area.append(btn_cerrar_dialog)
            spinner_respald.start()
            Vent_Respaldo_BD.show()

            # Esperar 3 segundos y comenzar respaldo paso a paso
            GLib.timeout_add_seconds(3, lambda: GLib.timeout_add_seconds(2, iniciar_respaldo_por_pasos))
        else:
            mostrar_vent_IEO(
                self.get_root(),
                "Error de respaldo",
                "No se han detectado bases de datos válidas para el respaldo.\nVerifique la lista filtrada.",
                Gtk.MessageType.ERROR,
                1,
                "Aceptar",
                None
            )

    def insertar_ubicacion_respaldo(self, id_get):
        """
        Inserta o actualiza la ubicación de respaldo predeterminada para una base de datos.

        - Obtiene la información de la base de datos usando su ID.
        - Si la base de datos es de tipo "sistema", calcula la ruta de respaldo predeterminada 
          (`BD/Resguardos_BD/<nombre>`) y la guarda en la propiedad `ubicacion_respaldo` 
          usando `self.BD_Informadora_Functions.modificar_UNA_propiedad`.

        Args:
            id_get (str): ID de la base de datos para la cual se configurará la ruta de respaldo.
        """
        dic_datos = self.BD_Informadora_Functions.obtener_registros_ID(id_get)

        obtn_dato_origen = dic_datos.get("origen", "Desconocido")
        obtn_dato_nombre = dic_datos.get("nombre", "Desconocido")

        if obtn_dato_origen.lower() == "sistema":

            Ruta_Preder_Respal = os.path.join(get_data_dir(),"BDs", "Resguardos_BD", obtn_dato_nombre)

            self.BD_Informadora_Functions.modificar_UNA_propiedad(obtn_dato_nombre,"ubicacion_respaldo",Ruta_Preder_Respal)

    def restaurar_bds_vent_SinInformadora (self, widget=None):
        """
        Muestra una ventana para restaurar bases de datos cuando la BD informadora no está disponible.

        Características principales:
        - Permite seleccionar una carpeta de respaldos que contenga subcarpetas con archivos `.sqlite` o `.sql`.
        - Analiza la estructura de la carpeta seleccionada y muestra los respaldos encontrados.
        - Permite al usuario elegir el tipo de archivo con el que trabajar (`.sqlite` o `.sql`).
        - Opción para eliminar los respaldos una vez finalizada la restauración.
        - Guarda la configuración de opciones en un archivo temporal para su uso posterior.
        - Realiza la restauración de manera controlada, mostrando mensajes de progreso y detalles 
          de cada acción en un `Gtk.TextView`.
        - Al finalizar, elimina todos los archivos temporales generados durante el proceso.

        Args:
            widget (Gtk.Widget, opcional): Widget que dispara la apertura de la ventana.
        """
        def mostrar_progreso():

            box_muestra_bds.remove(listbox_info_restauracion)
            spinner_restaur_info.start()

            box_muestra_bds.append(spinner_restaur_info)
            box_muestra_bds.append(label_mostrar_progreso)

            box_muestra_bds.append(textview_Datos_Restauracion_Mostr)

            textview_Datos_Restauracion_Mostr.get_buffer().set_text("-")

        def control_mensajes_infor(mensaje_label=None, mensaje_textview=None):
            """
            Controla y muestra mensajes de progreso.
            - Si mensaje_label es None, mantiene el texto anterior.
            - Si mensaje_textview es None, no cambia el contenido actual del TextView.
            - Si mensaje_textview tiene contenido, se añade al final del contenido actual.
            """

            # Actualizar el label solo si hay un nuevo mensaje
            if mensaje_label is not None:
                label_mostrar_progreso.set_text(mensaje_label)

            # Actualizar y acumular en el TextView solo si hay un nuevo mensaje
            if mensaje_textview is not None:
                buffer_tv = textview_Datos_Restauracion_Mostr.get_buffer()
                texto_actual = buffer_tv.get_text(buffer_tv.get_start_iter(), buffer_tv.get_end_iter(), True)

                nuevo_texto = texto_actual + mensaje_textview + "\n"
                buffer_tv.set_text(nuevo_texto)

        def abrir_respaldos_carpeta(self, widget=None):
            dialog = Gtk.FileChooserDialog(
                title="Seleccionar CARPETA de Respaldos",
                transient_for=self.get_root(),
                modal=True)

            dialog.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
            dialog.add_buttons(
                "Seleccionar", Gtk.ResponseType.ACCEPT,
                "Cancelar", Gtk.ResponseType.CANCEL)
            

            dialog.connect("response", on_response_dialog)
            dialog.present()

        def on_response_dialog(dialog, response_id):

            if response_id == Gtk.ResponseType.ACCEPT:
                
                ruta_base_get = dialog.get_file().get_path()

                lista_datos_restaur = []

                ruta_base = os.path.abspath(ruta_base_get)  # Asegura ruta absoluta


                for dirpath, dirnames, filenames in os.walk(ruta_base):
                    if dirpath == ruta_base:
                        # Solo se procesan las subcarpetas directas del directorio base
                        for subcarpeta in dirnames:
                            ruta_subcarpeta = os.path.join(dirpath, subcarpeta)

                            # Obtener archivos dentro de la subcarpeta (sin ir más profundo)
                            archivos = [
                                archivo for archivo in os.listdir(ruta_subcarpeta)
                                if os.path.isfile(os.path.join(ruta_subcarpeta, archivo))
                            ]

                            diccionario = {
                                "ruta_padre": ruta_base,
                                "nombre_carpeta": subcarpeta,
                                "archivos": archivos
                            }

                            lista_datos_restaur.append(diccionario)


                ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales", "Datos_dic_para_restar.tmp")

                #Solo se crea el tmp si hay algo en la lista
                if lista_datos_restaur:
                    with open(ruta_archivo_tmp, "w", encoding="utf-8") as archivo_tmp:
                        json.dump(lista_datos_restaur, archivo_tmp, indent=4, ensure_ascii=False)


                mostrar_datos_filtrados_restauracion(lista_datos_restaur, listbox_info_restauracion)

                dialog.destroy()
            

            else:
                dialog.destroy()

        def mostrar_datos_filtrados_restauracion(info_restauracion_get, listbox_wigdet):

            child = box_muestra_bds.get_first_child()
            while child:
                siguiente = child.get_next_sibling()
                box_muestra_bds.remove(child)
                child = siguiente

            datos_info_restauracion = info_restauracion_get

            if not datos_info_restauracion:
                label_ext = Gtk.Label(label="No se reconoce la estructura de la carpeta seleccionada.\nPor favor, vuelva a seleccionar una carpeta.")
                box_muestra_bds.append(label_ext)
                return

            for dic in datos_info_restauracion:
                box_prov = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                box_prov.get_style_context().add_class("boxs_filtradas")
                
                label_rutPadre = Gtk.Label(label=f"Carpeta de respaldo: {dic["ruta_padre"]}", xalign = 0.0)

                label_nombreCarpeta = Gtk.Label(label=f"Nombre carpeta individual: {dic["nombre_carpeta"]}", xalign= 0.0)

                list_datos_archivos = dic["archivos"]

                box_prov.append(label_rutPadre)
                box_prov.append(label_nombreCarpeta)

                for archivo in list_datos_archivos:

                    label_nombre_archivos = Gtk.Label(label=f"Archivo de respaldo encontrado: {archivo}", xalign= 0.0)
                    box_prov.append(label_nombre_archivos)
                

                row = Gtk.ListBoxRow()
                row.set_child(box_prov)
                listbox_wigdet.append(row)

            box_muestra_bds.append(listbox_wigdet)

            #Se activa el guardado de configuración una vez que se llenó la vista
            btn_guardar_configuracion.set_sensitive(True)

        def guardar_estados_checkbuttons(widget=None):
            dic_checkbutton = {

                "conSqlite": opc_conSqlite,
                "conSql": opc_conSql,
                "elimin_res": opc_elimin 
            }


            ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales", "Estado_checkbuttons.tmp")

            estado_dic = {}
            for nombre, checkbutton in dic_checkbutton.items():
                estado_dic[nombre] = checkbutton.get_active()

            with open(ruta_archivo_tmp, "w", encoding="utf-8") as file:
                json.dump(estado_dic, file, indent=4)


            btn_iniciar_restauracion.set_sensitive(True)

        def iniciar_restauracion(widget=None):

            #Iniciar el progreso (inserción del label correspondiente a ser manejado)
            mostrar_progreso()
            
            ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales", "Estado_checkbuttons.tmp")

            ruta_archivo_tmp2 = os.path.join(get_cache_dir(),"Archivos_Temporales","Datos_dic_para_bdRes_elimin.tmp")

            #Deshabilitación de botones y casillas
            btn_busqueda_carpeta.set_sensitive(False)
            btn_iniciar_restauracion.set_sensitive(False)
            btn_guardar_configuracion.set_sensitive(False)

            opc_conSqlite.set_sensitive(False)
            opc_conSql.set_sensitive(False)
            opc_elimin.set_sensitive(False)

            if os.path.exists(ruta_archivo_tmp):

                with open(ruta_archivo_tmp, "r", encoding="utf-8") as f:
                    datos = json.load(f)

            if datos["conSqlite"]:
                
                conElimin = datos["elimin_res"]
                self.restaurar_BD_SQlite(control_mensajes_infor, conElimin)

                if os.path.exists(ruta_archivo_tmp2):

                    control_mensajes_infor("Iniciando eliminación de archivos de respaldo", f"Leyendo archivo temporal: {ruta_archivo_tmp2}")
                    try:
                        with open(ruta_archivo_tmp2, "r", encoding="utf-8") as f:
                            datos2 = json.load(f)
                    except Exception as e:
                        control_mensajes_infor("Error de procesamiento", f"Archivo temporal faltante o dañado:{e} ")


                    control_mensajes_infor(None, "Lectura exitosa. Eliminando archivos...")

                    for bd in datos2:
                        control_mensajes_infor("Eliminando archivos de respaldo", f"Eliminando: {bd["ruta_respaldo_bd"]}")
                        error_elimin, estado_elimin = self.eliminar_arch_BDsRespaldo(bd["ruta_respaldo_bd"])

                        if error_elimin is None and estado_elimin:
                            control_mensajes_infor(None, "[OK] Eliminación de archivo exitosa.")
                        
                        elif error_elimin and not estado_elimin:
                            control_mensajes_infor(None, f"[ERROR] Eliminación de archivo fallida: {error_elimin}")
                        else:
                            control_mensajes_infor(None, f"[?] Proceso dudoso: {error_elimin}")


                control_mensajes_infor("Todos los procesos finalizados", None)               
                spinner_restaur_info.stop()
                btn_iniciar_nuevamente.set_sensitive(True)

            elif datos["conSql"]:
                conElimin = datos["elimin_res"]
                self.restaurar_BD_SQL(control_mensajes_infor, conElimin)

                if os.path.exists(ruta_archivo_tmp2):

                    control_mensajes_infor("Iniciando eliminación de archivos de respaldo", f"Leyendo archivo temporal: {ruta_archivo_tmp2}")
                    try:
                        with open(ruta_archivo_tmp2, "r", encoding="utf-8") as f:
                            datos2 = json.load(f)
                    except Exception as e:
                        control_mensajes_infor("Error de procesamiento", f"Archivo temporal faltante o dañado:{e} ")


                    control_mensajes_infor(None, "Lectura exitosa. Eliminando archivos...")

                    for bd in datos2:
                        control_mensajes_infor("Eliminando archivos de respaldo", f"Eliminando: {bd["ruta_respaldo_bd"]}")
                        error_elimin, estado_elimin = self.eliminar_arch_BDsRespaldo(bd["ruta_respaldo_bd"])

                        if error_elimin is None and estado_elimin:
                            control_mensajes_infor(None, "[OK] Eliminación de archivo exitosa.")
                        
                        elif error_elimin and not estado_elimin:
                            control_mensajes_infor(None, f"[ERROR] Eliminación de archivo fallida: {error_elimin}")
                        else:
                            control_mensajes_infor(None, f"[?] Proceso dudoso: {error_elimin}")

            #Eliminación de archivos temporales
            control_mensajes_infor("Finalizando procesos", "Iniciando eliminación de archivos temporales (.tmp)...")
            nombres_archivos_tmp = [
                "Datos_dic_para_bdRes_elimin.tmp",
                "Datos_dic_para_restar.tmp",
                "Estado_checkbuttons.tmp"
            ]

            for nombre in nombres_archivos_tmp:

                ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales", nombre)

                control_mensajes_infor(None, f"Eliminando <<{nombre}>> en <<{ruta_archivo_tmp}>>...")
                try:
                    os.remove(ruta_archivo_tmp)
                    control_mensajes_infor(None, f"[OK] Eliminación exitosa del archivo <<{nombre}>>")
                except Exception as e:
                    control_mensajes_infor(None, f"[ERROR] Eliminación de <<{nombre}>> fracasada: {e}")


            control_mensajes_infor("Procesos finalizados", "Todos los procesos finalizados.")
            spinner_restaur_info.stop()
            btn_iniciar_restauracion.set_sensitive(True)

        Vent_Restaur_BDs = Gtk.Dialog(
                title="Respaldo de Bases de Datos",
                transient_for=self.get_root(),
                modal=True,
            )


        Vent_Restaur_BDs.set_default_size(1100, 450)
        content_area = Vent_Restaur_BDs.get_content_area()

        listbox_info_restauracion=Gtk.ListBox()
        listbox_info_restauracion.set_selection_mode(Gtk.SelectionMode.SINGLE)

        spinner_restaur_info = Gtk.Spinner()

        label_mostrar_progreso = Gtk.Label(label="Iniciando restauración...")
        label_mostrar_progreso.set_wrap(True)

        box_pr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        box_sg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        box_muestra_bds = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        box_opciones_ejecucion = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5, vexpand=True)

        box_botones_ejecucion = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        scroll_muestrabds = Gtk.ScrolledWindow()
        scroll_muestrabds.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_muestrabds.set_child(box_muestra_bds)
        scroll_muestrabds.set_vexpand(True)
        scroll_muestrabds.set_hexpand(True)

        btn_busqueda_carpeta = Gtk.Button(label="Buscar carpeta de respaldo")
        btn_busqueda_carpeta.set_tooltip_text("Busqueda y selección de una carpeta que contenga varios archivos de respaldo")
        btn_busqueda_carpeta.connect("clicked", abrir_respaldos_carpeta)

        textview_Datos_Restauracion_Mostr = Gtk.TextView(vexpand=True, hexpand=True)
        textview_Datos_Restauracion_Mostr.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview_Datos_Restauracion_Mostr.set_editable(False)
        textview_Datos_Restauracion_Mostr.set_focusable(False)

        ruta_archivo_explict_1 = os.path.join(get_recursos_dir(), "Texto", "explicacion_restauracion_1.txt")


        try:
            with open(ruta_archivo_explict_1) as txt1:

                contenido_txt1 = txt1.read()
        except Exception as e:
            contenido_txt1 = "Archivo de explicacion no encontrado\nExplicación de emergencia: use archivos .sqlite y búsqueda por carpeta"


        textview_Datos_Restauracion_Mostr.get_buffer().set_text(contenido_txt1)

        label_ajustes1 = Gtk.Label(label="Seleccione un tipo de archivo con el que trabajar:")
        
        opc_conSqlite = Gtk.CheckButton.new_with_label(".sqlite")
        opc_conSqlite.set_group(None)#Como es el "grupo", se dice "None"
        opc_conSqlite.set_tooltip_text("Trabajar con archivos binarios: .sqlite, etc (Recomendado)")
        opc_conSqlite.set_active(True)

        opc_conSql = Gtk.CheckButton.new_with_label(".sql")
        opc_conSql.set_group(opc_conSqlite)#Establecemos como el grupo "a incorporar" al sqlite
        opc_conSql.set_tooltip_text("Trabajar con archivo de instrucciones: .sql (solo si el archivo binario es inaccesible)") 

        label_ajustes2 = Gtk.Label(label="Opciones Generales")

        opc_elimin = Gtk.CheckButton(label="Eliminar archivos de respaldo\nluego de finalizada la restauración")
        opc_elimin.set_tooltip_text("Elimina la carpeta individual de respaldos (archivo binario (.sqlite) y de instrucciones (.sql))")

        btn_iniciar_restauracion = Gtk.Button(label="Iniciar restauracion")
        btn_iniciar_restauracion.set_sensitive(False)
        btn_iniciar_restauracion.connect("clicked", iniciar_restauracion)

        btn_guardar_configuracion = Gtk.Button(label="Guardar Configuración")
        btn_guardar_configuracion.set_tooltip_text(
            "Guarda la selección de las casillas y habilita el boton para iniciar la restauración.")
        btn_guardar_configuracion.set_sensitive(False)
        btn_guardar_configuracion.connect("clicked", guardar_estados_checkbuttons)

        btn_iniciar_nuevamente = Gtk.Button(label="Iniciar nuevamente")
        btn_iniciar_nuevamente.set_sensitive(False)

        box_muestra_bds.append(textview_Datos_Restauracion_Mostr)

        box_opciones_ejecucion.append(label_ajustes1)
        box_opciones_ejecucion.append(opc_conSqlite)
        box_opciones_ejecucion.append(opc_conSql)
        box_opciones_ejecucion.append(label_ajustes2)
        box_opciones_ejecucion.append(opc_elimin)

        box_botones_ejecucion.append(btn_busqueda_carpeta)
        box_botones_ejecucion.append(btn_iniciar_restauracion)
        box_botones_ejecucion.append(btn_guardar_configuracion)
        box_botones_ejecucion.append(btn_iniciar_nuevamente)

        box_sg.append(box_opciones_ejecucion)
        box_sg.append(box_botones_ejecucion)

        box_pr.append(scroll_muestrabds)
        box_pr.append(box_sg)


        content_area.append(box_pr)


        Vent_Restaur_BDs.show()

    def restaurar_BD_SQlite(self, control_mensajes_infor_F, conElimin):
        """
        Restaura bases de datos SQLite desde respaldos previamente seleccionados.

        - Lee el archivo temporal `Datos_dic_para_restar.tmp` para obtener la lista de carpetas de respaldo.
        - Filtra y selecciona el archivo `.sqlite` más reciente de cada carpeta.
        - Llama a `self.BD_Utilidades_Generales.restaurar_sqlite()` para realizar la restauración individual.
        - Registra mensajes de progreso y estado usando la función `control_mensajes_infor_F`.
        - Si `conElimin` es True, genera el archivo temporal `Datos_dic_para_bdRes_elimin.tmp` 
          con las rutas de respaldo restauradas para su eliminación posterior.

        Args:
            control_mensajes_infor_F (function): Función para mostrar mensajes de progreso y resultados.
            conElimin (bool): Si True, prepara listado de respaldos para eliminar luego de la restauración.
        """
        control_mensajes_infor_F("Iniciando restauración SQLite...", None)

        ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales", "Datos_dic_para_restar.tmp")
        control_mensajes_infor_F(None, f"Buscando archivo temporal en: {ruta_archivo_tmp}")

        if not os.path.exists(ruta_archivo_tmp):
            control_mensajes_infor_F("Error: archivo temporal no encontrado", "Cancelando restauración")
            return

        control_mensajes_infor_F(None, "Archivo temporal encontrado. Procesando datos...")

        with open(ruta_archivo_tmp, "r", encoding="utf-8") as f:
            datos = json.load(f)

        datos_seleccionados_lista = []

        control_mensajes_infor_F("Analizando datos encontrados", "Filtrando y localizando archivos .sqlite más recientes...")

        for dic in datos:
            nombre_bd = dic.get("nombre_carpeta")
            archivos = dic.get("archivos", [])
            
            if not nombre_bd or not archivos:
                control_mensajes_infor_F(None, f"[AVISO] Saltando entrada sin nombre o sin archivos.")
                continue

            id_bd = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_bd)
            ruta_origen = self.BD_Informadora_Functions.Obtener_Ruta_BD(nombre_BD_get=nombre_bd)
            ruta_respaldo = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_bd, "ubicacion_respaldo")

            archivos_sqlite = [a for a in archivos if a.endswith(".sqlite")]
            archivo_mas_reciente = obtener_archivo_mas_reciente_ResplArch(archivos_sqlite)

            if not archivo_mas_reciente:
                control_mensajes_infor_F(None, f"[ERROR] No se encontró archivo .sqlite en {nombre_bd}")
                continue

            ruta_respaldo_absoluta = os.path.join(ruta_respaldo, archivo_mas_reciente)

            datos_seleccionados_lista.append({
                "id_bd": id_bd,
                "nombre_bd": nombre_bd,
                "ruta_origen_bd": ruta_origen,
                "ruta_respaldo_bd": ruta_respaldo_absoluta
            })

            control_mensajes_infor_F(None, f"✓ Seleccionado: {nombre_bd} → {archivo_mas_reciente}")

        control_mensajes_infor_F("Restaurando archivos seleccionados...", "Comenzando proceso de restauración individual...")

        for bd in datos_seleccionados_lista:
            control_mensajes_infor_F(None, f"→ Restaurando: {bd['nombre_bd']}")
            
            error, estado = self.BD_Utilidades_Generales.restaurar_sqlite(
                bd["ruta_origen_bd"],
                bd["ruta_respaldo_bd"]
            )

            if error is None and estado:
                control_mensajes_infor_F(None, f"[OK] Restauración exitosa: {bd['nombre_bd']}")
            elif error and not estado:
                control_mensajes_infor_F(None, f"[ERROR] Falló la restauración de '{bd['nombre_bd']}': {error}")
            elif not estado:
                control_mensajes_infor_F(None, f"[ERROR] Estado inválido para '{bd['nombre_bd']}'")
            elif error:
                control_mensajes_infor_F(None, f"[ADVERTENCIA] Restauración con errores en '{bd['nombre_bd']}': {error}")

        control_mensajes_infor_F("Proceso finalizado", "Todas las bases de datos procesadas.")

        if conElimin:
            ruta_archivo_tmp2 = os.path.join(get_cache_dir(),"Archivos_Temporales","Datos_dic_para_bdRes_elimin.tmp")

            control_mensajes_infor_F(None, "Creando archivo tmp para eliminaciones...")

            try:
                with open(ruta_archivo_tmp2, "w", encoding="utf-8") as file:
                        json.dump(datos_seleccionados_lista, file, indent=4)
            
            except Exception as e:
                control_mensajes_infor_F(None, f"Error al crear archivo temporal: {e}")

            control_mensajes_infor_F(None, "Archivo temporal creado.")

    def restaurar_BD_SQL(self, control_mensajes_infor_F, conElimin):
        """
        Restaura bases de datos ejecutando archivos de instrucciones `.sql`.

        - Lee el archivo temporal `Datos_dic_para_restar.tmp` para obtener la lista de carpetas de respaldo.
        - Filtra y selecciona el archivo `.sql` más reciente de cada carpeta.
        - Llama a `self.BD_Utilidades_Generales.restaurar_desde_sql()` para procesar las instrucciones.
        - Registra mensajes de progreso y estado usando la función `control_mensajes_infor_F`.
        - Si `conElimin` es True, genera el archivo temporal `Datos_dic_para_bdRes_elimin.tmp` 
          con las rutas de respaldo restauradas para su eliminación posterior.

        Args:
            control_mensajes_infor_F (function): Función para mostrar mensajes de progreso y resultados.
            conElimin (bool): Si True, prepara listado de respaldos para eliminar luego de la restauración.
        """
        control_mensajes_infor_F("Iniciando restauración desde archivos .sql...", None)

        ruta_archivo_tmp = os.path.join(get_cache_dir(),"Archivos_Temporales","Datos_dic_para_restar.tmp")
        control_mensajes_infor_F(None, f"Buscando archivo temporal en: {ruta_archivo_tmp}")

        if not os.path.exists(ruta_archivo_tmp):
            control_mensajes_infor_F("Error: archivo temporal no encontrado", "Cancelando restauración")
            return

        control_mensajes_infor_F(None, "Archivo temporal encontrado. Procesando datos...")

        with open(ruta_archivo_tmp, "r", encoding="utf-8") as f:
            datos = json.load(f)

        datos_seleccionados_lista = []

        control_mensajes_infor_F("Analizando datos encontrados", "Filtrando y localizando archivos .sql más recientes...")

        for dic in datos:
            nombre_bd = dic.get("nombre_carpeta")
            archivos = dic.get("archivos", [])
            
            if not nombre_bd or not archivos:
                control_mensajes_infor_F(None, f"[AVISO] Entrada inválida sin nombre o archivos. Saltando...")
                continue

            id_bd = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_bd)
            ruta_origen = self.BD_Informadora_Functions.Obtener_Ruta_BD(nombre_BD_get=nombre_bd)
            ruta_respaldo = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_bd, "ubicacion_respaldo")

            archivos_sql = [a for a in archivos if a.endswith(".sql")]
            archivo_mas_reciente = obtener_archivo_mas_reciente_ResplArch(archivos_sql)

            if not archivo_mas_reciente:
                control_mensajes_infor_F(None, f"[ERROR] No se encontró archivo .sql válido en {nombre_bd}")
                continue

            ruta_respaldo_absoluta = os.path.join(ruta_respaldo, archivo_mas_reciente)

            datos_seleccionados_lista.append({
                "id_bd": id_bd,
                "nombre_bd": nombre_bd,
                "ruta_origen_bd": ruta_origen,
                "ruta_respaldo_bd": ruta_respaldo_absoluta
            })

            control_mensajes_infor_F(None, f"✓ Seleccionado: {nombre_bd} → {archivo_mas_reciente}")

        control_mensajes_infor_F("Comenzando restauración individual de archivos SQL...", None)

        for bd in datos_seleccionados_lista:
            control_mensajes_infor_F(None, f"→ Restaurando: {bd['nombre_bd']}")

            error_restau, estado_restaur = self.BD_Utilidades_Generales.restaurar_desde_sql(
                bd["ruta_respaldo_bd"],
                bd["ruta_origen_bd"]
            )


            if error_restau is None and estado_restaur:
                control_mensajes_infor_F(None, f"[OK] Restauración exitosa: {bd['nombre_bd']}")
            elif error_restau and not estado_restaur:
                control_mensajes_infor_F(None, f"[ERROR] Falló la restauración de '{bd['nombre_bd']}': {error_restau}")
            elif not estado_restaur:
                control_mensajes_infor_F(None, f"[ERROR] Estado inválido para '{bd['nombre_bd']}'")
            elif error_restau:
                control_mensajes_infor_F(None, f"[ADVERTENCIA] Restauración con errores en '{bd['nombre_bd']}': {error_restau}")

        control_mensajes_infor_F("Restauración completada", "Todas las instrucciones .sql han sido procesadas.")


        if conElimin:
            ruta_archivo_tmp2 = os.path.join(get_cache_dir(),"Archivos_Temporales","Datos_dic_para_bdRes_elimin.tmp")

            control_mensajes_infor_F(None, "Creando archivo tmp para eliminaciones...")

            try:
                with open(ruta_archivo_tmp2, "w", encoding="utf-8") as file:
                        json.dump(datos_seleccionados_lista, file, indent=4)
            
            except Exception as e:
                control_mensajes_infor_F(None, f"Error al crear archivo temporal: {e}")

            control_mensajes_infor_F(None, "Archivo temporal creado.")

    def eliminar_arch_BDsRespaldo(self, ruta_bd_res_a_eliminar):
        """
        Elimina un archivo de respaldo de base de datos del sistema de archivos.

        - Verifica que la ruta exista.
        - Intenta eliminar el archivo con `os.remove()`.
        - Devuelve el estado y un posible mensaje de error.

        Args:
            ruta_bd_res_a_eliminar (str): Ruta absoluta del archivo de respaldo a eliminar.

        Returns:
            tuple:
                - error_elimin (str | None): Mensaje de error si falla, None si no hubo error.
                - estado_elimin (bool): True si se eliminó correctamente, False en caso contrario.
        """
        error_elimin = None 
        estado_elimin = False

        if not os.path.exists(ruta_bd_res_a_eliminar):
            error_elimin = f"El archivo a eliminar no existe en {ruta_bd_res_a_eliminar}"
            estado_elimin = False

            return error_elimin, estado_elimin

        try:
            os.remove(ruta_bd_res_a_eliminar)
            estado_elimin = True

            return error_elimin, estado_elimin

        except Exception as e:
            error_elimin = f"Error en la eliminación del archivo: {e}"
            estado_elimin=False

            return error_elimin, estado_elimin

    def vent_General_OpcIndividual(self, funcion_a_ejecutar, etiqueta_boton="Iniciar proceso", nombre_tmp_Archexplic="explicacion_0.txt"):
        """
        Crea una ventana de diálogo genérica para ejecutar procesos relacionados con bases de datos.

        - Muestra un área de texto con una explicación cargada desde un archivo.
        - Incluye un botón de acción que ejecuta la función `funcion_a_ejecutar` cuando se presiona.
        - Proporciona un sistema interno (`control_mensajes_infor_C`) para actualizar un label y un textview con mensajes de estado.

        Args:
            funcion_a_ejecutar (callable): Función a ejecutar al presionar el botón principal.
                Recibe como parámetros:
                - El botón que lo activó.
                - La función `control_mensajes_infor_C`.
                - El `Gtk.TextView` para mensajes.
                - El `Gtk.Spinner` de carga.
                - La ventana de diálogo.
            etiqueta_boton (str, opcional): Texto mostrado en el botón de acción.
            nombre_tmp_Archexplic (str, opcional): Nombre del archivo de texto que contiene la explicación mostrada en el `TextView`.
        """

        def control_mensajes_infor_C(mensaje_label=None, mensaje_textview=None):
            if mensaje_label is not None:
                label_estado1.set_text(mensaje_label)

            if mensaje_textview is not None:
                buffer_tv = textview_Datos_Infor_S.get_buffer()
                texto_actual = buffer_tv.get_text(buffer_tv.get_start_iter(), buffer_tv.get_end_iter(), True)
                nuevo_texto = texto_actual + mensaje_textview + "\n"
                buffer_tv.set_text(nuevo_texto)

        # Crear ventana
        vent = Gtk.Dialog(
            title="Procesos con base de datos",
            transient_for=self.get_root(),
            modal=True,
        )
        vent.set_default_size(600, 450)
        content_area = vent.get_content_area()

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        spiner_recons = Gtk.Spinner()
        label_estado1 = Gtk.Label(label="Esperando instrucciones...")

        textview_Datos_Infor_S = Gtk.TextView(vexpand=True, hexpand=True)
        textview_Datos_Infor_S.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview_Datos_Infor_S.set_editable(False)
        textview_Datos_Infor_S.set_focusable(False)

        scroll_infor = Gtk.ScrolledWindow()
        scroll_infor.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_infor.set_child(textview_Datos_Infor_S)
        scroll_infor.set_vexpand(True)
        scroll_infor.set_hexpand(True)

        ruta_archivo_explict = os.path.join(get_recursos_dir(), "Texto", nombre_tmp_Archexplic)

        try:
            with open(ruta_archivo_explict) as txt:
                contenido_txt = txt.read()
        except Exception:
            contenido_txt = "Archivo de explicación no encontrado."

        textview_Datos_Infor_S.get_buffer().set_text(contenido_txt)

        # Botón de acción
        btn_accion = Gtk.Button(label=etiqueta_boton)
        btn_accion.connect("clicked", funcion_a_ejecutar, control_mensajes_infor_C, textview_Datos_Infor_S, spiner_recons, vent)

        box_pr.append(spiner_recons)
        box_pr.append(label_estado1)
        box_pr.append(scroll_infor)
        box_pr.append(btn_accion)

        content_area.append(box_pr)
        vent.show()

    def reconstuir_BD_Individual(self, boton, control_mensajes_infor_C, textview, spinner, ventana):
        """
        Reconstruye una base de datos individual seleccionada.

        - Elimina el archivo actual de la base de datos.
        - Crea un nuevo archivo usando un constructor externo (`crear_BDs_Constructor`).
        - Reinicializa la base de datos internamente llamando a su objeto correspondiente.
        - Actualiza el registro en la base de datos informadora y valida rutas.
        - Crea un archivo temporal de estado (`estado_reinicio.tmp`).

        Args:
            boton (Gtk.Button): Botón que inició la acción.
            control_mensajes_infor_C (function): Función para mostrar mensajes de estado y progreso.
            textview (Gtk.TextView): Área de texto para mostrar mensajes detallados.
            spinner (Gtk.Spinner): Indicador de proceso en ejecución.
            ventana (Gtk.Dialog): Ventana que contiene la interfaz de la acción.
        """

        spinner.start()
        boton.set_sensitive(False)
        textview.get_buffer().set_text("")

        control_mensajes_infor_C("Iniciando reconstrucción", "Preparando procesos...")

        nombre_get = self.Entry_NombreBD.get_text()
        control_mensajes_infor_C(None, f"Obteniendo ID de la base de datos <<{nombre_get}>>")

        id_get_SUP = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_get)
        if not id_get_SUP:
            control_mensajes_infor_C("Error", f"[ERROR] No se encontró ID para la base de datos <<{nombre_get}>>.")
            spinner.stop()
            boton.set_sensitive(True)
            return

        # Eliminar archivo base de datos
        control_mensajes_infor_C("Eliminando archivo de base de datos", f"Buscando ruta del archivo con ID: <<{id_get_SUP}>>")
        ruta_bd_elimin = self.BD_Informadora_Functions.Obtener_Ruta_BD(id_get=id_get_SUP)

        if not ruta_bd_elimin or not os.path.isfile(ruta_bd_elimin):
            control_mensajes_infor_C("Advertencia", f"[AVISO] No se encontró archivo en la ruta: <<{ruta_bd_elimin}>>. Se continuará con la reconstrucción.")
        else:
            try:
                os.remove(ruta_bd_elimin)
                control_mensajes_infor_C(None, f"[OK] Archivo eliminado correctamente: <<{ruta_bd_elimin}>>")
            except Exception as e:
                control_mensajes_infor_C("Error", f"[ERROR] No se pudo eliminar el archivo: <<{e}>>")
                spinner.stop()
                boton.set_sensitive(True)
                return

        # Reconstruir archivo con el constructor externo
        nombre_bd = self.BD_Informadora_Functions.obtener_UNA_propiedad_ID(id_get_SUP, "nombre")
        if not nombre_bd:
            control_mensajes_infor_C("Error", f"[ERROR] No se encontró el nombre de la base de datos con ID <<{id_get_SUP}>>.")
            spinner.stop()
            boton.set_sensitive(True)
            return

        control_mensajes_infor_C("Reconstruyendo base de datos", f"Reconstruyendo archivo para <<{nombre_bd}>>...")
        estado, error = crear_BDs_Constructor(bases_a_construir=[nombre_bd])

        if estado:
            control_mensajes_infor_C(None, f"[OK] Reconstrucción completada: <<{nombre_bd}>>")
        else:
            control_mensajes_infor_C("Error", f"[ERROR] Falló la reconstrucción: {error}")
            spinner.stop()
            boton.set_sensitive(True)
            return

        # Reinicialización mediante objeto correspondiente
        control_mensajes_infor_C("Reinicialización", f"Inicializando <<{nombre_bd}>> internamente...")
        objeto_bd = getattr(self, f"{nombre_bd}_Functions", None)

        if objeto_bd:
            estado_reconstr, error_reconstr = objeto_bd.reconstruir_base_de_datos_completa()
            if estado_reconstr:
                control_mensajes_infor_C(None, f"[OK] Reinicialización exitosa: <<{nombre_bd}>>")
            else:
                control_mensajes_infor_C("Advertencia", f"[ERROR] Reinicialización fallida: {error_reconstr}")
        else:
            control_mensajes_infor_C("Error", f"[ERROR] No se encontró el objeto: <<{nombre_bd}_Functions>>")

        # Eliminar e insertar registro en BD Informadora
        control_mensajes_infor_C("Reinserción", f"Eliminando e insertando registro de <<{nombre_bd}>> en BD Informadora...")
        self.BD_Informadora_Functions.eliminar_registros(id_get_SUP)
        self.BD_Informadora_Functions.asegurar_bd_registro_preder_INDIVIDUAL(nombre_bd)
        control_mensajes_infor_C(None, "[OK] Registro reiniciado correctamente.")

        # Validar rutas
        control_mensajes_infor_C("Validando rutas", f"Verificando existencia y ruta de <<{nombre_bd}>>...")
        id_nuevo = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_bd)
        self.insertar_ubicacion_respaldo(id_nuevo)

        existe = self.verificar_BD_Existencia(ruta_bd_elimin)
        if existe:
            self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_bd, "estado", True)
            self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_bd, "ubicacion", ruta_bd_elimin)
            control_mensajes_infor_C(None, "[OK] Validación final completada.")
        else:
            control_mensajes_infor_C("Advertencia", "[AVISO] El archivo de la base de datos no existe tras la reconstrucción.")

        # Actualizar vista y crear archivo tmp
        control_mensajes_infor_C("Finalizando", "Actualizando vista y creando archivo de reinicio...")
        self.cargar_datos_seleccionados()

        estado_tmp, error_tmp = guardar_archivo_tmp("estado_reinicio.tmp", "reiniciado")
        if estado_tmp:
            control_mensajes_infor_C(None, "[OK] Archivo tmp creado correctamente.")
        else:
            control_mensajes_infor_C("Error", f"[ERROR] No se pudo crear archivo tmp: {error_tmp}")

        spinner.stop()
        boton.set_sensitive(True)
        control_mensajes_infor_C("Proceso finalizado", "Es necesario reiniciar el programa para aplicar los cambios.")

    def respaldar_BD_Individual(self, boton, control_mensajes_infor_C, textview, spinner, ventana):
        """
        Crea un respaldo de una base de datos individual en formato `.sqlite` y `.sql`.

        - Obtiene datos de nombre, origen, ubicación y carpeta de respaldo desde la interfaz.
        - Si el origen es "sistema", ejecuta la función de respaldo de `BD_Utilidades_Generales`.
        - Guarda los archivos de respaldo en la ubicación especificada.
        - Muestra mensajes de estado y progreso durante el proceso.

        Args:
            boton (Gtk.Button): Botón que inició la acción.
            control_mensajes_infor_C (function): Función para mostrar mensajes de estado y progreso.
            textview (Gtk.TextView): Área de texto para mostrar mensajes detallados.
            spinner (Gtk.Spinner): Indicador de proceso en ejecución.
            ventana (Gtk.Dialog): Ventana que contiene la interfaz de la acción.
        """
        spinner.start()
        boton.set_sensitive(False)
        textview.get_buffer().set_text("")

        #Recuperación de datos
        control_mensajes_infor_C("Iniciando respaldo", "Obteniendo y procesando datos importantes: nombre, origen e ubicación...")
        nombre_bd = self.Entry_NombreBD.get_text()
        origen_bd = self.Entry_orgienBD.get_text()
        ubicacion_arch = self.Entry_ubicacionBD.get_text()

        #Se extrae la "última parte" de la ruta para evitar "carpetas dentro de carpetas"
        #Ya que la función de respaldo de utilidades ya genera la carpeta individual.
        ubicacion_respald = os.path.dirname(self.Entry_ubicacionResBD.get_text())

        if origen_bd.lower() == "sistema": 
            control_mensajes_infor_C(
                "Respaldando base de datos",
                f"Creando archivos de respaldo de <<{nombre_bd}>> en <<{ubicacion_respald}>>...")
            self.BD_Utilidades_Generales.respaldar_base_de_datos(
                nombre_bd,
                origen_bd,
                ubicacion_respald,
                ubicacion_arch)
            
            control_mensajes_infor_C(
                "Respaldo finalizado con exito",
                f"[OK] Los archivos de respaldo (.sqlite y .sql) para <<{nombre_bd}>> fueron creados con exito en <<{ubicacion_respald}>>...")

            control_mensajes_infor_C(None,f"Finalizando procesos para <<{nombre_bd}>>...")
            spinner.stop()
            boton.set_sensitive(True)

            control_mensajes_infor_C(None, "Todos los procesos terminados.")

        else:
            control_mensajes_infor_C(
                "Error de permisos",
                f"[ERROR] Se ha detectado un origen incorrecto para las base de datos <<{nombre_bd}>>: {origen_bd}. SOLO SE PERMITEN BASES DE DATOS DEL <<SISTEMA>>.")

    def restaurar_BD_Individual(self, boton, control_mensajes_infor_C, textview, spinner, ventana):
        """
        Restaura una base de datos individual desde un respaldo.

        - Intenta primero restaurar usando un archivo `.sqlite` más reciente encontrado en la carpeta de respaldo.
        - Si no se encuentra `.sqlite`, busca un archivo `.sql` y lo utiliza para la restauración.
        - Muestra mensajes de estado y progreso durante el proceso.
        - Finaliza el proceso desactivando el spinner y reactivando el botón.

        Args:
            boton (Gtk.Button): Botón que inició la acción.
            control_mensajes_infor_C (function): Función para mostrar mensajes de estado y progreso.
            textview (Gtk.TextView): Área de texto para mostrar mensajes detallados.
            spinner (Gtk.Spinner): Indicador de proceso en ejecución.
            ventana (Gtk.Dialog): Ventana que contiene la interfaz de la acción.
        """
        def finalizar_procesos():
            control_mensajes_infor_C("Finalizando procesos", "Finalizando procesos remanentes...")
            spinner.stop()
            boton.set_sensitive(True)
            control_mensajes_infor_C("Proceso de restauración finalizado", "Se ha detenido todos los procesos. Se recomienda reiniciar el programa.")

        # Inicio del proceso
        spinner.start()
        boton.set_sensitive(False)
        textview.get_buffer().set_text("")

        control_mensajes_infor_C("Iniciando restauración", "Obteniendo y procesando datos importantes...")

        nombre_bd = self.Entry_NombreBD.get_text()
        origen_bd = self.Entry_orgienBD.get_text()
        ubicacion_arch = self.Entry_ubicacionBD.get_text()
        ubicacion_respald = self.Entry_ubicacionResBD.get_text()

        if not os.path.isdir(ubicacion_respald):
            control_mensajes_infor_C(
                "Error de procesamiento",
                f"[ERROR] La ruta <<{ubicacion_respald}>> no es correcta o no existe.")
            return

        archivos_get = []

        # Restauración por .sqlite
        control_mensajes_infor_C(
            "Restaurando por .sqlite",
            f"Buscando archivo .sqlite en <<{ubicacion_respald}>> de la base de datos <<{nombre_bd}>>...")

        for archivo in os.listdir(ubicacion_respald):
            ruta_archivo = os.path.join(ubicacion_respald, archivo)

            if archivo.endswith(".sqlite") and os.path.isfile(ruta_archivo):
                control_mensajes_infor_C(None, f"Encontrado archivo: {ruta_archivo}")
                archivos_get.append(archivo)

        if archivos_get:
            control_mensajes_infor_C(None, "Filtrando archivos al más reciente...")
            archivo_masReciente = obtener_archivo_mas_reciente_ResplArch(archivos_get)

            control_mensajes_infor_C(None, f"Archivo filtrado como el más reciente: {archivo_masReciente}")
            archivo_sqliteRes = os.path.join(ubicacion_respald, archivo_masReciente)

            control_mensajes_infor_C(None, f"Comenzando restauración para <<{nombre_bd}>>...")
            control_mensajes_infor_C(None, f"Restaurando desde <<{archivo_sqliteRes}>> a <<{ubicacion_arch}>>...")

            error_restau, estado_restaur = self.BD_Utilidades_Generales.restaurar_sqlite(ubicacion_arch, archivo_sqliteRes)

            if error_restau is None and estado_restaur:
                control_mensajes_infor_C("Restauración por sqlite exitosa", f"[OK] Restauración exitosa: {nombre_bd}")
            elif error_restau and not estado_restaur:
                control_mensajes_infor_C("Restauración por sqlite fracasada", f"[ERROR] Falló la restauración de {nombre_bd}: {error_restau}")
            elif not estado_restaur:
                control_mensajes_infor_C("Error inesperado", f"[ERROR] Estado inválido para {nombre_bd}")
            elif error_restau:
                control_mensajes_infor_C("Error inesperado", f"[ADVERTENCIA] Restauración con errores en {nombre_bd}: {error_restau}")

            finalizar_procesos()
            return  # ← Importante: salir si ya se restauró correctamente por .sqlite

        # Si no hay .sqlite → Restauración por .sql
        control_mensajes_infor_C(None, f"No se encontraron archivos .sqlite en la ruta: {ubicacion_respald}")
        control_mensajes_infor_C("Iniciando restauración por .sql", "Buscando archivo .sql de respaldo...")

        archivos_get_sql = []
        for archivo in os.listdir(ubicacion_respald):
            ruta_archivo = os.path.join(ubicacion_respald, archivo)

            if archivo.endswith(".sql") and os.path.isfile(ruta_archivo):
                control_mensajes_infor_C(None, f"Encontrado archivo: {ruta_archivo}")
                archivos_get_sql.append(archivo)

        if not archivos_get_sql:
            control_mensajes_infor_C("Restauración fallida", "[ERROR] No se encontraron archivos .sql de respaldo.")
            return

        control_mensajes_infor_C(None, "Filtrando archivos .sql al más reciente...")
        archivoSQL_masReciente = obtener_archivo_mas_reciente_ResplArch(archivos_get_sql)

        control_mensajes_infor_C(None, f"Archivo filtrado como el más reciente: {archivoSQL_masReciente}")
        archivo_SQLRes = os.path.join(ubicacion_respald, archivoSQL_masReciente)

        control_mensajes_infor_C(None, f"Comenzando restauración para <<{nombre_bd}>>...")
        control_mensajes_infor_C(None, f"Restaurando desde <<{archivo_SQLRes}>> a <<{ubicacion_arch}>>...")

        error, estado = self.BD_Utilidades_Generales.restaurar_desde_sql(archivo_SQLRes, ubicacion_arch)

        if error is None and estado:
            control_mensajes_infor_C("Restauración por sql exitosa", f"[OK] Restauración exitosa: {nombre_bd}")
        elif error and not estado:
            control_mensajes_infor_C("Restauración por sql fracasada", f"[ERROR] Falló la restauración de {nombre_bd}: {error}")
        elif not estado:
            control_mensajes_infor_C("Error inesperado", f"[ERROR] Estado inválido para {nombre_bd}")
        elif error:
            control_mensajes_infor_C("Error inesperado", f"[ADVERTENCIA] Restauración con errores en {nombre_bd}: {error}")
        finalizar_procesos()

    def Verificar_Rutaexistencia_BD_Invidiual(self, boton, control_mensajes_infor_C, textview, spinner, ventana):
        """
        Verifica la existencia y rutas de una base de datos individual.

        - Comprueba si la ruta principal del archivo `.sqlite` existe.
        - Cambia el estado de la base de datos a `True` (existente) o `False` (inexistente) en la base de datos informadora.
        - Verifica la ruta de respaldo y la actualiza con valores predeterminados si es "sin comprobar".
        - Muestra mensajes de estado y progreso durante todo el proceso.

        Args:
            boton (Gtk.Button): Botón que inició la acción.
            control_mensajes_infor_C (function): Función para mostrar mensajes de estado y progreso.
            textview (Gtk.TextView): Área de texto para mostrar mensajes detallados.
            spinner (Gtk.Spinner): Indicador de proceso en ejecución.
            ventana (Gtk.Dialog): Ventana que contiene la interfaz de la acción.
        """

        spinner.start()
        boton.set_sensitive(False)
        textview.get_buffer().set_text("")

        control_mensajes_infor_C("Iniciando verificación", "Iniciando. Recolectando y procesando datos importantes...")
        nombre_bd = self.Entry_NombreBD.get_text()
        ubicacion_arch = self.Entry_ubicacionBD.get_text()
        ubicacion_respald = self.Entry_ubicacionResBD.get_text()

        #Verificacion de la existencia según la ubicación de la base de datos
        control_mensajes_infor_C(
            "Verificando ruta absoluta del archivo sqlite",
            f"Verificando ruta absoluta del archivo <<{nombre_bd}>>: {ubicacion_arch}")

        existe = self.verificar_BD_Existencia(ubicacion_arch)

        if existe:
            control_mensajes_infor_C(
                None,
                f"[OK] Verificación exitosa para el archivo <<{ubicacion_arch}>>...")

            control_mensajes_infor_C(
                "Cambiando ESTADO de la base de datos",
                f"Iniciando cambio del estado registrado de <<{nombre_bd}>> a Existente...")
            self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_bd, "estado", True)

        else:
            control_mensajes_infor_C(
                None,
                f"[OK] Verificación fracasada para el archivo <<{ubicacion_arch}>>...")

            control_mensajes_infor_C(
                "Cambiando ESTADO de la base de datos",
                f"Iniciando cambio del estado registrado de <<{nombre_bd}>> a INEXISTENTE...")
            self.BD_Informadora_Functions.modificar_UNA_propiedad(nombre_bd, "estado", False)


        #Verificación de la ruta de respaldo de la base de datos
        control_mensajes_infor_C(
            "Verificando ruta absoluta de respaldo de la base de datos",
            f"Verificando ruta absoluta de respaldos para <<{nombre_bd}>> en <<{ubicacion_respald}>>...")
        id_bd = self.BD_Informadora_Functions.obtener_id_registro("nombre", nombre_bd)

        if ubicacion_respald.lower() == "sin comprobar":
            control_mensajes_infor_C(
                "Verificación finalizada",
                f"Se ha detectado rutas sin comprobar en <<{nombre_bd}>>. Añadiendo rutas predeterminadas (si existen)...")
            self.insertar_ubicacion_respaldo(id_bd)
            control_mensajes_infor_C(None, f"[OK] Registro de ruta de respaldo terminado con exito (solo para origen SISTEMA)...")

        else:
            control_mensajes_infor_C(
                "Verificación finalizada",
                f"[OK] No se ha detectado rutas sin comprobar en <<{nombre_bd}>>")

        #Finalizando procesos
        control_mensajes_infor_C(
            "Finalizando procesos",
            "Verificaciones finalizadas. Terminando procesos pendientes...")
        spinner.stop()
        boton.set_sensitive(True)

        control_mensajes_infor_C("Verificación finalizada.", "Todos los procesos han sido detenidos.")