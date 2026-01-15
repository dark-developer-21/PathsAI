#!/usr/bin/env python3
"""
Script para segmentar objetos ESPECÍFICOS en tiempo real usando YOLOE con Prompts
Vocabulario abierto con detección enfocada en categorías personalizadas
Optimizado para RTX 4070 - ~35-45 FPS
"""
from ultralytics import YOLOE
import cv2
import signal
import sys
import numpy as np
import time
import torch

# ========================================
# CONFIGURA AQUÍ TUS PROMPTS PERSONALIZADOS
# ========================================
# YOLOE entiende LENGUAJE NATURAL! Puedes usar:
# 1. Palabras clave: "person, car, dog"
# 2. Descripciones: "a person walking", "red car", "small dog"
# 3. Frases naturales: "people in the video", "vehicles on the street"

CUSTOM_PROMPTS = """
person, car, motorcycle, bus, truck, bicycle
"""

# ============ EJEMPLOS CON PALABRAS CLAVE ============

# Solo personas:
# CUSTOM_PROMPTS = "person"

# Personas y mascotas:
# CUSTOM_PROMPTS = "person, dog, cat, bird"

# Oficina:
# CUSTOM_PROMPTS = "person, laptop, keyboard, mouse, monitor, phone, cup"

# Animales:
# CUSTOM_PROMPTS = "dog, cat, bird, horse, sheep, cow, elephant"

# ============ EJEMPLOS CON LENGUAJE NATURAL ============

# Descripción natural (funciona!):
# CUSTOM_PROMPTS = "people in the video, cars on the street"

# Solo personas:
# CUSTOM_PROMPTS = "a person, human, people"

# Objetos específicos con descripción:
# CUSTOM_PROMPTS = "a person wearing glasses, a red car, a laptop computer"

# Animales con descripción:
# CUSTOM_PROMPTS = "a dog, a cat, pets in the video"

# Vehículos con descripción:
# CUSTOM_PROMPTS = "vehicles on the road, cars, motorcycles, buses"

# Combinación (lo más flexible):
# CUSTOM_PROMPTS = """
# people, person walking, human face,
# cars, vehicles on street, motorcycle,
# laptop, computer, phone
# """

# ========================================

# Variables globales
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\nCerrando programa...")
    running = False

def parse_prompts(prompt_string):
    """Convierte el string de prompts en una lista limpia"""
    # Limpiar y separar por comas
    prompts = [p.strip() for p in prompt_string.strip().split(',')]
    # Filtrar vacíos
    prompts = [p for p in prompts if p]
    return prompts

def generate_colors(n):
    """Genera N colores distintos para las máscaras"""
    np.random.seed(42)
    colors = []
    for i in range(n):
        colors.append(tuple(np.random.randint(0, 255, 3).tolist()))
    return colors

