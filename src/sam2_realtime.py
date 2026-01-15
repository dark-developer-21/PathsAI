#!/usr/bin/env python3
"""
Script para segmentar TODO en tiempo real usando SAM 2
Segmentación automática continua similar a YOLO detection
Optimizado para GPU (RTX 4070)
"""
from ultralytics import SAM
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
    np.random.seed(42)  # Para colores consistentes
    colors = []
    for i in range(n):
        colors.append(tuple(np.random.randint(0, 255, 3).tolist()))
    return colors

def apply_masks_overlay(frame, masks, alpha=0.5):
    """Aplica múltiples máscaras con colores diferentes sobre el frame"""
    if masks is None or len(masks) == 0:
        return frame

    overlay = frame.copy()

    # Generar colores para las máscaras
    colors = generate_colors(len(masks))

    for idx, mask in enumerate(masks):
        # Convertir máscara a formato correcto
        if isinstance(mask, torch.Tensor):
            mask_np = mask.cpu().numpy()
        else:
            mask_np = mask

        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]

        # Redimensionar si es necesario
        if mask_np.shape[0] != frame.shape[0] or mask_np.shape[1] != frame.shape[1]:
            mask_np = cv2.resize(
                mask_np.astype(np.uint8),
                (frame.shape[1], frame.shape[0]),
                interpolation=cv2.INTER_NEAREST
            )

        # Aplicar color a esta máscara
        color = colors[idx % len(colors)]
        overlay[mask_np > 0.5] = color

    # Mezclar con el frame original
    result = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)

    # Dibujar contornos para mejor visualización
    for idx, mask in enumerate(masks):
        if isinstance(mask, torch.Tensor):
            mask_np = mask.cpu().numpy()
        else:
            mask_np = mask

        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]

        if mask_np.shape[0] != frame.shape[0] or mask_np.shape[1] != frame.shape[1]:
            mask_np = cv2.resize(
                mask_np.astype(np.uint8),
                (frame.shape[1], frame.shape[0]),
                interpolation=cv2.INTER_NEAREST
            )

        # Encontrar contornos
        contours, _ = cv2.findContours(
            (mask_np > 0.5).astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Dibujar contornos
        cv2.drawContours(result, contours, -1, (255, 255, 255), 2)

    return result

def main():
    global running

    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    # Verificar disponibilidad de GPU
    if torch.cuda.is_available():
        print(f"✓ GPU detectada: {torch.cuda.get_device_name(0)}")
        print(f"  VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        device = 'cuda'
    else:
        print("⚠ GPU no detectada, usando CPU (será más lento)")
        device = 'cpu'

    print("\nCargando modelo SAM 2...")
    try:
        # Cargar modelo SAM 2
        sam_model = SAM('sam2_b.pt')
        # Mover modelo a GPU si está disponible
        sam_model.to(device)
        print("✓ Modelo SAM 2 cargado correctamente en", device.upper())
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        print("Asegúrate de tener instalado ultralytics: pip install ultralytics torch")
        return

    print("\nAbriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Configurar resolución (menor resolución = más FPS)
    # Puedes ajustar estos valores
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Configurar ventana
    window_name = 'SAM 2 - Segmentacion en Tiempo Real'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\n" + "="*60)
    print("INSTRUCCIONES:")
    print("="*60)
    print("• El modelo segmentará AUTOMÁTICAMENTE todo lo visible")
    print("• 'q' o ESC: Salir")
    print("• 'f': Alternar modo FPS (rápido/preciso)")
    print("• Ctrl+C: Salir de emergencia")
    print("="*60)
    print("\nIniciando segmentación en tiempo real...")
    print("(Puede tardar unos segundos en el primer frame)\n")

    try:
        frame_count = 0
        fps_list = []
        last_time = time.time()

        # Modo FPS: cada cuántos frames procesar
        # 1 = procesar todos (más preciso, más lento)
        # 2-3 = procesar 1 de cada N (más rápido, menos suave)
        process_every = 1
        last_masks = None

        while running:
            # Capturar frame
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            # Procesar solo cada N frames para mejorar FPS
            if frame_count % process_every == 0:
                try:
                    # Medir tiempo de procesamiento
                    start_time = time.time()

                    # Ejecutar SAM2 sin prompts para segmentar todo
                    # retina_masks=True mejora calidad, conf ajusta sensibilidad
                    results = sam_model(
                        frame,
                        verbose=False,
                        retina_masks=True,
                        imgsz=640,  # Tamaño de imagen para inferencia
                        conf=0.4,   # Umbral de confianza (ajustable 0-1)
                    )

                    # Extraer máscaras
                    if results and len(results) > 0:
                        masks_data = results[0].masks
                        if masks_data is not None and len(masks_data.data) > 0:
                            last_masks = masks_data.data
                        else:
                            last_masks = None
                    else:
                        last_masks = None

                    # Calcular FPS
                    end_time = time.time()
                    inference_time = end_time - start_time
                    fps = 1.0 / inference_time if inference_time > 0 else 0
                    fps_list.append(fps)

                except Exception as e:
                    print(f"Error al procesar frame: {e}")
                    last_masks = None

            # Aplicar máscaras (usar las últimas si no procesamos este frame)
            display_frame = frame.copy()
            if last_masks is not None:
                display_frame = apply_masks_overlay(display_frame, last_masks, alpha=0.4)

                # Mostrar número de objetos detectados
                num_objects = len(last_masks)
                cv2.putText(
                    display_frame,
                    f"Objetos: {num_objects}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

            # Mostrar FPS promedio
            if len(fps_list) > 0:
                avg_fps = np.mean(fps_list[-30:])  # Promedio últimos 30 frames
                cv2.putText(
                    display_frame,
                    f"FPS: {avg_fps:.1f}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2
                )

            # Mostrar modo de procesamiento
            mode_text = f"Modo: {'PRECISO' if process_every == 1 else f'RAPIDO (1/{process_every})'}"
            cv2.putText(
                display_frame,
                mode_text,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                2
            )

            # Mostrar frame
            cv2.imshow(window_name, display_frame)

            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # q o ESC
                break
            elif key == ord('f'):  # Cambiar modo FPS
                if process_every == 1:
                    process_every = 2
                    print("→ Modo RÁPIDO activado (procesa 1/2 frames)")
                else:
                    process_every = 1
                    print("→ Modo PRECISO activado (procesa todos los frames)")

            frame_count += 1

            # Mostrar estadísticas cada 30 frames
            if frame_count % 30 == 0 and len(fps_list) > 0:
                avg_fps = np.mean(fps_list[-30:])
                print(f"Frames: {frame_count} | FPS promedio: {avg_fps:.1f} | Objetos: {len(last_masks) if last_masks is not None else 0}")

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
            print(f"\n" + "="*60)
            print("ESTADÍSTICAS FINALES:")
            print("="*60)
            print(f"Frames procesados: {frame_count}")
            print(f"FPS promedio: {np.mean(fps_list):.1f}")
            print(f"FPS máximo: {np.max(fps_list):.1f}")
            print(f"FPS mínimo: {np.min(fps_list):.1f}")
            print("="*60)

if __name__ == "__main__":
    main()
