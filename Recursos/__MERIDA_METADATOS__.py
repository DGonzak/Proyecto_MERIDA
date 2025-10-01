"""
ARCHIVO DE METADATOS DEL PROYECTO MERIDA

Este archivo contiene los metadatos esenciales del proyecto MERIDA. Esto incluye el numero de versión,
el autor, la licencia y una breve descripción del proyecto.

"""
class MERIDA_Metadata:
    def __init__(self):
        #=======================METADATOS BÁSICOS=======================#
        self.NOMBRE_DEL_PROGRAMA = "MERIDA"
        self.VERSION_DEL_PROGRAMA = "1.0.0"
        self.AUTOR = "Grupo Meridian"
        self.LICENCIA = "GPL-3.0"
        self.DESCRIPCION = "Software de escritura modular"

        #=======================METADATOS ADICIONALES=======================#
        self.VERSION_MINIMA_DE_PYTHON = "3.8"
        self.PLATAFORMAS_COMPATIBLES = ["Linux"]
        self.IDIOMAS_DISPONIBLES = ["es"]
        self.URL_DEL_PROYECTO = "https://github.com/DGonzak/Proyecto_MERIDA"


