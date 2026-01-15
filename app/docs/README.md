# PathsAI - Sistema de Navegación Asistida para Personas Ciegas

## 📋 Descripción del Proyecto

**PathsAI** es una aplicación móvil innovadora diseñada para asistir a personas con discapacidad visual en su navegación diaria. El sistema combina hardware inteligente (cámara y audífonos) con software de navegación guiada por voz, utilizando inteligencia artificial (SAM y VLM) para detectar obstáculos en tiempo real.

### Características Principales

- 🎥 **Detección en Tiempo Real**: Cámara con IA que captura frames y detecta obstáculos, baches, y peligros
- 🔊 **Guía por Voz**: Instrucciones de navegación mediante audio para guiar al usuario
- 🗺️ **Navegación Inteligente**: Generación de rutas seguras con alertas de peligros reportados
- 👥 **Comunidad Colaborativa**: Voluntarios y la IA reportan obstáculos para alertar a otros usuarios
- 📍 **Lugares Accesibles**: Base de datos de lugares diseñados para personas ciegas
- ⚠️ **Alertas Contextuales**: Notificaciones de baches, obstáculos, pisos mojados, etc.

---

## 🎨 Diseño Visual

### Paleta de Colores (Brand PathsAI)
- **Turquesa**: `#00D4FF` - Color principal, representa guía y tecnología
- **Naranja**: `#FF9500` - Color secundario, representa atención y alertas
- **Blanco**: `#FFFFFF` - Fondo limpio y accesible
- **Gris Oscuro**: `#2C2C2E` - Texto y elementos de contraste

### Estilo
- Diseño **minimalista y tierno** inspirado en Waze
- Botones grandes y accesibles
- Colores sólidos (sin degradados en fondos)
- Animaciones suaves y profesionales

---

## 📱 Estructura de Vistas

### Vista 1: Selección de Producto (`index.html`)

**Propósito**: Pantalla inicial donde el usuario elige el tipo de servicio que desea utilizar.

**Elementos**:
- Logo PathsAI centrado
- Título "PathsAI"
- Dos botones grandes:
  - 🟠 **Solo Cámara** (naranja): Hardware únicamente - cámara inteligente con audio guiado
  - 🟢 **Ruta Guiada** (verde): Hardware + Software completo - navegación GPS con voz

**Navegación**: Ambos botones redirigen a → `navigation.html`

**Archivos**:
- `index.html`
- `styles.css`
- `script.js`

---

### Vista 2: Navegación Principal (`navigation.html`)

**Propósito**: Pantalla principal de navegación donde el usuario puede elegir su destino.

**Elementos**:
- **Header**: Logo pequeño + título "¿A dónde quieres ir?"
- **Botón de Asistente** (grande, blanco con borde):
  - Icono de búsqueda
  - Texto: "Pregunta a tu asistente"
  - Subtítulo: "Dime a dónde quieres ir"
  - Icono de micrófono (turquesa)
- **Dos tarjetas cuadradas**:
  - ⭐ **Mis Favoritos** (fondo amarillo suave): Lugares guardados y frecuentes
  - 📍 **Explorar** (fondo verde suave): Restaurantes, hospitales, lugares predeterminados

**Navegación**: 
- Botón "Pregunta a tu asistente" → `voice-assistant.html`
- Botones de favoritos/explorar → (futuras vistas)

**Archivos**:
- `navigation.html`
- `navigation.css`
- `navigation.js`

---

### Vista 3: Asistente de Voz (`voice-assistant.html`)

**Propósito**: Interfaz de conversación en tiempo real con el asistente de IA mediante voz.

**Elementos**:
- **Área de conversación** (superior):
  - Mensajes del asistente (fondo gris claro)
  - Mensajes del usuario (fondo turquesa)
- **Visualizador de voz** (centro):
  - Círculo animado con efecto de pulso
  - Gradiente turquesa brillante
  - Ondas expansivas (ripple effect)
  - Texto: "Escuchando..."
- **Controles** (inferior):
  - ❌ Botón cerrar (naranja) - Regresa a `navigation.html`
  - 🎤 Botón micrófono (turquesa activo) - Toggle de voz

**Funcionalidad**:
- Reconocimiento de voz para solicitar rutas
- Respuestas del asistente en tiempo real
- Animaciones que indican actividad de voz

**Navegación**: Botón X → `navigation.html`

**Archivos**:
- `voice-assistant.html`
- `voice-assistant.css`
- `voice-assistant.js`

---

### Vista 4: Mapa de Navegación (`map-navigation.html`)

**Propósito**: Vista de navegación activa en tiempo real con la ruta generada y alertas de peligros.

**Elementos**:

#### Header (Negro)
- Distancia a la próxima acción: "200 m"
- Instrucción de navegación: "Continúa recto" (turquesa)

#### Mapa
- **Fondo**: Calles y bloques estilo Waze
- **Línea de ruta**: Azul turquesa (#00D4FF) vertical
- **Marcador de usuario**: Estrella turquesa pulsante (posición actual)
- **Marcador de destino**: Pin naranja (#FF9500) en la parte superior
- **Alertas de peligros** (tarjetas flotantes con animación):
  - ⚠️ **Bache** - Borde rojo
  - 🚧 **Obstáculo** - Borde naranja  
  - 💧 **Piso mojado** - Borde turquesa

#### Panel de Información (Inferior)
- **Llegada**: Hora estimada (ej: 12:45)
- **Distancia**: Total del recorrido (ej: 850 m)
- **Tiempo**: Duración estimada (ej: 11 min)

#### Notificación de Alerta
- Aparece automáticamente cuando hay peligros cercanos
- Ejemplo: "¡Precaución! Bache reportado en 50 metros"
- Desaparece después de 5 segundos

**Funcionalidad**:
- Actualización de distancia e instrucciones cada 5 segundos
- Anuncios de voz automáticos para personas ciegas
- Alertas visuales y auditivas de peligros

**Archivos**:
- `map-navigation.html`
- `map-navigation.css`
- `map-navigation.js`

---

## 🔄 Flujo de Navegación

```
index.html (Selección de Producto)
    ↓
navigation.html (Navegación Principal)
    ↓
voice-assistant.html (Asistente de Voz)
    ↓
map-navigation.html (Navegación Activa)
```

---

## 🛠️ Tecnologías Utilizadas

- **HTML5**: Estructura semántica
- **CSS3**: Diseño responsivo y animaciones
- **JavaScript**: Interactividad y lógica de navegación
- **Google Fonts**: Nunito (tipografía amigable y legible)
- **SVG**: Iconos vectoriales escalables

---

## 🎯 Público Objetivo

Personas con discapacidad visual que necesitan:
- Navegación independiente y segura
- Alertas de obstáculos en tiempo real
- Guía por voz clara y precisa
- Acceso a lugares diseñados para accesibilidad

---

## 🚀 Características Futuras

- Integración con hardware real (cámara y audífonos)
- Implementación de modelos SAM y VLM para detección de obstáculos
- Sistema de reportes comunitarios de voluntarios
- Base de datos de lugares accesibles
- Sincronización con GPS real
- Web Speech API para reconocimiento de voz real
- Modo offline para navegación sin conexión

---

## 📄 Licencia

Proyecto educativo - PathsAI © 2026
