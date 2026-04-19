import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

# ページ設定
st.set_page_config(page_title="JUOG UTUC_Conlidative CRF", layout="wide")

# デザイン調整 (CSS)
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 2rem; max-width: 1000px; margin: auto; }
    h1 { font-size: 26px !important; color: #0F172A; text-align: center; margin-bottom: 30px; font-weight: 800; }
    h2 { 
        font-size: 17px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; 
        padding: 12px 20px !important; border-radius: 8px !important; margin-top: 35px !important; margin-bottom: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    span[data-baseweb="tag"] {
        background-color: #E2E8F0 !important;
        color: #1E293B !important;
    }
    label { font-size: 14px !important; font-weight: 600 !important; color: #334155; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; }
    </style>
    """, unsafe_allow_html=True)

st.title("JUOG UTUC_Conlidative 登録用CRF")

# --- 1. 患者基本情報 ---
st.header("患者基本情報")
c1, c2, c3 = st.columns(3)
with c1:
    facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
    patient_id = st.text_input("症例ID（事務局用）")
    consent_date = st.date_input("同意取得日*", value=None)
with c2:
    age = st.number_input("同意取得時の年齢*", min_value=0, max_value=120, value=None)
    gender = st.radio("性別*", ["選択なし", "男", "女"], horizontal=True)
with c3:
    height = st.number_input("身長 (cm)*", format="%.1f", value=None)
    weight = st.number_input("体重 (kg)*", format="%.1f", value=None)
    ps = st.radio("ECOG PS*", ["0", "1", "2以上（不適）"], horizontal=True)

# --- 2. 原発巣情報 (診断時) ---
st.header("原発巣情報 (診断時)")
c4, c5 = st.columns(2)
with c4:
    diag_date = st.date_input("初回診断日*", value=None)
    diag_type = st.multiselect("診断根拠*", ["組織診", "細胞診"])
    primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], horizontal=True)
    primary_size_pre = st.number_input("原発巣：診断時_最大径 (mm)*", format="%.1f", value=None)
with c5:
    ct = st.selectbox("診断時_cT*", ["選択なし", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
    cn = st.selectbox("診断時_cN*", ["選択なし", "cN0", "cN1", "cN2", "cN3"])
    cm = st.selectbox("診断時_cM*", ["選択なし", "cM0", "cM1"])

# --- 3. 転移巣情報 (cM1のみ) ---
m_pre_total = 0.0
cm1_basis = "該当なし"
cned_date = None
site_1 = "選択なし"
size_1 = None

if cm == "cM1":
    st.header("転移巣情報 (cM1症例)")
    cm1_cols = st.columns(3)
    m_pre_list = []
    
    # 部位1 (入力必須)
    with cm1_cols[0]:
        site_1 = st.selectbox("部位1*", ["選択してください", "肺", "骨", "肝", "リンパ節", "その他"], key="site_1")
        if site_1 == "その他":
            st.text_input("部位1の詳細*", key="site_detail_1")
        size_1 = st.number_input("大きさ1 (mm)*", format="%.1f", value=None, key="size_1")
        m_pre_list.append(size_1 if size_1 is not None else 0.0)
    
    # 部位2 & 3 (任意)
    for i in range(2, 4):
        with cm1_cols[i-1]:
            site = st.selectbox(f"部位{i}", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key=f"site_{i}")
            if site == "その他":
                st.text_input(f"部位{i}の詳細", key=f"site_detail_{i}")
            v = st.number_input(f"大きさ{i} (mm)", format="%.1f", value=None, key=f"size_{i}")
            m_pre_list.append(v if v is not None else 0.0)
            
    m_pre_total = sum(m_pre_list)
    
    cb1, cb2 = st.columns(2)
    with cb1:
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択なし", "EVP療法によりCR", "局所療法により画像上活動性の遠隔転移病変消失、かつ3か月以上維持"])
    with cb2:
        local_tx = st.selectbox("局所療法の種類*", ["選択なし", "放射線治療（外照射）", "放射線治療（定位照射）", "転移巣切除", "RFA・凍結療法など", "血管塞栓術：TACE/TAEなど", "その他", "該当なし"])
        if local_tx == "その他":
            st.text_input("局所療法の詳細", key="local_tx_detail")
    cned_date = st.date_input("cNED確認日*", value=None)

# --- 4. EVP治療情報 ---
st.header("EVP治療情報")
ce1, ce2 = st.columns(2)
with ce1:
    evp_start = st.date_input("EVP 初回投与日*", value=None)
    evp_end = st.date_input("EVP 最終投与日*", value=None)
    ev_dose = st.number_input("EV 初回投与量 (mg/kg)*", format="%.2f", value=None)
    pembro_dose = st.number_input("Pembrolizumab 初回投与量 (mg/kg)*", format="%.2f", value=None)
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択なし", "CR", "PR", "SD", "PD"])
with ce2:
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
    courses_reason = st.text_input("3コース未満の場合：理由")
    reduction = st.radio("EVP 減量の有無*", ["なし", "あり"], horizontal=True)
    if reduction == "あり":
        reduction_detail = st.text_area("減量の詳細", height=68)
    eval_date = st.date_input("EVP 病勢制御確認日 (SDの場合は、投与後画像評価初回日)*", value=None)

# --- 5. 手術前評価 & RECIST判定 ---
st.header("手術前評価 & RECIST判定")
cp1, cp2 = st.columns(2)
with cp1:
    primary_size_post = st.number_input("原発巣：手術前_最大径 (mm)*", format="%.1f", value=None)
    m_post_total = 0.0
    if cm == "cM1":
        st.markdown("**転移巣：手術前**")
        m_post_list = []
        for i in range(1, 4):
            v = st.number_input(f"転移巣{i} 手術前 (mm)", format="%.1f", value=None, key=f"mpost_val_{i}")
            m_post_list.append(v if v is not None else 0.0)
        m_post_total = sum(m_post_list)

with cp2:
    auto_recist = "未入力"
    sld_change = 0.0
    if primary_size_pre and primary_size_post is not None:
        sld_pre = primary_size_pre + m_pre_total
        sld_post = primary_size_post + m_post_total
        sld_change = ((sld_post - sld_pre) / sld_pre * 100) if sld_pre > 0 else 0
        if sld_post == 0: auto_recist = "CR"
        elif sld_change <= -30: auto_recist = "PR"
        elif sld_change >= 20: auto_recist = "PD"
        else: auto_recist = "SD"
        
        st.write("### 評価結果（リアルタイム）")
        st.metric("長径和(SLD) 変化率", f"{sld_change:.1f}%")
        st.markdown(f"総合RECIST判定: **{auto_recist}**")

# --- 6. 除外基準 & 手術予定 ---
st.header("除外基準 & 手術予定")
cx1, cx2 = st.columns(2)
with cx1:
    vessel = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], horizontal=True)
    organ = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], horizontal=True)
    ae_g3 = st.radio("G3以上の未回復のEVP有害事象*", ["なし", "あり（不適）"], horizontal=True)
with cx2:
    other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], horizontal=True)
    pregnancy = st.radio("妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], horizontal=True)
    op_type = st.selectbox("予定している手術*", ["選択なし", "根治的腎尿管全摘除術", "尿管部分切除術"])
    op_date = st.date_input("手術予定日", value=None)

st.markdown("<br>", unsafe_allow_html=True)

# --- 最終判定 ---
if st.button("最終適格性を判定する", type="primary", use_container_width=True):
    reasons = []
    # 基本必須チェック
    if any(v is None for v in [age, consent_date, diag_date, evp_start, eval_date, primary_size_pre, primary_size_post]):
        st.error("必須項目（*印）をすべて入力してください。")
    else:
        # cM1時の必須項目チェック
        if cm == "cM1":
            if site_1 == "選択してください" or size_1 is None:
                reasons.append("転移巣の部位1およびその大きさは必須項目です")
            if cned_date and cned_date > (consent_date - timedelta(days=90)):
                reasons.append("cNED確認日は同意取得日より3ヶ月以上前である必要があります")
        
        # 日付・医学的チェック
        if evp_start <= diag_date:
            reasons.append("EVP初回投与日は診断日より後の日付である必要があります")
        if eval_date < (evp_start + timedelta(weeks=9)):
            reasons.append("病勢制御確認日はEVP開始から少なくとも9週間経過している必要があります")
        if age < 20: reasons.append("年齢20歳未満")
        if ps == "2以上（不適）": reasons.append("PS不良")
        
        is_stage_iv = (ct == "cT4") or (cn not in ["選択なし", "cN0"]) or (cm == "cM1")
        if not is_stage_iv: reasons.append("Stage IV条件未充足")
        if cm == "cM1" and cm1_basis == "選択なし": reasons.append("cM1登録根拠が未選択です")
        if auto_recist == "PD" or best_effect == "PD": reasons.append("PD(病勢進行)のため対象外")
        if any(v == "あり（不適）" for v in [vessel, organ, ae_g3, other_cancer, pregnancy]):
            reasons.append("除外基準に抵触しています")

        st.markdown("---")
        if not reasons:
            st.success("⭕ 適格 (Eligible): 研究登録可能です")
            st.balloons()
        else:
            st.error("❌ 不適格 (Ineligible)")
            for r in reasons: st.write(f"・{r}")
