import streamlit as st
import os
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import base64

# 1. 페이지 레이아웃 설정
st.set_page_config(layout="wide", page_title="Rising Inline Club")

# 2. 데이터 및 미디어 저장을 위한 로컬 폴더 경로 설정
DATA_DIR = "club_data"
ASSETS_DIR = os.path.join(DATA_DIR, "assets")
PHOTO_DIR = os.path.join(DATA_DIR, "photos")

for d in [DATA_DIR, ASSETS_DIR, PHOTO_DIR]:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
FOLDERS_FILE = os.path.join(DATA_DIR, "folders.json")
WINNERS_FILE = os.path.join(DATA_DIR, "winners.json")
SUGGESTIONS_FILE = os.path.join(DATA_DIR, "suggestions.json")
NOTICE_FILE = os.path.join(DATA_DIR, "notice.json")
COMPETITIONS_FILE = os.path.join(DATA_DIR, "competitions.json")

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

# 5. Session State 초기화
today_str = datetime.now().strftime("%Y-%m-%d")

if "club_notice" not in st.session_state:
    loaded_notice = load_json(NOTICE_FILE, None)
    st.session_state.club_notice = loaded_notice if loaded_notice else "📢 **[클럽 공지사항]**\n- 이번 주 토요일 정기 훈련 일정 정상 진행\n- 신규 입단 문의 및 승인은 관리자에게 요청해 주세요."

if "suggestions" not in st.session_state:
    st.session_state.suggestions = load_json(SUGGESTIONS_FILE, [])

if "competitions" not in st.session_state:
    st.session_state.competitions = load_json(COMPETITIONS_FILE, [])

if "selected_shop" not in st.session_state:
    st.session_state.selected_shop = None

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

def save_competitions_to_disk():
    save_json(COMPETITIONS_FILE, st.session_state.competitions)

current_id = st.session_state.logged_in_user
is_admin = False
if current_id and current_id in st.session_state.users:
    is_admin = (st.session_state.users[current_id].get("role") == "admin")

# 6. 사이드바 메인 메뉴 (라디오 버튼 키 매핑 적용)
st.sidebar.header("🏃 밴드 메뉴")
menu_options = [
    "홈 (기본 영상)", 
    "1. 개인별 LAB Time Recorder", 
    "2. 대회 참가 신청 및 명단", 
    "3. 대회 사진첩", 
    "4. 건의사항",
    "5. 🏁 전문 레이싱 샵 (대시보드 보기)"
]
if is_admin:
    menu_options.append("6. 👥 회원 승인 및 관리 (관리자 전용)")

if current_id:
    menu_options.append("🔐 개인정보 변경")

# 라디오 버튼 상태 유지를 위해 key 매개변수 활용
main_menu = st.sidebar.radio("메뉴를 선택하세요", menu_options, key="main_menu_radio")

