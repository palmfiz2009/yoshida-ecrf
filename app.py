import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 設定 ---
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

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .block-container { padding-top: 2rem; max-width: 950px; margin: auto; }
    h1 { font-size: 26px !important; color: #0F172A; text-align: center; margin-bottom: 30px; font-weight: 800; }
    h2 { font-size: 17px !important; color: #FFFFFF !important; background-color: #1E3A8A !important; 
         padding: 12px 20px !important; border-radius: 8px !important; margin-top: 35px !important; margin-bottom: 15px !important; }
    label { font-size: 14px !important; font-weight: 600 !important; color: #334155; }
    .result-card { background-color: #FFFFFF; padding: 25px; border-radius: 12px; border: 2px solid #1E3A8A; margin-top: 20px; }
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

# タブの作成
tab1, tab2 = st.tabs(["📝 適格性を判定", "✉️ 事務局に結果を送信"])

with tab1:
    # --- 1. 基本情報 ---
    st.header("患者基本情報")
    c1, c2, c3 = st.columns(3)
    with c1:
        facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
        patient_id = st.text_input("症例ID")
        consent_date = st.date_input("同意取得日*", value=None)
    with c2:
        age = st.number_input("同意取得時の年齢*", min_value=0, max_value=120, value=None)
        gender = st.radio("性別*", ["男", "女"], index=None, horizontal=True)
    with c3:
        height = st.number_input("身長 (cm)*", min_value=100.0, max_value=250.0, format="%.1f", value=None)
        weight = st.number_input("体重 (kg)*", min_value=20.0, max_value=200.0, format="%.1f", value=None)
        ps = st.radio("ECOG PS*", ["0", "1", "2以上（不適）"], index=None, horizontal=True)

    # --- 2. 診断情報 ---
    st.header("診断・原発巣情報")
    c4, c5 = st.columns(2)
    with c4:
        diag_date = st.date_input("初回診断日*", value=None)
        diag_type = st.multiselect("診断根拠*", ["組織診", "細胞診"])
        primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], index=None, horizontal=True)
        primary_size_pre = st.number_input("診断時_最大径 (mm)*", format="%.1f", value=None)
    with c5:
        ct = st.selectbox("診断時_cT*", ["選択してください", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
        cn = st.selectbox("診断時_cN*", ["選択してください", "cN0", "cN1", "cN2", "cN3"])
        cm = st.selectbox("診断時_cM*", ["選択してください", "cM0", "cM1"])

    # --- 3. 転移巣情報 (cM1のみ) ---
    m_pre_total, m_post_total, site_1, size_1, m_post_v1 = 0.0, 0.0, "選択なし", None, None
    if cm == "cM1":
        st.header("転移巣情報 (cM1症例)")
        cm_c1, cm_c2, cm_c3 = st.columns(3)
        m_pre_list = []
        with cm_c1:
            site_1 = st.selectbox("部位1*", ["選択してください", "肺", "骨", "肝", "リンパ節", "その他"], key="s1")
            size_1 = st.number_input("大きさ1 (診断時 mm)*", format="%.1f", value=None, key="sz1")
            m_pre_list.append(size_1 if size_1 is not None else 0.0)
        for i in range(2, 4):
            with cm_cols[i-1] if 'cm_cols' in locals() else cm_c2 if i==2 else cm_c3:
                st.selectbox(f"部位{i}", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key=f"s{i}")
                v = st.number_input(f"大きさ{i} (mm)", format="%.1f", value=None, key=f"sz{i}")
                m_pre_list.append(v if v is not None else 0.0)
        m_pre_total = sum(m_pre_list)
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択してください", "EVP療法によりCR", "局所療法により消失、3か月維持"])
        local_tx = st.selectbox("局所療法の種類*", ["選択してください", "放射線（外照射）", "放射線（定位）", "切除", "RFA等", "血管塞栓術", "その他"])
        cned_date = st.date_input("cNED確認日*", value=None)

    # --- 4. EVP & 5. 手術前 ---
    st.header("EVP治療 & 手術前評価")
    ce1, ce2 = st.columns(2)
    with ce1:
        evp_start = st.date_input("EVP 初回投与日*", value=None)
        eval_date = st.date_input("EVP 病勢制御確認日*", value=None)
        best_effect = st.selectbox("EVP 最良効果*", ["選択してください", "CR", "PR", "SD", "PD"])
    with ce2:
        primary_size_post = st.number_input("原発巣：手術前 (mm)*", format="%.1f", value=None)
        if cm == "cM1":
            m_post_v1 = st.number_input("転移巣1 手術前 (mm)*", format="%.1f", value=None, key="mp1")
            m_post_total = (m_post_v1 if m_post_v1 is not None else 0.0)

    # --- 6. 除外基準 ---
    st.header("除外基準")
    cx1, cx2 = st.columns(2)
    with cx1:
        vessel = st.radio("血管浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
        organ = st.radio("臓器浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    with cx2:
        ae = st.radio("有害事象(G3-)*", ["なし", "あり（不適）"], index=None, horizontal=True)
        other_cancer = st.radio("重複がん*", ["なし", "あり（不適）"], index=None, horizontal=True)

    if st.button("適格性を判定する", type="primary", use_container_width=True):
        # バリデーション
        errs = []
        if any(v is None for v in [age, gender, height, weight, consent_date, diag_date, evp_start, eval_date, primary_size_pre, primary_size_post]): errs.append("必須項目の入力")
        if cm == "cM1" and (site_1 == "選択してください" or size_1 is None or m_post_v1 is None): errs.append("転移巣1の情報")
        if vessel is None or organ is None or ae is None or other_cancer is None: errs.append("除外基準の選択")

        if errs: st.error(f"入力漏れ: {', '.join(errs)}")
        else:
            reasons = []
            sld_pre, sld_post = (primary_size_pre + m_pre_total), (primary_size_post + m_post_total)
            chg = ((sld_post - sld_pre) / sld_pre * 100) if sld_pre > 0 else 0
            res_recist = "PD" if chg >= 20 else "PR" if chg <= -30 else "CR" if sld_post == 0 else "SD"
            
            if eval_date < (evp_start + timedelta(weeks=9)): reasons.append("9週間ルール不備")
            if res_recist == "PD" or best_effect == "PD": reasons.append("PD(病勢進行)")
            if any(v == "あり（不適）" for v in [vessel, organ, ae, other_cancer]): reasons.append("除外基準抵触")

            res_final = "【適格】" if not reasons else "【不適格】"
            report = f"施設: {facility}\nID: {patient_id}\n結果: {res_final}\nRECIST: {res_recist}\n変化率: {chg:.1f}%\n理由: {', '.join(reasons) if reasons else 'なし'}"
            st.session_state.report = report
            
            st.markdown(f'<div class="result-card"><h3>判定: {res_final}</h3>', unsafe_allow_html=True)
            if not reasons: st.success("登録可能です。タブを『送信』へ切り替えてください。"); st.balloons()
            else: st.error("登録対象外です。"); [st.write(f"・{r}") for r in reasons]
            
            st.download_button("💾 この判定レポートをPCに保存する", report, file_name=f"CRF_{patient_id}.txt")
            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.header("判定結果の送信")
    if "report" in st.session_state:
        st.info("以下の内容を送信します：")
        st.code(st.session_state.report)
        if st.button("✉️ 事務局・吉田先生へ送信する", type="primary", use_container_width=True):
            if send_result_email(st.session_state.report):
                st.success("無事に送信されました。お疲れ様でした！")
                del st.session_state.report
            else: st.error("メール設定を確認してください。")
    else:
        st.warning("先に『適格性を判定』タブで判定を行ってください。")
