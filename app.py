import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
    .block-container { padding-top: 2rem; max-width: 950px; margin: auto; }
    h1 { font-size: 26px !important; color: #0F172A; text-align: center; margin-bottom: 30px; font-weight: 800; }
    h2 { 
        font-size: 17px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; 
        padding: 12px 20px !important; border-radius: 8px !important; margin-top: 35px !important; margin-bottom: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    label { font-size: 14px !important; font-weight: 600 !important; color: #334155; }
    .report-box { background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 2px solid #E2E8F0; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# メール送信関数
def send_result_email(content):
    try:
        mail_user = st.secrets["email"]["user"]
        mail_pass = st.secrets["email"]["pass"]
        to_addrs = ["urosec@kmu.ac.jp", "yoshida.tks@kmu.ac.jp"]
        
        msg = MIMEMultipart()
        msg['From'] = mail_user
        msg['To'] = ", ".join(to_addrs)
        msg['Subject'] = "【JUOG eCRF】判定結果レポート"
        msg.attach(MIMEText(content, 'plain'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(mail_user, mail_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"メール送信エラー: {e}")
        return False

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
    gender = st.radio("性別*", ["男", "女"], index=None, horizontal=True)
with c3:
    height = st.number_input("身長 (cm)*", min_value=100.0, max_value=250.0, format="%.1f", value=None)
    weight = st.number_input("体重 (kg)*", min_value=20.0, max_value=200.0, format="%.1f", value=None)
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
site_1 = "選択してください"
size_1 = None
m_post_val_1 = None

if cm == "cM1":
    st.header("転移巣情報 (cM1症例)")
    cm1_cols = st.columns(3)
    m_pre_list = []
    with cm1_cols[0]:
        site_1 = st.selectbox("部位1*", ["選択してください", "肺", "骨", "肝", "リンパ節", "その他"], key="s1")
        if site_1 == "その他": st.text_input("部位1の詳細*", key="sd1")
        size_1 = st.number_input("大きさ1 (診断時 mm)*", format="%.1f", value=None, key="sz1")
        m_pre_list.append(size_1 if size_1 is not None else 0.0)
    for i in range(2, 4):
        with cm1_cols[i-1]:
            st.selectbox(f"部位{i}", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key=f"s{i}")
            v = st.number_input(f"大きさ{i} (mm)", format="%.1f", value=None, key=f"sz{i}")
            m_pre_list.append(v if v is not None else 0.0)
    m_pre_total = sum(m_pre_list)
    cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択なし", "EVP療法によりCR", "局所療法により消失、3か月維持"])
    local_tx = st.selectbox("局所療法の種類*", ["選択なし", "放射線治療（外照射）", "放射線治療（定位照射）", "転移巣切除", "RFA・凍結療法など", "血管塞栓術", "その他", "該当なし"])
    cned_date = st.date_input("cNED確認日*", value=None)

# --- 4. EVP治療情報 ---
st.header("EVP治療情報")
ce1, ce2 = st.columns(2)
with ce1:
    evp_start = st.date_input("EVP 初回投与日*", value=None)
    evp_end = st.date_input("EVP 最終投与日*", value=None)
    ev_dose = st.number_input("EV 初回投与量 (mg/kg)*", format="%.2f", value=None)
    pembro_dose = st.number_input("Pembrolizumab 初回投与量 (mg/kg)*", format="%.2f", value=None)
with ce2:
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択なし", "CR", "PR", "SD", "PD"])
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
    eval_date = st.date_input("EVP 病勢制御確認日 (SDの場合は、投与後画像評価初回日)*", value=None)

# --- 5. 手術前評価 ---
st.header("手術前評価")
cp1, cp2 = st.columns(2)
with cp1:
    primary_size_post = st.number_input("原発巣：手術前_最大径 (mm)*", format="%.1f", value=None)
    m_post_total = 0.0
    if cm == "cM1":
        st.markdown("**転移巣：手術前**")
        m_post_list = []
        m_post_val_1 = st.number_input("転移巣1 手術前 (mm)*", format="%.1f", value=None, key="mp1")
        m_post_list.append(m_post_val_1 if m_post_val_1 is not None else 0.0)
        for i in range(2, 4):
            v = st.number_input(f"転移巣{i} 手術前 (mm)", format="%.1f", value=None, key=f"mp{i}")
            m_post_list.append(v if v is not None else 0.0)
        m_post_total = sum(m_post_list)

with cp2:
    auto_recist, sld_change = "未入力", 0.0
    if primary_size_pre and primary_size_post is not None:
        sld_pre = primary_size_pre + m_pre_total
        sld_post = primary_size_post + m_post_total
        sld_change = ((sld_post - sld_pre) / sld_pre * 100) if sld_pre > 0 else 0
        if sld_post == 0: auto_recist = "CR"
        elif sld_change <= -30: auto_recist = "PR"
        elif sld_change >= 20: auto_recist = "PD"
        else: auto_recist = "SD"
        st.metric("SLD 変化率 (リアルタイム)", f"{sld_change:.1f}%")
        st.markdown(f"総合判定: **{auto_recist}**")

# --- 6. 除外基準 ---
st.header("除外基準 & 手術予定")
cx1, cx2 = st.columns(2)
with cx1:
    vessel = st.radio("血管浸潤*", ["なし", "あり（不適）"], horizontal=True)
    organ = st.radio("臓器浸潤*", ["なし", "あり（不適）"], horizontal=True)
    ae = st.radio("G3以上の有害事象*", ["なし", "あり（不適）"], horizontal=True)
with cx2:
    other_cancer = st.radio("重複がん*", ["なし", "あり（不適）"], horizontal=True)
    pregnancy = st.radio("妊娠等*", ["なし", "あり（不適）"], horizontal=True)
    op_date = st.date_input("手術予定日", value=None)

st.markdown("<br>", unsafe_allow_html=True)

# --- 判定と送信のロジック ---
if st.button("① まずは適格性を確認する", use_container_width=True):
    missing = []
    if any(v is None for v in [age, gender, height, weight, consent_date, diag_date, evp_start, eval_date, primary_size_pre, primary_size_post]):
        missing.append("基本必須項目")
    if cm == "cM1":
        if site_1 == "選択してください" or size_1 is None or m_post_val_1 is None: missing.append("転移巣1(診断時/手術前)")
    
    if missing:
        st.error(f"入力漏れがあります: {', '.join(missing)}")
    else:
        reasons = []
        if cm == "cM1" and cned_date and cned_date > (consent_date - timedelta(days=90)): reasons.append("cNED確認日(3ヶ月前ルール不備)")
        if eval_date < (evp_start + timedelta(weeks=9)): reasons.append("評価時期不足(9週間ルール不備)")
        is_st4 = (ct == "cT4") or (cn not in ["選択なし", "cN0"]) or (cm == "cM1")
        if not is_st4: reasons.append("Stage IV条件未充足")
        if auto_recist == "PD" or best_effect == "PD": reasons.append("PD(病勢進行)")
        if any(v == "あり（不適）" for v in [vessel, organ, ae, other_cancer, pregnancy]): reasons.append("除外基準抵触")

        res_text = "【適格】" if not reasons else "【不適格】"
        st.session_state.report = f"""JUOG UTUC_Conlidative 判定レポート
--------------------------------------
施設名: {facility}
症例ID: {patient_id}
判定結果: {res_text}
理由: {', '.join(reasons) if reasons else 'なし'}
SLD変化率: {sld_change:.1f}%
RECIST: {auto_recist}
--------------------------------------
(本メールはシステムより自動送信されました)"""
        
        st.markdown(f'<div class="report-box"><h3>判定結果: {res_text}</h3>', unsafe_allow_html=True)
        if not reasons: st.success("研究登録可能です")
        else:
            st.error("登録対象外です")
            for r in reasons: st.write(f"・{r}")
        st.write("---")
        st.info("内容を確認し、問題なければ下のボタンで結果を送信してください。修正する場合は数値を書き換えて再度確認ボタンを押してください。")
        st.markdown('</div>', unsafe_allow_html=True)

if "report" in st.session_state:
    if st.button("② この内容で事務局へ結果を送信する", type="primary", use_container_width=True):
        if send_result_email(st.session_state.report):
            st.success("事務局および吉田先生へメールを送信しました。")
            del st.session_state.report # 送信後はレポートをクリア
