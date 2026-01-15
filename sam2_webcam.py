#!/usr/bin/env python3
"""
Script para segmentar objetos en tiempo real usando SAM 2 y webcam
Segmentación interactiva con clicks del mouse
"""
from ultralytics import SAM
import cv2
import signal
import sys
import numpy as np

# Variables globales
running = True
current_point = None
current_mask = None
freeze_frame = None
selecting_mode = True
sam_model = None

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\nCerrando programa...")
    running = False

def mouse_callback(event, x, y, flags, param):
    """Maneja clicks del mouse para seleccionar objetos"""
    global current_point, selecting_mode, freeze_frame

    if event == cv2.EVENT_LBUTTONDOWN and selecting_mode and freeze_frame is not None:
        current_point = [x, y]
        print(f"Punto seleccionado: ({x}, {y})")

def apply_mask_overlay(frame, mask, color=(0, 255, 0), alpha=0.5):
    """Aplica una máscara semitransparente sobre el frame"""
    overlay = frame.copy()

    # Convertir máscara a formato correcto
    if len(mask.shape) == 3:
        mask = mask[0]  # Tomar primera máscara si hay múltiples

    # Crear overlay de color donde la máscara es True
    overlay[mask > 0.5] = color

    # Mezclar con el frame original
    result = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)

    return result

def segment_object(frame, point):
    """Segmenta objeto usando SAM 2 con un punto"""
    global sam_model, current_mask

    try:
        # Ejecutar predicción con el punto
        results = sam_model(frame, points=[point], labels=[1])

        if results and len(results) > 0:
            # Obtener la máscara del resultado
            masks = results[0].masks
            if masks is not None and len(masks.data) > 0:
                # Tomar la primera máscara (mejor predicción)
                mask = masks.data[0].cpu().numpy()
                current_mask = mask
                print("✓ Objeto segmentado correctamente")
                return mask

        print("⚠ No se pudo generar máscara")
        return None

    except Exception as e:
        print(f"Error al segmentar: {e}")
        return None

def main():
    global running, current_point, current_mask, freeze_frame, selecting_mode, sam_model

    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    print("Cargando modelo SAM 2...")
    try:
        # Cargar modelo SAM 2 (se descarga automáticamente si no existe)
        sam_model = SAM('sam2_b.pt')
        print("✓ Modelo SAM 2 cargado correctamente")
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        print("Asegúrate de tener instalado ultralytics: pip install ultralytics")
        return

    print("Abriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Configurar ventana
    window_name = 'SAM 2 - Segmentacion Interactiva'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("\n" + "="*60)
    print("INSTRUCCIONES:")
    print("="*60)
    print("• ESPACIO: Congelar imagen y seleccionar nuevo objeto")
    print("• Click izquierdo: Seleccionar punto en objeto (en modo selección)")
    print("• 'r': Reiniciar segmentación")
    print("• 'q' o ESC: Salir")
    print("• Ctrl+C: Salir de emergencia")
    print("="*60 + "\n")

    try:
        frame_count = 0

        while running:
            if not selecting_mode:
                # Modo normal: capturar y mostrar con máscara
                ret, frame = cap.read()
                if not ret:
                    print("Error al capturar frame")
                    break

                display_frame = frame.copy()

                # Aplicar máscara si existe
                if current_mask is not None:
                    # Redimensionar máscara al tamaño del frame
                    mask_resized = cv2.resize(
                        current_mask.astype(np.uint8),
                        (frame.shape[1], frame.shape[0]),
                        interpolation=cv2.INTER_NEAREST
                    )
                    display_frame = apply_mask_overlay(display_frame, mask_resized)

                    # Agregar texto indicando que hay objeto segmentado
                    cv2.putText(
                        display_frame,
                        "Objeto segmentado (ESPACIO para nuevo)",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

            else:
                # Modo selección: mostrar frame congelado
                if freeze_frame is not None:
                    display_frame = freeze_frame.copy()

                    # Dibujar punto seleccionado si existe
                    if current_point is not None:
                        cv2.circle(display_frame, tuple(current_point), 5, (0, 0, 255), -1)
                        cv2.circle(display_frame, tuple(current_point), 8, (255, 255, 255), 2)

                    # Instrucciones en pantalla
                    cv2.putText(
                        display_frame,
                        "MODO SELECCION: Click en objeto",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )
                    cv2.putText(
                        display_frame,
                        "Presiona ESPACIO para continuar",
                        (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )
                else:
                    # Primera vez, capturar frame
                    ret, frame = cap.read()
                    if not ret:
                        break
                    freeze_frame = frame.copy()
                    display_frame = freeze_frame.copy()

            # Mostrar frame
            cv2.imshow(window_name, display_frame)

            # Procesar teclas
            key = cv2.waitKey(10) & 0xFF

            if key == ord('q') or key == 27:  # q o ESC
                break
            elif key == ord(' '):  # ESPACIO
                if selecting_mode and current_point is not None:
                    # Segmentar objeto y volver a modo normal
                    print("Segmentando objeto...")
                    mask = segment_object(freeze_frame, current_point)
                    if mask is not None:
                        selecting_mode = False
                        freeze_frame = None
                        print("✓ Volviendo a modo normal")
                elif not selecting_mode:
                    # Entrar en modo selección
                    print("Entrando en modo selección...")
                    ret, frame = cap.read()
                    if ret:
                        freeze_frame = frame.copy()
                        selecting_mode = True
                        current_point = None
                        current_mask = None
                else:
                    print("⚠ Primero selecciona un punto con click izquierdo")
            elif key == ord('r'):  # Reiniciar
                print("Reiniciando...")
                current_point = None
                current_mask = None
                freeze_frame = None
                selecting_mode = True

            frame_count += 1

    except KeyboardInterrupt:
        print("\nInterrupción detectada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Liberar recursos
        print("Liberando recursos...")
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        print(f"Programa terminado. Frames procesados: {frame_count}")

if __name__ == "__main__":
    main()
