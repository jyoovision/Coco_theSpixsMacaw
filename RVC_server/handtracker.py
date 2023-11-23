import cv2
import mediapipe as mp

# MediaPipe 손바닥 인식 모듈 초기화
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# 웹캠에서 영상 캡처
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # BGR 이미지를 RGB로 변환
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # MediaPipe로 이미지 처리
    results = hands.process(image)

    # RGB 이미지를 BGR로 되돌림 (OpenCV에서 사용하기 위해)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 인식된 손바닥 정보를 화면에 그림
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 결과 이미지를 화면에 표시
    cv2.imshow("MediaPipe Hands", image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
