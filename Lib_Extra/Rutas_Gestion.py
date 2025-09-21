import os
import sys
import platform

from pathlib import Path
import os
import platform

def get_config_dir():
    if platform.system() == "Linux":
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "MERIDA"
    elif platform.system() == "Windows":
        return Path(os.getenv("APPDATA")) / "MERIDA"
    else:
        return Path.home() / ".merida_config"

def get_data_dir():
    if platform.system() == "Linux":
        return Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "MERIDA"
    elif platform.system() == "Windows":
        return Path(os.getenv("LOCALAPPDATA")) / "MERIDA"
    else:
        return Path.home() / ".merida_data"

def get_cache_dir():
    if platform.system() == "Linux":
        return Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "MERIDA"
    elif platform.system() == "Windows":
        return Path(os.getenv("LOCALAPPDATA")) / "MERIDA" / "cache"
    else:
        return Path.home() / ".merida_cache"

def get_log_dir():
    system = platform.system()

    if system == "Linux":
        # Ruta moderna XDG
        state_dir = Path(os.getenv("XDG_STATE_HOME", Path.home() / ".local" / "state"))
        log_dir = state_dir / "MERIDA" / "logs"
        if not state_dir.exists():
            # Si .local/state no existe, usar .cache
            cache_dir = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
            log_dir = cache_dir / "MERIDA" / "logs"

    elif system == "Windows":
        # En Windows → usar LOCALAPPDATA (no APPDATA)
        local_appdata = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        log_dir = local_appdata / "MERIDA" / "logs"

    else:
        # Fallback para otros sistemas (ej. MacOS, BSD, etc.)
        log_dir = Path.home() / ".merida_logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def get_recursos_dir():
    """
    Obtiene la ruta de la carpeta de RECURSOS de MERIDA. Esta carpeta contiene
    datos inmutables (textos, imágenes, etc.) y no debe crearse en Inicializar_Carpetas.
    Se busca en la raíz del proyecto (un nivel arriba de Lib_Extra) o en el directorio
    del sistema según el entorno (Linux/Windows).
    """
    sistema = platform.system()

    if getattr(sys, 'frozen', False):  
        # Caso: ejecutable empaquetado (PyInstaller, .exe, AppImage, etc.)
        base_dir = os.path.dirname(sys.executable)
    else:
        # Caso: ejecución en código fuente → estamos en Proyecto_MERIDA/Lib_Extra/
        # Necesitamos subir un nivel para llegar a Proyecto_MERIDA/
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if sistema == "Linux":
        # Prioridad: carpeta local del proyecto → /usr/share en sistemas instalados
        posibles = [
            os.path.join(base_dir, "Recursos"),      # Proyecto_MERIDA/Recursos
            "/usr/share/MERIDA/Recursos"             # Instalación en Linux
        ]

    elif sistema == "Windows":
        # En Windows los recursos suelen estar junto al .exe
        posibles = [
            os.path.join(base_dir, "Recursos")
        ]

    else:
        # Otros sistemas (MacOS, BSD, etc.)
        posibles = [
            os.path.join(base_dir, "Recursos")
        ]

    # Devolver el primer path que exista
    for ruta in posibles:
        if os.path.exists(ruta):
            return ruta

    # Si no existe ninguno, devolver el primero como fallback
    return posibles[0]

def inicializar_carpetas():
    resultados = []
    for carpeta in [get_config_dir(), get_data_dir(), get_cache_dir(), get_log_dir()]:
        try:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta, exist_ok=True)
                resultados.append((carpeta, "creada", None))
            else:
                resultados.append((carpeta, "existente", None))
        except Exception as e:
            resultados.append((carpeta, "fallo", str(e)))
    return resultados