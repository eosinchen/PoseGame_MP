# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import numpy
import time
from PIL import Image, ImageDraw, ImageFont

# 設定遊玩次數
game_total_count = 5
# 設定自由活動秒數
game_free_time = 5
# 設定停止活動秒數
game_stop_time = 5


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

    # 進行不斷循環的撥放
    while True:
        # 擷取影像
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:

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
                image = add_chinese_font_to_image(image, "目前是第 " + str(play_loop_count + 1) + " 次", 10, 10, text_size=48)

                # 用來判斷與顯示活動或停止的資訊
                if time_interval <= game_free_time:
                    image = add_chinese_font_to_image(image, "自由活動：時間經過 " + str(time_interval) + " 秒", 10, 60, text_size=48)
                else:
                    image = add_chinese_font_to_image(image, "停止活動：時間經過 " + str(round(time_interval - game_free_time, 1)) + " 秒", 10, 60, text_color=(255, 0, 0), text_size=48)

                # 當秒數為 10 時，更新次數與回覆時間值
                if time_interval >= game_free_time + game_stop_time:
                    begin_time = 0
                    play_loop_count += 1

                # 當已經跑 5 次時就回到一般模式
                if play_loop_count == game_total_count:
                    is_game_mode = False

            else:
                # 若還不是遊戲模式，則顯示按下"空白鍵"進入遊戲模式
                image = add_chinese_font_to_image(image, "請按空白鍵開始", 10, 10, text_size=48)

            cv2.imshow('Pose Game', image)

        # 需有 waitKey，畫面才會顯示內容
        press_key = cv2.waitKey(5) & 0xFF

        # 依照不同的按鍵，進行不同的操作
        if press_key == 32:
            is_game_mode = True

        if press_key == 27:
            break
