import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class Linea_de_Tiempo_Modulo:
    def __init__(self, API):
        
        #Se inicializa el modulo y se guarda el API para usarla después
        self.API = API

        
    
    def crear_panel(self):
        self.box_pr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        label = Gtk.Label(label="Sin lineas de tiempo creadas")

        self.box_pr.append(label)

        return self.box_pr


def Inicializar_Modulo(API):
    """Punto de entrada del modulo. Esta función es llamada por MERIDA al cargar el modulo."""

    modulo = Linea_de_Tiempo_Modulo(API)
    
    API.añadir_pestana_BarraLateral_Izquierda("Linea de Tiempo", modulo.crear_panel())

    print("Módulo 'Linea de Tiempo' inicializado y pestaña añadida a la barra lateral izquierda.")