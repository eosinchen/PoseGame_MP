#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import random

import cv2
import numpy
import time
from PIL import Image, ImageDraw, ImageFont
import mediapipe_hand
import queue
import os

# 強制設定遊戲視窗大小
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 設定遊玩次數
game_total_count = 10
# 設定每次活動秒數
game_play_time = 7

# 得分紀錄
total_score = 0
# 紀錄遊戲過程的 queue
game_movie_queue = None
# 錄影存檔的檔名
game_save_file_name = None

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
# 左邊框的起始位置
left_box_x = 160
left_box_y = 240
# 左手是否在左邊框
left_hand_in_box = False

# 不填滿框的內容
no_fill_color = None

# 中文字型檔
font_text_24 = ImageFont.truetype("jf-openhuninn-1.1.ttf", 24, encoding="utf-8")
font_text_36 = ImageFont.truetype("jf-openhuninn-1.1.ttf", 36, encoding="utf-8")
font_text_48 = ImageFont.truetype("jf-openhuninn-1.1.ttf", 48, encoding="utf-8")


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


# 使用 Random 隨機定義左右手框的位置
def random_get_box_xy():

    random.seed()

    # 中心點的隨機值，必須要符合框能劃入的大小
    a_right_box_x = random.randint(rect_box_width_half, FRAME_WIDTH - rect_box_width_half)
    a_right_box_y = random.randint(rect_box_height_half, FRAME_HEIGHT - rect_box_height_half)
    a_left_box_x = random.randint(rect_box_width_half, FRAME_WIDTH - rect_box_width_half)
    a_left_box_y = random.randint(rect_box_height_half, FRAME_HEIGHT - rect_box_height_half)

    return a_right_box_x, a_right_box_y, a_left_box_x, a_left_box_y

# 確認存檔檔名
def decide_file_name():

    global game_save_file_name

    # 依序找看看檔銘是否存在，若不存在則用此檔名
    origin_index = 0
    while True:
        temp_filename = "H" + ("%05d" % origin_index) + ".mp4"

        if os.path.isfile(temp_filename):
            origin_index += 1
        else:
            game_save_file_name = temp_filename
            break


# 遊戲的入口點
def play_game():

    global right_box_x, right_box_y, left_box_x, left_box_y, total_score, game_movie_queue

    # 是否從一般模式進入 Game Mode
    is_first_in_game_mode = True
    # 紀錄目前是否為遊戲模式，還是只顯示畫面
    is_game_mode = False
    # 紀錄目前已經經歷了幾次
    play_loop_count = 0
    # 記錄每一個 loop 開始的時間
    begin_time = 0
    # 記錄每一個畫面當下的時間
    now_time = 0
    # 建立存放預先錄影用 image 的 queue
    game_movie_queue = queue.Queue(100)
    # 錄影格式
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # 錄影串流
    out_movie = None

    # 開啟攝影機
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # 設定攝影機尺寸為固定大小，以便標示方框與文字
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

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

                # 第一次開始到 game mode 時要作的事
                if is_first_in_game_mode:
                    # 關閉第一次的標記
                    is_first_in_game_mode = False
                    # 開始錄影 - 決定檔名
                    decide_file_name()
                    # 取得影像的高與寬
                    image_height, image_width, _ = image.shape
                    # 開啟影片檔
                    out_movie = cv2.VideoWriter(game_save_file_name, fourcc, 30.0, (image_width, image_height))
                    # 先將 Queue 中所有的影像寫到檔案中
                    while not game_movie_queue.empty():
                        frame = game_movie_queue.get_nowait()
                        out_movie.write(frame)

                # 每一個 game loop 的開始
                if begin_time == 0:
                    begin_time = time.time()
                    now_time = time.time()
                    right_box_x, right_box_y, left_box_x, left_box_y = random_get_box_xy()

                # 取得時間與計算間隔秒數
                time_interval = round(now_time - begin_time, 1)
                now_time = time.time()

                # 先進行手部位置評估
                image, in_r_rect, in_l_rect = mediapipe_hand.hands_estimation(image, right_box_x, right_box_y, left_box_x, left_box_y)

                # 依照左右手位置的條件來畫框
                image = draw_rect_box(image, in_r_rect, in_l_rect)

                # 顯示目前為第幾輪的遊戲，倒數時間與分數
                image = add_chinese_font_to_image(image, "手忙腳亂：第" + str(play_loop_count + 1) + "輪 已得分=" + str(total_score) + "分", 10, 10, font_text=font_text_36)
                image = add_chinese_font_to_image(image, "時間倒數 " + str(int(game_play_time - time_interval)) + " 秒", 10, 70, font_text=font_text_36)

                # 當秒數為 game_play_time 時，更新次數與回覆時間值
                if time_interval >= game_play_time:
                    begin_time = 0
                    play_loop_count += 1
                    # 此時若左右手都在框中，就算各得一分
                    if in_r_rect:
                        total_score += 1
                    if in_l_rect:
                        total_score += 1
                    right_box_x, right_box_y, left_box_x, left_box_y = random_get_box_xy()

                # 當已經跑 total 次時就回到一般模式
                if play_loop_count == game_total_count:
                    is_game_mode = False
                    # 右邊框的起始位置
                    right_box_x = 480
                    right_box_y = 240
                    # 左邊框的起始位置
                    left_box_x = 160
                    left_box_y = 240

            else:
                # 若在一般模式之下，顯示啟動畫面
                image = add_chinese_font_to_image(image, "手忙腳亂：請將左右手掌放於框中開始", 10, 10, font_text=font_text_36)
                image = add_chinese_font_to_image(image, "上次得分：" + str(total_score) + "分", 150, 50, font_text=font_text_48)

                # 先進行手部位置評估
                image, in_r_rect, in_l_rect = mediapipe_hand.hands_estimation(image, right_box_x, right_box_y, left_box_x, left_box_y)

                # 依照左右手位置的條件來畫框
                image = draw_rect_box(image, in_r_rect, in_l_rect)

                # 在一般模式下，將這兒設為 True，以便下一次開始遊戲時，要作一些事
                is_first_in_game_mode = True

                # 若左手此時都在框中，就進入遊戲模式
                is_game_mode = in_r_rect and in_l_rect
                if is_game_mode:
                    play_loop_count = 0
                    total_score = 0

            # 存放到 Queue 中，若 Queue 已滿，就先取出一個舊的，加入一個新的
            if game_movie_queue.full():
                game_movie_queue.get_nowait()
            if not is_game_mode:
                game_movie_queue.put(image)

            # 每 image 錄影
            if out_movie is not None:
                out_movie.write(image)

            cv2.imshow('手忙腳亂', cv2.resize(image, (1024, 768), interpolation=cv2.INTER_AREA))

        # 需有 waitKey，畫面才會顯示內容
        press_key = cv2.waitKey(5) & 0xFF

        # 保留按下 ESC 結束整個畫面的功能
        if press_key == 27:
            break
