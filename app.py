import streamlit as st
import json
from datetime import date, datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# --- ページ設定 ---
st.set_page_config(page_title="JUOG UTUC_Consolidative 登録CRF", layout="wide")

# --- JUOG専用デザインCSS ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; }
    .block-container { 
        max-width: 1100px !important; 
        padding-top: 1.5rem !important; 
        padding-bottom: 5rem !important; 
        margin: auto !important;
    }
    h1 { 
        font-size: 26px !important; 
        color: #0F172A; 
        text-align: center; 
        margin-top: 0px !important; 
        margin-bottom: 80px !important; 
        font-weight: 800; 
        height: 40px;
    }
    .juog-header {
        background-color: #1E3A8A;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    label { font-weight: 600 !important; color: #334155 !important; }
    div[data-baseweb="select"] ul { white-space: normal !important; }
    div[role="option"] { line-height: 1.4 !important; padding: 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 施設リスト ---
FACILITY_LIST = ["選択してください", "愛知県がんセンター", "秋田大学", "愛媛大学", "大分大学", "大阪公立大学", "大阪大学", "大阪府済生会野江病院", "岡山大学", "香川大学", "鹿児島大学", "関西医科大学", "岐阜大学", "九州大学病院", "京都大学", "久留米大学", "神戸大学", "国立がん研究センター中央病院", "国立病院機構四国がんセンター", "札幌医科大学", "千葉大学", "筑波大学", "東京科学大学", "東京慈恵会医科大学", "東京慈恵会医科大学附属柏病院", "東北大学", "鳥取大学", "富山大学", "長崎大学病院", "名古屋大学", "奈良県立医科大学", "新潟大学大学院 医歯学総合研究科", "浜松医科大学", "原三信病院", "兵庫医科大学", "弘前大学", "北海道大学", "三重大学", "横浜市立大学", "琉球大学", "和歌山県立医科大学", "その他"]

# --- セッション状態の初期化 ---
if 'init_reg_v_original_restored' not in st.session_state:
    st.session_state['init_reg_v_original_restored'] = True
    defaults = {
        "facility_name": "選択してください", "reporter_email": "", "patient_id": "",
        "age": 65, "sex": "選択してください", "ps": "選択してください",
        "disease_type": "選択してください", "t_factor": "選択してください", "n_factor": "選択してください", "m_factor": "選択してください",
        "m_sites": [], "m_other_detail": "", "prior_tx_evp": None,
        "max_size_diag": None, "ct_date_diag": None, "cysto_date": None, "biopsy_date": None,
        "hb_pre": None, "wbc_pre": None, "cre_pre": None, "egfr_pre": None, "blood_date_pre": None,
        "evp_start_date": None, "evp_end_date": None, "evp_cycles": 1, "evp_reduction": None, "evp_reduction_detail": "", "evp_stop": None, "evp_stop_detail": "",
        "max_size_post": None, "ct_date_post": None, "response_eval": "選択してください",
        "hb_post": None, "wbc_post": None, "cre_post": None, "egfr_post": None, "blood_date_post": None
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def get_idx(options, value):
    try: return options.index(value)
    except: return 0

def send_email(report_content, pid, facility, reporter_email=None):
    try:
        mail_user = st.secrets["email"]["user"]; mail_pass = st.secrets["email"]["pass"]
        to_addrs = ["urosec@kmu.ac.jp", "yoshida.tks@kmu.ac.jp"]
        if reporter_email: to_addrs.append(reporter_email)
        msg = MIMEMultipart(); msg['From'] = mail_user; msg['To'] = ", ".join(to_addrs)
        msg['Subject'] = f"【JUOG 登録】（{facility} / ID: {pid}）"
        msg.attach(MIMEText(report_content, 'plain'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(mail_user, mail_pass); server.send_message(msg); server.quit()
        return True
    except: return False

st.title("JUOG UTUC_Consolidative 症例登録システム")

# --- 共通ヘッダー（基本情報） ---
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.session_state.facility_name = st.selectbox("施設名*", FACILITY_LIST, index=get_idx(FACILITY_LIST, st.session_state.facility_name))
    st.session_state.reporter_email = st.text_input("担当者メールアドレス*", value=st.session_state.reporter_email)
with col_h2:
    st.session_state.patient_id = st.text_input("研究対象者識別コード*", value=st.session_state.patient_id)

st.divider()

# --- 1. 患者基本情報・適格性判定 ---
st.markdown('<div class="juog-header">1. 患者基本情報・適格性判定</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.session_state.age = st.number_input("登録時年齢*", min_value=20, max_value=120, value=st.session_state.age)
    st.session_state.sex = st.radio("性別*", ["選択してください", "男性", "女性"], index=get_idx(["選択してください", "男性", "女性"], st.session_state.sex), horizontal=True)
    ps_opts = ["選択してください", "0", "1", "2", "3", "4"]
    st.session_state.ps = st.selectbox("ECOG PS*", ps_opts, index=get_idx(ps_opts, st.session_state.ps))
    dt_opts = ["選択してください", "上部尿路癌（尿路上皮癌）", "その他の癌（不適格）"]
    st.session_state.disease_type = st.selectbox("対象疾患・組織型*", dt_opts, index=get_idx(dt_opts, st.session_state.disease_type))
    st.session_state.prior_tx_evp = st.radio("本試験前のEVP療法歴*", ["なし", "あり（不適格）"], index=(0 if st.session_state.prior_tx_evp=="なし" else 1 if st.session_state.prior_tx_evp=="あり（不適格）" else None), horizontal=True)

with c2:
    st.markdown("**【cTNM分類 (EVP療法開始前)】**")
    t_opts = ["選択してください", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4", "cTx"]
    st.session_state.t_factor = st.selectbox("cT*", t_opts, index=get_idx(t_opts, st.session_state.t_factor))
    n_opts = ["選択してください", "cN0", "cN1", "cN2", "cN3", "cNx"]
    st.session_state.n_factor = st.selectbox("cN*", n_opts, index=get_idx(n_opts, st.session_state.n_factor))
    m_opts = ["選択してください", "cM0", "cM1"]
    st.session_state.m_factor = st.selectbox("cM*", m_opts, index=get_idx(m_opts, st.session_state.m_factor))
    
    if st.session_state.m_factor == "cM1":
        st.session_state.m_sites = st.multiselect("転移部位*", ["リンパ節（所属外）", "肺", "肝", "骨", "その他"], default=st.session_state.m_sites)
        if "その他" in st.session_state.m_sites:
            st.session_state.m_other_detail = st.text_input("転移部位の詳細*", value=st.session_state.m_other_detail)

# --- 2. 診断時・EVP療法前の臨床データ ---
st.markdown('<div class="juog-header">2. 診断時・EVP療法前の臨床データ</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    # クラッシュ防止のkey設定
    st.session_state.max_size_diag = st.number_input("診断時最大径（画像・内視鏡）(mm)*", value=st.session_state.max_size_diag, step=1.0, key="k_size_pre")
    st.session_state.ct_date_diag = st.date_input("診断時CT/MRI 撮影日*", value=st.session_state.ct_date_diag)
    st.session_state.cysto_date = st.date_input("診断時膀胱鏡/尿管鏡 実施日*", value=st.session_state.cysto_date)
    st.session_state.biopsy_date = st.date_input("診断時生検 実施日*", value=st.session_state.biopsy_date)
with c4:
    st.markdown("**EVP療法開始前の主要採血データ**")
    st.session_state.blood_date_pre = st.date_input("採血実施日(Pre)*", value=st.session_state.blood_date_pre)
    bx1, bx2 = st.columns(2)
    st.session_state.hb_pre = bx1.number_input("Hb (g/dL)*", value=st.session_state.hb_pre, key="h_pre")
    st.session_state.wbc_pre = bx2.number_input("WBC (/μL)*", value=st.session_state.wbc_pre, key="w_pre")
    st.session_state.cre_pre = bx1.number_input("Cre (mg/dL)*", value=st.session_state.cre_pre, key="c_pre")
    st.session_state.egfr_pre = bx2.number_input("eGFR*", value=st.session_state.egfr_pre, key="e_pre")

# --- 3. 術前EVP療法の実施状況 ---
st.markdown('<div class="juog-header">3. 術前EVP療法の実施状況</div>', unsafe_allow_html=True)
ec1, ec2 = st.columns(2)
with ec1:
    st.session_state.evp_start_date = st.date_input("EVP療法 開始日*", value=st.session_state.evp_start_date)
    st.session_state.evp_end_date = st.date_input("EVP療法 最終投与日*", value=st.session_state.evp_end_date)
    st.session_state.evp_cycles = st.number_input("実施サイクル数*", min_value=1, max_value=20, value=st.session_state.evp_cycles)
with ec2:
    st.session_state.evp_reduction = st.radio("減量の有無*", ["なし", "あり"], index=(0 if st.session_state.evp_reduction=="なし" else 1 if st.session_state.evp_reduction=="あり" else None), horizontal=True)
    if st.session_state.evp_reduction == "あり":
        st.session_state.evp_reduction_detail = st.text_area("減量の詳細*", value=st.session_state.evp_reduction_detail)
    st.session_state.evp_stop = st.radio("途中中止の有無*", ["なし", "あり"], index=(0 if st.session_state.evp_stop=="なし" else 1 if st.session_state.evp_stop=="あり" else None), horizontal=True)
    if st.session_state.evp_stop == "あり":
        st.session_state.evp_stop_detail = st.text_area("中止の詳細*", value=st.session_state.evp_stop_detail)

# --- 4. 術前EVP療法後の評価 (手術前) ---
st.markdown('<div class="juog-header">4. 術前EVP療法後の評価 (手術前)</div>', unsafe_allow_html=True)
pc1, pc2 = st.columns(2)
with pc1:
    st.session_state.ct_date_post = st.date_input("EVP後CT/MRI 撮影日*", value=st.session_state.ct_date_post)
    # クラッシュ防止のkey設定
    st.session_state.max_size_post = st.number_input("腫瘍最大径（画像）(mm)*", value=st.session_state.max_size_post, step=1.0, key="k_size_post")
    res_opts = ["選択してください", "CR", "PR", "SD", "PD", "NE"]
    st.session_state.response_eval = st.selectbox("総合効果判定 (RECIST v1.1等)*", res_opts, index=get_idx(res_opts, st.session_state.response_eval))
with pc2:
    st.markdown("**EVP療法後(手術前)の主要採血データ**")
    st.session_state.blood_date_post = st.date_input("採血実施日(Post)*", value=st.session_state.blood_date_post)
    bx3, bx4 = st.columns(2)
    st.session_state.hb_post = bx3.number_input("Hb (g/dL)*", value=st.session_state.hb_post, key="h_post")
    st.session_state.wbc_post = bx4.number_input("WBC (/μL)*", value=st.session_state.wbc_post, key="w_post")
    st.session_state.cre_post = bx3.number_input("Cre (mg/dL)*", value=st.session_state.cre_post, key="c_post")
    st.session_state.egfr_post = bx4.number_input("eGFR*", value=st.session_state.egfr_post, key="e_post")

st.divider()

# --- 送信ボタン ---
if st.button("🚀 登録データを送信", type="primary", use_container_width=True):
    err = []
    d = st.session_state
    if d.facility_name == "選択してください": err.append("・施設名")
    if not d.patient_id: err.append("・識別コード")
    if d.disease_type == "その他の癌（不適格）": err.append("・対象疾患（不適格）")
    
    if err:
        st.error("未入力、または不適格な項目があります：\n" + "\n".join(err))
    else:
        # 管理者へメール送信
        rep = f"【JUOG 登録CRF】施設: {d.facility_name} / ID: {d.patient_id} / 年齢: {d.age}"
        if send_email(rep, d.patient_id, d.facility_name, d.reporter_email):
            st.success("データが正常に送信されました。"); st.balloons()
