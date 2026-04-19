import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

st.set_page_config(page_title="JUOG UTUC_Conlidative CRF", layout="wide")

# デザイン調整 (CSS) - ゆとりある空間と統一感のあるコンポーネント
st.markdown("""
    <style>
    .main { background-color: #F1F5F9; }
    
    /* コンテンツ全体の幅を調整 */
    .block-container { 
        padding-top: 3rem; 
        max-width: 1200px; 
        margin: auto; 
        padding-bottom: 7rem; 
    }
    
    h1 { font-size: 32px !important; color: #0F172A; text-align: center; margin-bottom: 45px; font-weight: 800; }
    
    h2 { 
        font-size: 19px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; 
        padding: 14px 25px !important; border-radius: 12px !important; margin-top: 50px !important; margin-bottom: 30px !important;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.2);
    }
    
    label { font-size: 15px !important; font-weight: 600 !important; color: #334155; margin-bottom: 10px !important; }
    
    /* セレクトボックスや入力欄の長さを揃え、余白を持たせる */
    .stSelectbox, .stNumberInput, .stTextInput, .stDateInput {
        margin-bottom: 20px !important;
    }

    /* 判定結果セクションのデザイン */
    .result-section { 
        background-color: #FFFFFF; 
        padding: 45px; 
        border-radius: 20px; 
        border: none; 
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
        margin-top: 50px; 
    }

    /* ラジオボタンの配置 */
    .stRadio > div { gap: 20px; }

    /* タグの色修正 */
    span[data-baseweb="tag"] { background-color: #E2E8F0 !important; color: #1E293B !important; }
    </style>
    """, unsafe_allow_html=True)

# メール送信関数
def send_result_email(content):
    try:
        mail_user = st.secrets["email"]["user"]
        mail_pass = st.secrets["email"]["pass"]
        to_addrs = ["urosec@kmu.ac.jp", "yoshida.tks@kmu.ac.jp"]
        msg = MIMEMultipart(); msg['From'] = mail_user; msg['To'] = ", ".join(to_addrs)
        msg['Subject'] = "【JUOG eCRF】判定レポート"
        msg.attach(MIMEText(content, 'plain'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(mail_user, mail_pass); server.send_message(msg); server.quit()
        return True
    except: return False

st.title("JUOG UTUC_Conlidative 登録用CRF")

# --- 1. 患者基本情報 ---
st.header("患者基本情報")
# 中央にスペースを作るためにダミー列を配置
c1, gap, c2, gap2, c3 = st.columns([10, 1, 10, 1, 10])
with c1:
    facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
    patient_id = st.text_input("症例ID（事務局用）")
with c2:
    consent_date = st.date_input("同意取得日*", value=None)
    age = st.number_input("同意取得時の年齢*", min_value=0, max_value=120, value=None)
with c3:
    gender = st.radio("性別*", ["男", "女"], index=None, horizontal=True)
    ps = st.radio("ECOG PS*", ["0", "1", "2以上（不適）"], index=None, horizontal=True)

cc1, gap3, cc2 = st.columns([10, 1, 10])
with cc1:
    height = st.number_input("身長 (cm)*", min_value=100.0, max_value=250.0, format="%.1f", value=None)
with cc2:
    weight = st.number_input("体重 (kg)*", min_value=20.0, max_value=200.0, format="%.1f", value=None)

# --- 2. 診断・原発巣情報 ---
st.header("診断・原発巣情報")
c4, gap4, c5 = st.columns([10, 2, 10])
with c4:
    diag_date = st.date_input("上部尿路上皮癌＿初回診断日：画像所見＋組織診/細胞診(疑いも含む)*", value=None)
    diag_type = st.multiselect("診断根拠となった検体*", ["組織診", "細胞診"])
    primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], index=None, horizontal=True)
