# import cv2
# import mediapipe as mp
# import numpy as np


# # 거리 계산 함수
# def calculate_distance(landmark1, landmark2, frame):
#     h, w, _ = frame.shape
#     x1, y1 = int(landmark1.x * w), int(landmark1.y * h)
#     x2, y2 = int(landmark2.x * w), int(landmark2.y * h)
#     distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
#     return distance


# def isOpenHand(hand_landmarks, frame):
#     h, w, _ = frame.shape

#     # 손가락 끝 인덱스와 손목 위치를 NumPy 배열로 변환
#     tips = np.array([hand_landmarks.landmark[tip] for tip in [4, 8, 12, 16, 20]])
#     wrist = np.array([hand_landmarks.landmark[0]] * 5)  # 같은 손목 위치를 5번 반복

#     # 화면 크기에 따라 위치 조정
#     tips = np.array([[tip.x * w, tip.y * h] for tip in tips])
#     wrist = np.array([[wrist[i].x * w, wrist[i].y * h] for i in range(5)])

#     # 거리 계산 (유클리디안 거리)
#     heights = np.sqrt(np.sum((tips - wrist) ** 2, axis=1))

#     # 너비 조건 체크
#     width = calculate_distance(
#         hand_landmarks.landmark[5], hand_landmarks.landmark[17], frame
#     )

#     # 모든 손가락의 거리가 100 이상인지 확인
#     if np.all(heights >= 10) and width > 40:
#         return True, width
#     return False, 0


# # 손 끝 인덱스
# hello_features = [1, 2, 3, 4, 7, 8, 11, 12, 15, 16, 19, 20]

# # 이전 프레임의 손 끝 위치 저장
# prev_hello_features_positions = {i: None for i in hello_features}

# # 그리팅 상태 체크를 위한 변수
# movement_left_count, movement_right_count, movement_count = 0, 0, 0

# noHandCount = 0
# isUniqueHand = False


# # 미디어파이프 초기화
# mp_hands = mp.solutions.hands
# mp_drawing = mp.solutions.drawing_utils
# hands = mp_hands.Hands()

# # 카메라 캡처
# cap = cv2.VideoCapture(0)


# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         continue

#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = hands.process(frame_rgb)

#     if results.multi_hand_landmarks:
#         for hand_landmarks in results.multi_hand_landmarks:
#             hand_open, width = isOpenHand(hand_landmarks, frame)

#             # 조건 체크
#             if hand_open:
#                 # 이전 프레임과의 비교로 오른쪽 왼쪽 움직임 체크
#                 for tip in hello_features:
#                     current_x = hand_landmarks.landmark[tip].x
#                     if prev_hello_features_positions[tip] is not None:
#                         prev_x = prev_hello_features_positions[tip]
#                         movement = current_x - prev_x
#                         if movement > width * 0.001:  # 임의의 움직임 기준 (우로 움직임)
#                             movement_right_count += 1
#                             movement_count += 1
#                         elif movement < width * -0.001:  # 임의의 움직임 기준 (좌로 움직임)
#                             movement_left_count += 1
#                             movement_count += 1
#                         movement_detected = True
#                     prev_hello_features_positions[tip] = current_x

#                 # print(movement_left_count, movement_right_count)

#                 if (
#                     movement_count >= 30
#                     and movement_left_count >= 10
#                     and movement_right_count >= 10
#                     and not isUniqueHand
#                 ):
#                     print("Greeting Detected")
#                     isUniqueHand = True
#                     movement_left_count, movement_right_count, movement_count = (
#                         0,
#                         0,
#                         0,
#                     )

#                 # 조건을 만족할 때만 흰색으로 손 관절 그리기
#                 mp_drawing.draw_landmarks(
#                     frame,
#                     hand_landmarks,
#                     mp_hands.HAND_CONNECTIONS,
#                     mp_drawing.DrawingSpec(
#                         color=(0, 0, 0), thickness=1, circle_radius=2
#                     ),
#                     mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2),
#                 )

#                 # 각 관절의 인덱스 표시
#                 for idx, landmark in enumerate(hand_landmarks.landmark):
#                     x, y = int(landmark.x * frame.shape[1]), int(
#                         landmark.y * frame.shape[0]
#                     )
#                     cv2.putText(
#                         frame,
#                         str(idx),
#                         (x, y),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         0.4,
#                         (255, 255, 255),
#                         1,
#                     )

