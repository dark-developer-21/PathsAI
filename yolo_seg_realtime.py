#!/usr/bin/env python3
"""
Script para segmentar objetos en tiempo real usando YOLOv8 Segmentation
Instance segmentation de alta velocidad optimizado para GPU
Mucho más rápido que SAM2 (~30-60 FPS vs ~1 FPS)
"""
from ultralytics import YOLO
import cv2
import signal
import sys
import numpy as np
import time
import torch

# Variables globales
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\nCerrando programa...")
    running = False

def generate_colors(n):
    """Genera N colores distintos para las máscaras"""
    np.random.seed(42)
    colors = []
    for i in range(n):
        color = np.random.randint(0, 255, 3).tolist()
        colors.append(tuple(color))
    return colors

def apply_segmentation_masks(frame, results, alpha=0.5, show_boxes=True, show_labels=True):
    """
    Aplica máscaras de segmentación con colores y labels
    Más customizable que el .plot() por defecto
    """
    if not results or len(results) == 0:
        return frame

    result = results[0]

    # Si no hay detecciones, retornar frame original
    if result.masks is None or len(result.masks.data) == 0:
        return frame

    overlay = frame.copy()
    output = frame.copy()

    # Obtener datos
    masks = result.masks.data.cpu().numpy()
    boxes = result.boxes.xyxy.cpu().numpy() if result.boxes is not None else None
    scores = result.boxes.conf.cpu().numpy() if result.boxes is not None else None
    classes = result.boxes.cls.cpu().numpy().astype(int) if result.boxes is not None else None
    class_names = result.names

    # Generar colores
    num_objects = len(masks)
    colors = generate_colors(100)  # Pool de colores

    # Aplicar cada máscara
    for idx in range(num_objects):
        mask = masks[idx]

        # Redimensionar máscara al tamaño del frame
        mask_resized = cv2.resize(
            mask,
            (frame.shape[1], frame.shape[0]),
            interpolation=cv2.INTER_NEAREST
        )

        # Color para esta clase
        class_id = classes[idx] if classes is not None else idx
        color = colors[class_id % len(colors)]

        # Aplicar color a la máscara
        mask_bool = mask_resized > 0.5
        overlay[mask_bool] = color

        # Dibujar contorno
        contours, _ = cv2.findContours(
            mask_resized.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(output, contours, -1, (255, 255, 255), 2)

    # Mezclar overlay con frame original
    output = cv2.addWeighted(output, 1 - alpha, overlay, alpha, 0)

    # Dibujar bounding boxes y labels si está habilitado
    if show_boxes and boxes is not None:
        for idx in range(num_objects):
            x1, y1, x2, y2 = boxes[idx].astype(int)
            class_id = classes[idx]
            score = scores[idx]
            class_name = class_names[class_id]

            # Color para esta clase
            color = colors[class_id % len(colors)]

            # Dibujar box
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)

            # Preparar label
            if show_labels:
                label = f"{class_name} {score:.2f}"

                # Fondo para el texto
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(output, (x1, y1 - 20), (x1 + w, y1), color, -1)

                # Texto
                cv2.putText(
                    output,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )

    return output

