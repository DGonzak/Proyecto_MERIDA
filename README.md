# MERIDA
*_"Pensado para escritores, organizado para tus ideas.”_*


**Versión actual: 1.0**

MERIDA es un software diseñado para asistir a autores de todo tipo. Su propósito es proporcionar un entorno de escritura cómodo, rápido y sencillo, con herramientas que potencien la organización y productividad del escritor.

---

## ✨ Características actuales

- **Editor principal**: Un editor básico que admite sintaxis inspirada en Markdown (títulos con `#`, subtítulos con `##`, etc.).
- **Sistema de etiquetas personalizadas**: Permite asignar una o varias etiquetas a un documento, determinando automáticamente dónde se guardará. Cada etiqueta representa una carpeta del sistema.
- **Notas vinculadas**: Posibilidad de generar notas asociadas al documento principal.
- **Interfaz ligera**: Creada con GTK4 para un rendimiento fluido y visual limpio.

---

## 🧠 ¿Cómo funcionan las etiquetas?

Cada etiqueta está vinculada a una ruta de carpeta. Puedes crear etiquetas desde la sección de menú y usarlas al momento de escribir. Los documentos `.merida` se guardan automáticamente en todas las carpetas correspondientes a las etiquetas asignadas al texto. Esto permite, por ejemplo, organizar documentos por proyecto, tema o cualquier criterio útil para el usuario.

---

## 🧭 Visión a futuro

En versiones posteriores se prevé incluir:

- Línea de tiempo para estructurar eventos narrativos o investigaciones.
- Lector de archivos PDF integrado.
- Almacenamiento de imágenes dentro del proyecto.
- Conexiones entre documentos y notas.
- Exportaciones en distintos formatos.
- Y mucho más...

---

## 🛠 Tecnologías utilizadas

- **Python 3**
- **GTK4** – Para la interfaz gráfica.
- **SQLAlchemy** – Manejo de bases de datos.
- **Sistema operativo de desarrollo**: Linux Debian 13 Stable.

---

## 🏁 Estado del proyecto

Este proyecto se encuentra en su **primera versión estable (1.0)**. Actualmente ofrece herramientas básicas para la escritura modular, gestión de notas y etiquetas, así como organización inicial de proyectos.

El desarrollo es **activo y continuo**, con la meta de expandir MERIDA en el corto y mediano plazo.

**En desarrollo:**
- Mejoras en la interfaz gráfica (más intuitiva y personalizable).
- Creación e implementación del sistema de instalación de paquetes (módulos) MERIDA.
- Desarrollo del módulo **MERIDA: Líneas de Tiempo**.
- Optimización de la gestión de bases de datos y operaciones grupales.
- Ajustes menores y corrección de errores.

---

## 📂 Instalación

Actualmente se ofrecen los siguientes métodos de instalación:

- **Linux (Debian y derivados)**: Paquetes `.deb` que pueden instalarse directamente mediante el gestor de paquetes del sistema (`dpkg -i merida_1.0.deb`).

También puede optar por descargar el **código fuente** y ejecutar el programa directamente (se usa, como ejemplo, el método https):

```bash
git clone https://github.com/DGonzak/Proyecto_MERIDA.git
cd merida
python3 main.py
```
Asegúrese de instalar todas las dependencias (listadas en **requirements.txt**) y contar con GTK4 instalado y disponible en el sistema. 

💡**Recomendación:** utilice un entorno virtual de Python para instalar 	las dependencias y garantizar la compatibilidad. Verifique, además, que el entorno virtual tenga acceso a GTK4.


📘 **Nota:** Para una explicación detallada del funcionamiento de MERIDA, puedes consultar el **Manual de Usuario** incluido en el respositorio del proyecto. Allí encontrarás instrucciones paso a paso y descripciones completas de cada módulo.

---

## 🤝 Contribuciones

Por ahora, MERIDA es desarrollado por un único autor.
En el futuro, se habilitará la participación de la comunidad a través de:

- Apertura de issues en GitHub para reportar errores y sugerir mejoras.

- Revisión y aceptación de pull requests con nuevas funcionalidades.

- Discusiones abiertas para decidir el rumbo del proyecto.

**Desarrollador principal:**

 - DGonzak (DGonzak Ada Lovelace) — dgonzak4@gmail.com

Si deseas contribuir en las etapas iniciales (testing, documentación o sugerencias), puedes ponerte en contacto directo con el autor.

---

## 📜 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3 (GPLv3)**.

Esto significa que:

- Tienes la libertad de usar el programa para cualquier propósito.

- Puedes estudiar cómo funciona y adaptarlo a tus necesidades.

- Estás autorizado a redistribuir copias.

- Puedes mejorar el software y hacer públicas esas mejoras.

No obstante, cualquier redistribución o derivación de **MERIDA** debe conservar la misma licencia (GPLv3), asegurando que el software siga siendo libre para toda la comunidad.

Consulta el archivo **LICENSE.md** para más información.