selected_event = None
if main_menu == "3. 대회 사진첩":
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 대회 폴더 선택")
    if st.session_state.event_folders:
        selected_event = st.sidebar.radio("이동할 사진첩을 선택하세요", st.session_state.event_folders)
    
    if is_admin:
        with st.sidebar.expander("🛠️ 폴더 추가/삭제 관리"):
            with st.sidebar.form("add_folder_form", clear_on_submit=True):
                new_folder_name = st.text_input("새 폴더 이름")
                if st.form_submit_button("폴더 생성"):
                    if new_folder_name.strip() and new_folder_name.strip() not in st.session_state.event_folders:
                        st.session_state.event_folders.append(new_folder_name.strip())
                        if new_folder_name.strip() not in st.session_state.competition_winners:
                            st.session_state.competition_winners[new_folder_name.strip()] = []
                        save_folders_to_disk()
                        st.success("폴더가 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error("올바르거나 중복되지 않는 이름을 입력하세요.")
            
            if st.session_state.event_folders:
                folder_to_delete = st.selectbox("삭제할 폴더 선택", st.session_state.event_folders, key="del_folder_sb")
                if st.button("선택한 폴더 삭제"):
                    st.session_state.event_folders.remove(folder_to_delete)
                    if folder_to_delete in st.session_state.competition_winners:
                        del st.session_state.competition_winners[folder_to_delete]
                    save_folders_to_disk()
                    st.success("폴더가 삭제되었습니다.")
                    st.rerun()

# 6-1. 사이드바 레이싱 전문 샵 및 동영상 링크 섹션
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 인라인 레이싱 샵 & 동영상")

with st.sidebar.expander("🏎️ 인라인 레이싱 전문 샵"):
    # st.link_button을 사용하여 새 창에서 안전하게 열리도록 유도 (동작 오류 원천 차단)
    st.link_button("⚡ 스피드인라인 레이싱몰 바로가기", "http://www.speedinline.co.kr/", use_container_width=True)

with st.sidebar.expander("🎥 인라인 강습 및 주행 영상"):
    st.markdown("- [인라인 초급 과정 강좌보기](https://www.youtube.com/watch?v=l7cuAsNMtTE)", unsafe_allow_html=True)
    st.markdown("- [기초 턴 및 기술 연습보기](https://www.youtube.com/watch?v=nzpLqBZ-1lQ)", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 계정 관리")

if st.session_state.logged_in_user:
    u_info = st.session_state.users[st.session_state.logged_in_user]
    st.sidebar.success(f"👤 **{u_info['name']}**님 ({u_info.get('gender', '-')}/{u_info.get('grade', '회원')})")
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()
else:
    with st.sidebar.form("login_form"):
        uid_input = st.text_input("아이디")
        pw_input = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            if uid_input in st.session_state.users and st.session_state.users[uid_input]["pw"] == pw_input:
                st.session_state.logged_in_user = uid_input
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 잘못되었습니다.")

# 7. 메인 화면 분기 처리
if main_menu == "홈 (기본 영상)":
    st.title("🏆 Rising Inline Club 대시보드")
    st.markdown(st.session_state.club_notice)
    st.markdown("---")
    play_main_video()

elif main_menu == "5. 🏁 전문 레이싱 샵 (대시보드 보기)":
    st.title("🏁 전문 레이싱(스피드) 샵 대시보드")
    st.markdown("외부 쇼핑몰 사이트들은 보안(X-Frame-Options) 정책상 내부 미리보기(iframe)가 차단되는 경우가 많습니다. 아래 버튼을 통해 **새 창에서 안전하게 접속**하실 수 있습니다.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("⚡ 스피드인라인 레이싱몰")
            st.write("전문 스피드 인라인 스케이트, 부츠, 프레임, 부품 판매 쇼핑몰")
            st.link_button("🚀 쇼핑몰 새 창으로 열기", "http://www.speedinline.co.kr/", use_container_width=True)

elif main_menu == "1. 개인별 LAB Time Recorder":
    st.title("⏱️ 개인별 LAB Time Recorder")
    st.write("기록 측정 및 분석 기능 영역입니다.")

elif main_menu == "2. 대회 참가 신청 및 명단":
    st.title("📝 대회 참가 신청 및 명단")
    st.write("대회 참가 신청 영역입니다.")

elif main_menu == "3. 대회 사진첩":
    st.title(f"📷 대회 사진첩 - {selected_event if selected_event else '전체'}")
    if selected_event:
        folder_path = os.path.join(PHOTO_DIR, selected_event)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            
        with st.form(f"upload_photo_form_{selected_event}", clear_on_submit=True):
            st.markdown("### 📤 사진 업로드하기")
            uploaded_files = st.file_uploader("대회 현장 사진을 선택하세요 (다중 선택 가능)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
            submit_photos = st.form_submit_button("사진 업로드 완료")
            
            if submit_photos and uploaded_files:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(folder_path, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                st.success(f"총 {len(uploaded_files)}장의 사진이 성공적으로 업로드되었습니다!")
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 🖼️ 사진 갤러리")
        
        if os.path.exists(folder_path):
            photo_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if photo_files:
                cols = st.columns(3)
                for idx, photo_file in enumerate(photo_files):
                    p_path = os.path.join(folder_path, photo_file)
                    
                    with open(p_path, "rb") as img_f:
                        encoded_img = base64.b64encode(img_f.read()).decode()
                    
                    with cols[idx % 3]:
                        st.markdown(
                            f"""
                            <div style="margin-bottom: 10px;">
                                <img src="data:image/jpeg;base64,{encoded_img}" style="width: 100%; height: 240px; object-fit: cover; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                                <p style="font-size: 0.85rem; color: #b0b0b0; text-align: center; margin-top: 5px; margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{photo_file}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if is_admin:
                            if st.button("삭제", key=f"del_photo_{selected_event}_{photo_file}", use_container_width=True):
                                os.remove(p_path)
                                st.success(f"'{photo_file}' 사진이 삭제되었습니다.")
                                st.rerun()
            else:
                st.info("이 폴더에 업로드된 사진이 아직 없습니다. 위에서 사진을 업로드해 보세요!")
    else:
        st.info("사이드바에서 사진을 확인할 대회 폴더를 선택해주세요.")

elif main_menu == "4. 건의사항":
    st.title("📢 건의사항")
    with st.form("sug"):
        t = st.text_input("제목")
        c = st.text_area("내용")
        if st.form_submit_button("제출"):
            st.session_state.suggestions.append({"title": t, "content": c})
            save_suggestions_to_disk()
            st.success("건의사항이 등록되었습니다.")
            st.rerun()

elif is_admin and main_menu == "6. 👥 회원 승인 및 관리 (관리자 전용)":
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

elif current_id and main_menu == "🔐 개인정보 변경":
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
