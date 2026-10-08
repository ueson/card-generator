import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import io
import os
import base64
import json

SAVE_DIR = "saved_cards"
os.makedirs(SAVE_DIR, exist_ok=True)

with open("static/fonts/MavenPro-VariableFont_wght.ttf", "rb") as f:
    font_data = base64.b64encode (f.read()).decode()

st.markdown("""
<style>
[data-testid="stMainBlockContainer"]{
    max-width:52%%;
}
/* スマホ */
@media(max-width:1000px){
[data-testid="stMainBlockContainer"]{
    max-width:95%%;
    }
}
[data-testid="stAppViewContainer"] {
    background: #f7f7f7 !important;
}

@font-face {
    font-family: 'MavenPro';
    src: url("data:font/ttf;base64,%s")format('truetype');
}

h1 {
    background: transparent !important;
    
    font-family: 'MavenPro',
    sans-serif !important;
    text-align: center;
    font-size: clamp(40px,4vw,70px) !important;
    line-height:1.1 !important;
    color: #000000 !important;
    text-shadow: 2px 2px 0px #c0c0c0!important;
    
    white-space: nowrap !important;
    padding: 30px 0 !important;
    margin-top:-50px !important;
}

h1 {
    position: relative;
}

/* タイトル下の黄色ライン */
h1::after {
    content: "";
    display: block;
    width: 100%%;
    height: 6px;
    background: #FFD84D; 
    margin: 12px auto 0;
    border-radius: 3px;
}

/* 入力項目のラベルを常に黒にする */
label{
    color: #000000 !important;
}

/* スマホ用 */
@media (max-width:1000px){
    [data-testid="stImage"]img
    {
        max-width:90vw !important;
        height:auto !important;
    }
    h1 {
        width: fit-content;
        margin: 0 auto;
        text-align: center !important;
        font-size: clamp(26px, 5vw, 50px) !important;
        white-space: normal !important; /* ← nowrapだと横幅が広がる */
        letter-spacing: -1px;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    h1::after {
        width: 95%% !important;
        height: 5px;
        margin-top: 10px;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
}

}
</style>
""" % font_data,unsafe_allow_html=True)

st.title("ORIGINAL CARD MAKER", width="stretch")

# ▼テンプレート選択（日本語表示）
template_options = {
    "RED": "standard_red.png",
    "BLUE":"standard_blue.png",
    "YELLOW":"standard_yellow.png",
    "GREEN":"standard_green.png",
    "GRAY":"standard_gray.png",
    "フルイメージ":"full_image.png",
    "フルテキスト":"full_text.png"
}
template_label = st.selectbox("テンプレートを選ぶ", list(template_options.keys()))
template_name = template_options[template_label]

# ▼テンプレートごとの設定
if template_name.startswith("standard_"):
    image_size=(980,845)
    image_position=(40,120)
elif template_name =="full_image.png":
    image_size=(980,1300)
    image_position=(40,120)     
elif template_name =="full_text.png":
    image_size=(0,0)
    image_position=(0,0)

# ▼テンプレートのプレビュー表示
st.image(f"template/{template_name}", caption=f"{template_label} のプレビュー", width=150)

# ▼ 保存済みカード一覧
st.subheader("💾 保存済みカード")
saved_files = [
    f for f in os.listdir(SAVE_DIR)
    if f.endswith(".json")
]
if saved_files:
    selected_file = st.selectbox(
        "保存済みカードを選択",
        saved_files
    )
    if st.button("📂 このカードを読み込む", key="load_card"):
        file_path = os.path.join(SAVE_DIR, selected_file)
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        # 読み込んだデータを入力欄に直接セット
        st.session_state["card_name"] = loaded_data.get("name", "")
        st.session_state["name_font_size"] = loaded_data.get("name_font_size", 65)
        st.session_state["cost"] = loaded_data.get("cost", 0)
        st.session_state["ctype"] = loaded_data.get("ctype", "")
        st.session_state["skill"] = loaded_data.get("skill", "")

        if loaded_data.get("image"):
            st.session_state["loaded_image_bytes"] = base64.b64decode(
                loaded_data["image"]
            )
        else:
            st.session_state["loaded_image_bytes"] = None

        st.session_state["selected_file"]=selected_file
        st.session_state["uploader_version"]+=1
        st.rerun()

else:
    st.info("まだ保存されているカードはありません。")

name = st.text_input(
    "カード名",
    key="card_name"
)
name_font_size = st.slider(
    "カード名の文字サイズ（※手動で文字を小さくするとき）",
    min_value=20,
    max_value=65,
    step=1,
    key="name_font_size"
)
st.caption("※カード名が長い場合は、自動で文字が小さくなります")
cost = st.number_input(
    "数字（No. / コスト）",
    min_value=0,
    max_value=999,
    step=1,
    key="cost"
)
ctype = st.text_input(
    "タイプ（属性 / 種族）",
    key="ctype"
)
skill = st.text_area(
    "スキル",
    height=200,
    key="skill"
)
if template_name=="full_text.png":
    uploaded_img=None
else:
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 0
    uploaded_img = st.file_uploader(
        "カードの絵をアップロード",
        type=["png", "jpg", "jpeg"],
        key=f"image_uploader_{st.session_state['uploader_version']}"
    )
frame = Image.open(f"template/{template_name}").convert("RGBA")
card = Image.new("RGBA", frame.size, (255, 255, 255, 0))

if uploaded_img:
    st.session_state["loaded_image_bytes"]=uploaded_img.getvalue()
    st.image(uploaded_img, caption="現在選択中の画像", width=200)

