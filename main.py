# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import time
import mediapipe_pose


# 單純開啟攝影機，與擷取畫面做顯示
def open_camera(camera_num):
    cap = cv2.VideoCapture(camera_num, cv2.CAP_DSHOW)

    # 進行不斷循環的撥放
    while True:
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:
            cv2.imshow('MediaPipe Pose', image)

        # 需有 waitKey，畫面才會顯示內容，並在此查看是否按下 ESC，若有按下，則停止擷取與播放
        if cv2.waitKey(5) & 0xFF == 27:
            break

    # 釋放攝影機資源，與關閉視窗
    cap.release()
    cv2.destroyAllWindows()


# 開啟攝影機，擷取畫面顯示，並加入 fps 計算與顯示
def open_camera_and_show_fps(camera_num):
    cap = cv2.VideoCapture(camera_num, cv2.CAP_DSHOW)

    # 記錄前一個 frame 的結束時間
    prev_frame_time = 0
    # 記錄這一格 frame 的結束時間
    new_frame_time = 0
    # 用來顯示文字的字型
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 進行不斷循環的撥放
    while True:
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:
            # 從 time.time() 中取得時間
            new_frame_time = time.time()

            # 計算 fps，使用 每個 frame 需要多少時間的計算方式
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time

            # 取小數點兩位，並轉換成字串
            fps = 'fps:' + str(round(fps, 2))

            # putting the FPS count on the frame
            cv2.putText(image, fps, (10, 30), font, 1, (100, 255, 0), 2, cv2.LINE_AA)

            # 使用 OpenCV 功能來顯示影像
            cv2.imshow('MediaPipe Pose', image)

        # 需有 waitKey，畫面才會顯示內容，並在此查看是否按下 ESC，若有按下，則停止擷取與播放
        if cv2.waitKey(5) & 0xFF == 27:
            break

    # 釋放攝影機資源，與關閉視窗
    cap.release()
    cv2.destroyAllWindows()


# 開啟攝影機，擷取畫面顯示，並加入 fps 計算與顯示
def open_camera_show_fps_pose_estimation(camera_num):
    cap = cv2.VideoCapture(camera_num, cv2.CAP_DSHOW)

    # 記錄前一個 frame 的結束時間
    prev_frame_time = 0
    # 記錄這一格 frame 的結束時間
    new_frame_time = 0
    # 用來顯示文字的字型
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 進行不斷循環的撥放
    while True:
        success, image = cap.read()

        # 若有攫取到畫面，就在視窗中顯示
        if success:
            # 傳入 MediaPipe 模組，進行 Pose 評估
            image = mediapipe_pose.pose_estimation(image)

            # 從 time.time() 中取得時間
            new_frame_time = time.time()

            # 計算 fps，使用 每個 frame 需要多少時間的計算方式
            fps = 1 / (new_frame_time - prev_frame_time)
            prev_frame_time = new_frame_time

            # 取小數點兩位，並轉換成字串
            fps = 'fps:' + str(round(fps, 2))

            # putting the FPS count on the frame
            cv2.putText(image, fps, (10, 30), font, 1, (100, 255, 0), 2, cv2.LINE_AA)

            # 使用 OpenCV 功能來顯示影像
            cv2.imshow('MediaPipe Pose', image)

        # 需有 waitKey，畫面才會顯示內容，並在此查看是否按下 ESC，若有按下，則停止擷取與播放
        if cv2.waitKey(5) & 0xFF == 27:
            break

    # 釋放攝影機資源，與關閉視窗
    cap.release()
    cv2.destroyAllWindows()


# main enter point
if __name__ == '__main__':
    # open_camera(0)
    # open_camera_and_show_fps(0)
    open_camera_show_fps_pose_estimation(0)