#     else:
#         noHandCount += 1
#         if noHandCount >= 6:
#             isUniqueHand = False
#             movement_left_count, movement_right_count, movement_count = 0, 0, 0

#     cv2.imshow("Hand Tracking", frame)

#     if cv2.waitKey(5) & 0xFF == 27:
#         break

# cap.release()
# cv2.destroyAllWindows()


import cv2
import mediapipe as mp
import numpy as np


# 거리 계산 함수
def calculate_distance(landmark1, landmark2, frame):
    h, w, _ = frame.shape
    x1, y1 = int(landmark1.x * w), int(landmark1.y * h)
    x2, y2 = int(landmark2.x * w), int(landmark2.y * h)
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def isOpenHand(hand_landmarks, frame):
    h, w, _ = frame.shape

    # 손가락 끝 인덱스와 손목 위치를 NumPy 배열로 변환
    tips = np.array([hand_landmarks.landmark[tip] for tip in [4, 8, 12, 16, 20]])
    wrist = np.array([hand_landmarks.landmark[0]] * 5)  # 같은 손목 위치를 5번 반복

    # 화면 크기에 따라 위치 조정
    tips = np.array([[tip.x * w, tip.y * h] for tip in tips])
    wrist = np.array([[wrist[i].x * w, wrist[i].y * h] for i in range(5)])

    # 거리 계산 (유클리디안 거리)
    heights = np.sqrt(np.sum((tips - wrist) ** 2, axis=1))

    # 너비 조건 체크
    width = calculate_distance(
        hand_landmarks.landmark[5], hand_landmarks.landmark[17], frame
    )

    # 모든 손가락의 거리가 100 이상인지 확인
    if np.all(heights >= 10) and width > 40:
        return True, width
    return False, 0


class HandTracker:
    def __init__(self, on_greeting_detected):
        self.on_greeting_detected = on_greeting_detected
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_drawing = mp.solutions.drawing_utils
        self.hello_features = [1, 2, 3, 4, 7, 8, 11, 12, 15, 16, 19, 20]
        self.prev_hello_features_positions = {i: None for i in self.hello_features}

        self.movement_left_count, self.movement_right_count, self.movement_count = (
            0,
            0,
            0,
        )
        self.noHandCount = 0
        self.isUniqueHand = False

    def start(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand_open, width = isOpenHand(hand_landmarks, frame)

                if hand_open:
                    # 이전 프레임과의 비교로 오른쪽 왼쪽 움직임 체크
                    for tip in self.hello_features:
                        current_x = hand_landmarks.landmark[tip].x
                        if self.prev_hello_features_positions[tip] is not None:
                            prev_x = self.prev_hello_features_positions[tip]
                            movement = current_x - prev_x
                            if movement > width * 0.001:  # 임의의 움직임 기준 (우로 움직임)
                                movement_right_count += 1
                                movement_count += 1
                            elif movement < width * -0.001:  # 임의의 움직임 기준 (좌로 움직임)
                                movement_left_count += 1
                                movement_count += 1
                            movement_detected = True
                        self.prev_hello_features_positions[tip] = current_x

                    # print(movement_left_count, movement_right_count)

                    if (
                        movement_count >= 30
                        and movement_left_count >= 10
                        and movement_right_count >= 10
                        and not isUniqueHand
                    ):
                        print("Greeting Detected")
                        isUniqueHand = True
                        movement_left_count, movement_right_count, movement_count = (
                            0,
                            0,
                            0,
                        )

                    # 조건을 만족할 때만 흰색으로 손 관절 그리기
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(
                            color=(0, 0, 0), thickness=1, circle_radius=2
                        ),
                        self.mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=2),
                    )

                    # 각 관절의 인덱스 표시
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        x, y = int(landmark.x * frame.shape[1]), int(
                            landmark.y * frame.shape[0]
                        )
                        cv2.putText(
                            frame,
                            str(idx),
                            (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            (255, 255, 255),
                            1,
                        )

            else:
                self.noHandCount += 1
                if self.noHandCount >= 6:
                    isUniqueHand = False
                    movement_left_count, movement_right_count, movement_count = 0, 0, 0

            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()


def greeting_detected_callback():
    print("Greeting Detected")


hand_tracker = HandTracker(greeting_detected_callback)
hand_tracker.start()
