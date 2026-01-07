import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from keras.models import load_model
import os
import pygame
from flappy_game import FlappyGame

CNN_THRESHOLD = 0.5 
is_jumping = False

MODEL_PATH = os.path.join('models', 'hand_gesture_model.h5')
model = load_model(MODEL_PATH)
game = FlappyGame()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

print("Kusursuz Hibrit Model + Otomatik Sesler Aktif!")

while True:
    ret, frame = cap.read()
    if not ret: break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_prediction = "Bekleniyor..."
    color = (0, 0, 255)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            lm = hand_lms.landmark
            dist = np.sqrt((lm[8].x - lm[0].x)**2 + (lm[8].y - lm[0].y)**2)
            is_anatomically_fist = dist < 0.25 

            coords = [(int(l.x*w), int(l.y*h)) for l in hand_lms.landmark]
            x_min, y_min = max(0, min(c[0] for c in coords)-30), max(0, min(c[1] for c in coords)-30)
            x_max, y_max = min(w, max(c[0] for c in coords)+30), min(h, max(c[1] for c in coords)+30)
            
            try:
                roi = frame[y_min:y_max, x_min:x_max]
                if roi.size > 0:
                    img = cv2.resize(roi, (128, 128)) / 255.0
                    cnn_pred = model.predict(np.expand_dims(img, axis=0), verbose=0)[0][0]
                    
            
                    if cnn_pred < CNN_THRESHOLD and is_anatomically_fist:
                        if not is_jumping:
                            game.trigger_jump()
                            is_jumping = True
                        current_prediction = "YUMRUK: ZIPLA!"
                        color = (0, 255, 0)
                    else:
                        is_jumping = False
                        current_prediction = "ACIK EL: BEKLE"
                        color = (0, 0, 255)
            except: pass
            
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

    cv2.rectangle(frame, (0,0), (350, 60), (0,0,0), -1)
    cv2.putText(frame, current_prediction, (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("Final AI Kontrol", frame)

    game.run_frame()
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            cap.release(); cv2.destroyAllWindows(); pygame.quit(); exit()

cap.release()
cv2.destroyAllWindows()

