import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 레이아웃 설정
st.set_page_config(layout="wide", page_title="Rising Inline Club")

# 2. 데이터 및 미디어 저장을 위한 로컬 폴더 경로 설정
DATA_DIR = "club_data"
ASSETS_DIR = os.path.join(DATA_DIR, "assets")

for d in [DATA_DIR, ASSETS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
FOLDERS_FILE = os.path.join(DATA_DIR, "folders.json")
WINNERS_FILE = os.path.join(DATA_DIR, "winners.json")
SUGGESTIONS_FILE = os.path.join(DATA_DIR, "suggestions.json")
NOTICE_FILE = os.path.join(DATA_DIR, "notice.json")

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_val
    return default_val

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 3. 비디오 파일 처리
def play_main_video():
    video_path = os.path.join(ASSETS_DIR, "video.mp4")
    
    if os.path.exists(video_path):
        import base64
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        video_base64 = base64.b64encode(video_bytes).decode()
        
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 10px;">
                <video controls autoplay muted loop style="height: 72vh; max-height: 800px; width: auto; object-fit: contain; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.25);">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"동영상 파일을 찾을 수 없습니다. 경로를 확인해주세요: {video_path}")

# 4. 나이 및 정확한 학년 계산 함수
def get_age_by_birth_year(birth_year):
    current_year = datetime.now().year
    try:
        return current_year - int(birth_year) + 1
    except:
        return 0

def get_grade_by_birth_year(birth_year):
    age = get_age_by_birth_year(birth_year)
    if age < 8: return "유치부"
    elif age == 8: return "1학년"
    elif age == 9: return "2학년"
    elif age == 10: return "3학년"
    elif age == 11: return "4학년"
    elif age == 12: return "5학년"
    elif age == 13: return "6학년"
    elif 14 <= age <= 16: return "중등부"
    elif 17 <= age <= 19: return "고등부"
    else: return "성인부"

STANDARD_BENCHMARK_DATA = [
    {"학년": "유치부", "성별": "남자", "종목": "300m", "최상위권": 45.00, "상위권평균": 50.50},
    {"학년": "유치부", "성별": "여자", "종목": "300m", "최상위권": 46.00, "상위권평균": 51.50},
    {"학년": "3학년", "성별": "남자", "종목": "300m", "최상위권": 32.10, "상위권평균": 34.80},
    {"학년": "3학년", "성별": "여자", "종목": "300m", "최상위권": 33.40, "상위권평균": 35.90},
    {"학년": "4학년", "성별": "남자", "종목": "300m", "최상위권": 31.00, "상위권평균": 33.50},
    {"학년": "4학년", "성별": "여자", "종목": "300m", "최상위권": 32.20, "상위권평균": 34.80},
    {"학년": "5학년", "성별": "남자", "종목": "300m", "최상위권": 28.50, "상위권평균": 30.50},
    {"학년": "5학년", "성별": "여자", "종목": "300m", "최상위권": 29.20, "상위권평균": 31.50},
    {"학년": "6학년", "성별": "남자", "종목": "300m", "최상위권": 27.20, "상위권평균": 29.50},
    {"학년": "6학년", "성별": "여자", "종목": "300m", "최상위권": 28.10, "상위권평균": 30.80},
    {"학년": "초등부전체", "성별": "남자", "종목": "500m", "최상위권": 55.00, "상위권평균": 62.00},
]
benchmark_df = pd.DataFrame(STANDARD_BENCHMARK_DATA)

# 5. Session State 초기화
today_str = datetime.now().strftime("%Y-%m-%d")

if "club_notice" not in st.session_state:
    loaded_notice = load_json(NOTICE_FILE, None)
    st.session_state.club_notice = loaded_notice if loaded_notice else "📢 **[클럽 공지사항]**\n- 이번 주 토요일 정기 훈련 일정 정상 진행\n- 신규 입단 문의 및 승인은 관리자에게 요청해 주세요."

if "suggestions" not in st.session_state:
    st.session_state.suggestions = load_json(SUGGESTIONS_FILE, [])

default_users = {
    "admin": {
        "pw": "1234", "name": "최고관리자", "phone": "010-0000-0000",
        "gender": "남자", "birth_year": 1990, "grade": "성인부",
        "role": "admin", "status": "approved",
        "join_date": today_str, "pay_status": "완료"
    }
}
if "users" not in st.session_state:
    st.session_state.users = load_json(USERS_FILE, default_users)
    if "admin" not in st.session_state.users:
        st.session_state.users["admin"] = default_users["admin"]

