import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


from BDs_Functions.BD_Comtecl_Funct import BD_ComTecl_Functions
from BDs_Functions.Models_BD import BD_Comb_Teclas, BD_Tags_General
from BDs_Functions.BD_TAGS_Funct import BD_TAGS_Functions

from Lib_Extra.Funciones_extras import mostrar_vent_IEO,crear_archivos_recurrentes,leer_archivo_recurrente
from Pantallas.Clases_Pantalla_Administrativa.Vista_CombTeclas import Vista_Combinacion_Teclas

import os
from platformdirs import user_documents_path
from collections import defaultdict
from datetime import datetime, timedelta



class Vista_AjustesGenerales (Gtk.Box):
    def __init__(self, Pantalla_principal_SUP):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_vexpand(True)

        self.BD_ComTecl_Functions = BD_ComTecl_Functions()
        self.BD_TAGS_Funct = BD_TAGS_Functions()


        self.Vista_Combinacion_Teclas = Vista_Combinacion_Teclas(Pantalla_principal_SUP)

        self.Dict_ArchRecurr_AjusGenerales_SUP = {}


        titulo_AjusSelec = Gtk.Label(label="Ajustes Generales")
        titulo_AjusSelec.set_xalign(0)

        titulo_AjusZonaHoraria = Gtk.Label(label="Zona Horaria")
        titulo_AjusZonaHoraria.set_xalign(0)

        titulo_AjusRutaPreder = Gtk.Label(label="Ajustes de la Ruta Predeterminada")
        titulo_AjusRutaPreder.set_xalign(0)

        titulo_ConfgRespalAuto = Gtk.Label(label="Configurar Respaldo Automático")
        titulo_ConfgRespalAuto.set_xalign(0)

        stitulo_respalautoSistema = Gtk.Label(label="Respaldo automático para las bases de datos del SISTEMA")
        stitulo_respalautoSistema.set_xalign(0)
        stitulo_respalautoSistema.set_wrap(True)       

        titulo_RestValorPreder = Gtk.Label(label="Restaurar Valores Predeterminados")
        titulo_RestValorPreder.set_xalign(0)



        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        label.title {
            font-weight: bold;
            font-size: 20pt;
        }

        label.title2 {
            font-weight: bold;
            font-size: 14pt;
        }

        label.title3 {

            font-weight: bold;
            font-size: 12pt;
        }

        """)

        style_context1 = titulo_AjusSelec.get_style_context()
        style_context1.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context1.add_class("title")

        style_context_6 = titulo_AjusZonaHoraria.get_style_context()
        style_context_6.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context_6.add_class("title2")

        style_context2 = titulo_AjusRutaPreder.get_style_context()
        style_context2.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context2.add_class("title2")

        style_context_4 = titulo_ConfgRespalAuto.get_style_context()
        style_context_4.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context_4.add_class("title2")

        style_context_5 = stitulo_respalautoSistema.get_style_context()
        style_context_5.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context_5.add_class("title3")

        style_context3 = titulo_RestValorPreder.get_style_context()
        style_context3.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        style_context3.add_class("title2")



        self.append(titulo_AjusSelec)
        
        self.append(titulo_AjusZonaHoraria)
        self.append(self.confg_Zona_Horaria())

        self.append(titulo_AjusRutaPreder)
        self.append(self.ajustes_rutaPreder())
        
        self.append(titulo_ConfgRespalAuto)
        self.append(self.mostrar_ajustes_generales_RespaldAutomatic())
        self.append(stitulo_respalautoSistema)
        self.append(self.mostrar_configuracion_RespalAutoSistema())

        self.append(titulo_RestValorPreder)
        self.append(self.btns_restaurativos())


    def restaur_combteclas(self, widget=None):
        """
        Restaura todas las combinaciones de teclas a sus valores predeterminados.

        Parámetros:
            widget (Gtk.Widget, opcional): El widget que disparó la acción 
            (puede ser None).

        Comportamiento:
            - Muestra un diálogo de advertencia que informa al usuario que todas las 
            combinaciones personalizadas
              serán eliminadas si continúa.
            - Si el usuario confirma (OK):
                - Llama a `eliminar_todas_comteclas()` para borrar todas las combinaciones personalizadas.
                - Llama a `asegurar_entradas_preder()` para garantizar que las entradas predeterminadas estén presentes.
                - Actualiza la vista (`Vista_Combinacion_Teclas`) llamando a `cargar_datos_comteclas()`.
            - Si el usuario cancela, no se realiza ninguna acción.
            - El diálogo se destruye al finalizar cualquier respuesta.

        Esta función es llamada por: __init__
        """
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Advertencia de Eliminación"
        )

        content_area = dialog.get_content_area()

        label1 = Gtk.Label(label="Todos los valores personalizados serán eliminados.\n¿Desea continuar?")
        label1.set_wrap(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_vexpand(True)

        vbox.append(label1)

        content_area.append(vbox)

        def on_response_dialog(dialog, respuesta_get):

            if respuesta_get == Gtk.ResponseType.OK:
                self.BD_ComTecl_Functions.eliminar_todas_comteclas()
                self.BD_ComTecl_Functions.asegurar_entradas_preder()
                self.Vista_Combinacion_Teclas.cargar_datos_comteclas()

            dialog.destroy()

        dialog.connect("response", on_response_dialog)
        dialog.present()

    def btns_restaurativos(self):
        """
        Crea una caja vertical con botones para restaurar configuraciones predeterminadas.

        Retorna:
            Gtk.Box: Contenedor con botones para:
                - Restaurar combinaciones de teclas predeterminadas.
                - Restaurar la ruta predeterminada de fábrica.
        """

        box_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)


        btn_restaurar_ComTecl = Gtk.Button(label="Restaurar Combinaciones de Teclas Predeterminadas")
        btn_restaurar_ComTecl.connect("clicked", self.restaur_combteclas)

        btn_restaurar_rutapreder = Gtk.Button(label="Restaurar la Ruta Predeterminada de Fabrica")
        btn_restaurar_rutapreder.connect("clicked", self.restaurar_ruta_de_Fabrica)

        box_res.append(btn_restaurar_ComTecl)
        box_res.append(btn_restaurar_rutapreder)

        return box_res

    def ajustes_rutaPreder(self):
        """
        Crea la interfaz para visualizar y modificar la ruta predeterminada del sistema.

        Incluye:
        - Un `Gtk.Entry` para mostrar y editar la ruta.
        - Un botón para habilitar edición.
        - Un botón para guardar los cambios.

        Retorna:
            Gtk.Box: Contenedor con widgets relacionados a la configuración de la ruta predeterminada.
        """
        
        box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box1.set_hexpand(True)

        box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box2.set_hexpand(True)

        labelind1 = Gtk.Label(label="Ruta Predeterminada:")
        labelind1.set_xalign(0)

        entryind1 = Gtk.Entry(placeholder_text="Ingresa la Ruta Predeterminada")
        entryind1.set_hexpand(True)

        btn_entr1 = Gtk.Button(label="Modificar ruta")
        btn_entr1.connect("clicked", self.habiliatar_modificar_ruta, entryind1)

        box_espacio = Gtk.Box()
        box_espacio.set_hexpand(True)

        btn_entr2 = Gtk.Button(label="Guardar ruta")
        btn_entr2.connect("clicked", self.guardar_modificacion_ruta, entryind1)


        ruta_preder_get = self.BD_TAGS_Funct.obtener_registro_NombEtiq("Etiqueta Predeterminada")

        entryind1.set_text(ruta_preder_get)
        entryind1.set_sensitive(False)


        box1.append(labelind1)
        box1.append(entryind1)

        box2.append(btn_entr1)
        box2.append(box_espacio)
        box2.append(btn_entr2)


        box.append(box1)
        box.append(box2)



        return box

    def habiliatar_modificar_ruta(self, widget=None, entry_get=None):
        """
        Habilita la edición manual del campo `Gtk.Entry` que contiene la ruta predeterminada.

        Parámetros:
            widget (Gtk.Widget, opcional): El botón que dispara la acción.
            entry_get (Gtk.Entry): Campo de entrada a habilitar.
        """

        entry_get.set_sensitive(True)

    def guardar_modificacion_ruta(self, widget=None, entry_get=None):
        """
        Guarda los cambios realizados a la ruta predeterminada si son distintos a la actual.

        Verifica si la ruta fue modificada y, en caso afirmativo, actualiza la base de datos
        con la nueva ruta. Muestra un mensaje de éxito o error, según el caso.

        Parámetros:
            widget (Gtk.Widget, opcional): Botón que dispara la acción.
            entry_get (Gtk.Entry): Campo que contiene la nueva ruta a guardar.
        """

        Nueva_Ruta = entry_get.get_text()

        ruta_preder_aVerificar = self.BD_TAGS_Funct.obtener_registro_NombEtiq("Etiqueta Predeterminada")

        if not ruta_preder_aVerificar == Nueva_Ruta:
            
            estado_y_registro = self.BD_TAGS_Funct.modificar_lista_existente(
                filtro_etiqueta="Etiqueta Predeterminada",
                filtro_ruta=None,
                nueva_etiqueta="Etiqueta Predeterminada",
                nueva_ruta = Nueva_Ruta
                )

            if estado_y_registro:
                mostrar_vent_IEO(
                    self.get_root(),
                    "Registro Exitoso",
                    "La nueva Ruta Predeterminada ha sido creada satisfactoriamente.\nEs necesario reiniciar para aplicarla completamente.",
                    Gtk.MessageType.INFO,
                    1,
                    "Claro, reiniciaré el programa.",
                    None,
                    None)
            else:
                    mostrar_vent_IEO(
                    self.get_root(),
                    "Error de Registro",
                    "No se pudo completar el registro de la ruta predeterminada.",
                    Gtk.MessageType.ERROR,
                    1,
                    "Aceptar",
                    None,
                    None)




        entry_get.set_sensitive(False)

    def restaurar_ruta_de_Fabrica(self, widget=None):
        """
        Restaura la ruta predeterminada a su valor original de fábrica (en la carpeta Documentos).

        Muestra un diálogo de confirmación y actualiza la ruta en la base de datos si se acepta.

        Parámetros:
            widget (Gtk.Widget, opcional): Botón que dispara la restauración.
        """

        RUTA_DE_FABRICA = os.path.join(user_documents_path(), "MERIDA")


        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Advertencia de Restauración"
        )

        content_area = dialog.get_content_area()

        label1 = Gtk.Label(label="La ruta predeterminada será devuelta al estado de fábrica.\n¿Desea continuar?")
        label1.set_wrap(True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_vexpand(True)

        vbox.append(label1)

        content_area.append(vbox)

        def on_response_dialog(dialog, respuesta_get):

            if respuesta_get == Gtk.ResponseType.OK:
                estado_y_registro = self.BD_TAGS_Funct.modificar_lista_existente(
                    filtro_etiqueta="Etiqueta Predeterminada",
                    filtro_ruta=None,
                    nueva_etiqueta="Etiqueta Predeterminada",
                    nueva_ruta=RUTA_DE_FABRICA
                    )

                if estado_y_registro:
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Registro Exitoso",
                        "La Ruta Predeterminada ha sido devuelto a su estado de fábrica.\nEs necesario reiniciar para aplicarla completamente.",
                        Gtk.MessageType.INFO,
                        1,
                        "Gracias, reiniciaré el programa.",
                        None,
                        None)
                else:
                    mostrar_vent_IEO(
                        self.get_root(),
                        "Error de Registro",
                        "No se pudo completar el registro de la ruta predeterminada.",
                        Gtk.MessageType.ERROR,
                        1,
                        "Aceptar",
                        None,
                        None)

            dialog.destroy()

        dialog.connect("response", on_response_dialog)
        dialog.present()

    def mostrar_ajustes_generales_RespaldAutomatic(self):
        """
        Crea y devuelve un contenedor con la interfaz para configurar
        la cantidad de archivos de respaldo a mantener.

        Incluye un Gtk.SpinButton para seleccionar el número de archivos
        más recientes que se conservarán en la carpeta de respaldo.
        El valor inicial se carga desde el archivo recurrente
        'Archivo_Recurrente_Spinn.json', si existe.
        
        Returns:
            Gtk.Box: Contenedor con los controles de configuración.
        """
        box_1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        #Spinner y label para eliminación de archivos
        label_Elimin1 = Gtk.Label(label="Mantener los")
        self.Spin_Elimin = Gtk.SpinButton()
        self.Spin_Elimin.set_tooltip_text(
            "Controla la cantidad de archivos de restauración (sqlite y sql) que se mantendrán en la carpta de respaldo.\nTodos los demás serán eliminados.")
        self.Spin_Elimin.set_adjustment(Gtk.Adjustment(lower=1, upper=30, step_increment=1))
        self.Spin_Elimin.set_value(3)
        label_Elimin2 = Gtk.Label(label="archivos de restauración más recientes")

        box_1.append(label_Elimin1)
        box_1.append(self.Spin_Elimin)
        box_1.append(label_Elimin2)

        #Carga los datos del archivo recurrente para mantenerlos siempre actualizados
        datos_archRecurrent = leer_archivo_recurrente("Archivo_Recurrente_Spinn.json","json")

        if datos_archRecurrent is not None:
            self.Spin_Elimin.set_value(datos_archRecurrent["Número_Arch_a_Mantener"])

        return box_1

    def mostrar_configuracion_RespalAutoSistema(self):
        """
        Crea y devuelve un contenedor con la interfaz para configurar
        el intervalo de tiempo entre respaldos automáticos.

        Incluye Gtk.SpinButton para días, meses y años, así como un botón
        para guardar la configuración. El valor inicial se carga desde el
        archivo recurrente 'Archivo_Recurrente_Spinn.json', si existe.

        Returns:
            Gtk.Box: Contenedor con los controles de configuración.
        """

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        box_entradas = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        box_botones = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        label1 = Gtk.Label(label="Cada  ")
        
        #Spinner y label para días
        Spin_dias = Gtk.SpinButton()
        Spin_dias.set_adjustment(Gtk.Adjustment(lower=0, upper=365, step_increment=1))
        Spin_dias.set_value(7)
        label_dias = Gtk.Label(label="día/s    ")

        #Spinner y label para meses
        Spin_meses = Gtk.SpinButton()
        Spin_meses.set_adjustment(Gtk.Adjustment(lower=0, upper=12, step_increment=1))
        Spin_meses.set_value(0)
        label_meses = Gtk.Label(label="mese/s    ")

        #Spinner y label para años
        Spin_anos = Gtk.SpinButton()
        Spin_anos.set_adjustment(Gtk.Adjustment(lower=0, upper=10, step_increment=1))
        Spin_anos.set_value(0)
        label_anos = Gtk.Label(label="año/s")

        #Botones
        btn_GudardarConfig = Gtk.Button(label="Guardar configuración de guardado automático")
        btn_GudardarConfig.set_tooltip_text(
            "Guarda la configuración del intervalo para realizar los respaldos automáticos. Estos se contarán cada inicio del programa.z")
        btn_GudardarConfig.connect("clicked", self.confg_RespaldAutoSistema, Spin_dias, Spin_meses, Spin_anos)

        box_entradas.append(label1)
        box_entradas.append(Spin_dias)
        box_entradas.append(label_dias)
        box_entradas.append(Spin_meses)
        box_entradas.append(label_meses)
        box_entradas.append(Spin_anos)
        box_entradas.append(label_anos)

        box_botones.append(btn_GudardarConfig)


        box_pr.append(box_entradas)
        box_pr.append(box_botones)


        #Carga los datos del archivo recurrente para mantenerlos siempre actualizados
        datos_archRecurrent = leer_archivo_recurrente("Archivo_Recurrente_Spinn.json","json")

        if datos_archRecurrent is not None:
            Spin_dias.set_value(datos_archRecurrent["dias"])
            Spin_meses.set_value(datos_archRecurrent["meses"])
            Spin_anos.set_value(datos_archRecurrent["años"])

        return box_pr

    def confg_RespaldAutoSistema(self,widget=None, spin_dias=None, spin_meses=None, spin_anos=None):
        """
        Guarda la configuración de respaldos automáticos y el número
        de archivos de respaldo a mantener.

        Crea un archivo recurrente 'Archivo_Recurrente_Spinn.json' con
        los valores obtenidos de los Gtk.SpinButton, y muestra una ventana
        informativa con el estado del proceso.

        Args:
            widget (Gtk.Widget, opcional): Widget que disparó la acción.
            spin_dias (Gtk.SpinButton, opcional): Control para el número de días.
            spin_meses (Gtk.SpinButton, opcional): Control para el número de meses.
            spin_anos (Gtk.SpinButton, opcional): Control para el número de años.
        """

        def crear_arhc_spins():
            # Obtener valores de los spinners
            dias = spin_dias.get_value_as_int()
            meses = spin_meses.get_value_as_int()
            anos = spin_anos.get_value_as_int()

            N_Archivos_Manten = self.Spin_Elimin.get_value_as_int()
            dic_spinss = {

                "dias": dias,
                "meses": meses,
                "años": anos,
                "Número_Arch_a_Mantener": N_Archivos_Manten
            }

            estado, error = crear_archivos_recurrentes(
                "Archivo_Recurrente_Spinn.json",
                "json",
                dic_spinss)

            if not error and estado:
                mostrar_mensaje(None, "[OK] Creación finalizada con exito." )
                mostrar_mensaje(
                    None, 
                    f"Datos guardados: Intervalo guardado:D{dias};M{meses};A{anos} | Archivos a mantener:{N_Archivos_Manten}")

            elif not estado and error:
                mostrar_mensaje(
                    "Error de creación",
                    f"[ERROR] No se pudo crear el archivo: {error}")
            else:
                mostrar_mensaje(
                    "Estado desconocido",
                    f"[?] Error desconocido: {error}")

        def cerrar_dialogo(widget=None):
            vent.destroy()

        def mostrar_mensaje(mensaje_label, mensaje_textview):
            if mensaje_label is not None:
                label_estado.set_text(mensaje_label)

            if mensaje_textview is not None:
                buffer = textview_Infor.get_buffer()
                texto_actual = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
                nuevo_texto = texto_actual + mensaje_textview + "\n"
                buffer.set_text(nuevo_texto)

        # Crear ventana
        vent = Gtk.Dialog(
            title="Ventana de Información",
            transient_for=self.get_root(),
            modal=True,
        )
        vent.set_default_size(550, 200)
        content_area = vent.get_content_area()

        label_estado = Gtk.Label(label="Esperando instrucciones...")

        textview_Infor = Gtk.TextView(vexpand=True, hexpand=True)
        textview_Infor.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        textview_Infor.set_editable(False)
        textview_Infor.set_focusable(False)

        scroll_infor = Gtk.ScrolledWindow()
        scroll_infor.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_infor.set_child(textview_Infor)
        scroll_infor.set_vexpand(True)
        scroll_infor.set_hexpand(True)

        btn_cerrar_vent = Gtk.Button(label="Cerrar ventana")
        btn_cerrar_vent.connect("clicked", cerrar_dialogo)

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)

        box_pr.append(label_estado)
        box_pr.append(scroll_infor)
        box_pr.append(btn_cerrar_vent)

        content_area.append(box_pr)

        spiner_infor = Gtk.Spinner()
        #Creación del archivo recurrente spins
        spiner_infor.start()
        mostrar_mensaje("Guardando configuración para respaldos automáticos...", "Iniciando creación de archivo recurrente...")
        crear_arhc_spins()
        mostrar_mensaje("Guardado finalizado", "El archivo recurrente ha sido creado con exito.")
        spiner_infor.stop()


        vent.show()

    def confg_Zona_Horaria(self):
        """
        Crea y devuelve un contenedor con la interfaz para seleccionar
        la zona horaria del sistema.

        Utiliza un Gtk.DropDown con una lista de regiones predefinidas.
        La selección del usuario se guarda en 'Ajustes_Generales.json'
        para que se recuerde entre sesiones. Si no hay configuración previa,
        se selecciona 'Región No seleccionada' por defecto.

        Returns:
            Gtk.Box: Contenedor con el Gtk.DropDown y su etiqueta descriptiva.
        """
        def on_selection_reponse(dropdown, _):
            indice = dropdown.get_selected()
            if indice != Gtk.INVALID_LIST_POSITION:
                texto = dropdown.get_selected_item().get_string()

                self.C_M_ArchRecur_AjusGenerales("Zona_Horaria", texto)

        box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        label_tit = Gtk.Label(label="Seleccione una región válida:")
        label_tit.set_xalign(0)

        opciones_regiones = [
            "Región No seleccionada",
            "America/La_Paz",
            "America/Lima",
            "America/Bogota",
            "UTC"
        ]

        #Creación de modelo para dropdown

        modelo = Gio.ListStore.new(Gtk.StringObject)

        for opcion in opciones_regiones:
            modelo.append(Gtk.StringObject.new(opcion))


        #creación del widget (dropdown)
        dropdown = Gtk.DropDown(
            model=modelo,
            expression=Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))

        dropdown.set_tooltip_text(
            "Seleccione su región horaria según la lista presentada. Si no hay su región, seleccione UTC hasta que sea implementada.")
        dropdown.connect("notify::selected", on_selection_reponse)


        #Cargar última selección hecha
        datos_get = leer_archivo_recurrente("Ajustes_Generales.json", "json")
        
        if datos_get is None:
            ultima_select = "Región No seleccionada"
        else:    
            ultima_select = datos_get["Zona_Horaria"]

        #Recuperar el indice (necesario para selección autmática del widget)
        indice = opciones_regiones.index(ultima_select) if ultima_select in opciones_regiones else 0

        #Selección autmámtica del widget
        dropdown.set_selected(indice)

        box_pr.append(label_tit)
        box_pr.append(dropdown)

        return box_pr

    def C_M_ArchRecur_AjusGenerales(self, llave, contenido):
        """
        Añade o actualiza una entrada en el diccionario general,
        asegurando que el contenido nuevo quede al final.
        """

        # Eliminar si ya existe para reinsertar al final
        if llave in self.Dict_ArchRecurr_AjusGenerales_SUP:
            del self.Dict_ArchRecurr_AjusGenerales_SUP[llave]

        # Insertar al final
        self.Dict_ArchRecurr_AjusGenerales_SUP[llave] = contenido
        
        crear_archivos_recurrentes("Ajustes_Generales.json","json", self.Dict_ArchRecurr_AjusGenerales_SUP)


    