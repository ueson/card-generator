import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import io
import os
import base64
import json

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

/* Streamlitボタン：水色 */
div.stButton > button {
    background-color: #4DB8FF !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.6em 1.2em !important;
    font-weight: bold !important;
}
/* ホバー時（PC用） */
div.stButton > button:hover {
    background-color: #3FA9F5 !important;
    color: #FFFFFF !important;
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
    color: #333333 !important;
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
    background: #FFCC00; 
    margin: 12px auto 0;
    border-radius: 3px;
}

/* スマホ用 */
@media (max-width:1000px){
    [data-testid="stImage"]img{
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

# 📄 タブ構成（カード生成 / A4印刷シート）
tab_card, tab_a4 = st.tabs(["カード生成", "A4印刷シート"])

# 🟥 タブ1：カード生成
with tab_card:

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
    st.markdown("#### 📜 カードデータを読み込む")

    uploaded_json = st.file_uploader(
        "保存したJSONファイルを選択",
        type=["json"],
        key="json_loader"
    )

    if uploaded_json is not None:
        if st.button("📂 このカードを読み込む", key="load_json_card"):
            try:
                loaded_data = json.load(uploaded_json)

                # 読み込んだデータを入力欄にセット
                st.session_state["card_name"] = loaded_data.get("name", "")
                st.session_state["name_font_size"] = loaded_data.get(
                    "name_font_size", 65
                )
                st.session_state["cost"] = loaded_data.get("cost", 0)
                st.session_state["ctype"] = loaded_data.get("ctype", "")
                st.session_state["skill"] = loaded_data.get("skill", "")

                # 画像データを復元
                if loaded_data.get("image"):
                    st.session_state["loaded_image_bytes"] = base64.b64decode(
                        loaded_data["image"]
                    )
                else:
                    st.session_state["loaded_image_bytes"] = None

                # テンプレートを復元
                st.session_state["selected_template"] = loaded_data.get(
                    "template_name", ""
                )

                # 画像アップロード欄をリセット
                st.session_state["uploader_version"] += 1

                st.success("カードデータを読み込みました！")
                st.rerun()

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                st.error(f"JSONファイルを読み込めませんでした: {e}")
    name = st.text_input(
        "カード名",
        key="card_name"
    )
    # 初期値を Session State にセット（初回のみ）
    if "name_font_size" not in st.session_state:
        st.session_state["name_font_size"] = 65

    # スライダー（value は session_state の値を使う）
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

        # アップロード画像、または読み込んだ画像を取得
        if uploaded_img:
            img_bytes = uploaded_img.getvalue()

        elif st.session_state.get("loaded_image_bytes"):
            img_bytes = st.session_state["loaded_image_bytes"]

        else:
            img_bytes = None

        # 画像データをJSONに含める
        if img_bytes:
            card_data["image"] = base64.b64encode(
                img_bytes
            ).decode("utf-8")
        else:
            card_data["image"] = None

        # JSONデータをダウンロードできる形にする
        json_data = json.dumps(
            card_data,
            ensure_ascii=False,
            indent=2
        )

        st.download_button(
            label="📥 JSONファイルをダウンロード",
            data=json_data,
            file_name=f"{name or 'カード'}.json",
            mime="application/json",
            key="download_card_json"
        )
    if st.button("カードを保存する"):
        save_card()

    if st.button("カードを生成する"):
        if uploaded_img or st.session_state.get("loaded_image_bytes") or template_name == "full_text.png":

            if uploaded_img:
                art = Image.open(uploaded_img).convert("RGBA")

            elif st.session_state.get("loaded_image_bytes"):
                art = Image.open(
                    io.BytesIO(st.session_state["loaded_image_bytes"])
                ).convert("RGBA")
            else: art=Image.new("RGBA",image_size,(0,0,0,0))

            # テンプレート読み込み
            frame = Image.open(f"template/{template_name}").convert("RGBA")

            # 絵を縦横比を維持してリサイズ＆トリミング
            # ▼ フルテキストテンプレートの場合は画像処理をスキップ
            if template_name == "full_text.png":
                resized_art = None
            else:
                resized_art = ImageOps.fit(
                    art,
                    image_size,
                    method=Image.Resampling.LANCZOS,
                    centering=(0.5, 0.4)
                ).convert("RGBA")

            # 画像がある場合だけ貼り付け
            if resized_art is not None:
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


# 🟦 タブ2：A4印刷シート

# ▼トンボ描画
def draw_tombo(a4_image, x, y, card_w=744, card_h=1040):
    draw = ImageDraw.Draw(a4_image)

    line_len = 25      # トンボの長さ
    line_w = 2         # トンボの太さ
    fill_color = "#000000"
    # 左上（十字）
    draw.line((x - line_len, y, x + line_len, y), fill=fill_color, width=line_w)
    draw.line((x, y - line_len, x, y + line_len), fill=fill_color, width=line_w)
    # 右上
    draw.line((x + card_w - line_len, y, x + card_w + line_len, y), fill=fill_color, width=line_w)
    draw.line((x + card_w, y - line_len, x + card_w, y + line_len), fill=fill_color, width=line_w)
    # 左下
    draw.line((x - line_len, y + card_h, x + line_len, y + card_h), fill=fill_color, width=line_w)
    draw.line((x, y + card_h - line_len, x, y + card_h + line_len), fill=fill_color, width=line_w)
    # 右下
    draw.line((x + card_w - line_len, y + card_h, x + card_w + line_len, y + card_h), fill=fill_color, width=line_w)
    draw.line((x + card_w, y + card_h - line_len, x + card_w, y + card_h + line_len), fill=fill_color, width=line_w)

with tab_a4:
    st.write("カード生成画面でダウンロードしたPNGファイルをアップロードして、A4サイズに9枚並べて印刷できます。")

    uploaded_png_files = st.file_uploader(
        "A4に並べるカードのPNGファイルを選択（複数可）",
        type=["png"],
        accept_multiple_files=True,
        key="png_loader_a4"
    )

    png_names = [file.name for file in uploaded_png_files] if uploaded_png_files else []

    selected_png_names = st.multiselect(
        "A4に並べるカードを選択（最大9枚）",
        png_names,
        max_selections=9
    )

    # ▼ 余白モード選択
    margin_mode = st.radio(
        "余白モードを選ぶ",
        ["余白なし（ピッタリ配置）", "余白あり（スペースあり）"],
        horizontal=True
    )
    margin = 20  # 余白ありのときのスペース量

    # ▼ 余白なし座標
    positions_no_margin = [
        (0, 0), (744, 0), (1488, 0),
        (0, 1040), (744, 1040), (1488, 1040),
        (0, 2080), (744, 2080), (1488, 2080),
    ]
    # ▼ 余白あり座標
    positions_with_margin = [
        (margin, margin),
        (744 + margin*2, margin),
        (1488 + margin*3, margin),

        (margin, 1040 + margin*2),
        (744 + margin*2, 1040 + margin*2),
        (1488 + margin*3, 1040 + margin*2),

        (margin, 2080 + margin*3),
        (744 + margin*2, 2080 + margin*3),
        (1488 + margin*3, 2080 + margin*3),
    ]

    # ▼ モードに応じて座標を決定
    positions = positions_no_margin if margin_mode == "余白なし（ピッタリ配置）" else positions_with_margin

    # ▼ A4シート生成ボタン
    if st.button("A4シートを作成する"):
        if len(selected_png_names) == 0:
            st.warning("カードを選んでください")
        else:
            a4 = Image.new("RGBA", (2480, 3508), "white")

            for i, name in enumerate(selected_png_names):
                file = next(f for f in uploaded_png_files if f.name == name)
                card_img = Image.open(file).convert("RGBA")
                card_img = card_img.resize((744, 1040))

                # ▼ ここで positions を使う（必ず定義済み）
                x, y = positions[i]
                a4.paste(card_img, (x, y))

                # ▼ 余白ありのときだけトンボを描く
                if margin_mode == "余白あり（スペースあり）":
                    draw_tombo(a4, x, y)

            # プレビュー表示
            st.image(a4, caption="A4印刷シート", width="stretch")

            # PNGダウンロード
            buf_png = io.BytesIO()
            a4.save(buf_png, format="PNG")
            st.download_button(
                "PNGでダウンロード",
                buf_png.getvalue(),
                file_name="a4_sheet.png",
                mime="image/png"
            )

            # PDFダウンロード
            buf_pdf = io.BytesIO()
            a4.save(buf_pdf, format="PDF")
            st.download_button(
                "PDFでダウンロード",
                buf_pdf.getvalue(),
                file_name="a4_sheet.pdf",
                mime="application/pdf"
            )
