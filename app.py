import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import os
import base64

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

/* スマホ用 */
@media (max-width:1000px){
    h1 {
        width: fit-content;
        margin: 0 auto;
        font-size: clamp(28px, 5vw, 55px) !important;
        white-space: nowrap !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }

    h1::after {
        width: 95% !important;
        height: 5px;
        margin-top: 10px;
        margin-left: auto !important;
        margin-right: auto !important;
    }
}

}
</style>
"""% font_data,unsafe_allow_html=True)

st.title("ORIGINAL CARD MAKER", width="stretch")

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
st.image(f"template/{template_name}", caption=f"{template_label} のプレビュー", width=200)

name = st.text_input("カード名")
name_font_size = st.slider("カード名の文字サイズ（※手動で文字を小さくするとき）",min_value=20, max_value=65, value=65, step=1)
st.caption("※カード名が長い場合は、自動で文字が小さくなります")
cost = st.number_input("数字（No. / コスト）", min_value=0, max_value=999, step=1)
ctype = st.text_input("タイプ（属性 / 種族）")
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
        draw.multiline_text((60,950),wrapped_skill,font=font_skill,fill="black",spacing=12)

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
