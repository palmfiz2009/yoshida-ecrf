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

# ページ設定
st.set_page_config(page_title="JUOG UTUC_Conlidative CRF", layout="wide")

# デザイン調整 (CSS)
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 2rem; max-width: 980px; margin: auto; }
    h1 { font-size: 26px !important; color: #0F172A; text-align: center; margin-bottom: 30px; font-weight: 800; }
    h2 { font-size: 17px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; 
         padding: 10px 20px !important; border-radius: 8px !important; margin-top: 35px !important; margin-bottom: 15px !important; }
    label { font-size: 14px !important; font-weight: 600 !important; color: #334155; }
    .metric-card { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("JUOG UTUC_Conlidative 登録用CRF")

# --- 1. 基本情報 ---
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

# --- 2. 診断時・原発巣情報 ---
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
if cm == "cM1":
    st.header("転移巣情報 (cM1症例)")
    cm1_col1, cm1_col2, cm1_col3 = st.columns(3)
    m_pre_list = []
    for i, col in enumerate([cm1_col1, cm1_col2, cm1_col3], 1):
        with col:
            st.selectbox(f"部位{i}", ["肺", "骨", "肝", "リンパ節", "その他", "該当なし"], key=f"s_pre{i}")
            v = st.number_input(f"大きさ{i} (mm)", format="%.1f", value=None, key=f"ms_pre{i}")
            m_pre_list.append(v if v is not None else 0.0)
    m_pre_total = sum(m_pre_list)
    
    cb1, cb2 = st.columns(2)
    with cb1:
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択なし", "EVP療法によりCR", "局所療法により消失、3か月維持", "該当なし"])
    with cb2:
        local_tx = st.selectbox("局所療法の種類*", ["選択なし", "放射線", "手術", "RFA", "その他"])
    cned_date = st.date_input("cNED確認日", value=None)

# --- 4. 手術前評価（リアルタイム計算用） ---
st.header("手術前評価 & RECIST判定")
st.info("数値を入力すると、下の計算結果がリアルタイムで更新されます。")
cp1, cp2 = st.columns(2)
with cp1:
    primary_size_post = st.number_input("原発巣：手術前_最大径 (mm)*", format="%.1f", value=None)
    # 総合評価のための入力
    m_post_total = 0.0
    if cm == "cM1":
        st.write("---")
        st.markdown("**転移巣：手術前**")
        m_post_list = []
        for i in range(1, 4):
            v = st.number_input(f"転移巣{i} 手術前 (mm)", format="%.1f", value=None, key=f"mp_post{i}")
            m_post_list.append(v if v is not None else 0.0)
        m_post_total = sum(m_post_list)

with cp2:
    # リアルタイム計算ロジック
    if primary_size_pre and primary_size_post is not None:
        # SLD (Sum of Longest Diameters)
        sld_pre = primary_size_pre + m_pre_total
        sld_post = primary_size_post + m_post_total
        sld_change = ((sld_post - sld_pre) / sld_pre * 100) if sld_pre > 0 else 0
        
        # RECIST 自動判定
        if sld_post == 0: auto_recist = "CR"
        elif sld_change <= -30: auto_recist = "PR"
        elif sld_change >= 20: auto_recist = "PD"
        else: auto_recist = "SD"
        
        # 表示
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📊 リアルタイム評価")
        st.metric("長径和(SLD) 変化率", f"{sld_change:.1f}%")
        
        color = "green" if auto_recist in ["CR", "PR"] else "orange" if auto_recist == "SD" else "red"
        st.markdown(f"総合判定(RECIST 1.1): <span style='color:{color}; font-weight:bold; font-size:20px;'>{auto_recist}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("サイズを入力すると判定が表示されます")

# --- 5. EVP治療情報 & 除外基準 ---
st.header("EVP治療情報 & 除外基準")
ce1, ce2 = st.columns(2)
with ce1:
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択なし", "CR", "PR", "SD", "PD"])
    vessel = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], horizontal=True)
    organ = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], horizontal=True)
with ce2:
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
    other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], horizontal=True)
    pregnancy = st.radio("妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], horizontal=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 判定ボタン ---
if st.button("最終適格性を確定する", type="primary", use_container_width=True):
    missing = []
    if age is None: missing.append("年齢")
    if primary_size_pre is None: missing.append("診断時サイズ")
    if primary_size_post is None: missing.append("手術前サイズ")
    
    if missing:
        st.error(f"判定不可。必須項目を入力してください: {', '.join(missing)}")
    else:
        reasons = []
        # 適格性ロジック
        if age < 20: reasons.append("年齢20歳未満")
        if ps == "2以上（不適）": reasons.append("PS不良")
        
        # Stage IV判定
        is_stage_iv = (ct == "cT4") or (cn not in ["選択なし", "cN0"]) or (cm == "cM1")
        if not is_stage_iv: reasons.append("Stage IV条件未充足")
        
        # RECIST不適格判定（自動判定を使用）
        if auto_recist == "PD": reasons.append("RECIST判定がPD（20%以上の増大）です")
        if best_effect == "PD": reasons.append("EVP治療効果がPDです")
        
        if any(v == "あり（不適）" for v in [vessel, organ, other_cancer, pregnancy]):
            reasons.append("除外基準に抵触")

        st.markdown("---")
        if not reasons:
            st.success("✅ 適格 (Eligible): 研究登録可能です")
            st.balloons()
        else:
            st.error("❌ 不適格 (Ineligible)")
            for r in reasons: st.write(f"・{r}")
