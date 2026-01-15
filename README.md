# 🚀 ICT Innovation: Computer Vision & Frontend Suite

Bienvenido al repositorio central de **ICT Innovation**. Este proyecto integra soluciones avanzadas de **Visión Artificial (Computer Vision)** en tiempo real con una interfaz de usuario moderna para la visualización y control.

El proyecto ha sido reestructurado para ofrecer un entorno de desarrollo profesional, modular y escalable.

---

## 📂 Estructura del Proyecto

El repositorio está organizado siguiendo las mejores prácticas de ingeniería de software:

```
ict-inovation/
├── app/                  # 🌐 Frontend & UI
│   ├── assets/           # Imágenes y recursos estáticos
│   ├── css/              # Hojas de estilo (Diseño responsivo)
│   ├── js/               # Lógica del frontend (Interacciones)
│   └── docs/             # Documentación técnica y diagramas
│
├── src/                  # 🧠 Núcleo de Inteligencia Artificial
│   ├── sam_webcam.py     # Segmentación con SAM (Segment Anything Model)
│   ├── fastsam_*.py      # Implementaciones optimizadas de FastSAM
│   ├── yolo_*.py         # Detección y segmentación con YOLOv8/11
│   └── ...
│
├── models/               # 📦 Pesos de los Modelos (Weights)
│   ├── yolov8n.pt
│   ├── FastSAM-s.pt
│   └── ...
│
└── requirements.txt      # 📋 Dependencias del proyecto
```

---

## 🛠️ Instalación y Configuración

Sigue estos pasos para configurar tu entorno de desarrollo.

### 1. Prerrequisitos
*   Sistema Operativo: Linux / Windows / MacOS
*   Python 3.8+
*   Webcam (para demos en tiempo real)
*   Navegador Web (Chrome/Firefox/Edge)

### 2. Configurar Entorno Virtual
Es recomendable usar un entorno virtual para aislar las dependencias.

```bash
# Crear entorno virtual
python3 -m venv env

# Activar entorno
source env/bin/activate  # Linux/Mac
# env\Scripts\activate   # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución de Demos de IA (Backend)

Todos los scripts de IA se encuentran en la carpeta `src/`. Para ejecutarlos correctamente, **hazlo desde la raíz del proyecto**.

### Segmentación en Tiempo Real (FastSAM)
Segmenta cualquier objeto en tiempo real con optimización para GPU.
```bash
python3 src/fastsam_realtime.py
```

### Detección de Objetos (YOLOv8)
Detección clásica rápida y eficiente.
```bash
python3 src/yolo_webcam.py
```

### Segmentación Semántica (YOLO-Seg)
Detección y segmentación simultánea.
```bash
python3 src/yolo_seg_realtime.py
```

---

## 🌐 Ejecución del Frontend (App)

La interfaz de usuario se encuentra en la carpeta `app/`. Es una aplicación web estática que puedes abrir directamente en tu navegador o servir localmente.

### Opción A: Abrir directamente
Navega a la carpeta `app/` y abre el archivo `index.html` con tu navegador preferido.

### Opción B: Servidor Local (Recomendado)
Para una mejor experiencia (especialmente con módulos JS), usa un servidor simple de Python:

```bash
cd app
python3 -m http.server 8000
```
Luego abre `http://localhost:8000` en tu navegador.

---

## 📚 Documentación Adicional

En la carpeta `app/docs/` encontrarás documentación detallada sobre la arquitectura del sistema:
*   **Arquitectura Completa:** `ARQUITECTURA_COMPLETA_PATHSAI.md`
*   **Diagramas Mermaid:** `arquitectura-mermaid.md`
*   **Avances e Informes:** Archivos PDF con detalles del progreso.

---

## 🤝 Contribución

Si deseas contribuir:
1.  Haz un Fork del repositorio.
2.  Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`).
3.  Commit a tus cambios (`git commit -m 'Add some AmazingFeature'`).
4.  Push a la rama (`git push origin feature/AmazingFeature`).
5.  Abre un Pull Request.

---

© 2026 ICT Innovation. Desarrollado con ❤️ e Inteligencia Artificial.
