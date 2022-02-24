# This is a sample Project for using MediaPipe in Game.
# And this is for teaching, so this is only demo, not a real game.
import cv2
import mediapipe as mp

# mediapipe 的繪圖與線條格式物件
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
# 建立 pose 物件
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


# 利用 MediaPipe Pose 進行動作評估與
def pose_estimation(image):

    # 利用 pose 進行肢體動作評估
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if not results.pose_landmarks:
        # 將 image 座左右翻轉與回傳
        return cv2.flip(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), 1)

    # 取得影像的高與寬
    image_height, image_width, _ = image.shape
    # 顯示鼻子的座標 mp_pose.PoseLandmark.NOSE
    print(
        f'Nose coordinates: ('
        f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * image_width}, '
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

    # 將 image 座左右翻轉與回傳
    return cv2.flip(image, 1)
