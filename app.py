import streamlit as st
import pandas as pd
from datetime import datetime

# --- 設定：施設リスト ---
HOSPITALS = [
    "愛知県がんセンター", "秋田大学", "愛媛大学", "大分大学", "大阪公立大学", "大阪大学",
    "大阪府済生会野江病院", "岡山大学病院", "香川大学", "鹿児島大学", "関西医科大学",
    "岐阜大学医学部附属病院", "九州大学病院", "京都大学", "久留米大学", "神戸大学",
    "国立がん研究センター中央病院", "国立病院機構四国がんセンター", "札幌医科大学",
    "千葉大学", "筑波大学", "東京科学大学", "東京慈恵会医科大学附属柏病院",
    "東京慈恵会医科大学附属病院", "東北大学", "鳥取大学", "富山大学附属病院",
    "長崎大学病院", "名古屋大学", "奈良県立医科大学", "新潟大学大学院 医歯学総合研究科",
    "浜松医科大学", "原三信病院", "兵庫医科大学", "弘前大学医学部附属病院",
    "北海道大学", "三重大学", "横浜市立大学附属病院", "琉球大学病院", "和歌山県立医科大学"
]

# --- アプリの見た目設定 ---
st.set_page_config(page_title="吉田式 eCRF", layout="wide")
st.title("🛡️ 吉田 崇 先生 研究用 eCRF 登録・判定システム")

# --- 入力フォーム ---
with st.form("ecrf_form"):
    st.header("1. 基本情報")
    col1, col2 = st.columns(2)
    with col1:
        facility = st.selectbox("施設名", HOSPITALS)
        patient_id = st.text_input("症例ID (事務局記入用、施設からは空欄可)")
        consent_date = st.date_input("同意取得日")
        age = st.number_input("同意取得時の年齢", min_value=0, max_value=120, value=70)
        ps = st.radio("ECOG PS", ["0", "1", "2以上（不適）"], horizontal=True)

    with col2:
        st.subheader("診断時 TNM分類")
        ct = st.selectbox("診断時 cT", ["cTa", "cTisc", "cT1", "cT2", "cT3", "cT4"])
        cn = st.selectbox("診断時 cN", ["cN0", "cN1", "cN2", "cN3"])
        cm = st.selectbox("診断時 cM", ["cM0", "cM1"])
        
        cm1_basis = "該当なし"
        if cm == "cM1":
            cm1_basis = st.selectbox("cM1症例 登録根拠", [
                "EVP療法によりCR", 
                "局所療法により画像上活動性の遠隔転移病変消失、かつ3か月以上維持",
                "該当なし"
            ])

    st.markdown("---")
    st.header("2. 治療効果 (RECIST)")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("原発巣サイズ (mm)")
        pri_pre = st.number_input("診断時_最大径", value=0.0, step=0.1)
        pri_post = st.number_input("手術前_最大径", value=0.0, step=0.1)
    with col4:
        st.subheader("転移巣サイズ (mm)")
        m_pre = [st.number_input(f"転移{i} 診断時", value=0.0) for i in [1,2,3]]
        m_post = [st.number_input(f"転移{i} 手術前", value=0.0) for i in [1,2,3]]

    st.markdown("---")
    st.header("3. 除外基準 & 総合判定")
    ex_cols = st.columns(3)
    c1 = ex_cols[0].checkbox("切除不能な血管浸潤")
    c2 = ex_cols[1].checkbox("切除不能な臓器浸潤")
    c3 = ex_cols[2].checkbox("G3以上のEVP有害事象")
    c4 = ex_cols[0].checkbox("活動性の重複がん")
    c5 = ex_cols[1].checkbox("妊娠・授乳・同意困難等")
    
    best_eff = st.selectbox("EVP 最良総合効果", ["CR", "PR", "SD", "PD"])
    recist_op = st.selectbox("手術前のRECIST判定", ["CR", "PR", "SD", "PD"])

    submit_button = st.form_submit_button("適格性を判定してデータを送信")

# --- 判定ロジック ---
if submit_button:
    reasons = []
    if age < 20: reasons.append("20歳未満")
    if ps == "2以上（不適）": reasons.append("PS不良")
    is_stage_iv = (ct == "cT4") or (cn != "cN0") or (cm == "cM1")
    if not is_stage_iv: reasons.append("Stage IV条件未充足")
    if cm == "cM1" and cm1_basis == "該当なし": reasons.append("cM1根拠なし")
    if best_eff == "PD" or recist_op == "PD": reasons.append("PD(病勢進行)")
    if any([c1, c2, c3, c4, c5]): reasons.append("除外基準抵触")

    pri_red = ((pri_post - pri_pre) / pri_pre * 100) if pri_pre > 0 else 0
    met_sum_pre = sum(m_pre)
    met_sum_post = sum(m_post)
    met_red = ((met_sum_post - met_sum_pre) / met_sum_pre * 100) if met_sum_pre > 0 else 0

    st.markdown("---")
    if not reasons:
        st.success(f"⭕ 適格 (Eligible) / 原発巣縮小率: {pri_red:.1f}% / 転移巣縮小率: {met_red:.1f}%")
        st.balloons()
        # ここでGoogle Sheetsなどに保存する処理を呼び出す
        st.info("データが事務局へ送信されました。この画面を保存してください。")
    else:
        st.error(f"❌ 不適格 (Ineligible): {', '.join(reasons)}")
