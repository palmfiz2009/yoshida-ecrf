import streamlit as st
import pandas as pd
from datetime import datetime

# 施設リスト
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

# ページ設定とカスタムCSS（デザイン調整）
st.set_page_config(page_title="JUOG UTUC_Conlidative CRF", layout="wide")

# CSSの修正: unsafe_allow_html=True が正しい引数です
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    h1 { font-size: 26px !important; color: #1E3A8A; margin-bottom: 30px; font-weight: bold; }
    h2 { font-size: 18px !important; color: #374151; border-left: 5px solid #1E3A8A; padding-left: 10px; margin-top: 35px; margin-bottom: 15px; }
    .stNumberInput, .stTextInput, .stSelectbox, .stDateInput { margin-bottom: -10px; }
    label { font-size: 14px !important; font-weight: 500 !important; color: #4B5563; }
    div[data-testid="stForm"] { border: 1px solid #E5E7EB; padding: 40px; border-radius: 12px; background-color: #FFFFFF; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stRadio > div { gap: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("JUOG UTUC_Conlidative 登録用CRF")

with st.form("main_form"):
    # --- セクション1：基本情報 ---
    st.header("患者基本情報")
    col1, col2, col3 = st.columns(3)
    with col1:
        facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
        patient_id = st.text_input("症例ID（事務局用）")
        consent_date = st.date_input("同意取得日*", value=None)
    with col2:
        age = st.number_input("同意取得時の年齢*", min_value=0, max_value=120, value=None)
        gender = st.radio("性別*", ["選択なし", "男", "女"], horizontal=True)
    with col3:
        height = st.number_input("身長 (cm)*", format="%.1f", value=None)
        weight = st.number_input("体重 (kg)*", format="%.1f", value=None)
        ps = st.radio("ECOG PS*", ["0", "1", "2以上（不適）"], horizontal=True)

    # --- セクション2：診断情報 ---
    st.header("診断・原発巣情報")
    col4, col5 = st.columns(2)
    with col4:
        diag_date = st.date_input("初回診断日（画像＋組織/細胞診）*", value=None)
        diag_type = st.multiselect("診断根拠となった検体*", ["組織診", "細胞診"])
        primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], horizontal=True)
    with col5:
        primary_size_pre = st.number_input("診断時_最大径 (mm)*", format="%.1f", value=None)
        ct = st.selectbox("診断時_cT*", ["選択なし", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
        cn = st.selectbox("診断時_cN*", ["選択なし", "cN0", "cN1", "cN2", "cN3"])
        cm = st.selectbox("診断時_cM*", ["選択なし", "cM0", "cM1"])

    # --- セクション3：転移巣情報 (cM1の時のみ表示) ---
    if cm == "cM1":
        st.header("転移巣情報 (cM1症例)")
        cols_met = st.columns(3)
        m_pre = []
        for i in range(1, 4):
            with cols_met[i-1]:
                st.selectbox(f"部位{i}", ["肺", "骨", "肝", "リンパ節", "その他", "該当なし"], key=f"site{i}")
                st.text_input(f"その他の場合：部位{i}", key=f"other{i}")
                m_pre.append(st.number_input(f"大きさ{i} (mm)", format="%.1f", value=None, key=f"msize{i}"))
        
        col_m_basis, col_m_tx = st.columns(2)
        with col_m_basis:
            cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択なし", "EVP療法によりCR", "局所療法により画像上活動性の遠隔転移病変消失、かつ3か月以上維持", "該当なし"])
        with col_m_tx:
            local_tx_type = st.selectbox("局所療法の種類*", ["選択なし", "放射線治療（外照射）", "放射線治療（定位照射）", "転移巣切除", "RFA・凍結療法など", "血管塞栓術", "その他", "該当なし"])
        cned_date = st.date_input("cNED確認日", value=None)

    # --- セクション4：EVP治療情報 ---
    st.header("EVP治療情報")
    col8, col9 = st.columns(2)
    with col8:
        evp_start = st.date_input("EVP 初回投与日*", value=None)
        evp_end = st.date_input("EVP 最終投与日*", value=None)
        ev_dose = st.number_input("EV 初回投与量 (mg/kg)*", format="%.2f", value=None)
        pembro_dose = st.number_input("Pembrolizumab 初回投与量 (mg/kg)*", format="%.2f", value=None)
    with col9:
        courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
        courses_reason = st.text_input("3コース未満の場合：理由")
        reduction = st.radio("EVP 減量の有無*", ["なし", "あり"], horizontal=True)
        reduction_detail = st.text_area("減量の詳細")

    col10, col11 = st.columns(2)
    with col10:
        eval_date = st.date_input("EVP 病勢制御確認日 (画像検査日)*", value=None)
        sd_date = st.text_input("SDの場合は、投与後画像評価初回日")
    with col11:
        best_effect = st.selectbox("EVP 最良総合効果*", ["選択なし", "CR", "PR", "SD", "PD"])
        recist_op = st.selectbox("手術前のRECIST判定*", ["選択なし", "CR", "PR", "SD", "PD（不適）"])

    # --- セクション5：手術前評価 ---
    st.header("手術前評価")
    col12, col13 = st.columns(2)
    with col12:
        primary_size_post = st.number_input("原発巣 手術前_最大径 (mm)*", format="%.1f", value=None)
    with col13:
        if cm == "cM1":
            m_post1 = st.number_input("転移巣① 手術前 (mm)", format="%.1f", value=None)
            m_post2 = st.number_input("転移巣② 手術前 (mm)", format="%.1f", value=None)
            m_post3 = st.number_input("転移巣③ 手術前 (mm)", format="%.1f", value=None)

    # --- セクション6：除外基準・手術予定 ---
    st.header("除外基準 & 手術予定")
    col14, col15 = st.columns(2)
    with col14:
        vessel_inv = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], horizontal=True)
        organ_inv = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], horizontal=True)
        ae_g3 = st.radio("G3以上の未回復のEVP有害事象*", ["なし", "あり（不適）"], horizontal=True)
    with col15:
        other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], horizontal=True)
        pregnancy = st.radio("妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], horizontal=True)
    
    col16, col17 = st.columns(2)
    with col16:
        op_type = st.selectbox("予定している手術*", ["選択なし", "根治的腎尿管全摘除術", "尿管部分切除術"])
    with col17:
        op_date = st.date_input("手術予定日", value=None)

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("適格性を判定する")

# --- 判定ロジック ---
if submit:
    reasons = []
    # 必須数値項目のチェック
    if any(v is None for v in [age, primary_size_pre, primary_size_post]):
        st.warning("必須項目（*印）を入力してください。")
    else:
        if age < 20: reasons.append("年齢20歳未満")
        if ps == "2以上（不適）": reasons.append("PS不良")
        
        # Stage IV判定 (T4 or N+ or M1)
        is_stage_iv = (ct == "cT4") or (cn not in ["選択なし", "cN0"]) or (cm == "cM1")
        if not is_stage_iv: reasons.
