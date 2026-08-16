import streamlit as st
import os
import shutil
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 레이아웃 설정
st.set_page_config(layout="wide", page_title="Rising Inline Club")

# 2. 정적 폴더(Static) 경로 설정
STREAMLIT_STATIC_PATH = os.path.join(os.path.dirname(st.__file__), "static")
ASSETS_PATH = os.path.join(STREAMLIT_STATIC_PATH, "assets")
if not os.path.exists(ASSETS_PATH):
    os.makedirs(ASSETS_PATH)

# [기본 동영상 파일 목록 설정]
video_files = {
    "main": r"C:\Users\User\Downloads\band_video_2026_07_18_23_28_26.mp4",
}

for key, source_path in video_files.items():
    if os.path.exists(source_path):
        filename = os.path.basename(source_path)
        target_path = os.path.join(ASSETS_PATH, filename)
        if not os.path.exists(target_path):
            shutil.copy(source_path, target_path)

def play_main_video():
    main_path = video_files["main"]
    filename = os.path.basename(main_path)
    target_path = os.path.join(ASSETS_PATH, filename)
    active_path = target_path if os.path.exists(target_path) else main_path
    
    if os.path.exists(active_path):
        video_html = f"""
        <div style="display: flex; justify-content: center; width: 100%;">
            <video controls autoplay muted loop playsinline preload="metadata" oncontextmenu="return false;" style="max-width: 100%; height: auto; border-radius: 12px;">
                <source src="assets/{filename}" type="video/mp4">
            </video>
        </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)

# 3. 기준 데이터 베이스
STANDARD_BENCHMARK_DATA = [
    {"학년": "유치부", "성별": "남자", "종목": "100m", "최상위권": 15.00, "상위권평균": 17.50},
    {"학년": "유치부", "성별": "여자", "종목": "100m", "최상위권": 16.00, "상위권평균": 18.50},
    {"학년": "1-2학년", "성별": "남자", "종목": "200m", "최상위권": 24.50, "상위권평균": 26.00},
    {"학년": "1-2학년", "성별": "남자", "종목": "300m", "최상위권": 36.80, "상위권평균": 39.50},
    {"학년": "1-2학년", "성별": "여자", "종목": "200m", "최상위권": 25.20, "상위권평균": 27.30},
    {"학년": "1-2학년", "성별": "여자", "종목": "300m", "최상위권": 38.10, "상위권평균": 41.20},
    {"학년": "3-4학년", "성별": "남자", "종목": "300m", "최상위권": 32.10, "상위권평균": 34.80},
    {"학년": "3-4학년", "성별": "남자", "종목": "500m", "최상위권": 51.50, "상위권평균": 55.20},
    {"학년": "3-4학년", "성별": "남자", "종목": "1,000m", "최상위권": 112.00, "상위권평균": 120.50},
    {"학년": "3-4학년", "성별": "여자", "종목": "300m", "최상위권": 33.40, "상위권평균": 35.90},
    {"학년": "3-4학년", "성별": "여자", "종목": "500m", "최상위권": 53.20, "상위권평균": 57.10},
    {"학년": "3-4학년", "성별": "여자", "종목": "1,000m", "최상위권": 115.60, "상위권평균": 124.00},
    {"학년": "5-6학년", "성별": "남자", "종목": "300m (DTT/T)", "최상위권": 27.20, "상위권평균": 29.50},
    {"학년": "5-6학년", "성별": "남자", "종목": "500m (+D)", "최상위권": 45.80, "상위권평균": 49.20},
    {"학년": "5-6학년", "성별": "남자", "종목": "1,000m", "최상위권": 94.50, "상위권평균": 102.00},
    {"학년": "5-6학년", "성별": "남자", "종목": "1,500m", "최상위권": 143.20, "상위권평균": 155.00},
    {"학년": "5-6학년", "성별": "여자", "종목": "300m (DTT/T)", "최상위권": 28.10, "상위권평균": 30.80},
    {"학년": "5-6학년", "성별": "여자", "종목": "500m (+D)", "최상위권": 46.90, "상위권평균": 51.10},
    {"학년": "5-6학년", "성별": "여자", "종목": "1,000m", "최상위권": 97.20, "상위권평균": 105.50},
    {"학년": "5-6학년", "성별": "여자", "종목": "1,500m", "최상위권": 160.00, "상위권평균": 160.00},
]
benchmark_df = pd.DataFrame(STANDARD_BENCHMARK_DATA)

def get_grade_by_birth_year(birth_year):
    current_year = datetime.now().year
    age = current_year - int(birth_year) + 1
    
    if age < 8:
        return "유치부"
    elif age in [8, 9]:
        return "1-2학년"
    elif age in [10, 11]:
        return "3-4학년"
    elif age in [12, 13]:
        return "5-6학년"
    elif 14 <= age <= 16:
        return "중등부"
    elif 17 <= age <= 19:
        return "고등부"
    else:
        return "성인부"

# 4. Session State 초기화
today_str = datetime.now().strftime("%Y-%m-%d")

if "club_notice" not in st.session_state:
    st.session_state.club_notice = "📢 **[클럽 공지사항]**\n- 이번 주 토요일 정기 훈련 일정 정상 진행\n- 신규 입단 문의 및 승인은 관리자에게 요청해 주세요."

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {
            "pw": "1234", "name": "최고관리자", "phone": "010-0000-0000",
            "gender": "남자", "birth_year": 1990, "grade": "성인부",
            "role": "admin", "status": "approved",
            "join_date": today_str, "pay_status": "완료"
        }
    }

for uid, uinfo in st.session_state.users.items():
    if "birth_year" in uinfo and uinfo["birth_year"]:
        uinfo["grade"] = get_grade_by_birth_year(uinfo["birth_year"])

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "lab_records" not in st.session_state:
    st.session_state.lab_records = pd.DataFrame(columns=[
        "ID", "입력 날짜", "이름", "학년", "성별", "종목", "기록"
    ])

if "event_folders" not in st.session_state:
    st.session_state.event_folders = ["남원 대회", "논산 대회", "양주 대회", "군산 마라톤"]

if "gallery_photos" not in st.session_state:
    st.session_state.gallery_photos = {folder: [] for folder in st.session_state.event_folders}

if "competition_winners" not in st.session_state:
    st.session_state.competition_winners = {folder: [] for folder in st.session_state.event_folders}

def convert_record_to_seconds(record_str):
    try:
        if ":" in str(record_str):
            parts = str(record_str).split(":")
            if len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(record_str)
    except:
        return None

current_id = st.session_state.logged_in_user
is_admin = False
if current_id and current_id in st.session_state.users:
    is_admin = (st.session_state.users[current_id].get("role") == "admin")

# 5. 사이드바 메인 메뉴
st.sidebar.header("🏃 밴드 메뉴")

menu_options = ["홈 (기본 영상)", "1. 개인별 LAB Time Recorder", "2. 대회 사진첩", "3. 건의사항"]
if is_admin:
    menu_options.append("4. 👥 회원 승인 및 관리 (관리자 전용)")

main_menu = st.sidebar.radio("메뉴를 선택하세요", menu_options)

selected_event = None
if main_menu == "2. 대회 사진첩":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 대회 폴더 선택")
    if st.session_state.event_folders:
        selected_event = st.sidebar.radio("이동할 사진첩을 선택하세요", st.session_state.event_folders)
    else:
        st.sidebar.warning("생성된 대회 폴더가 없습니다.")

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
            btn_login = st.form_submit_button("로그인", use_container_width=True)
            
            if btn_login:
                if login_id in st.session_state.users and st.session_state.users[login_id]["pw"] == login_pw:
                    user_status = st.session_state.users[login_id].get("status", "approved")
                    if user_status == "approved":
                        st.session_state.logged_in_user = login_id
                        st.sidebar.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.sidebar.warning("⏳ 관리자 가입 승인 대기 중입니다.")
                else:
                    st.sidebar.error("아이디 또는 비밀번호 오류")
    else:
        with st.sidebar.form("sb_signup_form"):
            new_id = st.text_input("신규 아이디", key="sb_s_id")
            new_pw = st.text_input("비밀번호", type="password", key="sb_s_pw")
            new_name = st.text_input("실명 (선수 본명)", placeholder="예: 홍길동", key="sb_s_name")
            new_phone = st.text_input("연락처 (알림톡용)", placeholder="010-0000-0000", key="sb_s_phone")
            new_gender = st.radio("👫 성별 선택", ["남자", "여자"], horizontal=True, key="sb_s_gender")
            
            curr_yr = datetime.now().year
            birth_yr = st.number_input("출생연도 (4자리)", min_value=1940, max_value=curr_yr, value=2018, step=1)
            
            auto_grade = get_grade_by_birth_year(birth_yr)
            st.caption(f"💡 현재 나이 기준 자동 분류: **[{auto_grade}]**")
            
            btn_signup = st.form_submit_button("가입 신청", use_container_width=True)
            
            if btn_signup:
                if not new_name.strip() or not new_phone.strip():
                    st.sidebar.error("⚠️ 실명과 연락처 입력이 필수입니다.")
                elif new_id in st.session_state.users:
                    st.sidebar.warning("이미 존재하는 아이디입니다.")
                elif new_id and new_pw:
                    reg_date = datetime.now()
                    
                    st.session_state.users[new_id] = {
                        "pw": new_pw, 
                        "name": new_name.strip(), 
                        "phone": new_phone.strip(),
                        "gender": new_gender,
                        "birth_year": int(birth_yr),
                        "grade": auto_grade,
                        "role": "user",
                        "status": "pending",
                        "join_date": reg_date.strftime("%Y-%m-%d"),
                        "pay_status": "미납"
                    }
                    st.sidebar.info(f"📩 [{new_gender}/{auto_grade}] 가입 신청 완료! 관리자 승인 후 로그인할 수 있습니다.")
                else:
                    st.sidebar.warning("모든 항목을 입력해주세요.")

# 6. 메인 페이지 로직
if main_menu == "홈 (기본 영상)":
    col_title, col_notice = st.columns([1, 1])
    
    with col_title:
        st.title("🛼 Rising Inline Club")
        
    with col_notice:
        st.info(st.session_state.club_notice)
        
        if is_admin:
            with st.expander("✏️ [관리자] 공지사항 수정하기"):
                updated_notice = st.text_area("공지사항 내용", value=st.session_state.club_notice, height=100)
                if st.button("공지사항 등록/수정"):
                    st.session_state.club_notice = updated_notice
                    st.success("✅ 공지사항이 수정되었습니다.")
                    st.rerun()
        
    st.write("---")
    play_main_video()

elif main_menu == "1. 개인별 LAB Time Recorder":
    st.title("⏱️ 개인별 LAB Time Recorder")
    st.write("월별/일별 기록 추이를 수치와 그래프로 한눈에 확인해보세요.")
    st.write("---")
    
    if not st.session_state.logged_in_user:
        st.warning("🔒 기록 조회를 위해 왼쪽 사이드바 하단에서 **로그인**을 진행해 주세요.")
        st.stop()

    current_user_info = st.session_state.users[current_id]
    
    if is_admin:
        st.success("👑 **[관리자 모드]** 신규 기록 등록, 삭제 및 회원 통합 관리가 가능합니다.")
        display_records = st.session_state.lab_records
    else:
        st.info(f"👁️ **[모니터링 모드]** **{current_user_info['name']}** 님의 기록 조회 전용 페이지입니다. (성별: {current_user_info.get('gender', '-')}, 소속: {current_user_info.get('grade', '-')})")
        c_name = current_user_info["name"].strip()
        display_records = st.session_state.lab_records[
            (st.session_state.lab_records["ID"] == current_id) | 
            (st.session_state.lab_records["이름"] == c_name)
        ]

    st.write("---")
    
    if is_admin:
        st.markdown("### 📝 신규 기록 등록 (관리자 전용)")
        grade_options = ["유치부", "1-2학년", "3-4학년", "5-6학년", "중등부", "고등부", "성인부"]
        selected_grade = st.selectbox("🎒 1. 학년/부서 선택", grade_options, key="rec_grade_select")
        
        grade_members = {
            uid: uinfo["name"] 
            for uid, uinfo in st.session_state.users.items() 
            if uinfo.get("grade") == selected_grade
        }
        
        if not grade_members:
            st.warning(f"⚠️ 현재 [{selected_grade}]에 등록된 회원이 없습니다.")
            member_names = ["등록 선수 없음"]
            selected_name = "등록 선수 없음"
        else:
            member_names = list(grade_members.values())
            selected_name = st.selectbox("👤 2. 선수 선택", member_names, key="rec_player_select")
            
        target_gender = "남자"
        for uid, uinfo in st.session_state.users.items():
            if uinfo.get("name") == selected_name and uinfo.get("grade") == selected_grade:
                target_gender = uinfo.get("gender", "남자")
                break

        with st.form(key="lab_time_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                record_date = st.date_input("📅 측정 날짜", datetime.now())
                st.text_input("👤 선택된 선수", value=selected_name, disabled=True)
            with col2:
                st.text_input("🎒 선택된 학년", value=selected_grade, disabled=True)
                gender_idx = 0 if target_gender == "남자" else 1
                gender = st.selectbox("👫 성별", ["남자", "여자"], index=gender_idx)
            with col3:
                filtered_events = benchmark_df[benchmark_df["학년"] == selected_grade]["종목"].unique()
                if len(filtered_events) == 0:
                    filtered_events = ["100m", "200m", "300m", "500m", "1,000m", "1,500m"]
                event_type = st.selectbox("👟 종목", filtered_events)
                record_time = st.text_input("⏱️ 내 기록(초)", placeholder="예: 32.32 초 (또는 01:32.00)")
                
            submit_button = st.form_submit_button(label="🚀 기록 저장 및 차트 반영", use_container_width=True)
            
            if submit_button:
                if selected_name == "등록 선수 없음":
                    st.error("❌ 등록된 선수가 없어 기록을 저장할 수 없습니다.")
                elif record_time and selected_name.strip():
                    date_str = record_date.strftime("%Y-%m-%d")
                    target_name = selected_name.strip()
                    target_id = current_id
                    for uid, uinfo in st.session_state.users.items():
                        if uinfo.get("name") == target_name:
                            target_id = uid
                            break

                    new_record = pd.DataFrame([{
                        "ID": target_id,
                        "입력 날짜": date_str,
                        "이름": target_name,
                        "학년": selected_grade.strip(),
                        "성별": gender.strip(),
                        "종목": event_type.strip(),
                        "기록": record_time.strip()
                    }])
                    st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_record], ignore_index=True)
                    st.success(f"✅ [{date_str}] [{selected_grade}] {target_name} 선수의 {event_type} 기록({record_time}초)이 저장되었습니다!")
                    st.rerun()
                else:
                    st.warning("⚠️ 선수 이름을 선택하고 기록을 입력해 주세요.")

        st.write("---")

    created_tabs = st.tabs(["🏆 기록 추이 차트", "📋 등록 기록 목록 및 관리", "📚 전국 초등 최상위권 기준표"])
    
    with created_tabs[0]:
        if not display_records.empty:
            st.markdown("### 📊 랩타임 기록 추이 차트")
            filtered_df = display_records.copy()
            
            if is_admin:
                st.markdown("#### 🔍 [관리자 필터] 학년 및 성별 조건 검색")
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                with f_col1:
                    filter_grade = st.selectbox("🎒 학년/부서 선택", ["전체", "유치부", "1-2학년", "3-4학년", "5-6학년", "중등부", "고등부", "성인부"])
                with f_col2:
                    filter_gender = st.selectbox("👫 성별 선택", ["전체", "남자", "여자"])
                    
                if filter_grade != "전체":
                    filtered_df = filtered_df[filtered_df["학년"] == filter_grade]
                if filter_gender != "전체":
                    filtered_df = filtered_df[filtered_df["성별"] == filter_gender]
                
                with f_col3:
                    view_mode = st.radio("👀 조회 방식", ["전체 (선수 통합)", "개별 선수 선택"], horizontal=True)
                with f_col4:
                    if view_mode == "개별 선수 선택":
                        available_users = filtered_df["이름"].unique()
                        if len(available_users) > 0:
                            target_user = st.selectbox("👤 개별 선수 선택", available_users)
                            filtered_df = filtered_df[filtered_df["이름"] == target_user]
                        else:
                            st.warning("조건에 맞는 선수가 없습니다.")
                            filtered_df = pd.DataFrame()
            else:
                view_mode = "개별 선수 선택"

            if not filtered_df.empty:
                st.write("---")
                c_event_col, c_time_unit_col = st.columns([1, 1])
                with c_event_col:
                    selected_event_type = st.selectbox("👟 조회할 종목 선택:", filtered_df["종목"].unique())
                with c_time_unit_col:
                    time_unit = st.radio("📅 조회 단위 선택:", ["일별 (측정 날짜별)", "월별 (월평균)"], horizontal=True)
                
                user_event_df = filtered_df[filtered_df["종목"] == selected_event_type].copy()
                
                if not user_event_df.empty:
                    user_event_df["초"] = user_event_df["기록"].apply(convert_record_to_seconds)
                    user_event_df["입력 날짜_dt"] = pd.to_datetime(user_event_df["입력 날짜"])
                    user_event_df = user_event_df.sort_values("입력 날짜_dt")
                    user_event_df["날짜_str"] = user_event_df["입력 날짜_dt"].dt.strftime("%Y-%m-%d")
                    user_event_df["월_str"] = user_event_df["입력 날짜_dt"].dt.strftime("%Y-%m")
                    
                    latest_row = user_event_df.iloc[-1]
                    u_grade = str(latest_row["학년"]).strip()
                    u_gender = str(latest_row["성별"]).strip()
                    u_event = str(selected_event_type).strip()
                    
                    match_bench = benchmark_df[
                        (benchmark_df["학년"] == u_grade) & 
                        (benchmark_df["성별"] == u_gender) & 
                        (benchmark_df["종목"] == u_event)
                    ]
                    
                    top_sec = float(match_bench.iloc[0]["최상위권"]) if not match_bench.empty else None
                    avg_sec = float(match_bench.iloc[0]["상위권평균"]) if not match_bench.empty else None
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("⏱️ 최근 측정 기록", f"{user_event_df.iloc[-1]['초']:.2f} 초")
                    m2.metric("🏆 전국 최상위권 기준", f"{top_sec:.2f} 초" if top_sec else "N/A")
                    m3.metric("🥇 상위권 평균 기준", f"{avg_sec:.2f} 초" if avg_sec else "N/A")
                    st.write("")
                    
                    fig = go.Figure()
                    group_col = "날짜_str" if "일별" in time_unit else "월_str"
                    x_label = "측정 날짜 (일별)" if "일별" in time_unit else "측정 월 (월별)"

                    if is_admin and view_mode == "전체 (선수 통합)":
                        all_x_axis = sorted(user_event_df[group_col].unique())
                        for p_name in user_event_df["이름"].unique():
                            p_df = user_event_df[user_event_df["이름"] == p_name]
                            p_grouped = p_df.groupby(group_col, as_index=False)["초"].mean().round(2).sort_values(group_col)
                            
                            fig.add_trace(go.Scatter(
                                x=p_grouped[group_col], 
                                y=p_grouped["초"],
                                mode='lines+markers+text',
                                text=p_grouped["초"].apply(lambda x: f"{x:.2f}초"),
                                textposition="top center",
                                name=f'👤 {p_name}',
                                marker=dict(size=8)
                            ))
                        chart_title = f"📈 [{u_grade} {u_gender}] {selected_event_type} - 전체 선수 {time_unit.split()[0]} 기록 추이"
                        x_ref_axis = all_x_axis
                    else:
                        grouped_df = user_event_df.groupby(group_col, as_index=False)["초"].mean().round(2).sort_values(group_col)
                        disp_name = user_event_df.iloc[0]["이름"] if not user_event_df.empty else "선수"
                        
                        fig.add_trace(go.Scatter(
                            x=grouped_df[group_col], 
                            y=grouped_df["초"],
                            mode='lines+markers+text',
                            text=grouped_df["초"].apply(lambda x: f"{x:.2f}초"),
                            textposition="top center",
                            name=f'👤 {disp_name} 기록',
                            line=dict(color='#1f77b4', width=3), 
                            marker=dict(size=10)
                        ))
                        chart_title = f"📈 [{disp_name}] {selected_event_type} {time_unit.split()[0]} 기록 추이"
                        x_ref_axis = grouped_df[group_col]

                    if avg_sec is not None:
                        fig.add_trace(go.Scatter(
                            x=x_ref_axis, 
                            y=[avg_sec] * len(x_ref_axis),
                            mode='lines+markers+text',
                            text=[f"{avg_sec:.2f}초"] * len(x_ref_axis),
                            textposition="top center",
                            name='🥇 상위권 평균 기준',
                            line=dict(color='#ff7f0e', width=2, dash='dash'),
                            marker=dict(size=6)
                        ))
                        
                    if top_sec is not None:
                        fig.add_trace(go.Scatter(
                            x=x_ref_axis, 
                            y=[top_sec] * len(x_ref_axis),
                            mode='lines+markers+text',
                            text=[f"{top_sec:.2f}초"] * len(x_ref_axis),
                            textposition="bottom center",
                            name='🏆 전국 최상위권 기준',
                            line=dict(color='#d62728', width=2, dash='dot'),
                            marker=dict(size=6)
                        ))
                    
                    all_y_vals = list(user_event_df["초"])
                    if avg_sec: all_y_vals.append(avg_sec)
                    if top_sec: all_y_vals.append(top_sec)
                    max_y = (max(all_y_vals) * 1.2) if all_y_vals else 40
                        
                    fig.update_layout(
                        title=dict(text=chart_title, font=dict(size=18)),
                        xaxis=dict(title=x_label, type='category', showgrid=True),
                        yaxis=dict(title="기록 시간 (초)", rangemode="tozero", range=[0, max_y], zeroline=True, zerolinecolor='lightgrey', showgrid=True),
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("선택한 종목의 기록이 존재하지 않습니다.")
            else:
                st.warning("선택 조건에 부합하는 데이터가 없습니다.")
        else:
            st.info("등록된 기록 데이터가 존재하지 않습니다.")

    with created_tabs[1]:
        if not display_records.empty:
            st.markdown("### 📋 등록된 랩타임 기록 목록")
            if is_admin:
                af1, af2 = st.columns(2)
                with af1:
                    g_f = st.selectbox("🎒 학년 필터 (목록)", ["전체", "유치부", "1-2학년", "3-4학년", "5-6학년", "중등부", "고등부", "성인부"])
                with af2:
                    s_f = st.selectbox("👫 성별 필터 (목록)", ["전체", "남자", "여자"])
                
                table_df = display_records.copy()
                if g_f != "전체":
                    table_df = table_df[table_df["학년"] == g_f]
                if s_f != "전체":
                    table_df = table_df[table_df["성별"] == s_f]
                st.dataframe(table_df, use_container_width=True)
            else:
                st.dataframe(display_records, use_container_width=True)
            
            if is_admin:
                st.write("---")
                st.markdown("### 🗑️ 기록 삭제 기능 (관리자 전용)")
                records_to_delete = st.selectbox(
                    "삭제할 기록을 선택하세요:", 
                    display_records.index, 
                    format_func=lambda x: f"[{display_records.loc[x, '입력 날짜']}] {display_records.loc[x, '이름']} ({display_records.loc[x, '학년']} {display_records.loc[x, '성별']}) - {display_records.loc[x, '종목']} ({display_records.loc[x, '기록']}초)"
                )
                
                if st.button("선택한 기록 삭제"):
                    st.session_state.lab_records = st.session_state.lab_records.drop(records_to_delete).reset_index(drop=True)
                    st.success("선택한 기록이 삭제되었습니다.")
                    st.rerun()
        else:
            st.info("등록된 기록 데이터가 존재하지 않습니다.")

    with created_tabs[2]:
        st.markdown("### 📚 전국 유치부 및 초등학생 최상위권/상위권 기준 기록표")
        custom_table_css = """