def apply_masks_with_labels(frame, results, alpha=0.5, show_boxes=True, show_labels=True):
    """Aplica máscaras de segmentación con labels y bounding boxes"""
    if not results or len(results) == 0:
        return frame

    result = results[0]

    if result.masks is None or len(result.masks.data) == 0:
        return frame

    overlay = frame.copy()
    output = frame.copy()

    # Obtener datos
    masks = result.masks.data.cpu().numpy()
    boxes = result.boxes.xyxy.cpu().numpy() if result.boxes is not None else None
    scores = result.boxes.conf.cpu().numpy() if result.boxes is not None else None
    classes = result.boxes.cls.cpu().numpy().astype(int) if result.boxes is not None else None

    # Nombres de clase
    class_names = result.names if hasattr(result, 'names') else {}

    # Generar colores
    num_objects = len(masks)
    colors = generate_colors(max(len(class_names), 100))

    # Aplicar cada máscara
    for idx in range(num_objects):
        mask = masks[idx]

        # Redimensionar máscara
        mask_resized = cv2.resize(
            mask,
            (frame.shape[1], frame.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

        # Color para esta instancia
        class_id = classes[idx] if classes is not None else idx
        color = colors[class_id % len(colors)]

        # Aplicar color
        mask_bool = mask_resized > 0.5
        overlay[mask_bool] = color

        # Dibujar contorno
        contours, _ = cv2.findContours(
            (mask_resized > 0.5).astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(output, contours, -1, (255, 255, 255), 3)

    # Mezclar overlay
    result_frame = cv2.addWeighted(output, 1 - alpha, overlay, alpha, 0)

    # Dibujar boxes y labels
    if show_boxes and boxes is not None:
        for idx in range(num_objects):
            x1, y1, x2, y2 = boxes[idx].astype(int)
            class_id = classes[idx]
            score = scores[idx]
            class_name = class_names.get(class_id, f"class_{class_id}")
            color = colors[class_id % len(colors)]

            # Box
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)

            # Label
            if show_labels:
                label = f"{class_name} {score:.2f}"
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(result_frame, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
                cv2.putText(
                    result_frame,
                    label,
                    (x1 + 5, y1 - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

    return result_frame

def main():
    global running

    # Parsear prompts personalizados
    custom_classes = parse_prompts(CUSTOM_PROMPTS)

    if not custom_classes:
        print("ERROR: No se especificaron prompts en CUSTOM_PROMPTS")
        print("Edita la variable CUSTOM_PROMPTS al inicio del script")
        return

    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    # Verificar GPU
    if torch.cuda.is_available():
        print(f"✓ GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        device = 'cuda'
    else:
        print("⚠ GPU no detectada, usando CPU")
        device = 'cpu'

    print("\nCargando modelo YOLOE-11s-seg (con prompts)...")
    try:
        # YOLOE con soporte de prompts de texto y visuales
        model = YOLOE('yoloe-11s-seg.pt')
        model.to(device)
        print("✓ Modelo YOLOE-11s-seg cargado correctamente")
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        print("El modelo se descargará automáticamente...")
        return

    # Configurar prompts personalizados
    print(f"\n{'='*70}")
    print("PROMPTS PERSONALIZADOS CONFIGURADOS:")
    print(f"{'='*70}")
    for i, cls in enumerate(custom_classes, 1):
        print(f"  {i}. {cls}")
    print(f"\nTotal de clases: {len(custom_classes)}")
    print(f"{'='*70}\n")

    try:
        # Establecer las clases personalizadas
        model.set_classes(custom_classes, model.get_text_pe(custom_classes))
        print("✓ Prompts configurados correctamente")
        print("  Solo se detectarán las clases especificadas\n")
    except Exception as e:
        print(f"Error al configurar prompts: {e}")
        return

    print("Abriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Configurar resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  Resolución: {actual_width}x{actual_height}")

    # Configurar ventana
    window_name = 'YOLOE - Detección con Prompts Personalizados'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\n" + "="*70)
    print("YOLOE CON PROMPTS - DETECCIÓN ENFOCADA")
    print("="*70)
    print("MODO:")
    print(f"  • Detecta SOLO: {', '.join(custom_classes[:5])}")
    if len(custom_classes) > 5:
        print(f"    ... y {len(custom_classes)-5} más")
    print("  • Ignora todo lo demás (100% enfocado)")
    print("")
    print("CONTROLES:")
    print("  • 'c': Cambiar confianza (0.15/0.25/0.4)")
    print("  • 'b': Toggle bounding boxes")
    print("  • 'l': Toggle labels")
    print("  • 'i': Cambiar resolución (640/800/1024)")
    print("  • 'q' o ESC: Salir")
    print("")
    print("NOTA: Para cambiar objetos a detectar, edita CUSTOM_PROMPTS")
    print("="*70 + "\n")

    try:
        frame_count = 0
        fps_list = []

        # Configuración
        conf_threshold = 0.25
        show_boxes = True
        show_labels = True
        imgsz = 640

        print("Iniciando detección enfocada...\n")

        while running:
            # Capturar frame
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            # Medir tiempo
            start_time = time.time()

            # Ejecutar YOLOE con prompts
            results = model(
                frame,
                verbose=False,
                conf=conf_threshold,
                iou=0.7,
                max_det=30,
                device=device,
                imgsz=imgsz,
                retina_masks=True
            )

            # Aplicar máscaras
            display_frame = apply_masks_with_labels(
                frame,
                results,
                alpha=0.4,
                show_boxes=show_boxes,
                show_labels=show_labels
            )

            # Calcular FPS
            end_time = time.time()
            inference_time = end_time - start_time
            fps = 1.0 / inference_time if inference_time > 0 else 0
            fps_list.append(fps)

            # Contar objetos
            num_objects = 0
            if results and len(results) > 0 and results[0].masks is not None:
                num_objects = len(results[0].masks.data)

            # Información en pantalla
            avg_fps = np.mean(fps_list[-30:]) if len(fps_list) > 0 else 0

            # Panel
            info_y = 30
            cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Detectados: {num_objects}", (10, info_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Conf: {conf_threshold}", (10, info_y + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Mostrar prompts activos
            prompts_text = ", ".join(custom_classes[:3])
            if len(custom_classes) > 3:
                prompts_text += f"... (+{len(custom_classes)-3})"
            cv2.putText(display_frame, f"Prompts: {prompts_text}", (10, info_y + 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 255), 1)

            # Mostrar frame
            cv2.imshow(window_name, display_frame)

            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:
                break
            elif key == ord('c'):
                if conf_threshold == 0.15:
                    conf_threshold = 0.25
                elif conf_threshold == 0.25:
                    conf_threshold = 0.4
                else:
                    conf_threshold = 0.15
                print(f"→ Umbral de confianza: {conf_threshold}")
            elif key == ord('b'):
                show_boxes = not show_boxes
                print(f"→ Bounding boxes: {'ON' if show_boxes else 'OFF'}")
            elif key == ord('l'):
                show_labels = not show_labels
                print(f"→ Labels: {'ON' if show_labels else 'OFF'}")
            elif key == ord('i'):
                if imgsz == 640:
                    imgsz = 800
                elif imgsz == 800:
                    imgsz = 1024
                else:
                    imgsz = 640
                print(f"→ Tamaño de inferencia: {imgsz}px")
                fps_list = []

            frame_count += 1

            # Estadísticas
            if frame_count % 60 == 0 and len(fps_list) > 0:
                avg_fps = np.mean(fps_list[-60:])
                print(f"Frames: {frame_count} | FPS: {avg_fps:.1f} | Detectados: {num_objects}")

    except KeyboardInterrupt:
        print("\nInterrupción detectada")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Liberar recursos
        print("\nLiberando recursos...")
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        # Estadísticas finales
        if len(fps_list) > 0:
            print(f"\n" + "="*70)
            print("ESTADÍSTICAS FINALES:")
            print("="*70)
            print(f"Frames procesados: {frame_count}")
            print(f"FPS promedio: {np.mean(fps_list):.1f}")
            print(f"FPS máximo: {np.max(fps_list):.1f}")
            print(f"FPS mínimo: {np.min(fps_list):.1f}")
            print(f"Prompts usados: {', '.join(custom_classes)}")
            print("="*70)

if __name__ == "__main__":
    main()
