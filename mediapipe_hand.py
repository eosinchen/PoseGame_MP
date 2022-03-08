#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import mediapipe as mp

# mediapipe 的繪圖與線條格式物件
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 建立 hand 物件
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)


# 利用 MediaPipe Hands 進行動作評估
def hands_estimation(image, r_up_x, r_up_y, r_down_x, r_down_y, l_up_x, l_up_y, l_down_x, l_down_y):

    # 左右兩個 Rect 的評估結果
    in_r_rect = False
    in_l_rect = False

    # 利用 hand 進行肢體動作評估
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # 若有偵測到手，則進行左右框的辨識
    if results.multi_hand_landmarks:

        # print('Handedness:', results.multi_handedness)

        # 取得影像的高與寬
        image_height, image_width, _ = image.shape

        # 在 image 上畫 landmark
        for hand_landmarks in results.multi_hand_landmarks:

            index_finger_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x * image_width
            index_finger_mcp_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y * image_height

            # 判斷左右兩框內是否有手
            if not in_r_rect:
                in_r_rect = ((r_up_x <= index_finger_mcp_x <= r_down_x) and (r_up_y <= index_finger_mcp_y <= r_down_y))

            # 判斷左右兩框內是否有手
            if not in_l_rect:
                in_l_rect = ((l_up_x <= index_finger_mcp_x <= l_down_x) and (l_up_y <= index_finger_mcp_y <= l_down_y))

            # print('hand_landmarks:', hand_landmarks)
            print(
                f'Index finger mcp coordinates: (',
                f'{in_r_rect}, '
                f'{in_l_rect}, '
                f'{index_finger_mcp_x}, '
                f'{index_finger_mcp_y})'
            )

            # 繪製兩手的 landmark 與連接線
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

    # 將 image 座左右翻轉與回傳
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR), in_r_rect, in_l_rect
