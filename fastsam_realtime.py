#!/usr/bin/env python3
"""
Script para segmentar CUALQUIER COSA en tiempo real usando FastSAM
Segmentación automática continua con capacidad de prompts
Optimizado para GPU (RTX 4070) - ~15-20 FPS
"""
from ultralytics import FastSAM
from ultralytics.models.fastsam import FastSAMPredictor
import cv2
import signal
import sys
import numpy as np
import time
import torch

# Variables globales
running = True
prompt_mode = False
prompt_point = None
prompt_bbox = None
bbox_start = None
drawing_bbox = False

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\nCerrando programa...")
    running = False

def mouse_callback(event, x, y, flags, param):
    """Maneja clicks del mouse para prompts interactivos"""
    global prompt_point, prompt_bbox, bbox_start, drawing_bbox

    if not prompt_mode:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing_bbox:
            # Primer click - guardar punto o iniciar bbox
            if flags & cv2.EVENT_FLAG_SHIFTKEY:
                # Shift + Click = Punto prompt
                prompt_point = [x, y]
                prompt_bbox = None
                print(f"→ Punto seleccionado: ({x}, {y})")
            else:
                # Click normal = Inicio de bbox
                bbox_start = [x, y]
                drawing_bbox = True
                prompt_bbox = None
                prompt_point = None

    elif event == cv2.EVENT_LBUTTONUP:
        if drawing_bbox and bbox_start is not None:
            # Finalizar bbox
            x1, y1 = bbox_start
            x2, y2 = x, y
            # Asegurar que x1,y1 sea esquina superior izquierda
            prompt_bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
            drawing_bbox = False
            bbox_start = None
            prompt_point = None
            print(f"→ Bbox seleccionada: {prompt_bbox}")

def generate_colors(n):
    """Genera N colores distintos para las máscaras"""
    np.random.seed(42)
    colors = []
    for i in range(n):
        colors.append(tuple(np.random.randint(0, 255, 3).tolist()))
    return colors

def filter_small_masks(masks, frame_shape, min_area_percent=0.5):
    """Filtra máscaras pequeñas basándose en área mínima"""
    if masks is None or len(masks) == 0:
        return []

    filtered = []
    total_pixels = frame_shape[0] * frame_shape[1]
    min_pixels = total_pixels * (min_area_percent / 100)

    for mask in masks:
        if isinstance(mask, torch.Tensor):
            mask_np = mask.cpu().numpy()
        else:
            mask_np = mask

        if len(mask_np.shape) == 3:
            mask_np = mask_np[0]

        # Contar píxeles activos
        num_pixels = np.sum(mask_np > 0.5)

        if num_pixels >= min_pixels:
            filtered.append(mask)

    return filtered

