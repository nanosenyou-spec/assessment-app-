
import streamlit as st
import pandas as pd

# ==========================================
# 1. ページ基本設定
# ==========================================

st.set_page_config(
    page_title="情報理解アセスメント",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. デザイン設定
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa;
    color: #212529;
}

.stButton > button {
    width: 100%;
    min-height: 85px;
    font-size: 22px !important;
    font-weight: bold;
    border-radius: 12px;
    border: 2px solid #ced4da;
    background-color: #ffffff;
    color: #333333;
    margin-bottom: 10px;
}

.stButton > button:hover {
    border-color: #4d90fe;
    background-color: #e8f0fe;
    color: #1a365d;
}

.prompt-box {
    background-color: #ffffff;
    border: 3px solid #4a90e2;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: #1a365d;
    margin-bottom: 24px;
}

.support-badge {
    background-color: #fff3cd;
    color: #856404;
    border: 1px solid #ffeeba;
    padding: 12px 18px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. アセスメント問題データ
# ==========================================

ASSESSMENT_MODULES = [

    {
        "id": "L1",
        "level_name": "Level 1：文字（単語）理解",
        "media_type": "文字",
        "prompt": "【コップ】",
        "correct": "コップ",
        "options": ["コップ", "タオル", "スプーン", "椅子"],
        "support_options": ["コップ", "タオル"],
        "hint": "身近な飲み物を飲む道具です。"
    },

    {
        "id": "L2",
        "level_name": "Level 2：文字（文章）理解",
        "media_type": "文章",
        "prompt": "【てをあらう】",
        "correct": "手を洗う",
        "options": ["手を洗う", "片付ける", "椅子に座る", "ドアを開ける"],
        "support_options": ["手を洗う", "片付ける"],
        "hint": "石鹸を使ってきれいにする動作です。"
    },

    {
        "id": "L3",
        "level_name": "Level 3：絵（単一イラスト）理解",
        "media_type": "絵カード",
        "prompt": "【絵：タオルのイラスト】",
        "correct": "タオル",
        "options": ["コップ", "タオル", "スプーン", "椅子"],
        "support_options": ["タオル", "スプーン"],
        "hint": "手や顔を拭くものです。"
    },

    {
        "id": "L4",
        "level_name": "Level 4：絵（動作イラスト）理解",
        "media_type": "動作絵カード",
        "prompt": "【絵：椅子に座る動作イラスト】",
        "correct": "座る",
        "options": ["洗う", "座る", "片付ける", "歩く"],
        "support_options": ["座る", "洗う"],
        "hint": "椅子を使う動作です。"
    },

    {
        "id": "L5",
        "level_name": "Level 5：写真（実物写真）理解",
        "media_type": "実物写真カード",
        "prompt": "【写真：スプーンの実物写真】",
        "correct": "スプーン",
        "options": ["コップ", "タオル", "スプーン", "椅子"],
        "support_options": ["スプーン", "コップ"],
        "hint": "食事のときに使う道具です。"
    },

    {
        "id": "L6",
        "level_name": "Level 6：写真（動作写真）理解",
        "media_type": "動作写真カード",
        "prompt": "【写真：おもちゃを箱に片付ける様子】",
        "correct": "片付ける",
        "options": ["洗う", "座る", "片付ける", "開ける"],
        "support_options": ["片付ける", "座る"],
        "hint": "使ったものを元の場所に戻す動作です。"
    },

    {
        "id": "L7",
        "level_name": "Level 7：2工程手順（手順配列）理解",
        "media_type": "2工程手順カード",
        "prompt": "①【てをあらう】→②【てをふく】",
        "correct": "1. 手を洗う 2. 手を拭く",
        "options": [
            "1. 手を洗う 2. 手を拭く",
            "1. 手を拭く 2. 手を洗う",
            "1. 座る 2. 片付ける",
            "1. 片付ける 2. 座る"
        ],
        "support_options": [
            "1. 手を洗う 2. 手を拭く",
            "1. 手を拭く 2. 手を洗う"
        ],
        "hint": "最初に手を洗ってから、タオルで拭きます。"
    }
]


# ==========================================
# 4. セッション状態の初期化
# ==========================================

defaults = {
    "current_index": 0,
    "support_mode": False,
    "results": {},
    "test_completed": False,
    "child_name": "",
    "child_id": "",
    "age": 18,
    "note": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# 5. 共通処理
# ==========================================

def next_question():
    """次の課題へ進む"""
    st.session_state.support_mode = False

    if st.session_state.current_index + 1 < len(ASSESSMENT_MODULES):
        st.session_state.current_index += 1
    else:
        st.session_state.test_completed = True

    st.rerun()


def save_result(question, evaluation, detail):
    """評価結果を保存する"""
    st.session_state.results[question["id"]] = {
        "level": question["level_name"],
        "media": question["media_type"],
        "eval": evaluation,
        "detail": detail
    }


def answer_question(option, question):
    """回答判定"""

    if option == question["correct"]:

        if st.session_state.support_mode:
            save_result(
                question,
                "E",
                "選択肢削減などの支援後に正答"
            )
        else:
            save_result(
                question,
                "P",
                "初回提示で正答"
            )

        next_question()

    else:

        if not st.session_state.support_mode:

            # 初回誤答：支援モードへ移行
            st.session_state.support_mode = True

            st.toast(
                "提示方法を調整します。選択肢を絞り込みます。"
            )

            st.rerun()

        else:

            # 支援後も誤答
            save_result(
                question,
                "F",
                "支援適用下でも不一致"
            )

            next_question()


# ==========================================
# 6. サイドバー
# ==========================================

st.sidebar.title("支援者用メニュー")

mode = st.sidebar.radio(
    "表示画面",
    [
        "テスト実施画面（当事者用）",
        "アセスメント結果レポート",
        "対象者設定"
    ]
)

st.sidebar.markdown("---")

st.sidebar.subheader("現在の対象者情報")

st.sidebar.write(f"ID：{st.session_state.child_id or '未設定'}")
st.sidebar.write(f"氏名：{st.session_state.child_name or '未設定'}")

if st.sidebar.button("アセスメントをリセット"):

    st.session_state.current_index = 0
    st.session_state.support_mode = False
    st.session_state.results = {}
    st.session_state.test_completed = False

    st.rerun()


# ==========================================
# 7. 対象者設定画面
# ==========================================

if mode == "対象者設定":

    st.title("被評価者プロフィール設定")

    col1, col2 = st.columns(2)

    with col1:

        st.session_state.child_id = st.text_input(
            "ID",
            value=st.session_state.child_id
        )

        st.session_state.child_name = st.text_input(
            "対象者氏名 / ニックネーム",
            value=st.session_state.child_name
        )

        st.session_state.age = st.number_input(
            "年齢",
            min_value=1,
            max_value=100,
            value=st.session_state.age
        )

    with col2:

        st.session_state.note = st.text_area(
            "特記事項（得意な刺激・環境の配慮等）",
            value=st.session_state.note,
            height=150
        )

    st.success(
        "設定情報を入力しました。左メニューからテスト実施画面に切り替えてください。"
    )


# ==========================================
# 8. テスト実施画面
# ==========================================

elif mode == "テスト実施画面（当事者用）":

    st.title("情報理解アセスメント")

    if st.session_state.test_completed:

        st.balloons()

        st.success("すべてのアセスメント課題が完了しました！")

        st.info(
            "左側のメニューから「アセスメント結果レポート」を開いてください。"
        )

    else:

        current_q = ASSESSMENT_MODULES[
            st.session_state.current_index
        ]

        # 進行度
        progress = (
            st.session_state.current_index
            / len(ASSESSMENT_MODULES)
        )

        st.progress(progress)

        st.caption(
            f"課題 {st.session_state.current_index + 1} / "
            f"{len(ASSESSMENT_MODULES)}　"
            f"（{current_q['level_name']}）"
        )

        # 支援モード表示
        if st.session_state.support_mode:

            st.markdown(
                f"""
                <div class="support-badge">
                支援モード適用中：選択肢を減らしています
                <br>
                {current_q['hint']}
                </div>
                """,
                unsafe_allow_html=True
            )

        # 課題提示
        st.markdown(
            f"""
            <div class="prompt-box">
            {current_q['prompt']}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader(
            "同じもの・正しいカードを選んでタップしてください"
        )

        # 選択肢の決定
        if st.session_state.support_mode:
            current_options = current_q["support_options"]
        else:
            current_options = current_q["options"]

        # 2列配置
        col1, col2 = st.columns(2)

        for i, opt in enumerate(current_options):

            target_col = col1 if i % 2 == 0 else col2

            with target_col:

                if st.button(
                    opt,
                    key=(
                        f"btn_{st.session_state.current_index}_"
                        f"{i}_{st.session_state.support_mode}"
                    )
                ):

                    answer_question(opt, current_q)

        # 支援者用操作
        with st.expander("支援者用手動コントロール"):

            st.write(
                "対象者の状態に合わせて手動で支援や移動を行えます。"
            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(
                    "支援モード切り替え",
                    key="manual_support"
                ):

                    st.session_state.support_mode = (
                        not st.session_state.support_mode
                    )

                    st.rerun()

            with c2:

                if st.button(
                    "次の課題へスキップ",
                    key="manual_skip"
                ):

                    save_result(
                        current_q,
                        "F",
                        "支援者による手動スキップ"
                    )

                    next_question()


# ==========================================
# 9. アセスメント結果レポート
# ==========================================

elif mode == "アセスメント結果レポート":

    st.title("情報理解アセスメント 評価レポート")

    st.subheader(
        f"対象者：{st.session_state.child_name or '未設定'} "
        f"（ID：{st.session_state.child_id or '未設定'}）"
    )

    if not st.session_state.results:

        st.warning(
            "まだ評価データが記録されていません。"
            "テスト実施画面からテストを行ってください。"
        )

    else:

        # 結果一覧
        res_list = []

        for q_id, res in st.session_state.results.items():

            res_list.append({
                "課題ID": q_id,
                "課題モジュール": res["level"],
                "提示媒体": res["media"],
                "評価（P/E/F）": res["eval"],
                "評価詳細・応答状況": res["detail"]
            })

        df_res = pd.DataFrame(res_list)

        # 評価集計
        p_count = sum(
            1 for r in st.session_state.results.values()
            if r["eval"] == "P"
        )

        e_count = sum(
            1 for r in st.session_state.results.values()
            if r["eval"] == "E"
        )

        f_count = sum(
            1 for r in st.session_state.results.values()
            if r["eval"] == "F"
        )

        total = len(ASSESSMENT_MODULES)
        completed = len(st.session_state.results)

        # 指標表示
        m1, m2, m3 = st.columns(3)

        m1.metric("P：初回提示で正答", f"{p_count}課題")
        m2.metric("E：支援後に正答", f"{e_count}課題")
        m3.metric("F：支援後も誤答", f"{f_count}課題")

        st.caption(
            f"実施済み：{completed} / {total}課題"
        )

        st.markdown("---")

        # 課題別判定
        st.subheader("課題別判定詳細")

        def highlight_eval(val):

            if val == "P":
                return (
                    "background-color: #d4edda;"
                    "color: #155724;"
                    "font-weight: bold;"
                )

            elif val == "E":
                return (
                    "background-color: #fff3cd;"
                    "color: #856404;"
                    "font-weight: bold;"
                )

            elif val == "F":
                return (
                    "background-color: #f8d7da;"
                    "color: #721c24;"
                    "font-weight: bold;"
                )

            return ""

        styled_df = df_res.style.map(
            highlight_eval,
            subset=["評価（P/E/F）"]
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

        # ==================================
        # 10. 提示媒体別の分析
        # ==================================

        st.markdown("---")

        st.subheader("提示媒体別の評価")

        media_summary = (
            df_res.groupby(["提示媒体", "評価（P/E/F）"])
            .size()
            .unstack(fill_value=0)
        )

        for col in ["P", "E", "F"]:
            if col not in media_summary.columns:
                media_summary[col] = 0

        st.dataframe(
            media_summary[["P", "E", "F"]],
            use_container_width=True
        )

        # ==================================
        # 11. 支援方法の推奨
        # ==================================

        st.markdown("---")

        st.subheader(
            "個別支援計画への推奨事項"
        )

        p_medias = [
            r["media"]
            for r in st.session_state.results.values()
            if r["eval"] == "P"
        ]

        e_medias = [
            r["media"]
            for r in st.session_state.results.values()
            if r["eval"] == "E"
        ]

        f_medias = [
            r["media"]
            for r in st.session_state.results.values()
            if r["eval"] == "F"
        ]

        if p_medias:

            st.success(
                "初回提示で正答した媒体："
                + "、".join(p_medias)
            )

            if "文字" in p_medias or "文章" in p_medias:

                st.write(
                    "・文字によるスケジュールや手順書の提示を検討できます。"
                )

            if "絵カード" in p_medias or "動作絵カード" in p_medias:

                st.write(
                    "・イラストを用いた視覚的な手順提示を検討できます。"
                )

            if (
                "実物写真カード" in p_medias
                or "動作写真カード" in p_medias
            ):

                st.write(
                    "・実際の物品や活動場面に近い写真カードの活用を検討できます。"
                )

            if "2工程手順カード" in p_medias:

                st.write(
                    "・2工程の手順提示を検討できます。"
                )

        else:

            st.info(
                "初回提示で正答した媒体はありません。"
                "具体物や実際の活動場面での理解も確認してください。"
            )

        if e_medias:

            st.warning(
                "支援後に正答した媒体："
                + "、".join(e_medias)
            )

            st.write(
                "・選択肢の削減や提示方法の調整によって、"
                "理解しやすくなる可能性があります。"
            )

        if f_medias:

            st.error(
                "支援後も誤答した媒体："
                + "、".join(f_medias)
            )

            st.write(
                "・具体物を用いた確認、課題の細分化、"
                "提示方法や環境の再検討が必要です。"
            )

        if (
            "2工程手順カード" in e_medias
            or "2工程手順カード" in f_medias
        ):

            st.write(
                "・連続した指示では、1工程ずつ提示し、"
                "各工程の完了を確認する方法を検討してください。"
            )

        st.caption(
            "※これらは本アセスメント内の応答に基づく支援仮説です。"
            "日常生活での行動観察や実際の課題遂行と併せて判断してください。"
        )

        # ==================================
        # 12. CSV出力
        # ==================================

        st.markdown("---")

        csv_data = df_res.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            label="アセスメント結果データ（CSV）をダウンロード",
            data=csv_data,
            file_name=(
                f"assessment_report_"
                f"{st.session_state.child_id or 'unknown'}.csv"
            ),
            mime="text/csv"
        )

