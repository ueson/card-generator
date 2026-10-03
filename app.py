import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import os
import base64

with open("static/fonts/Jersey15-Regular.ttf", "rb") as f:
    font_data = base64.b64encode (f.read()).decode()

st.markdown("""
<style>
[data-testid="stMainBlockContainer"]{
    max-width:52%%;
}
/* スマホ */
@media(max-width:768px){
[data-testid="stMainBlockCotainer"]{
    max-width:90%%;
    }
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #66aaff, #99ccff);
}

@font-face {
    font-family: 'Jersey15';
    src: url("data:font/ttf;base64,%s")format('truetype');
}

h1 {
    font-family: 'Jersey15',
    sans-serif !important;
    text-align: center;
    font-size: clamp(50px,8vw,120px) !important;
    line-height:1.1 !important;
    color: #ffcc33 !important;
    text-shadow: 6px 6px 0px black; !important;
}
</style>
"""% font_data,unsafe_allow_html=True)

st.title("ORIGINAL CARD MAKER")

# ▼テンプレート選択（日本語表示）
template_options = {
    "RED": "red.png",
    "BLUE":"blue.png",
    "YELLOW":"yellow.png",
    "GREEN":"green.png",
    "GRAY":"gray.png"
}
template_label = st.selectbox("テンプレートを選ぶ", list(template_options.keys()))
template_name = template_options[template_label]

# ▼テンプレートのプレビュー表示
st.image(f"template/{template_name}", caption=f"{template_label} のプレビュー", width=170)

name = st.text_input("カード名")
cost = st.number_input("コスト", min_value=0, max_value=999, step=1)
ctype = st.text_input("属性")
skill = st.text_area("スキル", height=200)
uploaded_img = st.file_uploader("カードの絵をアップロード", type=["png", "jpg", "jpeg"])
frame = Image.open(f"template/{template_name}").convert("RGBA")
card = Image.new("RGBA", frame.size, (255, 255, 255, 0))

if st.button("カードを生成する"):
    if uploaded_img:
        art = Image.open(uploaded_img).convert("RGBA")

        # テンプレート読み込み
        frame = Image.open(f"template/{template_name}").convert("RGBA")
        
        # 絵をリサイズして統一
        resized_art = art.resize((980,845)).convert("RGBA")

        # 絵の貼り付け
        card.paste(resized_art, (40, 120), resized_art)

        card = Image.alpha_composite(card, frame)

        draw = ImageDraw.Draw(card)

        # フォント設定
        font_name = ImageFont.truetype("static/fonts/SourceHanSansJP-Heavy.otf",65)   # name 太字
        font_cost = ImageFont.truetype("static/fonts/Jersey15-Regular.ttf", 100)   # cost 太字
        font_type = ImageFont.truetype("static/fonts/SourceHanSansJP-Heavy.otf", 30)   # 属性
        font_skill = ImageFont.truetype("static/fonts/SourceHanSansJP-Medium.otf", 27) # スキル

        # name
        name_text = str(name)
        bbox = draw.textbbox((0, 0), name_text, font=font_name)
        text_width = bbox[2] - bbox[0]
        center_x = 570
        draw.text((center_x - text_width/2, 25), name_text, font=font_name, fill="white")

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
        lines = skill_text.split("\n")
        wrapped_lines = [textwrap.fill(line, width=33) for line in lines]
        wrapped_skill = "\n".join(wrapped_lines)
        draw.multiline_text((60, 950), wrapped_skill, font=font_skill, fill="black", spacing=12)

        st.image(card, width=450, caption="生成されたカード")

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
