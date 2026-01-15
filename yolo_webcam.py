#!/usr/bin/env python3
"""
Script para detectar objetos en tiempo real usando YOLOv8 y webcam
"""
from ultralytics import YOLO
import cv2
import signal
import sys

# Variable global para manejar el cierre
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\nCerrando programa...")
    running = False

def main():
    global running

    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)

    print("Cargando modelo YOLO...")
    # Puedes cambiar 'yolov8n.pt' por 'yolov8s.pt', 'yolov8m.pt', etc.
    # n = nano (más rápido), s = small, m = medium, l = large, x = extra large
    model = YOLO('yolov8n.pt')

    print("Abriendo webcam...")
    # 0 es la webcam por defecto, si tienes varias prueba con 1, 2, etc.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Nombre de la ventana (constante para evitar crear múltiples ventanas)
    window_name = 'YOLO - Deteccion en tiempo real'

    # Crear la ventana una sola vez
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("Presiona 'q' para salir o Ctrl+C")

    try:
        frame_count = 0
        while running:
            # Capturar frame
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            # Detectar objetos
            results = model(frame, verbose=False)

            # Dibujar resultados en el frame
            annotated_frame = results[0].plot()

            # Mostrar frame con detecciones en la ventana ya creada
            cv2.imshow(window_name, annotated_frame)

            # Esperar 10ms en lugar de 1ms para dar tiempo al sistema de ventanas
            key = cv2.waitKey(10) & 0xFF

            # Salir con 'q' o ESC
            if key == ord('q') or key == 27:
                break

            frame_count += 1

    except KeyboardInterrupt:
        print("\nInterrupción detectada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Liberar recursos SIEMPRE
        print("Liberando recursos...")
        cap.release()
        cv2.destroyAllWindows()
        # Esperar un momento para que las ventanas se cierren
        cv2.waitKey(1)
        print(f"Programa terminado. Frames procesados: {frame_count}")

if __name__ == "__main__":
    main()