def main():
    global running

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

    print("\nCargando modelo YOLOv8 Segmentation...")
    try:
        # Modelos disponibles (de más rápido a más preciso):
        # yolov8n-seg.pt - Nano (MÁS RÁPIDO, ~60+ FPS)
        # yolov8s-seg.pt - Small (~45-55 FPS) ⭐ RECOMENDADO RTX 4070
        # yolov8m-seg.pt - Medium (~35-45 FPS)
        # yolov8l-seg.pt - Large (~25-35 FPS)
        # yolov8x-seg.pt - Extra Large (MÁS PRECISO, ~20-30 FPS)

        model = YOLO('yolov8s-seg.pt')  # Small - Balance perfecto para RTX 4070
        model.to(device)
        print(f"✓ Modelo YOLOv8-seg cargado en {device.upper()}")
        print("  Clases detectables: 80 (personas, vehículos, animales, objetos, etc.)")
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        print("Instalando dependencias: pip install ultralytics torch")
        return

    print("\nAbriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Configurar resolución (ajusta según tu preferencia)
    # Menor resolución = más FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Obtener resolución real
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  Resolución: {actual_width}x{actual_height}")

    # Configurar ventana
    window_name = 'YOLOv8 Segmentation - Tiempo Real'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\n" + "="*70)
    print("INSTRUCCIONES:")
    print("="*70)
    print("• Segmentación automática en tiempo real de 80 clases de objetos")
    print("• 'q' o ESC: Salir")
    print("• 'm': Cambiar modelo (nano/small/medium)")
    print("• 'c': Alternar umbral de confianza (0.25/0.5/0.7)")
    print("• 'b': Mostrar/ocultar bounding boxes")
    print("• 'l': Mostrar/ocultar labels")
    print("• Ctrl+C: Salir de emergencia")
    print("="*70 + "\n")

    try:
        frame_count = 0
        fps_list = []

        # Configuración ajustable
        current_model_idx = 1  # Empezamos en Small (índice 1)
        models = ['yolov8n-seg.pt', 'yolov8s-seg.pt', 'yolov8m-seg.pt']
        model_names = ['Nano (Rápido)', 'Small (Balanceado) ⭐', 'Medium (Preciso)']

        conf_threshold = 0.25  # Umbral de confianza
        show_boxes = True
        show_labels = True

        print("Iniciando detección (puede tardar en el primer frame)...\n")

        while running:
            # Capturar frame
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            # Medir tiempo de procesamiento
            start_time = time.time()

            # Ejecutar YOLO Segmentation
            results = model(
                frame,
                verbose=False,
                conf=conf_threshold,  # Umbral de confianza
                iou=0.45,            # Umbral de NMS
                max_det=50,          # Máximo de detecciones
                device=device
            )

            # Aplicar máscaras
            display_frame = apply_segmentation_masks(
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

            # Contar objetos detectados
            num_objects = 0
            if results and len(results) > 0 and results[0].masks is not None:
                num_objects = len(results[0].masks.data)

            # Mostrar información en pantalla
            avg_fps = np.mean(fps_list[-30:]) if len(fps_list) > 0 else 0

            # Panel de información
            info_y = 30
            cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Objetos: {num_objects}", (10, info_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Conf: {conf_threshold}", (10, info_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            cv2.putText(display_frame, f"Modelo: {model_names[current_model_idx]}", (10, info_y + 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            # Mostrar frame
            cv2.imshow(window_name, display_frame)

            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # q o ESC
                break
            elif key == ord('m'):  # Cambiar modelo
                current_model_idx = (current_model_idx + 1) % len(models)
                print(f"\n→ Cambiando a modelo: {model_names[current_model_idx]}")
                print("  Cargando...")
                model = YOLO(models[current_model_idx])
                model.to(device)
                fps_list = []  # Reset FPS counter
                print("  ✓ Modelo cargado")
            elif key == ord('c'):  # Cambiar confianza
                if conf_threshold == 0.25:
                    conf_threshold = 0.5
                elif conf_threshold == 0.5:
                    conf_threshold = 0.7
                else:
                    conf_threshold = 0.25
                print(f"→ Umbral de confianza: {conf_threshold}")
            elif key == ord('b'):  # Toggle boxes
                show_boxes = not show_boxes
                print(f"→ Bounding boxes: {'ON' if show_boxes else 'OFF'}")
            elif key == ord('l'):  # Toggle labels
                show_labels = not show_labels
                print(f"→ Labels: {'ON' if show_labels else 'OFF'}")

            frame_count += 1

            # Estadísticas cada 60 frames
            if frame_count % 60 == 0 and len(fps_list) > 0:
                avg_fps = np.mean(fps_list[-60:])
                print(f"Frames: {frame_count} | FPS: {avg_fps:.1f} | Objetos: {num_objects}")

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
            print(f"Modelo usado: {model_names[current_model_idx]}")
            print("="*70)

if __name__ == "__main__":
    main()
