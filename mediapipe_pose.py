#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import numpy
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont

# mediapipe 的繪圖與線條格式物件
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
# 建立 pose 物件
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


# 利用 MediaPipe Pose 進行動作評估
def pose_estimation(image):
    # 利用 pose 進行肢體動作評估
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if not results.pose_landmarks:
        # 將 image 色調調回，翻轉與回傳
        return cv2.flip(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), 1)

    # 取得影像的高與寬
    image_height, image_width, _ = image.shape

    # 顯示鼻子的座標 mp_pose.PoseLandmark.NOSE
    print(
        f'Nose coordinates: ('
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].z},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].visibility})'
    )

    # 在 image 上畫 landmark
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    # 回傳 image
    return image


# 利用 MediaPipe Pose 取得資料
def get_pose_result(image):

    # 利用 pose 進行肢體動作評估
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if not results.pose_landmarks:
        return None

    # 取得影像的高與寬
    image_height, image_width, _ = image.shape

    # 顯示鼻子的座標 mp_pose.PoseLandmark.NOSE
    print(
        f'Nose coordinates: ('
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].z},'
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].visibility})'
    )

    # 回傳 Pose 的結果
    return results


# 使用紀錄的 Pose 資料來繪圖
def draw_nose_rect(image, pose_result, first_stop=False):

    # 若沒有 landmark
    if not pose_result.pose_landmarks:
        return image

    # 取得影像的高與寬
    image_height, image_width, _ = image.shape

    nose_x = int(pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width)
    nose_y = int(pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height)

    # 判斷圖片格式，若為 OpenCV 格式，就要做 BGR->RGB 的轉變
    if isinstance(image, numpy.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # 將 img 切換成 PIL 格式
    draw = ImageDraw.Draw(image)

    # 計算 Rect 座標
    up_x = nose_x - 100
    if up_x < 0:
        up_x = 0

    up_y = nose_y - 150
    if up_y < 0:
        up_y = 0

    down_x = nose_x + 100
    if down_x > image_width:
        down_x = image_width

    down_y = nose_y + 50
    if down_y > image_height:
        down_y = image_height

    # 畫 圓角矩形
    if first_stop:
        # 畫第一次的框
        draw.rounded_rectangle((up_x, up_y, down_x, down_y), outline="yellow", width=5, radius=7)
    else:
        # 畫後續的框
        draw.rounded_rectangle((up_x, up_y, down_x, down_y), outline="red", width=3, radius=7)

    # 返回繪製好的 圖片+圓框
    return cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)


# 計算移動的距離，看看有沒有"動作"
def cal_move_distance(image, stop_time_pose_result, stop_time_continue_pose):

    # 若沒有 landmark
    if not stop_time_pose_result.pose_landmarks:
        return 0

    if not stop_time_continue_pose.pose_landmarks:
        return 0

    # 取得影像的高與寬
    image_height, image_width, _ = image.shape

    stop_time_pose_result_nose_x = int(stop_time_pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width)
    stop_time_pose_result_nose_y = int(stop_time_pose_result.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height)

    stop_time_continue_pose_nose_x = int(stop_time_continue_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width)
    stop_time_continue_pose_nose_y = int(stop_time_continue_pose.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y * image_height)

    distance = abs(stop_time_pose_result_nose_x - stop_time_continue_pose_nose_x) + abs(stop_time_pose_result_nose_y - stop_time_continue_pose_nose_y)

    return distance
