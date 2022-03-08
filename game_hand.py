#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import numpy
import time
from PIL import Image, ImageDraw, ImageFont
import mediapipe_hand

# 強制設定遊戲視窗大小
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 設定遊玩次數
game_total_count = 5
# 設定自由活動秒數
game_free_time = 10
# 設定停止活動秒數
game_stop_time = 10

# 框之大小，用一半的量，比較好計算左上右下
rect_box_width_half = 75
rect_box_height_half = 100

# 右手相關資訊
right_hand_line_color = (255, 255, 0)
right_hand_fill_color = (80, 80, 0)
right_hand_width = 10
right_hand_mark = "右"
# 右邊框的起始位置
right_box_x = 480
right_box_y = 240
# 右手是否在右邊框
right_hand_in_box = False

# 左手相關資訊
left_hand_line_color = (0, 255, 255)
left_hand_fill_color = (0, 80, 80)
left_hand_width = 10
left_hand_mark = "左"
# 右邊框的起始位置
left_box_x = 160
left_box_y = 240
# 右手是否在右邊框
left_hand_in_box = False

# 不填滿框的內容
no_fill_color = None

# 中文字型檔
font_text_24 = ImageFont.truetype("HYWenHei-75W.ttf", 24, encoding="utf-8")
font_text_36 = ImageFont.truetype("HYWenHei-75W.ttf", 36, encoding="utf-8")
font_text_48 = ImageFont.truetype("HYWenHei-75W.ttf", 48, encoding="utf-8")


# 顯示中文字之副程式
def add_chinese_font_to_image(img, text, left, top, text_color=(0, 255, 0), font_text=font_text_24):

    # 判斷圖片格式，若為 OpenCV 格式，就做陣列與 BGR->RGB 的轉變
    if isinstance(img, numpy.ndarray):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # 將 img 切換成 PIL 格式
    draw = ImageDraw.Draw(img)

    # 利用 draw 進行文字繪製
    draw.text((left, top), text, text_color, font=font_text)

    # 返回繪製好的 圖片+文字
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


# 畫左右兩框
def draw_rect_box(image, in_r_rect, in_l_rect):

    # 判斷圖片格式，若為 OpenCV 格式，就做陣列與 BGR->RGB 的轉變
    if isinstance(image, numpy.ndarray):
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # 將 image 切換成 pil 格式
    draw = ImageDraw.Draw(image)

    # 計算 r-xy 座標
    r_up_x = int(right_box_x - rect_box_width_half)
    r_up_y = int(right_box_y - rect_box_height_half)
    r_down_x = int(right_box_x + rect_box_width_half)
    r_down_y = int(right_box_y + rect_box_height_half)

    # 計算 l-xy 座標
    l_up_x = int(left_box_x - rect_box_width_half)
    l_up_y = int(left_box_y - rect_box_height_half)
    l_down_x = int(left_box_x + rect_box_width_half)
    l_down_y = int(left_box_y + rect_box_height_half)

    # 繪製 right 的框
    if in_r_rect:
        draw.rectangle((r_up_x, r_up_y, r_down_x, r_down_y), outline=right_hand_line_color, fill=no_fill_color, width=7)
    else:
        draw.rectangle((r_up_x, r_up_y, r_down_x, r_down_y), outline=right_hand_line_color, fill=no_fill_color, width=2)

    # 標上 right 文字
    draw.text((r_up_x+10, r_up_y+10), right_hand_mark, right_hand_line_color, font=font_text_36)

    # 繪製 left 的框
    if in_l_rect:
        draw.rectangle((l_up_x, l_up_y, l_down_x, l_down_y), outline=left_hand_line_color, fill=no_fill_color, width=7)
    else:
        draw.rectangle((l_up_x, l_up_y, l_down_x, l_down_y), outline=left_hand_line_color, fill=no_fill_color, width=2)

    # 標上 left 文字
    draw.text((l_up_x+10, l_up_y+10), left_hand_mark, left_hand_line_color, font=font_text_36)

    # 返回繪製好的 圖片+框
    return cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)


# 遊戲的入口點
def play_game():
    # 紀錄目前是否為遊戲模式，還是只顯示畫面
    is_game_mode = False
    # 紀錄目前已經經歷了幾次
    play_loop_count = 0
    # 記錄每一個 loop 開始的時間
    begin_time = 0
    # 記錄每一個畫面當下的時間
    now_time = 0

    # 開啟攝影機
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # 設定攝影機尺寸為固定大小，以便標示方框與文字
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    # 進行不斷循環的撥放
    while True:
        # 擷取影像，在 play_game 這一層中， image 都要保持 OpenCV 格式
        # 其他副程式若用到 Pillow，則自行轉換，但返回值仍要保持 OpenCV(BGR) 格式
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:

            # 用 WebCam 拍自己，所以先做水平翻轉
            image = cv2.flip(image, 1)

            # 若在遊戲模式中
            if is_game_mode:

                # 每一個 game loop 的開始
                if begin_time == 0:
                    begin_time = time.time()
                    now_time = time.time()

                # 取得時間與計算間隔秒數
                time_interval = round(now_time - begin_time, 1)
                now_time = time.time()

                # 顯示目前為第幾次的遊戲
                image = add_chinese_font_to_image(image, "目前是第 " + str(play_loop_count + 1) + " 次", 10, 10,
                                                  font_text=font_text_36)

                # 用來判斷與顯示活動或停止的資訊
                if time_interval <= game_free_time:
                    image = add_chinese_font_to_image(image, "自由活動：時間經過 " + str(time_interval) + " 秒", 10, 60,
                                                      font_text=font_text_36)
                else:
                    image = add_chinese_font_to_image(image, "停止活動：時間經過 " + str(
                        round(time_interval - game_free_time, 1)) + " 秒", 10, 60, text_color=(255, 0, 0),
                                                      font_text=font_text_36)

                # 當秒數為 10 時，更新次數與回覆時間值
                if time_interval >= game_free_time + game_stop_time:
                    begin_time = 0
                    play_loop_count += 1

                # 當已經跑 5 次時就回到一般模式
                if play_loop_count == game_total_count:
                    is_game_mode = False

            else:
                # 若在一般模式之下，顯示啟動畫面
                image = add_chinese_font_to_image(image, "請將左右手掌放於框中", 80, 10, font_text=font_text_48)

                # 計算 r-xy 座標
                r_up_x = int(right_box_x - rect_box_width_half)
                r_up_y = int(right_box_y - rect_box_height_half)
                r_down_x = int(right_box_x + rect_box_width_half)
                r_down_y = int(right_box_y + rect_box_height_half)

                # 計算 l-xy 座標
                l_up_x = int(left_box_x - rect_box_width_half)
                l_up_y = int(left_box_x - rect_box_height_half)
                l_down_x = int(left_box_x + rect_box_width_half)
                l_down_y = int(left_box_y + rect_box_height_half)

                # 先進行手部位置評估
                image, in_r_rect, in_l_rect = mediapipe_hand.hands_estimation(image, r_up_x, r_up_y, r_down_x, r_down_y, l_up_x, l_up_y, l_down_x, l_down_y)

                # 依照左右手位置的條件來畫框
                image = draw_rect_box(image, in_r_rect, in_l_rect)

            cv2.imshow('Hand Game', image)

        # 需有 waitKey，畫面才會顯示內容
        press_key = cv2.waitKey(5) & 0xFF

        # 依照不同的按鍵，進行不同的操作
        if press_key == 32:
            is_game_mode = True

        if press_key == 27:
            break
