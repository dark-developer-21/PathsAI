#!/usr/bin/env python3
"""
Script para segmentar objetos en tiempo real usando SAM 3 y webcam
Permite buscar objetos por texto (ej: "persona", "celular", "taza")
"""
from ultralytics.models.sam import SAM3SemanticPredictor
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

    print("=== SAM 3 - Segmentacion por Conceptos ===")
    print("\nEjemplos de conceptos que puedes buscar:")
    print("  - person, people (persona/s)")
    print("  - cell phone, phone (celular)")
    print("  - cup, bottle (taza, botella)")
    print("  - keyboard, mouse (teclado, raton)")
    print("  - book, glasses (libro, lentes)")
    print("  - hand, face (mano, cara)")

    # Pedir al usuario que conceptos quiere segmentar
    print("\nIngresa los conceptos a buscar separados por comas")
    print("Ejemplo: person, cell phone, cup")
    concepts_input = input("Conceptos: ").strip()

    if not concepts_input:
        print("Usando conceptos por defecto: person, cell phone")
        concepts = ["person", "cell phone"]
    else:
        concepts = [c.strip() for c in concepts_input.split(",")]

    print(f"\nBuscando: {', '.join(concepts)}")
    print("\nCargando modelo SAM 3...")

    # Configurar predictor
    overrides = dict(
        conf=0.25,  # Umbral de confianza
        task="segment",
        mode="predict",
        model="models/sam3.pt",
        half=True,  # Usar FP16 para inferencia mas rapida
        save=False,
        verbose=False
    )

    try:
        predictor = SAM3SemanticPredictor(overrides=overrides)
    except Exception as e:
        print(f"\nError: No se pudo cargar el modelo SAM 3")
        print(f"Asegurate de tener el archivo 'models/sam3.pt' descargado")
        print(f"Descargalo desde: https://huggingface.co/facebook/sam3")
        print(f"\nError tecnico: {e}")
        return

    print("Abriendo webcam...")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return

    # Nombre de la ventana
    window_name = 'SAM 3 - Segmentacion en tiempo real'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("\nPresiona 'q' para salir, 'c' para cambiar conceptos, o Ctrl+C")
    print("Procesando frames...")

    try:
        frame_count = 0

        while running:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame")
                break

            try:
                # Configurar imagen en el predictor
                predictor.set_image(frame)

                # Realizar segmentacion con los conceptos especificados
                results = predictor(text=concepts)

                # Si hay resultados, dibujarlos
                if results and len(results) > 0:
                    result = results[0]

                    # Obtener frame anotado con las mascaras
                    if hasattr(result, 'plot'):
                        annotated_frame = result.plot()
                    else:
                        annotated_frame = frame

                    # Mostrar informacion de detecciones
                    if hasattr(result, 'boxes') and result.boxes is not None:
                        num_detections = len(result.boxes)
                        cv2.putText(
                            annotated_frame,
                            f"Detectados: {num_detections}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )
                else:
                    annotated_frame = frame
                    cv2.putText(
                        annotated_frame,
                        "No se encontraron objetos",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2
                    )

            except Exception as e:
                print(f"Error en frame {frame_count}: {e}")
                annotated_frame = frame

            # Mostrar conceptos buscados
            y_offset = 60
            for concept in concepts:
                cv2.putText(
                    annotated_frame,
                    f"Buscando: {concept}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    1
                )
                y_offset += 25

            cv2.imshow(window_name, annotated_frame)

            key = cv2.waitKey(10) & 0xFF

            # Salir con 'q' o ESC
            if key == ord('q') or key == 27:
                break

            # Cambiar conceptos con 'c'
            elif key == ord('c'):
                print("\n--- Cambiar conceptos ---")
                new_concepts = input("Nuevos conceptos (separados por comas): ").strip()
                if new_concepts:
                    concepts = [c.strip() for c in new_concepts.split(",")]
                    print(f"Ahora buscando: {', '.join(concepts)}")

            frame_count += 1

            # Verificar si la ventana fue cerrada manualmente
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            except:
                # Ignorar error en sistemas con Wayland
                pass

    except KeyboardInterrupt:
        print("\nInterrupcion detectada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Liberando recursos...")
        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        print(f"Programa terminado. Frames procesados: {frame_count}")

if __name__ == "__main__":
    main()
