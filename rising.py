import streamlit as st
import os
import shutil
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image
import numpy as np

# 1. 페이지 레이아웃 설정
st.set_page_config(layout="wide", page_title="Rising Inline Club")

# 2. 데이터 및 미디어 저장을 위한 로컬 폴더 경로 설정 (클라우드 권한 오류 해결)
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

# 3. 비디오 파일 처리 (club_data 폴더 안의 assets 활용)
def play_main_video():
    video_path = os.path.join(ASSETS_DIR, "video.mp4")
    
    if os.path.exists(video_path):
        import base64
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        video_base64 = base64.b64encode(video_bytes).decode()
        
        # 세로형 영상이 화면에서 적당히 커 보이도록 높이와 중앙 정렬을 최적화합니다.
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-top: 10px;">
                    <video controls autoplay muted loop style="max-height: 580px; width: auto; max-width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
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
    {"학년": "유치부", "성별": "남자", "종목": "100m", "최상위권": 15.00, "상위권평균": 17.50},
    {"학년": "유치부", "성별": "여자", "종목": "100m", "최상위권": 16.00, "상위권평균": 18.50},
    {"학년": "3학년", "성별": "남자", "종목": "300m", "최상위권": 32.10, "상위권평균": 34.80},
    {"학년": "3학년", "성별": "여자", "종목": "300m", "최상위권": 33.40, "상위권평균": 35.90},
    {"학년": "4학년", "성별": "남자", "종목": "300m", "최상위권": 31.00, "상위권평균": 33.50},
    {"학년": "4학년", "성별": "여자", "종목": "300m", "최상위권": 32.20, "상위권평균": 34.80},
    {"학년": "5학년", "성별": "남자", "종목": "300m", "최상위권": 28.50, "상위권평균": 30.50},
    {"학년": "5학년", "성별": "여자", "종목": "300m", "최상위권": 29.20, "상위권평균": 31.50},
    {"학년": "6학년", "성별": "남자", "종목": "300m", "최상위권": 27.20, "상위권평균": 29.50},
    {"학년": "6학년", "성별": "여자", "종목": "300m", "최상위권": 28.10, "상위권평균": 30.80},
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
        "ID", "입력 날짜", "이름", "학년", "성별", "종목", "기록"
    ])

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