def apply_masks_overlay(frame, masks, alpha=0.5, min_area_percent=0.5):
    """Aplica múltiples máscaras con colores diferentes sobre el frame"""
    if masks is None or len(masks) == 0:
        return frame

    # Filtrar máscaras pequeñas
    masks = filter_small_masks(masks, frame.shape, min_area_percent)

    if len(masks) == 0:
        return frame

    overlay = frame.copy()
    output = frame.copy()

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
                mask_np.astype(np.float32),
                (frame.shape[1], frame.shape[0]),
                interpolation=cv2.INTER_NEAREST
            )

        # Aplicar color a esta máscara
        color = colors[idx % len(colors)]
        mask_bool = mask_np > 0.5
        overlay[mask_bool] = color

        # Dibujar contorno más grueso para mejor visibilidad
        contours, _ = cv2.findContours(
            (mask_np > 0.5).astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        cv2.drawContours(output, contours, -1, (255, 255, 255), 3)

    # Mezclar overlay con frame original
    result = cv2.addWeighted(output, 1 - alpha, overlay, alpha, 0)

    return result

def main():
    global running, prompt_mode, prompt_point, prompt_bbox, drawing_bbox, bbox_start

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

    print("\nCargando modelo FastSAM...")
    try:
        # FastSAM-s.pt (más rápido ~15-20 FPS) o FastSAM-x.pt (más preciso ~10-15 FPS)
        model = FastSAM('FastSAM-s.pt')
        print("✓ Modelo FastSAM-s cargado correctamente")
        print("  Capacidad: Segmenta CUALQUIER COSA (no limitado a clases)")
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        print("El modelo se descargará automáticamente...")
        return

    print("\nAbriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Configurar resolución
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Obtener resolución real
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  Resolución: {actual_width}x{actual_height}")

    # Configurar ventana
    window_name = 'FastSAM - Segment Anything en Tiempo Real'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n" + "="*70)
    print("INSTRUCCIONES - FastSAM OPTIMIZADO:")
    print("="*70)
    print("MODO AUTOMÁTICO (default):")
    print("  • Segmenta solo objetos GRANDES (>1% del frame)")
    print("  • Máximo 20 objetos simultáneos")
    print("")
    print("MODO PROMPTS INTERACTIVOS (tecla 'p'):")
    print("  • Shift + Click: Segmentar objeto en punto")
    print("  • Click y arrastrar: Segmentar objeto en bbox")
    print("  • 'r': Reiniciar prompts")
    print("")
    print("CONTROLES:")
    print("  • 'p': Alternar modo Prompts ON/OFF")
    print("  • 'c': Cambiar umbral de confianza (0.4/0.6/0.8)")
    print("  • 'a': Cambiar área mínima (0.5%/1%/2%/5%)")
    print("  • 'q' o ESC: Salir")
    print("  • Ctrl+C: Salir de emergencia")
    print("="*70 + "\n")

    try:
        frame_count = 0
        fps_list = []

        # Configuración optimizada para reducir fragmentación
        conf_threshold = 0.6  # Mayor confianza = menos detecciones falsas
        min_area_percent = 1.0  # Filtrar máscaras menores al 1% del frame
        last_results = None  # Para modo prompts

        print("Iniciando segmentación en tiempo real...\n")

        while running:
            # Capturar frame
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            display_frame = frame.copy()

            # Modo automático - procesar cada frame
            if not prompt_mode:
                start_time = time.time()

                try:
                    # Ejecutar FastSAM para segmentar todo (optimizado)
                    results = model(
                        frame,
                        device=device,
                        retina_masks=True,
                        imgsz=1024,
                        conf=conf_threshold,
                        iou=0.7,  # Más agresivo fusionando máscaras superpuestas
                        max_det=20,  # Limitar a máximo 20 objetos
                        verbose=False
                    )

                    # Extraer y filtrar máscaras
                    if results and len(results) > 0:
                        masks_data = results[0].masks
                        if masks_data is not None and len(masks_data.data) > 0:
                            masks = masks_data.data
                            display_frame = apply_masks_overlay(
                                display_frame,
                                masks,
                                alpha=0.4,
                                min_area_percent=min_area_percent
                            )
                            # Contar objetos DESPUÉS del filtro
                            filtered_masks = filter_small_masks(masks, frame.shape, min_area_percent)
                            num_objects = len(filtered_masks)
                        else:
                            num_objects = 0
                    else:
                        num_objects = 0

                except Exception as e:
                    print(f"Error al procesar frame: {e}")
                    num_objects = 0

                # Calcular FPS
                end_time = time.time()
                inference_time = end_time - start_time
                fps = 1.0 / inference_time if inference_time > 0 else 0
                fps_list.append(fps)

            else:
                # Modo prompts - solo procesar cuando hay un prompt activo
                num_objects = 0

                # Procesar prompts cada 10 frames para mantener fluidez
                if frame_count % 10 == 0:
                    start_time = time.time()

                    try:
                        # Primero ejecutar "segment everything" (optimizado)
                        everything_results = model(
                            frame,
                            device=device,
                            retina_masks=True,
                            imgsz=1024,
                            conf=conf_threshold,
                            iou=0.7,
                            max_det=20,
                            verbose=False
                        )

                        # Si hay prompt activo, aplicarlo
                        if prompt_point is not None:
                            # Prompt de punto
                            results = model(
                                frame,
                                points=[prompt_point],
                                labels=[1],
                                device=device,
                                retina_masks=True,
                                verbose=False
                            )
                        elif prompt_bbox is not None:
                            # Prompt de bbox
                            results = model(
                                frame,
                                bboxes=[prompt_bbox],
                                device=device,
                                retina_masks=True,
                                verbose=False
                            )
                        else:
                            # Sin prompt - mostrar todo
                            results = everything_results

                        last_results = results

                    except Exception as e:
                        print(f"Error al procesar prompt: {e}")

                    end_time = time.time()
                    inference_time = end_time - start_time
                    fps = 1.0 / inference_time if inference_time > 0 else 0
                    fps_list.append(fps)

                # Aplicar últimos resultados
                if last_results and len(last_results) > 0:
                    masks_data = last_results[0].masks
                    if masks_data is not None and len(masks_data.data) > 0:
                        masks = masks_data.data
                        display_frame = apply_masks_overlay(
                            display_frame,
                            masks,
                            alpha=0.4,
                            min_area_percent=min_area_percent
                        )
                        filtered_masks = filter_small_masks(masks, frame.shape, min_area_percent)
                        num_objects = len(filtered_masks)

                # Dibujar prompt visual
                if prompt_point is not None:
                    cv2.circle(display_frame, tuple(prompt_point), 8, (0, 0, 255), -1)
                    cv2.circle(display_frame, tuple(prompt_point), 12, (255, 255, 255), 2)
                elif prompt_bbox is not None:
                    x1, y1, x2, y2 = prompt_bbox
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                elif drawing_bbox and bbox_start is not None:
                    # Mostrar bbox mientras se dibuja
                    cv2.rectangle(display_frame, tuple(bbox_start),
                                (int(cv2.getWindowImageRect(window_name)[0]),
                                 int(cv2.getWindowImageRect(window_name)[1])),
                                (255, 255, 0), 2)

            # Mostrar información en pantalla
            avg_fps = np.mean(fps_list[-30:]) if len(fps_list) > 0 else 0

            # Panel superior
            info_y = 30
            mode_text = "PROMPTS" if prompt_mode else "AUTO"
            mode_color = (255, 100, 0) if prompt_mode else (0, 255, 0)

            cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Objetos: {num_objects}", (10, info_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.putText(display_frame, f"Modo: {mode_text}", (10, info_y + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)

            cv2.putText(display_frame, f"Conf: {conf_threshold}", (10, info_y + 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            cv2.putText(display_frame, f"Area min: {min_area_percent}%", (10, info_y + 140),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

            # Instrucciones modo prompts
            if prompt_mode:
                instructions = [
                    "Shift+Click: Punto | Click+Arrastre: Bbox",
                    "'r': Reiniciar | 'p': Volver a auto"
                ]
                for i, text in enumerate(instructions):
                    cv2.putText(display_frame, text,
                               (10, display_frame.shape[0] - 50 + i*25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

            # Mostrar frame
            cv2.imshow(window_name, display_frame)

            # Procesar teclas
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # q o ESC
                break
            elif key == ord('p'):  # Toggle modo prompts
                prompt_mode = not prompt_mode
                prompt_point = None
                prompt_bbox = None
                bbox_start = None
                drawing_bbox = False
                last_results = None
                mode_name = "PROMPTS INTERACTIVOS" if prompt_mode else "AUTOMÁTICO"
                print(f"\n→ Modo {mode_name} activado")
            elif key == ord('c'):  # Cambiar confianza
                if conf_threshold == 0.4:
                    conf_threshold = 0.6
                elif conf_threshold == 0.6:
                    conf_threshold = 0.8
                else:
                    conf_threshold = 0.4
                print(f"→ Umbral de confianza: {conf_threshold}")
            elif key == ord('a'):  # Cambiar área mínima
                if min_area_percent == 0.5:
                    min_area_percent = 1.0
                elif min_area_percent == 1.0:
                    min_area_percent = 2.0
                elif min_area_percent == 2.0:
                    min_area_percent = 5.0
                else:
                    min_area_percent = 0.5
                print(f"→ Área mínima: {min_area_percent}% (filtra objetos pequeños)")
            elif key == ord('r'):  # Reiniciar prompts
                prompt_point = None
                prompt_bbox = None
                bbox_start = None
                drawing_bbox = False
                print("→ Prompts reiniciados")

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
            print("="*70)

if __name__ == "__main__":
    main()
