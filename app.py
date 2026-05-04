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
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #E2E8F0; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #64748B !important;
        padding: 10px 4px !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1E3A8A !important;
        border-bottom: 3px solid #1E3A8A !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 施設リスト ---
FACILITY_LIST = ["選択してください", "愛知県がんセンター", "秋田大学", "愛媛大学", "大分大学", "大阪公立大学", "大阪大学", "大阪府済生会野江病院", "岡山大学", "香川大学", "鹿児島大学", "関西医科大学", "岐阜大学", "九州大学病院", "京都大学", "久留米大学", "神戸大学", "国立がん研究センター中央病院", "国立病院機構四国がんセンター", "札幌医科大学", "千葉大学", "筑波大学", "東京科学大学", "東京慈恵会医科大学", "東京慈恵会医科大学附属柏病院", "東北大学", "鳥取大学", "富山大学", "長崎大学病院", "名古屋大学", "奈良県立医科大学", "新潟大学大学院 医歯学総合研究科", "浜松医科大学", "原三信病院", "兵庫医科大学", "弘前大学", "北海道大学", "三重大学", "横浜市立大学", "琉球大学", "和歌山県立医科大学", "その他"]

# --- セッション状態の初期化 ---
if 'init_reg_v2' not in st.session_state:
    st.session_state['init_reg_v2'] = True
    defaults = {
        "facility_name": "選択してください", "reporter_email": "", "patient_id": "",
        "age": 65, "sex": "選択してください", "ps": "選択してください",
        "disease_type": "選択してください", "t_factor": "選択してください", "n_factor": "選択してください", "m_factor": "選択してください",
        "m_sites": [], "m_other_detail": "", "prior_tx_evp": None,
        "max_size_diag": None, "max_size_diag_unmeasurable": False, "ct_date_diag": None, "cysto_date": None, "biopsy_date": None,
        "hb_pre": None, "wbc_pre": None, "plt_pre": None, "neutro_pre": None, "lympho_pre": None, "mono_pre": None, "eosino_pre": None, "baso_pre": None,
        "cre_pre": None, "egfr_pre": None, "alb_pre": None, "crp_pre": None, "ldh_pre": None, "ast_pre": None, "alt_pre": None, "blood_date_pre": None,
        "evp_start_date": None, "evp_end_date": None, "evp_cycles": 1, "evp_reduction": None, "evp_reduction_detail": "", "evp_stop": None, "evp_stop_detail": "",
        "max_size_post": None, "max_size_post_unmeasurable": False, "ct_date_post": None, "response_eval": "選択してください",
        "wbc_post": None, "hb_post": None, "plt_post": None, "neutro_post": None, "lympho_post": None, "mono_post": None, "eosino_post": None, "baso_post": None,
        "cre_post": None, "egfr_post": None, "alb_post": None, "crp_post": None, "ldh_post": None, "ast_post": None, "alt_post": None, "blood_date_post": None,
        "ex_other_cancer": False, "ex_evp_allergy": False, "ex_interstitial_lung": False, "ex_active_infection": False,
        "ex_uncontrolled_dm": False, "ex_investigator_judge": False
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

# --- 1. 基本情報 ---
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.session_state.facility_name = st.selectbox("施設名*", FACILITY_LIST, index=get_idx(FACILITY_LIST, st.session_state.facility_name))
    st.session_state.reporter_email = st.text_input("担当者メールアドレス（控え送付先）*", value=st.session_state.reporter_email)
with col_h2:
    st.session_state.patient_id = st.text_input("研究対象者識別コード*", value=st.session_state.patient_id)
    # 本試験の適格条件（TNM）を満たすかどうかの内部フラグ
    tnm_is_eligible = False

tab1, tab2, tab3 = st.tabs(["📋 適格性・患者背景", "🧪 術前EVP療法", "❌ 除外基準"])

with tab1:
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
        
        # TNM適格判定ロジック： (N1-3 AND M0) OR (M1)
        if st.session_state.n_factor in ["cN1", "cN2", "cN3"] and st.session_state.m_factor == "cM0":
            tnm_is_eligible = True
        elif st.session_state.m_factor == "cM1":
            tnm_is_eligible = True
            
        if st.session_state.m_factor == "cM1":
            st.session_state.m_sites = st.multiselect("転移部位*", ["リンパ節（所属外）", "肺", "肝", "骨", "その他"], default=st.session_state.m_sites)
            if "その他" in st.session_state.m_sites:
                st.session_state.m_other_detail = st.text_input("転移部位の詳細*", value=st.session_state.m_other_detail)

    st.markdown('<div class="juog-header">2. 診断時・EVP療法前の臨床データ</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        # --- 修正点①：最大径のラベル変更と「測定不能」チェックボックスの追加 ---
        st.markdown("**④原発巣の診断時最大径（画像・内視鏡 / 3D最大径）***")
        sc1, sc2 = st.columns([2, 1])
        st.session_state.max_size_diag = sc1.number_input("最大径 (mm)", value=st.session_state.max_size_diag, step=1.0, disabled=st.session_state.max_size_diag_unmeasurable)
        st.session_state.max_size_diag_unmeasurable = sc2.checkbox("測定不能", value=st.session_state.max_size_diag_unmeasurable)
        
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

with tab2:
    st.markdown('<div class="juog-header">3. 術前EVP療法の実施状況</div>', unsafe_allow_html=True)
    ec1, ec2 = st.columns(2)
    with ec1:
        st.session_state.evp_start_date = st.date_input("EVP療法 開始日*", value=st.session_state.evp_start_date)
        st.session_state.evp_end_date = st.date_input("EVP療法 最終投与日*", value=st.session_state.evp_end_date)
        st.session_state.evp_cycles = st.number_input("実施サイクル数*", min_value=1, max_value=20, value=st.session_state.evp_cycles)
    with ec2:
        st.session_state.evp_reduction = st.radio("減量の有無*", ["なし", "あり"], index=(0 if st.session_state.evp_reduction=="なし" else 1 if st.session_state.evp_reduction=="あり" else None), horizontal=True)
        # --- 修正点②：プレースホルダーで記載例を提示 ---
        if st.session_state.evp_reduction == "あり":
            st.session_state.evp_reduction_detail = st.text_area("減量の詳細*", value=st.session_state.evp_reduction_detail, placeholder="例：Grade3の末梢神経障害のため、Day8からEVを〇〇mg/kgに減量して継続")
        st.session_state.evp_stop = st.radio("途中中止の有無*", ["なし", "あり"], index=(0 if st.session_state.evp_stop=="なし" else 1 if st.session_state.evp_stop=="あり" else None), horizontal=True)
        if st.session_state.evp_stop == "あり":
            st.session_state.evp_stop_detail = st.text_area("中止の詳細*", value=st.session_state.evp_stop_detail, placeholder="例：Grade4の好中球減少および発熱性好中球減少症のため、2サイクル目Day1で投与を完全中止")

    st.markdown('<div class="juog-header">4. 術前EVP療法後の評価 (手術前)</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.session_state.ct_date_post = st.date_input("EVP後CT/MRI 撮影日*", value=st.session_state.ct_date_post)
        
        # --- 修正点①：最大径のラベル変更と「測定不能」チェックボックスの追加 ---
        st.markdown("**⑤術前EVP後の原発巣最大径（画像 / 3D最大径）***")
        px1, px2 = st.columns([2, 1])
        st.session_state.max_size_post = px1.number_input("最大径 (mm)", value=st.session_state.max_size_post, step=1.0, disabled=st.session_state.max_size_post_unmeasurable)
        st.session_state.max_size_post_unmeasurable = px2.checkbox("測定不能", value=st.session_state.max_size_post_unmeasurable, key="unm_post")
        
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

with tab3:
    st.markdown('<div class="juog-header">5. 除外基準の確認</div>', unsafe_allow_html=True)
    st.markdown("以下の項目に**「該当する（チェックあり）」場合は不適格**となります。")
    
    st.session_state.ex_other_cancer = st.checkbox("1. 他の活動性重複癌を有する", value=st.session_state.ex_other_cancer)
    st.session_state.ex_evp_allergy = st.checkbox("2. EVP療法の成分に対する重篤な過敏症の既往", value=st.session_state.ex_evp_allergy)
    st.session_state.ex_interstitial_lung = st.checkbox("3. 間質性肺疾患（非感染性肺臓炎）の合併または既往", value=st.session_state.ex_interstitial_lung)
    st.session_state.ex_active_infection = st.checkbox("4. 全身性の活動性感染症（B型/C型肝炎、HIV等を含む）", value=st.session_state.ex_active_infection)
    st.session_state.ex_uncontrolled_dm = st.checkbox("5. コントロール不良な糖尿病", value=st.session_state.ex_uncontrolled_dm)
    st.session_state.ex_investigator_judge = st.checkbox("6. その他、担当医師が本試験への参加を不適当と判断した", value=st.session_state.ex_investigator_judge)

st.divider()

if st.button("🚀 登録データ（Eligibility & Baseline）を事務局へ送信", type="primary", use_container_width=True):
    err = []
    d = st.session_state
    
    # 必須チェック
    if d.facility_name == "選択してください": err.append("・施設名")
    if not d.patient_id: err.append("・識別コード")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", d.reporter_email): err.append("・有効な担当者メールアドレス")
    
    if d.sex == "選択してください": err.append("・性別")
    if d.ps == "選択してください": err.append("・ECOG PS")
    if d.disease_type == "選択してください": err.append("・対象疾患・組織型")
    if d.prior_tx_evp is None: err.append("・本試験前のEVP療法歴")
    
    if d.t_factor == "選択してください" or d.n_factor == "選択してください" or d.m_factor == "選択してください":
        err.append("・cTNM分類")
        
    # --- 修正点①：測定不能チェックが外れているのに数値が未入力ならエラー ---
    if not d.max_size_diag_unmeasurable and d.max_size_diag is None: err.append("・原発巣の診断時最大径（または「測定不能」にチェック）")
    if not d.max_size_post_unmeasurable and d.max_size_post is None: err.append("・術前EVP後の原発巣最大径（または「測定不能」にチェック）")
    
    if not d.ct_date_diag: err.append("・診断時CT/MRI 撮影日")
    if d.hb_pre is None or d.wbc_pre is None or d.cre_pre is None: err.append("・EVP前の主要採血データ")
    
    if not d.evp_start_date or not d.evp_end_date: err.append("・EVP療法の日程")
    if d.evp_reduction == "あり" and not d.evp_reduction_detail: err.append("・減量の詳細")
    if d.evp_stop == "あり" and not d.evp_stop_detail: err.append("・途中中止の詳細")
    
    if not d.ct_date_post: err.append("・EVP後CT/MRI 撮影日")
    if d.response_eval == "選択してください": err.append("・総合効果判定")

    # --- 修正点③：適格性判定ロジックと、理由の明示 ---
    ineligible_reasons = []
    
    # 疾患の除外
    if d.disease_type == "その他の癌（不適格）":
        ineligible_reasons.append("「対象疾患・組織型」が「上部尿路癌（尿路上皮癌）」ではありません。")
    # 既往歴の除外
    if d.prior_tx_evp == "あり（不適格）":
        ineligible_reasons.append("「本試験前のEVP療法歴」があります。")
    # TNMの除外
    if d.n_factor != "選択してください" and d.m_factor != "選択してください":
        if not tnm_is_eligible:
            ineligible_reasons.append("「cTNM分類」が、本試験の適格基準（N1-3 M0 または M1）を満たしていません。")
            
    # Tab 3 除外基準のチェック
    ex_flags = [d.ex_other_cancer, d.ex_evp_allergy, d.ex_interstitial_lung, d.ex_active_infection, d.ex_uncontrolled_dm, d.ex_investigator_judge]
    ex_labels = ["他の活動性重複癌", "EVPアレルギー", "間質性肺疾患", "活動性感染症", "コントロール不良な糖尿病", "医師の不適当判断"]
    for flag, label in zip(ex_flags, ex_labels):
        if flag:
            ineligible_reasons.append(f"除外基準の「{label}」に該当しています。")

    if err:
        st.error("入力不備があります。以下の必須項目を入力してください：\n" + "\n".join(err))
    elif ineligible_reasons:
        # 具体的な不適格理由を箇条書きで表示
        st.error("❌ 以下の理由により、本試験には **【不適格】** となります。登録できません。")
        for reason in ineligible_reasons:
            st.warning(f"・{reason}")
    else:
        rep = f"【JUOG 登録CRF】施設: {d.facility_name}\nID: {d.patient_id}\n適格性: 判定OK"
        if send_email(rep, d.patient_id, d.facility_name, d.reporter_email):
            st.success("✅ 適格性が確認され、登録データが正常に送信されました。事務局からの受付完了メールをお待ちください。")
            st.balloons()
