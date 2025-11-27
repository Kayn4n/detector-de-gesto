import cv2
import mediapipe as mp
import numpy as np
import os
import webbrowser

SPOTIFY_URI = "spotify:track:0cuJv0ZLfTp6XY77fXSA6N"  

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.6,
                       min_tracking_confidence=0.6,
                       model_complexity=1)


def checar_gesto_L(hand_landmarks):
    try:
        lm = hand_landmarks.landmark

        def estendido(tip, pip):
            return lm[tip].y < lm[pip].y - 0.02

        
        indicador = estendido(8, 6)

        
        polegar = lm[4].x < lm[3].x - 0.04 

       
        medio = estendido(12, 10)
        anelar = estendido(16, 14)
        minimo = estendido(20, 18)

        outros_fechados = (not medio) and (not anelar) and (not minimo)

        return indicador and polegar and outros_fechados

    except:
        return False

def abrir_spotify(uri):
    
    webbrowser.open(uri)


def abrir_camera(indices=(0, 1, 2, 3, 4)):
    for idx in indices:
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            for _ in range(5):
                ok, _ = cap.read()
                if not ok:
                    break
                cv2.waitKey(5)
            ok, _ = cap.read()
            if ok:
                print(f"Câmera aberta no índice {idx}")
                return cap
            cap.release()
    return None

cap = abrir_camera()
if cap is None:
    print("Não foi possível abrir a câmera.")
    raise SystemExit(1)

NOME_JANELA = 'Detector de Gestos'
cv2.namedWindow(NOME_JANELA, cv2.WINDOW_NORMAL)

musica_tocou = False  

try:
    while cap.isOpened():

        if cv2.getWindowProperty(NOME_JANELA, cv2.WND_PROP_VISIBLE) < 1:
            break

        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        gesto_L = False

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                if checar_gesto_L(hand):
                    gesto_L = True

        
        cv2.putText(frame, f"Fez o L: {'SIM' if gesto_L else 'NAO'}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        
        if gesto_L:
            cv2.putText(frame, "GESTO L DETECTADO!", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if not musica_tocou:
                print(">> Abrindo música no Spotify...")
                abrir_spotify(SPOTIFY_URI)
                musica_tocou = True

        else:
            musica_tocou = False  

        cv2.imshow(NOME_JANELA, frame)

        if cv2.waitKey(1) & 0xFF in (27, ord('q'), ord('Q')):
            break

except KeyboardInterrupt:
    print("Finalizado pelo usuário.")

finally:
    cap.release()
    cv2.destroyAllWindows()
