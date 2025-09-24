
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk



class MERIDA_API:
    def __init__(self, pantalla_principal):
        
        self.pantalla_principal = pantalla_principal

    
    def añadir_pestana_BarraLateral_Izquierda(self,label, instancia):
        """
        Añade una nueva pestaña a la barra lateral izquierda de la pantalla principal.

        Args:
            label (str): El texto que se mostrará en la pestaña.
            instancia (Gtk.Widget): La instancia del widget que se añadirá como contenido de la pestaña.
        """
        self.pantalla_principal.Pestana_BarraLateral_Izquierda.append_page(instancia, Gtk.Label(label=label))
        
        