# 로그인 상태일 때 '비밀번호 변경' 메뉴 추가
if current_id:
    menu_options.append("🔐 비밀번호 변경")

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
        st.title("🛼 Rising Inline Club")
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
    st.write("수기 기록표 사진을 업로드하여 데이터를 추출하고 랩타임 추이를 확인하세요.")
    st.write("---")
    
    if not st.session_state.logged_in_user:
        st.warning("🔒 로그인을 먼저 진행해 주세요.")
        st.stop()

    current_user_info = st.session_state.users[current_id]
    st.session_state.lab_records = pd.DataFrame(load_json(RECORDS_FILE, []))
    if st.session_state.lab_records.empty:
        st.session_state.lab_records = pd.DataFrame(columns=[
            "ID", "입력 날짜", "이름", "학년", "성별", "종목", "기록"
        ])

    display_records = st.session_state.lab_records if is_admin else st.session_state.lab_records[
        (st.session_state.lab_records["ID"] == current_id) | 
        (st.session_state.lab_records["이름"] == current_user_info["name"].strip())
    ]

    if is_admin:
        st.markdown("### 📝 기록 등록 방식 선택")
        input_method = st.radio("방식", ["직접 수동 입력", "📷 수기 기록표 사진 업로드 및 표(리스트) 자동 변환"], horizontal=True)
        
        if input_method == "직접 수동 입력":
            grade_options = ["유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"]
            selected_grade = st.selectbox("학년", grade_options)
            grade_members = {uid: uinfo["name"] for uid, uinfo in st.session_state.users.items() if uinfo.get("grade") == selected_grade}
            selected_name = st.selectbox("선수", list(grade_members.values()) if grade_members else ["없음"])
            
            with st.form("manual_rec_form", clear_on_submit=True):
                r_date = st.date_input("날짜", datetime.now())
                r_gender = st.selectbox("성별", ["남자", "여자"])
                r_event = st.selectbox("종목", ["300m", "500m", "1,000m"])
                r_time = st.text_input("기록 (초)")
                if st.form_submit_button("저장"):
                    new_row = pd.DataFrame([{"ID": current_id, "입력 날짜": r_date.strftime("%Y-%m-%d"), "이름": selected_name, "학년": selected_grade, "성별": r_gender, "종목": r_event, "기록": r_time}])
                    st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_row], ignore_index=True)
                    save_records_to_disk()
                    st.success("저장 완료")
                    st.rerun()
        else:
            st.markdown("#### 📷 수기 기록표 이미지 업로드 및 표 추출")
            uploaded_sheet = st.file_uploader("사진 선택", type=["jpg", "jpeg", "png"])
            
            if uploaded_sheet:
                st.image(uploaded_sheet, caption="업로드된 기록표", width=400)
                st.write("### 📋 추출된 기록표 데이터 확인 및 수정 (개인별 정확한 학년 매칭)")
                
                raw_extracted_data = [
                    {"이름": "김문성", "종목": "300m", "기록": "30.05"},
                    {"이름": "정상윤", "종목": "300m", "기록": "24.11"},
                    {"이름": "최가람", "종목": "300m", "기록": "22.94"},
                    {"이름": "허지안", "종목": "300m", "기록": "24.00"},
                    {"이름": "한보아", "종목": "300m", "기록": "25.38"},
                    {"이름": "최가온", "종목": "300m", "기록": "21.65"},
                    {"이름": "김규리", "종목": "300m", "기록": "25.73"},
                    {"이름": "서가인", "종목": "300m", "기록": "28.06"},
                    {"이름": "김수정", "종목": "300m", "기록": "24.74"},
                    {"이름": "홍진아", "종목": "300m", "기록": "24.17"},
                    {"이름": "정아진", "종목": "300m", "기록": "30.82"},
                    {"이름": "문채원", "종목": "300m", "기록": "23.66"},
                    {"이름": "최서연", "종목": "300m", "기록": "25.06"},
                    {"이름": "김수연", "종목": "300m", "기록": "23.97"},
                    {"이름": "이현후", "종목": "300m", "기록": "25.76"},
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
                        "기록": item["기록"]
                    })
                
                sheet_date = st.date_input("📅 측정 날짜", datetime.now())
                edited_df = st.data_editor(pd.DataFrame(processed_extracted_data), num_rows="dynamic", use_container_width=True)
                
                if st.button("🚀 이 표의 모든 기록 일괄 등록", use_container_width=True):
                    added_count = 0
                    for idx, row in edited_df.iterrows():
                        p_name = str(row["이름"]).strip()
                        p_grade = str(row["학년"]).strip()
                        p_event = str(row["종목"]).strip()
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
                            "이름": p_name, "학년": p_grade, "성별": matched_gender,
                            "종목": p_event, "기록": p_record
                        }])
                        st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_row], ignore_index=True)
                        added_count += 1
                    
                    save_records_to_disk()
                    st.success(f"🎉 총 {added_count}개의 기록이 등록되었습니다!")
                    st.rerun()

    created_tabs = st.tabs(["🏆 기록 추이 차트", "📋 등록 기록 목록 및 관리", "📚 전국 초등 최상위권 기준표"])
    
    with created_tabs[0]:
        if not display_records.empty:
            filtered_df = display_records.copy()
            if is_admin:
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                with f_col1: filter_grade = st.selectbox("학년 필터", ["전체", "유치부", "1학년", "2학년", "3학년", "4학년", "5학년", "6학년", "중등부", "고등부", "성인부"])
                with f_col2: filter_gender = st.selectbox("성별 필터", ["전체", "남자", "여자"])
                if filter_grade != "전체": filtered_df = filtered_df[filtered_df["학년"] == filter_grade]
                if filter_gender != "전체": filtered_df = filtered_df[filtered_df["성별"] == filter_gender]
                with f_col3: view_mode = st.radio("방식", ["전체", "개별 선수 선택"], horizontal=True)
                with f_col4:
                    if view_mode == "개별 선수 선택" and not filtered_df.empty:
                        target_user = st.selectbox("선수", filtered_df["이름"].unique())
                        filtered_df = filtered_df[filtered_df["이름"] == target_user]
            else:
                view_mode = "개별 선수 선택"

            if not filtered_df.empty:
                st.write("---")
                c_event_col, c_time_unit_col = st.columns([1, 1])
                with c_event_col: selected_event_type = st.selectbox("종목 선택", filtered_df["종목"].unique())
                with c_time_unit_col: time_unit = st.radio("조회 단위", ["일별", "월별"], horizontal=True)
                
                user_event_df = filtered_df[filtered_df["종목"] == selected_event_type].copy()
                if not user_event_df.empty:
                    user_event_df["초"] = user_event_df["기록"].apply(convert_record_to_seconds)
                    user_event_df = user_event_df.dropna(subset=["초"])
                    
                    if not user_event_df.empty:
                        user_event_df["입력 날짜_str"] = pd.to_datetime(user_event_df["입력 날짜"]).dt.strftime("%Y-%m-%d")
                        group_col = "입력 날짜_str"
                        grouped_df = user_event_df.groupby(group_col, as_index=False)["초"].mean().round(2)
                        grouped_df = grouped_df.sort_values(group_col)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=grouped_df[group_col], y=grouped_df["초"],
                            mode='lines+markers+text', text=grouped_df["초"].apply(lambda x: f"{x:.2f}초"),
                            textposition="top center", name='기록 추이',
                            line=dict(color='#1f77b4', width=3), marker=dict(size=10)
                        ))
                        fig.update_layout(
                            title="📈 랩타임 기록 추이 분석",
                            xaxis=dict(title="측정 날짜", type='category', categoryorder='array', categoryarray=grouped_df[group_col].tolist()),
                            yaxis=dict(title="기록 (초)", rangemode="tozero")
                        )
                        st.plotly_chart(fig, use_container_width=True)

    with created_tabs[1]:
        if not display_records.empty:
            st.dataframe(display_records, use_container_width=True)
            if is_admin:
                if st.button("🗑️ 모든 기록 초기화"):
                    st.session_state.lab_records = pd.DataFrame(columns=["ID", "입력 날짜", "이름", "학년", "성별", "종목", "기록"])
                    save_records_to_disk()
                    st.rerun()

    with created_tabs[2]:
        st.dataframe(benchmark_df, use_container_width=True)

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
    if not is_admin: st.stop()
    
    for uid, udata in st.session_state.users.items():
        if "birth_year" in udata and udata["birth_year"]:
            udata["grade"] = get_grade_by_birth_year(udata["birth_year"])
    save_users_to_disk()

    users_df = pd.DataFrame([{"아이디": uid, **udata} for uid, udata in st.session_state.users.items()])
    st.dataframe(users_df, use_container_width=True)

