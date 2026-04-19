import streamlit as st
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 施設リスト（計画書記載の全施設）
HOSPITALS = ["愛知県がんセンター", "秋田大学", "愛媛大学", "大分大学", "大阪公立大学", "大阪大学", "大阪府済生会野江病院", "岡山大学病院", "香川大学", "鹿児島大学", "関西医科大学", "岐阜大学医学部附属病院", "九州大学病院", "京都大学", "久留米大学", "神戸大学", "国立がん研究センター中央病院", "国立病院機構四国がんセンター", "札幌医科大学", "千葉大学", "筑波大学", "東京科学大学", "東京慈恵会医科大学附属柏病院", "東京慈恵会医科大学附属病院", "東北大学", "鳥取大学", "富山大学附属病院", "長崎大学病院", "名古屋大学", "奈良県立医科大学", "新潟大学大学院 医歯学総合研究科", "浜松医科大学", "原三信病院", "兵庫医科大学", "弘前大学医学部附属病院", "北海道大学", "三重大学", "横浜市立大学附属病院", "琉球大学病院", "和歌山県立医科大学"]

st.set_page_config(page_title="JUOG UTUC_Conlidative CRF", layout="wide")

# デザイン調整 (CSS) - 先生お気に入りの2カラム・コンパクト版
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 1.5rem !important; max-width: 1050px !important; margin: auto; padding-bottom: 5rem !important; }
    h1 { font-size: 26px !important; color: #0F172A; text-align: center; margin-bottom: 25px !important; font-weight: 800; }
    h2 { font-size: 15px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; padding: 10px 20px !important; border-radius: 8px !important; margin-top: 25px !important; margin-bottom: 15px !important; }
    label { font-size: 13px !important; font-weight: 600 !important; color: #334155; margin-bottom: 4px !important; }
    div[data-testid="column"] { padding: 0 15px !important; }
    .result-section { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 2px solid #1E3A8A; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

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

# 初期化
m_pre_total = 0.0
m_post_total = 0.0
sz1, sz2, sz3 = 0.0, 0.0, 0.0
mp1, mp2, mp3 = 0.0, 0.0, 0.0
cned_date = None

# --- 1. 患者基本情報 ---
st.header("1. 患者基本情報")
c1, c2 = st.columns(2)
with c1:
    facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
    patient_id = st.text_input("症例ID（事務局で割り当てます）")
    consent_date = st.date_input("同意取得日*", value=None)
    age = st.number_input("同意取得時の年齢*", min_value=0, max_value=120, value=None)
with c2:
    gender = st.radio("性別*", ["男", "女"], index=None, horizontal=True)
    height = st.number_input("身長 (cm)*", min_value=100.0, format="%.1f", value=None)
    weight = st.number_input("体重 (kg)*", min_value=20.0, format="%.1f", value=None)
    ps = st.radio("ECOG PS*", ["0", "1", "2以上（不適）"], index=None, horizontal=True)

# --- 2. 診断・原発巣情報 ---
st.header("2. 診断・原発巣情報")
c3, c4 = st.columns(2)
with c3:
    diag_date = st.date_input("初回診断日：画像所見＋組織診/細胞診(疑いも含む)*", value=None)
    diag_type = st.multiselect("診断根拠となった検体*", ["組織診", "細胞診"])
    primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], index=None, horizontal=True)
    primary_size_pre = st.number_input("診断時_最大径 (mm)*", format="%.1f", value=None)
with c4:
    ct = st.selectbox("診断時_cT*", ["選択してください", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
    cn = st.selectbox("診断時_cN*", ["選択してください", "cN0", "cN1", "cN2", "cN3"])
    cm = st.selectbox("診断時_cM*", ["選択してください", "cM0", "cM1"])

# --- 3. 転移巣情報 (cM1のみ表示) ---
if cm == "cM1":
    st.header("3. 転移巣情報 (cM1症例のみ)")
    mc1, mc2 = st.columns(2)
    with mc1:
        st.selectbox("転移巣 部位①*", ["肺", "骨", "肝", "リンパ節", "その他"], key="s1")
        sz1 = st.number_input("大きさ① (診断時 mm)*", format="%.1f", value=0.0)
        st.selectbox("転移巣 部位②", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s2")
        sz2 = st.number_input("大きさ② (mm)", format="%.1f", value=0.0)
        st.selectbox("転移巣 部位③", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s3")
        sz3 = st.number_input("大きさ③ (mm)", format="%.1f", value=0.0)
        m_pre_total = sz1 + sz2 + sz3
        st.info(f"転移巣 診断時 合計: {m_pre_total:.1f} mm")
    with mc2:
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択してください", "EVPによりCR", "局所療法により消失、3か月維持"])
        local_tx = st.selectbox("局所療法の種類*", ["選択してください", "放射線（外照射）", "放射線（定位）", "切除", "RFA・凍結", "血管塞栓術", "その他", "該当なし"])
        cned_date = st.date_input("cNED確認日*", value=None)

# --- 4. EVP治療情報 ---
st.header("4. EVP治療情報")
ce1, ce2 = st.columns(2)
with ce1:
    evp_start = st.date_input("EVP 初回投与日*", value=None)
    evp_end = st.date_input("EVP 最終投与日*", value=None)
    ev_dose = st.number_input("EV 初回量 (mg/kg)*", format="%.2f", value=None)
    pembro_dose = st.number_input("Pembro 初回量 (mg/kg)*", format="%.2f", value=None)
    reduction = st.radio("EVP 減量の有無*", ["なし", "あり"], index=None, horizontal=True)
    if reduction == "あり": st.text_area("減量の詳細")
with ce2:
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
    courses_reason = st.text_input("3コース未満の場合：理由")
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択してください", "CR", "PR", "SD", "PD"])
    eval_date = st.date_input("病勢制御確認日 (SDの場合は画像初回日)*", value=None)

# --- 5. 手術前評価 ---
st.header("5. 手術前評価 & RECIST判定")
cp1, cp2 = st.columns(2)
with cp1:
    primary_size_post = st.number_input("原発巣 手術前_最大径 (mm)*", format="%.1f", value=None)
    if cm == "cM1":
        mp1 = st.number_input("転移巣① 手術前 (mm)*", format="%.1f", value=0.0)
        mp2 = st.number_input("転移巣② 手術前 (mm)", format="%.1f", value=0.0)
        mp3 = st.number_input("転移巣③ 手術前 (mm)", format="%.1f", value=0.0)
        m_post_total = mp1 + mp2 + mp3
with cp2:
    res_recist, sld_chg = "未入力", 0.0
    pre_sum = (primary_size_pre or 0.0) + m_pre_total
    post_sum = (primary_size_post or 0.0) + m_post_total
    if pre_sum > 0:
        sld_chg = ((post_sum - pre_sum) / pre_sum * 100)
        res_recist = "PD" if sld_chg >= 20 else "PR" if sld_chg <= -30 else "CR" if post_sum == 0 else "SD"
        st.metric("SLD 変化率", f"{sld_chg:.1f}%")
        st.markdown(f"RECIST判定: **{res_recist}**")

# --- 6. 除外基準 ---
st.header("6. 除外基準 & 手術予定")
cx1, cx2 = st.columns(2)
with cx1:
    vessel = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    organ = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    ae = st.radio("Grade 3以上の未回復有害事象*", ["なし", "あり（不適）"], index=None, horizontal=True)
with cx2:
    other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], index=None, horizontal=True)
    pregnancy = st.radio("妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], index=None, horizontal=True)
    op_type = st.selectbox("予定している手術*", ["選択なし", "根治的腎尿管全摘除術", "尿管部分切除術"])
    op_date = st.date_input("手術予定日", value=None)

# --- 判定ロジック ---
if st.button("適格性を判定する", type="primary", use_container_width=True):
    missing = []
    if any(v is None for v in [age, gender, height, weight, consent_date, diag_date, evp_start, eval_date, primary_size_pre, primary_size_post]): missing.append("必須項目の未入力")
    
    if missing: st.error(f"入力漏れがあります: {', '.join(missing)}")
    else:
        reasons = []
        if cm == "cM1" and cned_date and cned_date > (consent_date - timedelta(days=90)): reasons.append("cNED 3ヶ月ルール不備")
        if eval_date < (evp_start + timedelta(weeks=9)): reasons.append("評価時期不足(9週間)")
        if res_recist == "PD" or best_effect == "PD": reasons.append("PD(病勢進行)")
        if any(v == "あり（不適）" for v in [vessel, organ, ae, other_cancer, pregnancy]): reasons.append("除外基準抵触")
        
        res_final = "【適格】" if not reasons else "【不適格】"
        report = f"施設: {facility}\nID: {patient_id}\n判定: {res_final}\nRECIST: {res_recist}\n理由: {', '.join(reasons) if reasons else 'なし'}"
        st.session_state.report = report
        
        st.markdown(f'<div class="result-section"><h3>判定結果: {res_final}</h3>', unsafe_allow_html=True)
        if not reasons: st.success("登録可能です。"); st.balloons()
        else: st.error("登録対象外です。"); [st.write(f"・{r}") for r in reasons]
        
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1: st.download_button("📄 印刷用レポート(HTML)保存", f"<html><body><h3>JUOG レポート</h3><p>施設: {facility}<br>ID: {patient_id}<br>判定: {res_final}</p></body></html>", file_name=f"Report_{patient_id}.html", mime="text/html")
        with c_dl2: st.download_button("💾 控え(TXT)保存", report, file_name=f"Report_{patient_id}.txt")
        st.markdown('</div>', unsafe_allow_html=True)

if "report" in st.session_state:
    if st.button("✉️ 事務局へ結果を送信する", use_container_width=True):
        if send_result_email(st.session_state.report):
            st.success("送信完了しました！"); del st.session_state.report
        else: st.error("送信エラー")