for uid, udata in st.session_state.users.items():
    if "birth_year" in udata and udata["birth_year"]:
        udata["grade"] = get_grade_by_birth_year(udata["birth_year"])

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "lab_records" not in st.session_state:
    raw_records = load_json(RECORDS_FILE, [])
    st.session_state.lab_records = pd.DataFrame(raw_records) if raw_records else pd.DataFrame(columns=[
        "ID", "입력 날짜", "측정 회차", "이름", "학년", "성별", "종목", "기록"
    ])
else:
    if "측정 회차" not in st.session_state.lab_records.columns:
        st.session_state.lab_records["측정 회차"] = "1회차"

if "event_folders" not in st.session_state:
    st.session_state.event_folders = load_json(FOLDERS_FILE, ["남원 대회", "논산 대회", "양주 대회", "군산 마라톤"])

if "competition_winners" not in st.session_state:
    st.session_state.competition_winners = load_json(WINNERS_FILE, {f: [] for f in st.session_state.event_folders})

def save_users_to_disk():
    save_json(USERS_FILE, st.session_state.users)

def save_records_to_disk():
    save_json(RECORDS_FILE, st.session_state.lab_records.to_dict(orient="records"))

def save_folders_to_disk():
    save_json(FOLDERS_FILE, st.session_state.event_folders)
    save_json(WINNERS_FILE, st.session_state.competition_winners)

def save_suggestions_to_disk():
    save_json(SUGGESTIONS_FILE, st.session_state.suggestions)

def save_notice_to_disk():
    save_json(NOTICE_FILE, st.session_state.club_notice)

def convert_record_to_seconds(record_str):
    try:
        s_val = str(record_str).strip()
        s_val = s_val.replace("초", "").replace("s", "").strip()
        if ":" in s_val:
            parts = s_val.split(":")
            if len(parts) == 2: 
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3: 
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(s_val)
    except:
        return None

current_id = st.session_state.logged_in_user
is_admin = False
if current_id and current_id in st.session_state.users:
    is_admin = (st.session_state.users[current_id].get("role") == "admin")

# 6. 사이드바 메인 메뉴
st.sidebar.header("🏃 밴드 메뉴")
menu_options = ["홈 (기본 영상)", "1. 개인별 LAB Time Recorder", "2. 대회 사진첩", "3. 건의사항"]
if is_admin:
    menu_options.append("4. 👥 회원 승인 및 관리 (관리자 전용)")

if current_id:
    menu_options.append("🔐 개인정보 변경")

main_menu = st.sidebar.radio("메뉴를 선택하세요", menu_options)

selected_event = None
if main_menu == "2. 대회 사진첩":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 대회 폴더 선택")
    if st.session_state.event_folders:
        selected_event = st.sidebar.radio("이동할 사진첩을 선택하세요", st.session_state.event_folders)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 계정 관리")

if st.session_state.logged_in_user:
    u_info = st.session_state.users[st.session_state.logged_in_user]
    st.sidebar.success(f"👤 **{u_info['name']}**님 ({u_info.get('gender', '-')}/{u_info.get('grade', '회원')})")
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
else:
    auth_choice = st.sidebar.radio("로그인 / 회원가입", ["로그인", "회원가입"], key="sb_auth_choice")
    if auth_choice == "로그인":
        with st.sidebar.form("sb_login_form"):
            login_id = st.text_input("아이디 (ID)", key="sb_l_id")
            login_pw = st.text_input("비밀번호", type="password", key="sb_l_pw")
            if st.form_submit_button("로그인", use_container_width=True):
                st.session_state.users = load_json(USERS_FILE, default_users)
                if login_id in st.session_state.users and st.session_state.users[login_id]["pw"] == login_pw:
                    if st.session_state.users[login_id].get("status", "approved") == "approved":
                        st.session_state.logged_in_user = login_id
                        st.rerun()
                    else:
                        st.sidebar.warning("⏳ 승인 대기 중입니다.")
                else:
                    st.sidebar.error("정보 불일치")
    else:
        with st.sidebar.form("sb_signup_form"):
            new_id = st.text_input("신규 아이디", key="sb_s_id")
            new_pw = st.text_input("비밀번호", type="password", key="sb_s_pw")
            new_name = st.text_input("실명", key="sb_s_name")
            new_phone = st.text_input("연락처", key="sb_s_phone")
            new_gender = st.radio("성별", ["남자", "여자"], horizontal=True, key="sb_s_gender")
            birth_yr = st.number_input("출생연도", min_value=1940, max_value=datetime.now().year, value=2016)
            auto_grade = get_grade_by_birth_year(birth_yr)
            if st.form_submit_button("가입 신청", use_container_width=True):
                if new_id in st.session_state.users:
                    st.sidebar.warning("존재하는 아이디")
                else:
                    st.session_state.users[new_id] = {
                        "pw": new_pw, "name": new_name.strip(), "phone": new_phone.strip(),
                        "gender": new_gender, "birth_year": int(birth_yr), "grade": auto_grade,
                        "role": "user", "status": "pending", "join_date": today_str, "pay_status": "미납"
                    }
                    save_users_to_disk()
                    st.sidebar.info("가입 신청 완료")

