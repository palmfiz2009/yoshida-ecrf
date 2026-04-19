import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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

st.set_page_config(page_title="JOUG UTUC_Consolidative eCRF(登録時)", layout="wide")
st.title("🛡️ 吉田 崇 先生 研究用 eCRF システム (全25項目網羅版)")

with st.form("main_form"):
    # --- セクション1：基本情報 (1-6) ---
    st.header("1. 患者基本情報")
    col1, col2, col3 = st.columns(3)
    with col1:
        patient_id = st.text_area("症例ID（事務局で割り当てます）", height=70)
        facility = st.selectbox("１．施設名*", HOSPITALS)
        consent_date = st.date_input("２．同意取得日*")
    with col2:
        age = st.number_input("３．同意取得時の年齢*", min_value=0, max_value=120, value=70)
        gender = st.radio("４．性別*", ["男", "女"], horizontal=True)
    with col3:
        height = st.number_input("５．身長 (cm)*", format="%.1f")
        weight = st.number_input("５．体重 (kg)*", format="%.1f")
        ps = st.radio("６．ECOG PS*", ["0", "1", "2以上（不適）"], horizontal=True)

    st.markdown("---")
    
    # --- セクション2：診断情報 (7-9) ---
    st.header("2. 診断・原発巣情報")
    col4, col5 = st.columns(2)
    with col4:
        diag_date = st.date_input("７．初回診断日（画像＋組織/細胞診）*")
        diag_type = st.multiselect("診断根拠となった検体*", ["組織診", "細胞診"])
        primary_site = st.radio("８．原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], horizontal=True)
    with col5:
        primary_size_pre = st.number_input("８．診断時_最大径 (mm)*", format="%.1f")
        ct = st.selectbox("９．診断時_cT*", ["cTac", "cTisc", "cT1", "cT2", "cT3", "cT4"])
        cn = st.selectbox("９．診断時_cN*", ["cN0", "cN1", "cN2", "cN3"])
        cm = st.selectbox("９．診断時_cM*", ["cM0", "cM1"])

    st.markdown("---")

    # --- セクション3：転移巣情報 (10-13) ---
    st.header("3. 転移巣情報 (cM1症例のみ)")
    st.info("10~13：cM1（転移あり）の症例のみ入力してください")
    
    met_data = []
    cols_met = st.columns(3)
    for i in range(1, 4):
        with cols_met[i-1]:
            st.subheader(f"転移巣 部位{i}")
            site = st.selectbox(f"部位{i}", ["肺", "骨", "肝", "リンパ節", "その他", "該当なし"], key=f"site{i}")
            other_site = st.text_input(f"その他の場合：部位{i}", key=f"other{i}")
            size = st.number_input(f"大きさ{i} (mm)", format="%.1f", key=f"msize{i}")
            met_data.append(size)
    
    met_sum_pre = sum(met_data)
    st.write(f"**１０．転移巣 診断時_腫瘍径 ①＋②＋③： {met_sum_pre:.1f} mm**")

    col6, col7 = st.columns(2)
    with col6:
        cm1_basis = st.selectbox("１１．ｃM1症例 登録根拠*", ["EVP療法によりCR", "局所療法により画像上活動性の遠隔転移病変消失、かつ3か月以上維持", "該当なし"])
        local_tx_type = st.selectbox("１２．局所療法の種類*", ["放射線治療（外照射）", "放射線治療（定位照射）", "転移巣切除", "RFA・凍結療法など", "血管塞栓術", "その他", "該当なし"])
    with col7:
        cned_date = st.date_input("１３．cNED確認日")
        cned_limit = consent_date - timedelta(days=90)
        st.write(f"cNED確認日の上限（参考）： {cned_limit}")

    st.markdown("---")

    # --- セクション4：EVP治療情報 (14-19) ---
    st.header("4. EVP治療情報")
    col8, col9 = st.columns(2)
    with col8:
        evp_start = st.date_input("１４．EVP 初回投与日*")
        evp_end = st.date_input("１４．EVP 最終投与日*")
        ev_dose = st.number_input("１５．EV 初回投与量 (mg/kg)*", format="%.2f")
        pembro_dose = st.number_input("１５．Pembrolizumab 初回投与量 (mg/kg)*", format="%.2f")
    with col9:
        courses = st.number_input("１６．EVP 総投与コース数*", min_value=0)
        courses_reason = st.text_input("3コース未満の場合：理由")
        reduction = st.radio("１７．EVP 減量の有無*", ["なし", "あり"], horizontal=True)
        reduction_detail = st.text_area("減量の詳細")

    col10, col11 = st.columns(2)
    with col10:
        eval_date = st.date_input("１８．EVP 病勢制御確認日 (画像検査日)*")
        sd_date = st.text_input("SDの場合は、投与後画像評価初回日")
    with col11:
        best_effect = st.selectbox("１９．EVP 最良総合効果*", ["CR", "PR", "SD", "PD"])
        recist_op = st.selectbox("２０．手術前のRECIST判定*", ["CR", "PR", "SD", "PD（不適）"])

    st.markdown("---")

    # --- セクション5：手術前評価 (21-22) ---
    st.header("5. 手術前評価")
    col12, col13 = st.columns(2)
    with col12:
        primary_size_post = st.number_input("２１．原発巣 手術前_最大径 (mm)*", format="%.1f")
        pri_red = ((primary_size_post - primary_size_pre) / primary_size_pre * 100) if primary_size_pre > 0 else 0
        st.write(f"原発巣 縮小率: **{pri_red:.1f} %**")
    with col13:
        m_post1 = st.number_input("２２．転移巣① 手術前 (mm)", format="%.1f")
        m_post2 = st.number_input("２２．転移巣② 手術前 (mm)", format="%.1f")
        m_post3 = st.number_input("２２．転移巣③ 手術前 (mm)", format="%.1f")
        met_sum_post = m_post1 + m_post2 + m_post3
        met_red = ((met_sum_post - met_sum_pre) / met_sum_pre * 100) if met_sum_pre > 0 else 0
        st.write(f"転移巣 縮小率: **{met_red:.1f} %**")

    st.markdown("---")

    # --- セクション6：除外基準・手術予定 (23-25) ---
    st.header("6. 除外基準 & 手術予定")
    col14, col15 = st.columns(2)
    with col14:
        vessel_inv = st.radio("２３．切除不能な血管浸潤*", ["なし", "あり（不適）"], horizontal=True)
        organ_inv = st.radio("２３．切除不能な臓器浸潤*", ["なし", "あり（不適）"], horizontal=True)
        ae_g3 = st.radio("２３．G3以上の未回復のEVP有害事象*", ["なし", "あり（不適）"], horizontal=True)
    with col15:
        other_cancer = st.radio("２５．活動性の重複がん*", ["なし", "あり（不適）"], horizontal=True)
        pregnancy = st.radio("２５．妊娠・授乳・同意困難等*", ["なし", "あり（不適）"], horizontal=True)
    
    st.markdown("---")
    op_type = st.selectbox("２４．予定している手術*", ["根治的腎尿管全摘除術", "尿管部分切除術"])
    op_date = st.date_input("２４．手術予定日")

    submit = st.form_submit_button("適格性を判定してデータを送信")

# --- 判定ロジック ---
if submit:
    reasons = []
    if age < 20: reasons.append("年齢20歳未満")
    if ps == "2以上（不適）": reasons.append("PS不良")
    is_stage_iv = (ct == "cT4") or (cn != "cN0") or (cm == "cM1")
    if not is_stage_iv: reasons.append("Stage IV条件未充足")
    if cm == "cM1" and cm1_basis == "該当なし": reasons.append("cM1登録根拠不足")
    if best_effect == "PD" or recist_op == "PD（不適）": reasons.append("PD(病勢進行)")
    if any(v == "あり（不適）" for v in [vessel_inv, organ_inv, ae_g3, other_cancer, pregnancy]):
        reasons.append("除外基準に抵触")

    st.markdown("---")
    st.header("📋 最終判定結果")
    if not reasons:
        st.success("⭕ 適格 (Eligible)：研究への登録が可能です。")
        st.balloons()
    else:
        st.error(f"❌ 不適格 (Ineligible)：以下の項目を確認してください\n\n- " + "\n- ".join(reasons))
