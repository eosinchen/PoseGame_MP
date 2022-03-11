#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import numpy
import time
from PIL import Image, ImageDraw, ImageFont
import queue
import os

# 設定遊玩次數
import mediapipe_pose

game_total_count = 5
# 設定自由活動秒數
game_free_time = 10
# 設定停止活動秒數
game_stop_time = 10

# 是否為停止活動時的一瞬間，這時要記錄位置檔
is_stop_time_begin = True
# 停止活動時瞬間的位置檔
stop_time_pose_result = None
# 停止活動時後續的位置檔
stop_time_continue_pose = None
# 判斷移動的閾值
move_thread_value = 50
# 停止活動時是否移動
is_move_in_stop = False
# 得分紀錄
total_score = 0
# 紀錄遊戲過程的 queue
game_movie_queue = None
# 錄影存檔的檔名
game_save_file_name = None


# 顯示中文字之副程式
def add_chinese_font_to_image(img, text, left, top, text_color=(0, 255, 0), text_size=24):

    # 判斷圖片格式，若為 OpenCV 格式，就要做 BGR->RGB 的轉變
    if isinstance(img, numpy.ndarray):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # 中文字型檔
    font_text = ImageFont.truetype("HYWenHei-75W.ttf", text_size, encoding="utf-8")

    # 將 img 切換成 PIL 格式
    draw = ImageDraw.Draw(img)

    # 利用 draw 進行文字繪製
    draw.text((left, top), text, text_color, font=font_text)

    # 返回繪製好的 圖片+文字
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)


# 取得當下的 pose 位置資料
def get_pose_result(image):
    return mediapipe_pose.get_pose_result(image)


# 確認存檔檔名
def decide_file_name():

    global game_save_file_name

    # 依序找看看檔銘是否存在，若不存在則用此檔名
    origin_index = 0
    while True:
        temp_filename = "M" + ("%05d" % origin_index) + ".mp4"

        if os.path.isfile(temp_filename):
            origin_index += 1
        else:
            game_save_file_name = temp_filename
            break


# 遊戲的入口點
def play_game():

    global is_stop_time_begin, stop_time_pose_result, stop_time_continue_pose, is_move_in_stop, total_score, game_movie_queue, game_save_file_name

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

    # 進行不斷循環的撥放
    while True:
        # 擷取影像
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:

            # 先作畫面翻轉
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

                # 取得時間與計算間隔秒數
                time_interval = round(now_time - begin_time, 0)
                now_time = time.time()

                # 顯示目前為第幾次的遊戲
                image = add_chinese_font_to_image(image, "123木頭人：第 " + str(play_loop_count + 1) + " 輪 得分= " + str(total_score) + " 分", 10, 10, text_size=36)

                # 用來判斷與顯示活動或停止的資訊
                if time_interval <= game_free_time:
                    image = add_chinese_font_to_image(image, "自由活動：時間還剩 " + str(int(game_free_time-time_interval)) + " 秒", 10, 70, text_size=36)
                else:
                    # 當一進入停止活動時，紀錄位置
                    if is_stop_time_begin:
                        stop_time_pose_result = get_pose_result(image)
                        is_stop_time_begin = False

                    # 進行繪圖 - 停止時的當下框
                    image = mediapipe_pose.draw_nose_rect(image, stop_time_pose_result, True)

                    # 後續活動時的位置與框
                    stop_time_continue_pose = get_pose_result(image)
                    image = mediapipe_pose.draw_nose_rect(image, stop_time_continue_pose)

                    # 顯示時間與文字資訊
                    image = add_chinese_font_to_image(image, "停止活動：時間還剩 " + str(int(game_stop_time-(time_interval-game_free_time))) + " 秒", 10, 70, text_color=(255, 0, 0), text_size=36)

                    # 計算移動的距離，看看有沒有"動作"
                    if not is_move_in_stop:
                        is_move_in_stop = (mediapipe_pose.cal_move_distance(image, stop_time_pose_result, stop_time_continue_pose) > move_thread_value)

                    if is_move_in_stop:
                        # 若有移動，就作顯示
                        image = add_chinese_font_to_image(image, "[你已移動]", 10, 120, text_color=(255, 0, 0), text_size=30)

                # 當秒數大於一個 loop 時，更新次數與回覆時間值
                if time_interval >= game_free_time + game_stop_time:
                    begin_time = 0
                    play_loop_count += 1
                    is_stop_time_begin = True
                    if not is_move_in_stop:
                        total_score += 1
                    is_move_in_stop = False

                # 當已經跑 5 次時就回到一般模式
                if play_loop_count == game_total_count:
                    is_game_mode = False

            else:
                # 若還不是遊戲模式，則顯示按下"空白鍵"進入遊戲模式
                image = add_chinese_font_to_image(image, "請按空白鍵開始", 70, 180, text_size=72)

                # 關閉錄影串流
                if out_movie is not None:
                    out_movie.release()
                    out_movie = None

                # 在一般模式下，將這兒設為 True，以便下一次開始遊戲時，要作一些事
                is_first_in_game_mode = True

            # 存放到 Queue 中，若 Queue 已滿，就先取出一個舊的，加入一個新的
            if game_movie_queue.full():
                game_movie_queue.get_nowait()
            if not is_game_mode:
                game_movie_queue.put(image)

            # 每 image 錄影
            if out_movie is not None:
                out_movie.write(image)

            cv2.imshow('Pose Game', image)

        # 需有 waitKey，畫面才會顯示內容
        press_key = cv2.waitKey(5) & 0xFF

        # 依照不同的按鍵，進行不同的操作
        if press_key == 32:
            is_game_mode = True

        if press_key == 27:
            break