elif st.session_state.get("loaded_image_bytes"):
    st.image(
        st.session_state["loaded_image_bytes"],
        caption="保存済みカードから読み込んだ画像",
        width=200
    )

def save_card():
    card_data = {
        "template_name": template_name,
        "name": name,
        "name_font_size": name_font_size,
        "cost": cost,
        "ctype": ctype,
        "skill": skill,
    }

    # アップロード画像がある場合
    if uploaded_img:
        img_bytes = uploaded_img.getvalue()

    elif st.session_state.get("loaded_image_bytes"):
        img_bytes = st.session_state["loaded_image_bytes"]

    else:
        img_bytes = None

    if img_bytes:
        card_data["image"] = base64.b64encode(
            img_bytes
        ).decode("utf-8")
    else:
        card_data["image"] = None

    filename = os.path.join(SAVE_DIR, f"{name}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(card_data, f, ensure_ascii=False, indent=2)

    st.success("カードデータを保存しました！")

if st.button("カードを保存する"):
    save_card()

if st.button("🔄 このカードを更新する"):
    selected_file = st.session_state.get("selected_file")

    if selected_file:
        file_path = os.path.join(SAVE_DIR, selected_file)

        card_data = {
            "template_name": template_name,
            "name": name,
            "name_font_size": name_font_size,
            "cost": cost,
            "ctype": ctype,
            "skill": skill,
        }

        if uploaded_img:
            img_bytes = uploaded_img.getvalue()
            st.session_state["loaded_image_bytes"]=img_bytes
            card_data["image"] = base64.b64encode(img_bytes).decode("utf-8")

        elif st.session_state.get("loaded_image_bytes"):
            card_data["image"] = base64.b64encode(
                st.session_state["loaded_image_bytes"]
            ).decode("utf-8")

        else:
            card_data["image"] = None

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(card_data, f, ensure_ascii=False, indent=2)

        st.success("カードを更新しました！")

    else:
        st.warning("先に保存済みカードを読み込んでください。")

if st.button("カードを生成する"):
    if uploaded_img or st.session_state.get("loaded_image_bytes") or template_name == "full_text.png":

        if uploaded_img:
            art = Image.open(uploaded_img).convert("RGBA")

        elif st.session_state.get("loaded_image_bytes"):
            art = Image.open(
                io.BytesIO(st.session_state["loaded_image_bytes"])
            ).convert("RGBA")

        # テンプレート読み込み
        frame = Image.open(f"template/{template_name}").convert("RGBA")

        # 絵を縦横比を維持してリサイズ＆トリミング
        resized_art = ImageOps.fit(
            art,
            image_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.4)
        ).convert("RGBA")

        # 絵の貼り付け
        card.paste(resized_art, image_position, resized_art)
        card = Image.alpha_composite(card, frame)
        draw = ImageDraw.Draw(card)

        # フォント設定
        font_cost = ImageFont.truetype("static/fonts/Jersey15-Regular.ttf", 100)   # cost 太字
        font_type = ImageFont.truetype("static/fonts/SourceHanSansJP-Heavy.otf", 30)   # 属性
        font_skill = ImageFont.truetype("static/fonts/SourceHanSansJP-Medium.otf", 27) # スキル

        # name
        name_text = str(name)
        max_name_width = 760
        current_size = name_font_size
        
        while current_size >= 20:
            test_font = ImageFont.truetype("static/fonts/SourceHanSansJP-Heavy.otf",current_size)
            bbox = draw.textbbox((0, 0), name_text, font=test_font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_name_width:
               break
            current_size -= 1
            
        font_name = ImageFont.truetype("static/fonts/SourceHanSansJP-Heavy.otf",current_size)   # name 太字
        bbox = draw.textbbox((0, 0), name_text, font=font_name)
        text_width = bbox[2] - bbox[0]
        center_x = 570
        draw.text((center_x - text_width / 2, 25),name_text,font=font_name,fill="white"
        )

        # cost
        cost_text = str(cost)
        bbox = draw.textbbox((0, 0), cost_text, font=font_cost)
        text_width = bbox[2] - bbox[0]
        center_x = 115
        draw.text((center_x - text_width/2, 48), cost_text, font=font_cost, fill="white")

        # type（白）
        ctype_text = str(ctype)
        bbox = draw.textbbox((0, 0), ctype_text, font=font_type)
        text_width = bbox[2] - bbox[0]
        center_x = 150
        draw.text((center_x - text_width/2, 867), ctype_text, font=font_type, fill="black")

        # skill（黒・自動折り返し）
        skill_text = str(skill)
        max_skill_width=870
        wrapped_lines=[]

        #入力した改行も維持する
        for line in skill_text.split("\n"):
            current_line=""
            for char in line:
                test_line=current_line+char
                bbox=draw.textbbox((0,0),test_line,font=font_skill)
                text_width=bbox[2]-bbox[0]
                if text_width <=max_skill_width:
                    current_line=test_line
                else:
                    if current_line:wrapped_lines.append(current_line)
                    current_line=char
            if current_line:wrapped_lines.append(current_line)
        wrapped_skill="\n".join(wrapped_lines)
        if template_name == "full_text.png":
            skill_x=80
            skill_y=200
        else:
            skill_x=60
            skill_y=950
        draw.multiline_text((skill_x,skill_y),wrapped_skill,font=font_skill,fill="black",spacing=12)

        st.image(card, width=320 , caption="生成されたカード")

        # ダウンロード用バッファ
        buf = io.BytesIO()
        card.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # ダウンロードボタン
        st.download_button(
            label="カードをダウンロードする",
            data=byte_im,
            file_name=f"{name}.png",
            mime="image/png"
        )
