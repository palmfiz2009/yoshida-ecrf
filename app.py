import streamlit as st
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 施設リスト（最新版：琉球大学へ修正）
HOSPITALS = ["愛知県がんセンター", "秋田大学", "愛媛大学", "大分大学", "大阪公立大学", "大阪大学", "大阪府済生会野江病院", "岡山大学病院", "香川大学", "鹿児島大学", "関西医科大学", "岐阜大学医学部附属病院", "九州大学病院", "京都大学", "久留米大学", "神戸大学", "国立がん研究センター中央病院", "国立病院機構四国がんセンター", "札幌医科大学", "千葉大学", "筑波大学", "東京科学大学", "東京慈恵会医科大学附属柏病院", "東京慈恵会医科大学附属病院", "東北大学", "鳥取大学", "富山大学附属病院", "長崎大学病院", "名古屋大学", "奈良県立医科大学", "新潟大学大学院 医歯学総合研究科", "浜松医科大学", "原三信病院", "兵庫医科大学", "弘前大学医学部附属病院", "北海道大学", "三重大学", "横浜市立大学附属病院", "琉球大学", "和歌山県立医科大学"]

st.set_page_config(page_title="JUOG UTUC_Consolidative CRF", layout="wide")

# デザイン調整 (CSS)
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

def send_result_email(content, reporter_mail=""):
    try:
        mail_user = st.secrets["email"]["user"]
        mail_pass = st.secrets["email"]["pass"]
        to_addrs = ["urosec@kmu.ac.jp", "yoshida.tks@kmu.ac.jp"]
        if reporter_mail:
            to_addrs.append(reporter_mail)
        msg = MIMEMultipart(); msg['From'] = mail_user; msg['To'] = ", ".join(to_addrs)
        msg['Subject'] = "【JUOG eCRF】登録判定レポート"
        msg.attach(MIMEText(content, 'plain'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(mail_user, mail_pass)
        server.send_message(msg)
        server.quit()
        return "OK"
    except Exception as e:
        return f"エラー詳細: {str(e)}"

st.title("JUOG UTUC_Consolidative 登録判定CRF")

# 初期化
m_pre_total, m_post_total = 0.0, 0.0
sz1, sz2, sz3 = None, None, None
mp1, mp2, mp3 = None, None, None
s1, s2, s3 = "", "", ""
sd1, sd2, sd3 = "", "", ""
cm1_basis, local_tx, red_det, pembro_stop_det = "", "", "", ""
cned_date = None

# --- RECIST用 共通ヘルプテキスト ---
RECIST_HELP = "【RECIST 1.1 測定基準】\n・腫瘍病変：少なくとも 1 方向で正確な測定が可能であり（測定断面における最大径（長径）を記録する）、長径 10 mm以上を測定\n\n※正確な測定が困難な「測定不能病変」は標的病変（Target Lesion）に含めず、ここには数値を入力しないで（空欄のままにして）ください。"

# --- 1. 患者基本情報 ---
st.header("1. 患者基本情報")
c1, c2 = st.columns(2)
with c1:
    facility = st.selectbox("施設名*", ["選択してください"] + HOSPITALS)
    reporter_email = st.text_input("担当者メールアドレス*")
    consent_date = st.date_input("本人同意取得日*", value=None)
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
    diag_date = st.date_input("初回診断日*", value=None)
    diag_type = st.multiselect("診断根拠となった検体*", ["組織診", "細胞診"])
    primary_site = st.radio("原発巣 部位*", ["腎盂", "尿管", "腎盂・尿管（両方）"], index=None, horizontal=True)
    primary_size_pre = st.number_input("診断時_最大径 (mm)*", format="%.1f", value=None, help=RECIST_HELP)
with c4:
    ct = st.selectbox("診断時_cT*", ["選択してください", "cTa", "cTis", "cT1", "cT2", "cT3", "cT4"])
    cn = st.selectbox("診断時_cN*", ["選択してください", "cN0", "cN1", "cN2", "cN3"])
    cm = st.selectbox("診断時_cM*", ["選択してください", "cM0", "cM1"])

# --- 3. 転移巣情報 (cM1のみ) ---
if cm == "cM1":
    st.header("3. 転移巣情報 (cM1症例のみ)")
    mc1, mc2 = st.columns(2)
    with mc1:
        s1 = st.selectbox("転移巣 部位①*", ["選択してください", "肺", "骨", "肝", "リンパ節", "その他"], key="s1")
        if s1 == "その他": sd1 = st.text_input("部位① 詳細")
        sz1 = st.number_input("大きさ① (診断時 mm)*", format="%.1f", value=None, help=RECIST_HELP)
        s2 = st.selectbox("転移巣 部位②", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s2")
        if s2 == "その他": sd2 = st.text_input("部位② 詳細")
        sz2 = st.number_input("大きさ② (mm)", format="%.1f", value=None, help=RECIST_HELP)
        s3 = st.selectbox("転移巣 部位③", ["該当なし", "肺", "骨", "肝", "リンパ節", "その他"], key="s3")
        if s3 == "その他": sd3 = st.text_input("部位③ 詳細")
        sz3 = st.number_input("大きさ③ (mm)", format="%.1f", value=None, help=RECIST_HELP)
        m_pre_total = (sz1 or 0.0) + (sz2 or 0.0) + (sz3 or 0.0)
    with mc2:
        cm1_basis = st.selectbox("ｃM1症例 登録根拠*", ["選択してください", "EVP療法によりCR", "局所療法により消失、3か月維持"])
        local_tx = st.selectbox("局所療法の種類*", ["選択してください", "放射線（外照射）", "放射線（定位）", "切除", "RFA・凍結", "血管塞栓術", "その他", "該当なし"])
        cned_date = st.date_input("cNED確認日*", value=None)

# --- 4. EVP治療情報 ---
st.header("4. EVP治療情報")
ce1, ce2 = st.columns(2)
with ce1:
    evp_start = st.date_input("EVP 初回投与日*", value=None)
    evp_end = st.date_input("EVP 最終投与日*", value=None)
    ev_dose = st.number_input("EV 初回量 (mg/kg)*", format="%.2f", value=None)
    reduction = st.radio("EV 減量の有無*", ["なし", "あり"], index=None, horizontal=True)
    if reduction == "あり": red_det = st.text_area("減量の詳細", placeholder="例：Grade 3の末梢神経障害のため、Day8からEVを〇〇mg/kgに減量して継続")
    pembro_stop = st.radio("irAEによるPembro中止の有無*", ["なし", "あり"], index=None, horizontal=True)
    if pembro_stop == "あり": pembro_stop_det = st.text_area("中止の詳細", placeholder="例：Grade 3のirAE腸炎（下痢）のため、3コース目でPembro投与を中止")
with ce2:
    courses = st.number_input("EVP 総投与コース数*", min_value=0, value=None)
    courses_reason = st.text_input("3コース未満の場合：理由")
    best_effect = st.selectbox("EVP 最良総合効果*", ["選択してください", "CR", "PR", "SD", "PD"])
    eval_date = st.date_input("病勢制御確認日 (SDの場合は画像初回日)*", value=None)
    
    if evp_start and eval_date:
        min_9w_date = evp_start + timedelta(weeks=9)
        if eval_date < min_9w_date:
            st.warning(f"⚠️ 時期が早すぎます。プロトコル上、評価は9週間（**{min_9w_date.strftime('%Y/%m/%d')} 以降**）が推奨されます。")

# --- 5. 手術前評価 & RECIST判定 ---
st.header("5. 手術前評価 & RECIST判定")
cp1, cp2 = st.columns(2)
with cp1:
    primary_size_post = st.number_input("原発巣 手術前_最大径 (mm)*", format="%.1f", value=None, help=RECIST_HELP)
    if cm == "cM1":
        mp1 = st.number_input("転移巣① 手術前 (mm)*", format="%.1f", value=None, help=RECIST_HELP)
        mp2 = st.number_input("転移巣② 手術前 (mm)", format="%.1f", value=None, help=RECIST_HELP)
        mp3 = st.number_input("転移巣③ 手術前 (mm)", format="%.1f", value=None, help=RECIST_HELP)
        m_post_total = (mp1 or 0.0) + (mp2 or 0.0) + (mp3 or 0.0)
with cp2:
    res_recist, sld_chg = "未入力", 0.0
    pre_sum = (primary_size_pre or 0.0) + m_pre_total
    
    if pre_sum > 0:
        missing_post = False
        if (primary_size_pre is not None) and (primary_size_post is None): missing_post = True
        if cm == "cM1":
            if (sz1 is not None) and (mp1 is None): missing_post = True
            if (sz2 is not None) and (mp2 is None): missing_post = True
            if (sz3 is not None) and (mp3 is None): missing_post = True
            
        if missing_post:
            res_recist = "NE（評価不能）"
            st.warning("⚠️ 手術前のサイズが空欄の病変があります。完全に消失した場合は明示的に「0」を入力してください。")
            st.markdown(f"RECIST判定: **{res_recist}**")
        else:
            post_sum = (primary_size_post or 0.0) + m_post_total
            sld_chg = ((post_sum - pre_sum) / pre_sum * 100)
            res_recist = "PD" if sld_chg >= 20 else "PR" if sld_chg <= -30 else "CR" if post_sum == 0 else "SD"
            st.metric("SLD 変化率", f"{sld_chg:.1f}%")
            st.markdown(f"RECIST判定: **{res_recist}**")
    else:
        st.markdown("RECIST判定: **標的病変なし (SLD計算不可)**")
        st.info("💡 測定可能な標的病変がない（非標的病変のみ等の）場合、SLDの自動計算は行われません。左記の「EVP 最良総合効果」の入力を用いて適格性（PD以外か）の判定を行います。")

# --- 6. 除外基準 & 手術予定 ---
st.header("6. 除外基準 & 手術予定")
cx1, cx2 = st.columns(2)
with cx1:
    vessel = st.radio("切除不能な血管浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    organ = st.radio("切除不能な臓器浸潤*", ["なし", "あり（不適）"], index=None, horizontal=True)
    ae = st.radio("Grade 3以上の未回復有害事象*", ["なし", "あり（不適）"], index=None, horizontal=True)
with cx2:
    other_cancer = st.radio("活動性の重複がん*", ["なし", "あり（不適）"], index=None, horizontal=True, help="病勢が制御され予後評価に影響しないと判断される悪性腫瘍（筋層非浸潤性膀胱癌、早期前立腺癌、治癒切除済みの皮膚基底細胞癌など）は登録を許容する")
    proxy_consent = st.radio("同意取得の形態（代諾者のみは不適格）*", ["本人同意", "代諾者のみ（不適）"], index=None, horizontal=True)
    op_type = st.selectbox("予定している手術*", ["選択なし", "根治的腎尿管全摘除術", "尿管部分切除術"])
    op_date = st.date_input("手術予定日", value=None)
    
    if evp_start and op_date:
        min_9w_date = evp_start + timedelta(weeks=9)
        if op_date < min_9w_date:
            st.warning(f"⚠️ 時期が早すぎます。手術は9週間（**{min_9w_date.strftime('%Y/%m/%d')} 以降**）の実施が推奨されます。")

# --- 判定ロジック ---
if st.button("適格性を判定する", type="primary", use_container_width=True):
    missing = []
    if any(v is None for v in [age, gender, height, weight, consent_date, diag_date, evp_start, eval_date, pembro_stop]): 
        missing.append("必須項目の未入力")
        
    if not reporter_email: missing.append("担当者メールアドレス")
    if cm == "cM1" and s1 == "選択してください": missing.append("転移巣部位①の選択")
    
    if missing: st.error(f"入力漏れがあります: {', '.join(missing)}")
    else:
        reasons = []
        warnings_list = []
        if cm == "cM1" and cm1_basis == "局所療法により消失、3か月維持":
            if cned_date and cned_date > (consent_date - timedelta(days=90)): reasons.append("cNED後3ヶ月の維持期間不足")
        if eval_date < (evp_start + timedelta(weeks=9)): warnings_list.append("EVP開始から評価までの期間が9週間未満です")
        if res_recist == "PD" or best_effect == "PD": reasons.append("病勢進行(PD)による不適格")
        if ps == "2以上（不適）": reasons.append("ECOG PSが2以上")
        if vessel == "あり（不適）": reasons.append("除外基準：切除不能な血管浸潤")
        if organ == "あり（不適）": reasons.append("除外基準：切除不能な臓器浸潤")
        if ae == "あり（不適）": reasons.append("除外基準：Grade 3以上の未回復有害事象")
        if other_cancer == "あり（不適）": reasons.append("除外基準：活動性の重複がん")
        if proxy_consent == "代諾者のみ（不適）": reasons.append("除外基準：本人同意が得られていない（代諾者のみ）")
        
        res_final = "【適格】" if not reasons else "【不適格】"
        reason_text = "\n".join([f"・{r}" for r in reasons]) if reasons else "なし"
        warning_text = "\n".join([f"・{w}" for w in warnings_list]) if warnings_list else "なし"
        
        disp_primary_pre = f"{primary_size_pre} mm" if primary_size_pre is not None else "測定不能(空欄)"
        
        report = f"""【JUOG eCRF 判定レポート】
施設: {facility}
メールアドレス: {reporter_email}
判定: {res_final}
理由:
{reason_text}
確認事項:
{warning_text}

--- 全入力データ ---
同意取得日: {consent_date}
年齢: {age}
性別: {gender}
身長: {height} cm
体重: {weight} kg
ECOG PS: {ps}
初回診断日: {diag_date}
診断根拠: {', '.join(diag_type) if diag_type else ''}
原発巣 部位: {primary_site}
診断時_最大径: {disp_primary_pre}
診断時_cT: {ct}
診断時_cN: {cn}
診断時_cM: {cm}
"""
        if cm == "cM1":
            report += f"cM1登録根拠: {cm1_basis}\ncNED確認日: {cned_date}\n"
        report += f"""
EVP初回/最終: {evp_start} / {evp_end}
EV初回量: {ev_dose} mg/kg
EV減量: {reduction} ({red_det})
Pembro中止: {pembro_stop} ({pembro_stop_det})
コース数: {courses} ({courses_reason})
最良効果: {best_effect}
病勢制御確認日: {eval_date}
RECIST判定: {res_recist} (SLD変化率: {sld_chg:.1f}%)
予定手術: {op_type} ({op_date})
"""
        st.session_state.report = report
        st.session_state.reporter_email_for_send = reporter_email
        st.markdown(f'<div class="result-section"><h3>判定結果: {res_final}</h3>', unsafe_allow_html=True)
        if not reasons: 
            st.success("登録可能です。"); st.balloons()
            if warnings_list:
                for w in warnings_list: st.warning(f"⚠️ 確認事項: {w}")
                st.info("💡 確認事項がありますが、送信は可能です。内容をご確認の上、下のボタンから送信してください。")
        else: 
            st.error("登録対象外です。")
            # --- 修正点：謎の[0:NULL]が出ないようにループ処理を修正 ---
            for r in reasons:
                st.markdown(f"❌ {r}")
        
        c_dl1, c_dl2 = st.columns(2)
        with c_dl1: st.download_button("📄 印刷用レポート(HTML)保存", f"<html><body><h3>JUOG レポート</h3><pre>{report}</pre></body></html>", file_name="Report.html", mime="text/html")
        with c_dl2: st.download_button("💾 控え(TXT)保存", report, file_name="Report.txt")
        st.markdown('</div>', unsafe_allow_html=True)

if "report" in st.session_state:
    if st.button("✉️ 事務局へ結果を送信する", use_container_width=True):
        send_result = send_result_email(st.session_state.report, st.session_state.reporter_email_for_send)
        if send_result == "OK":
            st.success("送信完了しました！画像データ（要匿名化）は別途事務局へ提出をお願いします。")
            del st.session_state.report
        else:
            st.error(f"送信エラーが発生しました。\n{send_result}")