<style>
.compact-table-container { width: 100%; overflow-x: auto; margin-top: 10px; }
.compact-table { width: 100%; border-collapse: collapse; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; }
.compact-table th { background-color: #f1f3f5; color: #1c1e21; font-weight: bold; padding: 6px 8px; border: 1px solid #dee2e6; white-space: nowrap; }
.compact-table td { padding: 4px 8px; border: 1px solid #dee2e6; color: #333333; }
.compact-table tr:nth-child(even) { background-color: #f8f9fa; }
.compact-table tr:hover { background-color: #e9ecef; }
.highlight-top { color: #d62728; font-weight: 600; }
.highlight-avg { color: #d97706; font-weight: 600; }
</style>
"""
        table_html = custom_table_css + '<div class="compact-table-container"><table class="compact-table">'
        table_html += '<thead><tr><th>학년</th><th>성별</th><th>종목</th><th>최상위권 (초)</th><th>상위권평균 (초)</th></tr></thead><tbody>'
        
        for _, row in benchmark_df.iterrows():
            table_html += f"<tr><td><b>{row['학년']}</b></td><td>{row['성별']}</td><td>{row['종목']}</td><td class=\"highlight-top\">{row['최상위권']:.2f} 초</td><td class=\"highlight-avg\">{row['상위권평균']:.2f} 초</td></tr>"
            
        table_html += '</tbody></table></div>'
        st.markdown(table_html, unsafe_allow_html=True)

elif main_menu == "2. 대회 사진첩":
    st.title("📸 대회 사진첩 및 입상자 명단")
    
    if not st.session_state.logged_in_user:
        st.error("🔒 **대회 사진첩 접근 제한**")
        st.warning("대회 사진첩 및 입상자 정보는 로그인한 승인 회원만 이용할 수 있습니다.")
        st.stop()

    if is_admin:
        with st.expander("⚙️ [관리자 전용] 대회 폴더 관리 (생성 / 수정 / 삭제)", expanded=False):
            f_tab1, f_tab2, f_tab3 = st.tabs(["➕ 새 폴더 생성", "✏️ 폴더 이름 변경", "🗑️ 폴더 삭제"])
            
            with f_tab1:
                new_folder_name = st.text_input("새 대회 폴더 이름", placeholder="예: 2026년 전국 남원대회")
                if st.button("폴더 생성"):
                    clean_name = new_folder_name.strip()
                    if clean_name and clean_name not in st.session_state.event_folders:
                        st.session_state.event_folders.append(clean_name)
                        st.session_state.gallery_photos[clean_name] = []
                        st.session_state.competition_winners[clean_name] = []
                        st.success(f"✅ [{clean_name}] 폴더가 추가되었습니다.")
                        st.rerun()
                    else:
                        st.warning("폴더명을 입력하지 않았거나 이미 존재하는 이름입니다.")

            with f_tab2:
                if st.session_state.event_folders:
                    target_rename = st.selectbox("이름을 변경할 폴더", st.session_state.event_folders, key="rename_select")
                    renamed_val = st.text_input("변경할 새 폴더 이름", value=target_rename)
                    if st.button("이름 변경"):
                        clean_rename = renamed_val.strip()
                        if clean_rename and clean_rename != target_rename:
                            idx = st.session_state.event_folders.index(target_rename)
                            st.session_state.event_folders[idx] = clean_rename
                            st.session_state.gallery_photos[clean_rename] = st.session_state.gallery_photos.pop(target_rename)
                            if target_rename in st.session_state.competition_winners:
                                st.session_state.competition_winners[clean_rename] = st.session_state.competition_winners.pop(target_rename)
                            else:
                                st.session_state.competition_winners[clean_rename] = []
                            st.success(f"✅ [{target_rename}] -> [{clean_rename}] (으로) 변경되었습니다.")
                            st.rerun()
                else:
                    st.info("변경할 폴더가 없습니다.")

            with f_tab3:
                if st.session_state.event_folders:
                    target_del = st.selectbox("삭제할 폴더 선택", st.session_state.event_folders, key="del_select")
                    if st.button("선택 폴더 삭제"):
                        st.session_state.event_folders.remove(target_del)
                        if target_del in st.session_state.gallery_photos:
                            del st.session_state.gallery_photos[target_del]
                        if target_del in st.session_state.competition_winners:
                            del st.session_state.competition_winners[target_del]
                        st.success(f"🗑️ [{target_del}] 폴더가 삭제되었습니다.")
                        st.rerun()
                else:
                    st.info("삭제할 폴더가 없습니다.")
        st.write("---")

    if not selected_event:
        st.info("📂 왼쪽 사이드바에서 조회할 대회 폴더를 선택해 주세요.")
        st.stop()

    st.subheader(f"📂 현재 선택된 대회: {selected_event}")

    # 대회별 탭 구분 (사진첩 vs 입상자 명단)
    folder_tabs = st.tabs(["📸 대회 현장 사진첩", "🏆 대회 입상자 명단"])

    with folder_tabs[0]:
        st.markdown("#### 📤 사진 등록하기")
        uploaded_files = st.file_uploader(f"[{selected_event}] 폴더에 사진 추가", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key=f"uploader_{selected_event}")
        if uploaded_files:
            if st.button("선택한 사진 등록", key=f"btn_upload_{selected_event}"):
                uploader_name = st.session_state.users[current_id]["name"]
                for uploaded_file in uploaded_files:
                    st.session_state.gallery_photos[selected_event].append({
                        "bytes": uploaded_file.getvalue(),
                        "filename": uploaded_file.name,
                        "uploader": uploader_name,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                st.success(f"🎉 {len(uploaded_files)}장의 사진이 성공적으로 등록되었습니다!")
                st.rerun()

        st.write("---")

        photos = st.session_state.gallery_photos.get(selected_event, [])
        if photos:
            st.markdown(f"총 **{len(photos)}**장의 사진이 있습니다.")
            cols = st.columns(3)
            current_user_name = st.session_state.users[current_id]["name"]
            
            for idx, photo in enumerate(photos):
                with cols[idx % 3]:
                    st.image(photo["bytes"], caption=f"📷 {photo['filename']}\n👤 {photo['uploader']} ({photo['date']})", use_container_width=True)
                    
                    if is_admin or photo["uploader"] == current_user_name:
                        if st.button("🗑️ 사진 삭제", key=f"del_photo_{selected_event}_{idx}", use_container_width=True):
                            st.session_state.gallery_photos[selected_event].pop(idx)
                            st.success("사진이 정상적으로 삭제되었습니다.")
                            st.rerun()
        else:
            st.info("🖼️ 해당 폴더에 등록된 사진이 없습니다. 위에서 새 사진을 등록해 보세요!")

    with folder_tabs[1]:
        st.markdown(f"### 🏆 [{selected_event}] 영광의 입상자 명단")
        st.write("이번 대회에서 멋진 성적을 거둔 우리 클럽 선수들을 축하합니다! 🎉")
        st.write("---")

        winners = st.session_state.competition_winners.get(selected_event, [])
        
        if winners:
            display_winners = []
            for w in winners:
                display_winners.append({
                    "이름": w.get("이름"),
                    "순위": w.get("순위"),
                    "종목": w.get("종목")
                })
            
            centered_table_css = """
            <style>
            .winner-table-container { width: 100%; overflow-x: auto; margin-top: 10px; }
            .winner-table { width: 100%; border-collapse: collapse; font-size: 14px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; }
            .winner-table th { background-color: #f1f3f5; color: #1c1e21; font-weight: bold; padding: 8px 12px; border: 1px solid #dee2e6; text-align: center; }
            .winner-table td { padding: 8px 12px; border: 1px solid #dee2e6; color: #333333; text-align: center; }
            .winner-table tr:nth-child(even) { background-color: #f8f9fa; }
            .winner-table tr:hover { background-color: #e9ecef; }
            </style>
            """
            table_html = centered_table_css + '<div class="winner-table-container"><table class="winner-table">'
            table_html += '<thead><tr><th>이름</th><th>순위</th><th>종목</th></tr></thead><tbody>'
            
            for row in display_winners:
                table_html += f"<tr><td>{row['이름']}</td><td>{row['순위']}</td><td>{row['종목']}</td></tr>"
                
            table_html += '</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("💡 아직 등록된 입상자 정보가 없습니다.")

        if is_admin:
            st.write("---")
            st.markdown("#### ➕ 입상자 등록 (관리자 전용)")
            
            all_club_members = [udata["name"] for uid, udata in st.session_state.users.items() if udata.get("name")]
            if not all_club_members:
                all_club_members = ["등록된 회원 없음"]

            with st.form(f"winner_add_form_{selected_event}", clear_on_submit=True):
                w_col1, w_col2, w_col3 = st.columns(3)
                with w_col1:
                    w_name = st.selectbox("선수 이름", all_club_members)
                with w_col2:
                    w_award = st.selectbox("순위", ["1위 (금메달)", "2위 (은메달)", "3위 (동메달)", "최우수상", "우수상", "장려상", "입상"])
                with w_col3:
                    w_event = st.selectbox("종목", ["100m", "200m", "300m", "500m", "1,000m", "1,500m", "초등 저학년부 500m", "초등 고학년부 1,000m"])
                
                btn_add_winner = st.form_submit_button("🌟 입상자 등록하기", use_container_width=True)
                if btn_add_winner:
                    if w_name != "등록된 회원 없음":
                        st.session_state.competition_winners[selected_event].append({
                            "이름": w_name,
                            "순위": w_award,
                            "종목": w_event,
                            "등록일": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success(f"✅ [{w_name}] 선수의 입상 정보가 성공적으로 등록되었습니다!")
                        st.rerun()
                    else:
                        st.warning("⚠️ 등록된 선수가 없습니다.")

            if winners:
                st.write("")
                st.markdown("#### 🗑️ 입상자 삭제 (관리자 전용)")
                del_win_idx = st.selectbox(
                    "삭제할 입상자를 선택하세요:", 
                    range(len(winners)), 
                    format_func=lambda i: f"👤 {winners[i]['이름']} - 🥇 {winners[i]['순위']} ({winners[i].get('종목', winners[i].get('종목 및 부서', '-'))})",
                    key=f"del_win_select_{selected_event}"
                )
                if st.button("선택 입상자 정보 삭제", key=f"btn_del_win_{selected_event}"):
                    st.session_state.competition_winners[selected_event].pop(del_win_idx)
                    st.success("선택한 입상자 정보가 삭제되었습니다.")
                    st.rerun()

elif main_menu == "3. 건의사항":
    st.title("💡 무기명 건의사항함")
    st.write("클럽 운영 및 시설 등 자유롭게 의견을 제출해 주세요. 작성자의 정보나 제출 시각은 전혀 기록되지 않습니다.")
    st.write("---")
    
    if is_admin:
        st.markdown("### 🔒 [관리자 전용] 건의사항 목록 및 피드백 작성")
        st.info("※ 관리자 계정에서는 건의사항 작성란이 노출되지 않으며, 등록된 건의 내용 확인 및 피드백 작성만 가능합니다.")
        st.write("---")
        
        if st.session_state.suggestions:
            for idx, item in enumerate(st.session_state.suggestions):
                with st.expander(f"📌 [{idx+1}] {item['title']}"):
                    st.markdown("**건의 내용:**")
                    st.write(item["content"])
                    st.write("---")
                    
                    fb_text = st.text_area("💬 관리자 Feedback (피드백 작성)", value=item.get("feedback", ""), key=f"fb_input_{idx}", height=100)
                    
                    c_btn1, c_btn2 = st.columns([1, 1])
                    with c_btn1:
                        if st.button(f"💾 피드백 저장", key=f"save_fb_{idx}", use_container_width=True):
                            st.session_state.suggestions[idx]["feedback"] = fb_text.strip()
                            st.success("피드백이 저장되었습니다.")
                            st.rerun()
                    with c_btn2:
                        if st.button(f"🗑️ 건의사항 삭제", key=f"del_sug_{idx}", use_container_width=True):
                            st.session_state.suggestions.pop(idx)
                            st.success("해당 건의사항이 삭제되었습니다.")
                            st.rerun()
        else:
            st.info("현재 등록된 건의사항이 없습니다.")
            
    else:
        if not st.session_state.logged_in_user:
            st.warning("🔒 건의사항은 **로그인한 승인 회원**만 작성할 수 있습니다. 왼쪽 사이드바 하단에서 로그인해 주세요.")
        else:
            current_user_status = st.session_state.users[current_id].get("status")
            if current_user_status != "approved":
                st.warning("⏳ 관리자 가입 승인 대기 중인 회원입니다. 승인 완료 후 건의사항을 작성하실 수 있습니다.")
            else:
                st.markdown("### ✍️ 건의사항 작성 (익명)")
                with st.form("suggestion_form", clear_on_submit=True):
                    s_title = st.text_input("제목", placeholder="건의사항 제목을 입력하세요")
                    s_content = st.text_area("내용", placeholder="개선되었으면 하는 점이나 의견을 자유롭게 작성해 주세요.", height=150)
                    btn_submit_s = st.form_submit_button("📩 무기명 제출하기", use_container_width=True)
                    
                    if btn_submit_s:
                        if s_title.strip() and s_content.strip():
                            st.session_state.suggestions.append({
                                "title": s_title.strip(),
                                "content": s_content.strip(),
                                "feedback": ""
                            })
                            st.success("✅ 건의사항이 성공적으로 제출되었습니다.")
                        else:
                            st.warning("⚠️ 제목과 내용을 모두 입력해 주세요.")

elif main_menu == "4. 👥 회원 승인 및 관리 (관리자 전용)":
    st.title("👥 회원 승인 및 학원비 관리")
    st.write("회원의 가입 승인 처리, 연락처, 성별 및 **월 학원비 납부 상태**를 관리합니다.")
    st.write("---")
    
    if not is_admin:
        st.error("🔒 관리자 권한이 필요합니다.")
        st.stop()

    st.markdown("### ⏳ 1. 가입 승인 대기 목록")
    # 수정된 부분 (괄호 정상화)
    pending_users = [uid for uid, udata in st.session_state.users.items() if udata.get("status") == "pending"]
    
    if pending_users:
        p_col1, p_col2 = st.columns([3, 1])
        selected_p_user = p_col1.selectbox("승인할 회원을 선택하세요:", pending_users, format_func=lambda x: f"ID: {x} | 이름: {st.session_state.users[x]['name']} ({st.session_state.users[x].get('gender', '-')}/{st.session_state.users[x].get('grade', '-')}) | 연락처: {st.session_state.users[x].get('phone')}")
        if p_col2.button("✅ 선택 회원 승인", use_container_width=True):
            st.session_state.users[selected_p_user]["status"] = "approved"
            st.success(f"🎉 [{st.session_state.users[selected_p_user]['name']}] 회원이 정상 승인되었습니다!")
            st.rerun()
    else:
        st.info("현재 승인 대기 중인 신청이 없습니다.")

    st.write("---")
    
    st.markdown("### 💳 2. 회원별 학원비 납부 상태 관리 (관리자 전용)")
    approved_users = [uid for uid, udata in st.session_state.users.items() if udata.get("role") != "admin" and udata.get("status") == "approved"]
    
    if approved_users:
        with st.form("pay_manage_form"):
            selected_m_user = st.selectbox(
                "관리할 회원을 선택하세요:", 
                approved_users, 
                format_func=lambda x: f"이름: {st.session_state.users[x]['name']} ({st.session_state.users[x].get('grade', '-')}) | 현재 상태: {st.session_state.users[x].get('pay_status', '미납')}"
            )
            m_user_info = st.session_state.users[selected_m_user]
            
            new_pay_status = st.selectbox(
                "납부 상태 설정", 
                ["완료", "미납"], 
                index=0 if m_user_info.get("pay_status") == "완료" else 1
            )
                
            btn_update_pay = st.form_submit_button("상태 업데이트", use_container_width=True)
            if btn_update_pay:
                st.session_state.users[selected_m_user]["pay_status"] = new_pay_status
                st.success(f"✅ [{m_user_info['name']}] 회원의 학원비 납부 상태가 [{new_pay_status}](으)로 변경되었습니다.")
                st.rerun()
    else:
        st.info("등록된 승인 회원이 없습니다.")