# 7. 메인 페이지 로직
if main_menu == "홈 (기본 영상)":
    col_title, col_notice = st.columns([1, 1])
    with col_title:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 2.2rem;">🛼</span>
                <h1 style="margin: 0; padding: 0; font-size: 2.5rem; color: white;">Rising Inline Club</h1>
            </div>
            <p style="margin-top: 8px; margin-left: 50px; font-size: 1.1rem; color: #b0b0b0;">
                문의 : 박희영(H.P 010.6677.0633)
            </p>
            """,
            unsafe_allow_html=True
        )
    with col_notice:
        st.info(st.session_state.club_notice)
        if is_admin:
            with st.expander("✏️ [관리자] 공지사항 수정"):
                updated_notice = st.text_area("내용", value=st.session_state.club_notice)
                if st.button("수정 완료"):
                    st.session_state.club_notice = updated_notice
                    save_notice_to_disk()
                    st.rerun()
    st.write("---")
    play_main_video()

elif main_menu == "1. 개인별 LAB Time Recorder":
    st.title("⏱️ 개인별 LAB Time Recorder")
    st.write("하루에 여러 번 측정한 다중 기록(1차, 2차, 3차 등)을 개별 세트로 분리하여 등록하고 분석하세요.")
    st.write("---")
    
    if not st.session_state.logged_in_user:
        st.warning("🔒 로그인을 먼저 진행해 주세요.")
        st.stop()

    current_user_info = st.session_state.users[current_id]
    st.session_state.lab_records = pd.DataFrame(load_json(RECORDS_FILE, []))
    if st.session_state.lab_records.empty:
        st.session_state.lab_records = pd.DataFrame(columns=[
            "ID", "입력 날짜", "측정 회차", "이름", "학년", "성별", "종목", "기록"
        ])
    if "측정 회차" not in st.session_state.lab_records.columns:
        st.session_state.lab_records["측정 회차"] = "1회차"

    # 기록 데이터의 학년 및 성별을 실제 회원 정보와 실시간 동기화
    for idx, row in st.session_state.lab_records.iterrows():
        r_id = row.get("ID")
        r_name = str(row.get("이름")).strip()
        
        matched_user = None
        if r_id in st.session_state.users:
            matched_user = st.session_state.users[r_id]
        else:
            for uid, udata in st.session_state.users.items():
                if udata.get("name", "").strip() == r_name:
                    matched_user = udata
                    break
        
        if matched_user:
            if matched_user.get("gender"):
                st.session_state.lab_records.at[idx, "성별"] = matched_user.get("gender")
            if matched_user.get("grade"):
                st.session_state.lab_records.at[idx, "학년"] = matched_user.get("grade")

    if is_admin:
        display_records = st.session_state.lab_records
    else:
        display_records = st.session_state.lab_records[
            (st.session_state.lab_records["ID"] == current_id) | 
            (st.session_state.lab_records["이름"] == current_user_info["name"].strip())
        ]

    if is_admin:
        st.markdown("### 📝 기록 등록 방식 선택")
        input_method = st.radio("방식", ["직접 수동 입력", "📷 수기 기록표 사진 업로드 및 다중 기록 자동 변환"], horizontal=True)
        
        if input_method == "직접 수동 입력":
            grade_options = ["유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"]
            selected_grade = st.selectbox("학년", grade_options)
            
            grade_members = {uid: uinfo["name"] for uid, uinfo in st.session_state.users.items() if uinfo.get("grade") == selected_grade and uinfo.get("role") != "admin"}
            
            if grade_members:
                selected_uid = st.selectbox("선수 선택", list(grade_members.keys()), format_func=lambda x: grade_members[x])
                selected_name = grade_members[selected_uid]
            else:
                selected_uid = "unknown"
                selected_name = "없음"
                st.warning("해당 학년에 등록된 승인된 회원이 없습니다.")
            
            with st.form("manual_rec_form", clear_on_submit=True):
                r_date = st.date_input("날짜", datetime.now())
                r_round = st.selectbox("측정 회차", ["1회차", "2회차", "3회차", "4회차", "5회차"])
                auto_gender = st.session_state.users.get(selected_uid, {}).get("gender", "남자")
                r_gender = st.selectbox("성별", ["남자", "여자"], index=0 if auto_gender == "남자" else 1)
                r_event = st.selectbox("종목", ["100m", "300m", "500m", "1,000m"])
                r_time = st.text_input("기록 (초)")
                if st.form_submit_button("저장"):
                    if selected_uid == "unknown":
                        st.error("올바른 선수를 선택해주세요.")
                    else:
                        new_row = pd.DataFrame([{
                            "ID": selected_uid, 
                            "입력 날짜": r_date.strftime("%Y-%m-%d"), 
                            "측정 회차": r_round,
                            "이름": selected_name, 
                            "학년": selected_grade, 
                            "성별": r_gender, 
                            "종목": r_event, 
                            "기록": r_time
                        }])
                        st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_row], ignore_index=True)
                        save_records_to_disk()
                        st.success("저장 완료")
                        st.rerun()
        else:
            st.markdown("#### 📷 수기 기록표 이미지 업로드 및 다중 기록 파싱")
            uploaded_sheet = st.file_uploader("사진 선택", type=["jpg", "jpeg", "png"])
            
            if uploaded_sheet:
                st.image(uploaded_sheet, caption="업로드된 기록표", width=400)
                st.write("### 📋 한 사람이 하루에 여러 번 뛴 기록(1차, 2차 등)이 모두 분리되어 추출된 표입니다. 확인 및 수정하세요.")
                
                raw_extracted_data = [
                    {"이름": "김문성", "종목": "300m", "측정 회차": "1회차", "기록": "1:21.31"},
                    {"이름": "김문성", "종목": "300m", "측정 회차": "2회차", "기록": "1:19.96"},
                    {"이름": "최가람", "종목": "300m", "측정 회차": "1회차", "기록": "1:02.79"},
                    {"이름": "최가람", "종목": "300m", "측정 회차": "2회차", "기록": "1:01.86"},
                    {"이름": "최가람", "종목": "300m", "측정 회차": "3회차", "기록": "1:04.70"},
                    {"이름": "허지안", "종목": "300m", "측정 회차": "1회차", "기록": "1:08.44"},
                    {"이름": "허지안", "종목": "300m", "측정 회차": "2회차", "기록": "1:02.50"},
                ]
                
                processed_extracted_data = []
                for item in raw_extracted_data:
                    p_name = item["이름"].strip()
                    matched_grade = "미등록회원"
                    for uid, udata in st.session_state.users.items():
                        if udata.get("name", "").strip() == p_name:
                            b_year = udata.get("birth_year")
                            if b_year:
                                matched_grade = get_grade_by_birth_year(b_year)
                            else:
                                matched_grade = udata.get("grade", "미등록회원")
                            break
                    processed_extracted_data.append({
                        "이름": p_name,
                        "학년": matched_grade,
                        "종목": item["종목"],
                        "측정 회차": item["측정 회차"],
                        "기록": item["기록"]
                    })
                
                sheet_date = st.date_input("📅 일괄 측정 날짜", datetime.now())
                
                grade_list_options = ["미등록회원", "유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"]
                event_list_options = ["100m", "200m", "300m", "500m", "1,000m", "1,500m", "3,000m"]
                round_list_options = ["1회차", "2회차", "3회차", "4회차", "5회차"]
                
                edited_df = st.data_editor(
                    pd.DataFrame(processed_extracted_data), 
                    num_rows="dynamic", 
                    use_container_width=True,
                    column_config={
                        "학년": st.column_config.SelectboxColumn("학년", options=grade_list_options, required=True),
                        "종목": st.column_config.SelectboxColumn("종목", options=event_list_options, required=True),
                        "측정 회차": st.column_config.SelectboxColumn("측정 회차", options=round_list_options, required=True)
                    }
                )
                
                if st.button("🚀 이 표의 다중 기록 일괄 등록", use_container_width=True):
                    added_count = 0
                    for idx, row in edited_df.iterrows():
                        p_name = str(row["이름"]).strip()
                        p_grade = str(row["학년"]).strip()
                        p_event = str(row["종목"]).strip()
                        p_round = str(row["측정 회차"]).strip()
                        p_record = str(row["기록"]).strip()
                        
                        if not p_name or not p_record: continue
                        
                        matched_id, matched_gender = "unknown", "남자"
                        for uid, udata in st.session_state.users.items():
                            if udata.get("name", "").strip() == p_name:
                                matched_id = uid
                                matched_gender = udata.get("gender", "남자")
                                break
                        
                        new_row = pd.DataFrame([{
                            "ID": matched_id, "입력 날짜": sheet_date.strftime("%Y-%m-%d"),
                            "측정 회차": p_round,
                            "이름": p_name, "학년": p_grade, "성별": matched_gender,
                            "종목": p_event, "기록": p_record
                        }])
                        st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_row], ignore_index=True)
                        added_count += 1
                    
                    save_records_to_disk()
                    st.success(f"🎉 총 {added_count}개의 다중 기록이 등록되었습니다!")
                    st.rerun()

    created_tabs = st.tabs(["🏆 기록 추이 및 기준표 비교 차트", "📋 등록 기록 목록 및 전국 최상위권 비교 관리"])
    
    with created_tabs[0]:
        if not display_records.empty:
            filtered_df = display_records.copy()
            
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1: 
                filter_grade = st.selectbox("학년 필터", ["전체", "유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"])
            with f_col2: 
                filter_gender = st.selectbox("성별 필터", ["전체", "남자", "여자"])
            
            if filter_grade != "전체": 
                filtered_df = filtered_df[filtered_df["학년"] == filter_grade]
            if filter_gender != "전체": 
                filtered_df = filtered_df[filtered_df["성별"] == filter_gender]
                
            with f_col3: 
                view_mode = st.radio("방식", ["전체 선수 비교", "개별 선수 선택"], horizontal=True)
            with f_col4:
                if view_mode == "개별 선수 선택" and not filtered_df.empty:
                    target_user = st.selectbox("선수", filtered_df["이름"].unique())
                    filtered_df = filtered_df[filtered_df["이름"] == target_user]

            if not filtered_df.empty:
                st.write("---")
                c_event_col, c_time_unit_col = st.columns([1, 1])
                with c_event_col: 
                    all_events = filtered_df["종목"].unique().tolist()
                    selected_event_type = st.selectbox("종목 선택", all_events if all_events else ["300m"])
                with c_time_unit_col: 
                    show_benchmark_line = st.checkbox("🎯 전국 최상위권 기준선 함께 표시", value=True)
                
                user_event_df = filtered_df[filtered_df["종목"] == selected_event_type].copy()
                if not user_event_df.empty:
                    user_event_df["초"] = user_event_df["기록"].apply(convert_record_to_seconds)
                    user_event_df = user_event_df.dropna(subset=["초"])
                    
                    if not user_event_df.empty:
                        user_event_df["측정일시"] = user_event_df["입력 날짜"] + " (" + user_event_df["측정 회차"] + ")"
                        
                        fig = go.Figure()
                        
                        if view_mode == "전체 선수 비교":
                            for athlete_name, group_data in user_event_df.groupby("이름"):
                                sorted_group = group_data.sort_values(["입력 날짜", "측정 회차"])
                                fig.add_trace(go.Scatter(
                                    x=sorted_group["측정일시"], 
                                    y=sorted_group["초"],
                                    mode='lines+markers+text', 
                                    text=sorted_group["초"].apply(lambda x: f"{x:.2f}s"),
                                    textposition="top center", 
                                    name=athlete_name
                                ))
                        else:
                            sorted_group = user_event_df.sort_values(["입력 날짜", "측정 회차"])
                            fig.add_trace(go.Scatter(
                                x=sorted_group["측정일시"], 
                                y=sorted_group["초"],
                                mode='lines+markers+text', 
                                text=sorted_group["초"].apply(lambda x: f"{x:.2f}s"),
                                textposition="top center", 
                                name=f"{target_user} 기록",
                                line=dict(color='#1f77b4', width=3), marker=dict(size=10)
                            ))
                        
                        if show_benchmark_line and filter_grade != "전체" and filter_gender != "전체":
                            bm_matched = benchmark_df[
                                (benchmark_df["학년"] == filter_grade) & 
                                (benchmark_df["성별"] == filter_gender) & 
                                (benchmark_df["종목"] == selected_event_type)
                            ]
                            if not bm_matched.empty:
                                bm_val = bm_matched.iloc[0]["최상위권"]
                                unique_times = user_event_df["측정일시"].unique()
                                fig.add_trace(go.Scatter(
                                    x=unique_times,
                                    y=[bm_val] * len(unique_times),
                                    mode='lines',
                                    name=f"전국 최상위권 기준 ({bm_val}초)",
                                    line=dict(color='red', dash='dash', width=2)
                                ))
                            else:
                                st.info(f"💡 현재 선택된 조건({filter_grade}, {filter_gender}, {selected_event_type})에 해당하는 최상위권 기준 데이터가 없습니다.")

                        fig.update_layout(
                            title="📈 하루 다중 측정(회차별) 기록 추이 및 최상위권 비교 그래프",
                            xaxis=dict(title="측정 날짜 및 회차", type='category'),
                            yaxis=dict(title="기록 (초)", rangemode="tozero")
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("유효한 초 기록 데이터가 없습니다.")
                else:
                    st.info("선택한 종목에 대한 기록이 없습니다.")
            else:
                st.info("조건에 맞는 기록 데이터가 없습니다.")

    with created_tabs[1]:
        st.markdown("### 📋 등록 기록 및 전국 최상위권 비교")
        if not display_records.empty:
            merged_view_df = display_records.copy()
            merged_view_df["초기록"] = merged_view_df["기록"].apply(convert_record_to_seconds)
            
            combined_record_list = []
            for idx, row in merged_view_df.iterrows():
                g = row["학년"]
                ge = row["성별"]
                ev = row["종목"]
                sec = row["초기록"]
                raw_rec = row["기록"]
                
                bm_row = benchmark_df[
                    (benchmark_df["학년"] == g) & 
                    (benchmark_df["성별"] == ge) & 
                    (benchmark_df["종목"] == ev)
                ]
                
                if not bm_row.empty and sec is not None:
                    top_val = float(bm_row.iloc[0]["최상위권"])
                    diff = sec - top_val
                    if diff > 0:
                        diff_str = f"+{diff:.2f}초 느림 ⚠️"
                    elif diff < 0:
                        diff_str = f"{diff:.2f}초 빠름 🔥"
                    else:
                        diff_str = "기준 동일 ✨"
                    
                    combined_record_list.append(f"{raw_rec} / 최상위권 {top_val:.2f}초 ({diff_str})")
                else:
                    combined_record_list.append(f"{raw_rec} / 기준 없음 ➖")
            
            merged_view_df["기록 (최상위권 비교)"] = combined_record_list
            
            display_cols_order = ["입력 날짜", "측정 회차", "이름", "학년", "성별", "종목", "기록 (최상위권 비교)"]
            final_show_df = merged_view_df[[c for c in display_cols_order if c in merged_view_df.columns]]
            
            st.dataframe(final_show_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📚 참고용 전체 전국 최상위권 기준표")
            st.dataframe(benchmark_df, use_container_width=True)
            
            if is_admin:
                if st.button("🗑️ 모든 기록 초기화"):
                    st.session_state.lab_records = pd.DataFrame(columns=["ID", "입력 날짜", "측정 회차", "이름", "학년", "성별", "종목", "기록"])
                    save_records_to_disk()
                    st.rerun()
        else:
            st.info("등록된 기록이 없습니다.")

elif main_menu == "2. 대회 사진첩":
    st.title("📸 대회 사진첩")
    if not st.session_state.logged_in_user:
        st.stop()
    st.info("사진첩 메뉴입니다.")

elif main_menu == "3. 건의사항":
    st.title("💡 건의사항")
    with st.form("sug"):
        t = st.text_input("제목")
        c = st.text_area("내용")
        if st.form_submit_button("제출"):
            st.session_state.suggestions.append({"title": t, "content": c})
            save_suggestions_to_disk()
            st.rerun()

elif main_menu == "4. 👥 회원 승인 및 관리 (관리자 전용)":
    st.title("👥 회원 관리")
    if not is_admin: 
        st.stop()
    
    for uid, udata in st.session_state.users.items():
        if "birth_year" in udata and udata["birth_year"]:
            udata["grade"] = get_grade_by_birth_year(udata["birth_year"])
    save_users_to_disk()

    st.subheader("⏳ 가입 승인 대기 목록")
    pending_users = {uid: udata for uid, udata in st.session_state.users.items() if udata.get("status") == "pending"}
    
    if pending_users:
        for uid, udata in pending_users.items():
            with st.container(border=True):
                cols = st.columns([3, 3, 2])
                with cols[0]:
                    st.write(f"**아이디:** {uid}")
                    st.write(f"**이름:** {udata.get('name', '-')}")
                with cols[1]:
                    st.write(f"**학년:** {udata.get('grade', '-')}")
                    st.write(f"**연락처:** {udata.get('phone', '-')}")
                with cols[2]:
                    if st.button("✅ 승인하기", key=f"approve_{uid}", use_container_width=True):
                        st.session_state.users[uid]["status"] = "approved"
                        save_users_to_disk()
                        st.success(f"{udata.get('name')}님 승인 완료!")
                        st.rerun()
    else:
        st.info("현재 승인 대기 중인 회원이 없습니다.")

    st.markdown("---")
    st.subheader("📋 전체 회원 목록")
    users_df = pd.DataFrame([{"아이디": uid, **udata} for uid, udata in st.session_state.users.items()])
    st.dataframe(users_df, use_container_width=True)

elif main_menu == "🔐 개인정보 변경":
    st.title("🔐 개인정보 변경 (비밀번호 / 학년 / 성별)")
    if not st.session_state.logged_in_user:
        st.warning("로그인이 필요합니다.")
        st.stop()
        
    user_id = st.session_state.logged_in_user
    current_user_data = st.session_state.users[user_id]
    
    with st.form("change_profile_form"):
        st.subheader("🔑 비밀번호 변경")
        current_pw = st.text_input("현재 비밀번호", type="password")
        new_pw = st.text_input("새로운 비밀번호 (변경하지 않으려면 공백)", type="password")
        new_pw_confirm = st.text_input("새로운 비밀번호 확인", type="password")
        
        st.markdown("---")
        st.subheader("👤 학년 및 성별 정보 수정")
        
        grade_options = ["유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"]
        current_grade = current_user_data.get("grade", "유치부")
        default_grade_idx = grade_options.index(current_grade) if current_grade in grade_options else 0
        new_grade = st.selectbox("학년 수정", grade_options, index=default_grade_idx)
        
        gender_options = ["남자", "여자"]
        current_gender = current_user_data.get("gender", "남자")
        default_gender_idx = gender_options.index(current_gender) if current_gender in gender_options else 0
        new_gender = st.radio("성별 수정", gender_options, index=default_gender_idx, horizontal=True)
        
        submitted = st.form_submit_button("개인정보 수정하기")
        if submitted:
            st.session_state.users = load_json(USERS_FILE, default_users)
            stored_pw = st.session_state.users[user_id]["pw"]
            
            id_check = (current_pw == stored_pw)
            if not id_check:
                st.error("현재 비밀번호가 일치하지 않습니다.")
            elif new_pw and new_pw != new_pw_confirm:
                st.error("새로운 비밀번호와 확인란이 서로 일치하지 않습니다.")
            else:
                if new_pw:
                    st.session_state.users[user_id]["pw"] = new_pw
                
                st.session_state.users[user_id]["grade"] = new_grade
                st.session_state.users[user_id]["gender"] = new_gender
                
                save_users_to_disk()
                st.success("🎉 개인정보(비밀번호, 학년, 성별)가 안전하게 수정되었습니다!")
                st.rerun()