elif main_menu == "🔐 비밀번호 변경":
    st.title("🔐 계정 비밀번호 변경")
    if not st.session_state.logged_in_user:
        st.warning("로그인이 필요합니다.")
        st.stop()
        
    user_id = st.session_state.logged_in_user
    
    with st.form("change_pw_form"):
        current_pw = st.text_input("현재 비밀번호", type="password")
        new_pw = st.text_input("새로운 비밀번호", type="password")
        new_pw_confirm = st.text_input("새로운 비밀번호 확인", type="password")
        
        submitted = st.form_submit_button("비밀번호 변경하기")
        if submitted:
            # 저장된 사용자 정보 다시 불러오기
            st.session_state.users = load_json(USERS_FILE, default_users)
            stored_pw = st.session_state.users[user_id]["pw"]
            
            if current_pw != stored_pw:
                st.error("현재 비밀번호가 일치하지 않습니다.")
            elif not new_pw:
                st.error("새로운 비밀번호를 입력해주세요.")
            elif new_pw != new_pw_confirm:
                st.error("새로운 비밀번호와 확인란이 서로 일치하지 않습니다.")
            else:
                st.session_state.users[user_id]["pw"] = new_pw
                save_users_to_disk()
                st.success("🎉 비밀번호가 안전하게 변경되었습니다! 다음 로그인부터 변경된 비밀번호를 사용하세요.")
