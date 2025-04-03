import streamlit as st
import cv2
import os
import shutil
from datetime import datetime
from PIL import Image

# 建立輸出資料夾
OUTPUT_DIR = "violations_output"
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# 違規法條對應（簡化示例）
VIOLATION_CODES = {
    "闖紅燈": "§53：駕駛人不依號誌指示行駛",
    "未保持安全距離": "§42：未保持行車間隔",
    "逆向行駛": "§45：車輛不按規定車道行駛",
    "違規變換車道": "§43：變換車道未確保安全",
}

st.set_page_config(page_title="交通事故畫面分析", layout="wide")
st.title("🚦 交通事故畫面擷取與違規標記工具")

uploaded_file = st.file_uploader("請上傳事故影片（mp4 格式）", type=["mp4"])

if uploaded_file:
    st.video(uploaded_file)
    video_path = os.path.join("temp_video.mp4")

    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("影片上傳完成，開始擷取畫面...")

    # 擷取影片畫面
    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    saved_frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # 每隔 15 幀擷取一張
        if frame_count % 15 != 0:
            continue

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        frame_filename = os.path.join(OUTPUT_DIR, f"frame_{timestamp}.jpg")
        cv2.imwrite(frame_filename, frame)
        saved_frame_count += 1

    cap.release()
    st.success(f"擷取完成，共儲存 {saved_frame_count} 張畫面。")

    # 顯示擷取畫面並允許標記違規
    st.subheader("🖼️ 擷取畫面與違規標記")
    image_files = sorted(os.listdir(OUTPUT_DIR))[:30]  # 最多顯示30張
    marked_violations = []

    cols = st.columns(3)
    for i, image_file in enumerate(image_files):
        img_path = os.path.join(OUTPUT_DIR, image_file)
        image = Image.open(img_path)

        with cols[i % 3]:
            st.image(image, caption=image_file, use_column_width=True)
            violation_type = st.selectbox(
                f"標記違規類型 ({image_file})",
                ["無", *VIOLATION_CODES.keys()],
                key=f"select_{i}"
            )
            if violation_type != "無":
                marked_violations.append((image_file, violation_type, VIOLATION_CODES[violation_type]))

    # 顯示違規標記報告
    if marked_violations:
        st.subheader("📋 違規畫面與對應法條")
        for filename, vtype, law in marked_violations:
            st.markdown(f"- **{filename}** → 🚫 {vtype} ｜📘 法條：{law}")

        if st.button("匯出違規報告（尚未實作）"):
            st.info("未來可整合匯出 PDF 或 CSV 功能")
    else:
        st.info("尚未標記任何違規畫面")