with c5:
    primary_size_pre = st.number_input("診断時_最大径 (mm)*", format="%.1f", value=None)
    ct = st.selectbox("診断時_cT*", ["選択してください", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
    cn = st.selectbox("診断時_cN*", ["選択してください", "cN0", "cN1", "cN2", "cN3"])
    cm = st.selectbox("診断時_cM*", ["選択してください", "cM0", "cM1"])

# --- 3. 転移巣情報 (cM1のみ) ---
m_pre_total, site_1, size_1, cned_date = 0.0, "選択なし", None, None
if cm == "cM1":
    st.header("転移巣情報 (cM1症例)")
    cm_cols = st.columns([10, 1, 10, 1, 10])
    m_pre_list = []
    with cm_cols[0]:
        site_1 = st.selectbox("転移巣 部位①*", ["選択してください", "肺", "骨", "肝", "リンパ節", "その他"], key="s1")
        if site_1 == "その他": st.text_input("その他の場合：部位①", key="sd1")
        size_1 = st.number_input("大きさ① (診断時 mm)*", format="%.1f", value=None, key="sz1")
        m_pre_list.append(size_1 if size_1 is not None else 0.0)
    with cm_cols[2]:
        site_2 = st.selectbox("転移巣 部位②", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s2")
        if site_2 == "その他": st.text_input("その他の場合：部位②", key="sd2")
        size_2 = st.number_input("大きさ② (mm)", format="%.1f", value=None, key="sz2")
        m_pre_list.append(size_2 if size_2 is not None else 0.0)
    with cm_cols[4]:
        site_3 = st.selectbox("転移巣 部位③", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s3")
        if site_3 == "その他": st.text_input("その他の場合：部位③", key="sd3")
        size_3 = st.number_input("大きさ③ (mm)", format="%.1f", value=None, key="sz3")
        m_pre_list.append(size_3 if size_3 is not None else 0.0)
    
    m_pre_total = sum(m_pre_list)
    cb1, gap5, cb2 = st.columns([10, 2, 10])
    with cb1:
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択してください", "EVP療法によりCR", "局所療法により消失、3か月維持"])
        cned_date = st.date_input("cNED確認日*", value=None)
    with cb2:
        local_tx = st.selectbox("局所療法の種類*", ["選択してください", "放射線（外照射）", "放射線（定位）", "転移巣切除", "RFA・凍結療法など", "血管塞栓術", "その他", "該当なし"])
        if local_tx == "その他": st.text_input("局所療法の詳細", key="l_det")

# --- 4. EVP治療情報 ---
st.header("EVP治療情報")
ce1, gap6, ce2 = st.columns([10, 2, 10])
with ce1:
    evp_start = st.date_input("EVP 初回投与日*", value=None)
    evp_end = st.date_input("EVP 最終投与日*", value=None)
    ev_dose = st.number_input("EV 初回投与量 (mg/kg)*", format="%.2f", value=None)
with ce2:
    pembro_dose = st.number_input("Pembrolizumab 初回投与量 (mg/kg)*", format="%.2f", value=None)
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択してください", "CR", "PR", "SD", "PD"])
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)

ce3, gap7, ce4 = st.columns([10, 2, 10])
with ce3:
    reduction = st.radio("EVP 減量の有無*", ["なし", "あり"], index=None, horizontal=True)
    if reduction == "あり": st.text_area("減量の詳細（自由記載）", height=85)
with ce4:
    eval_date = st.date_input("EVP 病勢制御確認日 (SDの場合は、画像評価初回日)*", value=None)

# --- 5. 手術前評価 ---
st.header("手術前評価 & RECIST判定")
cp1, gap8, cp2 = st.columns([10, 2, 10])
with cp1:
    primary_size_post = st.number_input("原発巣 手術前_最大径 (mm)*", format="%.1f", value=None)
    m_post_total, m_post_v1 = 0.0, None
    if cm == "cM1":
        st.markdown("**転移巣 手術前_大きさ**")
        m_post_v1 = st.number_input("転移巣① 手術前 (mm)*", format="%.1f", value=None, key="mp1")
        m_post_total = (m_post_v1 if m_post_v1 is not None else 0.0)
with cp2:
    res_recist, sld_chg = "未入力", 0.0
    if primary_size_pre and primary_size_post is not None:
        sld_pre, sld_post = (primary_size_pre + m_pre_total), (primary_size_post + m_post_total)
        sld_chg = ((sld_post - sld_pre) / sld_pre * 100) if sld_pre > 0 else 0
        res_recist = "PD" if sld_chg >= 20 else "PR" if sld_chg <= -30 else "CR" if sld_post == 0 else "SD"
        st.metric("長径和(SLD) 変化率", f"{sld_chg:.1f}%")
        st.markdown(f"総合RECIST判定 (自動): **{res_recist}**")

# --- 6. 除外基準 & 手術予定 ---
st.header("除外基準 & 手術予定")
cx1, gap9, cx2 = st.columns([10, 2, 10])
with cx1:
    vessel = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    organ = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    ae = st.radio("Grade 3以上の未回復のEVP有害事象*", ["なし", "あり（不適）"], index=None, horizontal=True)
with cx2:
    other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], index=None, horizontal=True)
    pregnancy = st.radio("妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], index=None, horizontal=True)
    op_type = st.selectbox("予定している手術", ["選択なし", "根治的腎尿管全摘除術", "尿管部分切除術"])
    op_date = st.date_input("手術予定日（決定していれば）", value=None)

st.markdown("<br>", unsafe_allow_html=True)

# --- 判定と送信のロジック ---
if st.button("適格性を判定する", type="primary", use_container_width=True):
    missing = []
    if any(v is None for v in [age, gender, height, weight, consent_date, diag_date, evp_start, eval_date, primary_size_pre, primary_size_post]): missing.append("基本必須項目")
    if cm == "cM1" and (site_1 == "選択してください" or size_1 is None or m_post_v1 is None): missing.append("転移巣①(診断時/手術前)")
    if any(v is None for v in [vessel, organ, ae, other_cancer, pregnancy]): missing.append("除外基準の選択")
    
    if missing:
        st.error(f"入力漏れがあります: {', '.join(missing)}")
    else:
        reasons = []
        if cm == "cM1" and cned_date and cned_date > (consent_date - timedelta(days=90)): reasons.append("cNED確認日(3ヶ月ルール)")
        if eval_date < (evp_start + timedelta(weeks=9)): reasons.append("評価時期不足(9週間ルール)")
        is_st4 = (ct == "cT4") or (cn not in ["選択してください", "cN0"]) or (cm == "cM1")
        if not is_st4: reasons.append("Stage IV条件未充足")
        if res_recist == "PD" or best_effect == "PD": reasons.append("PD(病勢進行)")
        if any(v == "あり（不適）" for v in [vessel, organ, ae, other_cancer, pregnancy]): reasons.append("除外基準抵触")

        res_final = "【適格】" if not reasons else "【不適格】"
        st.session_state.report = f"施設: {facility}\nID: {patient_id}\n結果: {res_final}\nRECIST: {res_recist}\n変化率: {sld_chg:.1f}%\n理由: {', '.join(reasons) if reasons else 'なし'}"
        
        st.markdown(f'<div class="result-section"><h3>判定結果: {res_final}</h3>', unsafe_allow_html=True)
        if not reasons: st.success("研究登録可能です。"); st.balloons()
        else:
            st.error("登録対象外です。")
            for r in reasons: st.write(f"・{r}")
        st.download_button("💾 判定レポートの控え(TXT)をダウンロード", st.session_state.report, file_name=f"CRF_{patient_id}.txt")
        st.markdown('</div>', unsafe_allow_html=True)

if "report" in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.header("事務局に結果を送信")
    st.info("内容を確認し、間違いなければ送信してください。")
    if st.button("✉️ 事務局・吉田先生へ結果を送信する", use_container_width=True):
        if send_result_email(st.session_state.report):
            st.success("送信完了しました。お疲れ様でした！")
            del st.session_state.report
        else: st.error("送信エラー。Secretsの設定を確認してください。")
