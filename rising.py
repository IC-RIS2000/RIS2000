import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re
import os
import json
from datetime import datetime

# ==========================================
# 0. 페이지 설정 및 영구 저장(JSON) 함수 정의
# ==========================================
st.set_page_config(
    page_title="클럽 통합 관리 시스템",
    page_icon="🏅",
    layout="wide"
)

USERS_FILE = "users_data.json"
RECORDS_FILE = "lab_records_data.json"
FOLDERS_FILE = "event_folders_data.json"
GALLERY_FILE = "gallery_photos_data.json"
WINNERS_FILE = "competition_winners_data.json"
SUGGESTIONS_FILE = "suggestions_data.json"

def load_all_data():
    # 1. 회원 정보 로드
    if "users" not in st.session_state:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                st.session_state.users = json.load(f)
        else:
            st.session_state.users = {
                "admin": {
                    "pw": "admin1234",
                    "name": "총관리자",
                    "role": "admin",
                    "status": "approved",
                    "phone": "010-0000-0000",
                    "gender": "기타",
                    "birth_year": 1990,
                    "grade": "성인",
                    "pay_status": "완료"
                }
            }
            save_users()

    # 2. 랩타임 기록 로드
    if "lab_records" not in st.session_state:
        if os.path.exists(RECORDS_FILE):
            st.session_state.lab_records = pd.read_json(RECORDS_FILE)
        else:
            st.session_state.lab_records = pd.DataFrame(columns=["ID", "이름", "학년", "성별", "종목", "기록", "입력 날짜"])

    # 3. 대회 폴더 로드
    if "event_folders" not in st.session_state:
        if os.path.exists(FOLDERS_FILE):
            with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
                st.session_state.event_folders = json.load(f)
        else:
            st.session_state.event_folders = ["2026년 전국 인라인 스프링 대회"]
            save_folders()

    # 4. 갤러리 사진 로드
    if "gallery_photos" not in st.session_state:
        if os.path.exists(GALLERY_FILE):
            with open(GALLERY_FILE, "r", encoding="utf-8") as f:
                st.session_state.gallery_photos = json.load(f)
        else:
            st.session_state.gallery_photos = {"2026년 전국 인라인 스프링 대회": []}
            save_gallery()

    # 5. 대회 입상자 로드
    if "competition_winners" not in st.session_state:
        if os.path.exists(WINNERS_FILE):
            with open(WINNERS_FILE, "r", encoding="utf-8") as f:
                st.session_state.competition_winners = json.load(f)
        else:
            st.session_state.competition_winners = {"2026년 전국 인라인 스프링 대회": []}
            save_winners()

    # 6. 건의사항 로드
    if "suggestions" not in st.session_state:
        if os.path.exists(SUGGESTIONS_FILE):
            with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                st.session_state.suggestions = json.load(f)
        else:
            st.session_state.suggestions = []
            save_suggestions()

    # 세션 상태 기본값 초기화
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    if "show_profile_edit" not in st.session_state:
        st.session_state.show_profile_edit = False

# 저장 함수들 정의
def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.users, f, ensure_ascii=False, indent=4)

def save_records():
    if not st.session_state.lab_records.empty:
        st.session_state.lab_records.to_json(RECORDS_FILE, orient="records", force_ascii=False)
    else:
        pd.DataFrame(columns=["ID", "이름", "학년", "성별", "종목", "기록", "입력 날짜"]).to_json(RECORDS_FILE, orient="records", force_ascii=False)

def save_folders():
    with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.event_folders, f, ensure_ascii=False, indent=4)

def save_gallery():
    with open(GALLERY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.gallery_photos, f, ensure_ascii=False, indent=4)

def save_winners():
    with open(WINNERS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.competition_winners, f, ensure_ascii=False, indent=4)

def save_suggestions():
    with open(SUGGESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.suggestions, f, ensure_ascii=False, indent=4)

# 데이터 불러오기 실행
load_all_data()

# ==========================================
# 1. 벤치마크 및 기준 데이터 정의
# ==========================================
BENCHMARK_RAW = [
    {"학년": "유치부", "성별": "남아", "종목": "100m", "최상위권": 15.50, "상위권평균": 17.80},
    {"학년": "유치부", "성별": "여아", "종목": "100m", "최상위권": 16.00, "상위권평균": 18.30},
    {"학년": "초등 1학년", "성별": "남", "종목": "100m", "최상위권": 14.20, "상위권평균": 16.50},
    {"학년": "초등 1학년", "성별": "여", "종목": "100m", "최상위권": 14.70, "상위권평균": 17.00},
    {"학년": "초등 2학년", "성별": "남", "종목": "100m", "최상위권": 13.50, "상위권평균": 15.60},
    {"학년": "초등 2학년", "성별": "여", "종목": "100m", "최상위권": 13.90, "상위권평균": 16.00},
    {"학년": "초등 3학년", "성별": "남", "종목": "100m", "최상위권": 12.80, "상위권평균": 14.70},
    {"학년": "초등 3학년", "성별": "여", "종목": "100m", "최상위권": 13.10, "상위권평균": 15.10},
    {"학년": "초등 4학년", "성별": "남", "종목": "100m", "최상위권": 12.10, "상위권평균": 13.90},
    {"학년": "초등 4학년", "성별": "여", "종목": "100m", "최상위권": 12.40, "상위권평균": 14.30},
    {"학년": "초등 5학년", "성별": "남", "종목": "100m", "최상위권": 11.50, "상위권평균": 13.20},
    {"학년": "초등 5학년", "성별": "여", "종목": "100m", "최상위권": 11.80, "상위권평균": 13.60},
    {"학년": "초등 6학년", "성별": "남", "종목": "100m", "최상위권": 11.00, "상위권평균": 12.60},
    {"학년": "초등 6학년", "성별": "여", "종목": "100m", "최상위권": 11.30, "상위권평균": 13.00},
]
benchmark_df = pd.DataFrame(BENCHMARK_RAW)

# ==========================================
# 2. 사이드바 및 로그인/회원가입 UI 구성
# ==========================================
st.sidebar.title("🏅 클럽 네비게이션")

# 로그인 상태 확인
current_id = st.session_state.logged_in_user
is_admin = False
if current_id and current_id in st.session_state.users:
    if st.session_state.users[current_id].get("role") == "admin":
        is_admin = True

# 회원가입 창이 활성화된 경우
if st.session_state.get("show_register", False):
    st.sidebar.markdown("### 📝 신규 회원 가입")
    with st.sidebar.form("register_form"):
        reg_id = st.text_input("아이디 (ID)")
        reg_pw = st.text_input("비밀번호", type="password", placeholder="영어, 숫자 조합 8자 이상")
        reg_name = st.text_input("실명 (이름)", placeholder="한글 입력 필수")
        reg_phone = st.text_input("연락처", placeholder="숫자만 입력 (예: 01012345678)")
        reg_gender = st.selectbox("성별", ["남", "여"])
        reg_birth = st.selectbox("출생 연도", list(range(2010, 2023))[::-1])
        reg_grade = st.selectbox("학년 구분", ["유치부", "초등 1학년", "초등 2학년", "초등 3학년", "초등 4학년", "초등 5학년", "초등 6학년"])
        
        btn_submit_reg = st.form_submit_button("회원가입 신청", use_container_width=True)
        btn_cancel_reg = st.form_submit_button("취소", use_container_width=True)
        
        if btn_submit_reg:
            clean_phone = re.sub(r'[^0-9]', '', reg_phone)
            pw_valid = bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', reg_pw))
            name_valid = bool(re.match(r'^[가-힣]+$', reg_name))
            phone_valid = (len(clean_phone) == 11)
            
            if not reg_id.strip():
                st.error("⚠️ 아이디를 입력해주세요.")
            elif reg_id in st.session_state.users:
                st.error("⚠️ 이미 존재하는 아이디입니다.")
            elif not pw_valid:
                st.error("⚠️ 비밀번호는 영어와 숫자를 조합하여 8글자 이상이어야 합니다.")
            elif not name_valid:
                st.error("⚠️ 실명은 무조건 한글로만 입력해야 합니다.")
            elif not phone_valid:
                st.error("⚠️ 연락처는 숫자 11자리여야 합니다.")
            else:
                st.session_state.users[reg_id] = {
                    "pw": reg_pw,
                    "name": reg_name.strip(),
                    "phone": clean_phone,
                    "gender": reg_gender,
                    "birth_year": int(reg_birth),
                    "grade": reg_grade,
                    "role": "user",
                    "status": "pending",
                    "pay_status": "미납"
                }
                save_users() # 영구 저장
                st.session_state.show_register = False
                st.success("✅ 가입 신청이 완료되었습니다! 관리자 승인 후 로그인할 수 있습니다.")
                st.rerun()
                
        if btn_cancel_reg:
            st.session_state.show_register = False
            st.rerun()

# 개인 정보 수정 창이 활성화된 경우
elif st.session_state.get("show_profile_edit", False):
    st.sidebar.markdown("### ⚙️ 내 정보 수정")
    u_info = st.session_state.users[current_id]
    with st.sidebar.form("profile_edit_form"):
        edit_pw = st.text_input("새 비밀번호", value=u_info["pw"], type="password")
        edit_name = st.text_input("실명 (이름)", value=u_info["name"])
        edit_phone = st.text_input("연락처", value=u_info.get("phone", ""))
        edit_gender = st.selectbox("성별", ["남", "여"], index=0 if u_info.get("gender") == "남" else 1)
        edit_birth = st.selectbox("출생 연도", list(range(2010, 2023))[::-1], index=list(range(2010, 2023))[::-1].index(u_info.get("birth_year", 2015)))
        calc_grade = st.selectbox("학년 구분", ["유치부", "초등 1학년", "초등 2학년", "초등 3학년", "초등 4학년", "초등 5학년", "초등 6학년"])
        
        btn_save_profile = st.form_submit_button("정보 저장", use_container_width=True)
        btn_cancel_profile = st.form_submit_button("취소", use_container_width=True)
        
        if btn_save_profile:
            clean_edit_phone = re.sub(r'[^0-9]', '', edit_phone)
            pw_valid = bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', edit_pw))
            name_valid = bool(re.match(r'^[가-힣]+$', edit_name))
            phone_valid = (len(clean_edit_phone) == 11)

            if not pw_valid:
                st.error("⚠️ 비밀번호는 영어와 숫자를 조합하여 8글자 이상이어야 합니다.")
            elif not name_valid:
                st.error("⚠️ 실명은 무조건 한글로만 입력해야 합니다.")
            elif not phone_valid:
                st.error("⚠️ 연락처는 무조건 숫자 11개여야 합니다.")
            else:
                st.session_state.users[current_id].update({
                    "pw": edit_pw,
                    "name": edit_name.strip(),
                    "phone": clean_edit_phone,
                    "gender": edit_gender,
                    "birth_year": int(edit_birth),
                    "grade": calc_grade
                })
                save_users() # 영구 저장
                st.session_state.show_profile_edit = False
                st.success("✅ 회원 정보가 성공적으로 수정되었습니다!")
                st.rerun()
                
        if btn_cancel_profile:
            st.session_state.show_profile_edit = False
            st.rerun()

# 기본 로그인 및 사용자 상태 패널
elif not current_id:
    st.sidebar.markdown("### 🔑 로그인")
    with st.sidebar.form("login_form"):
        login_id = st.text_input("아이디")
        login_pw = st.text_input("비밀번호", type="password")
        btn_login = st.form_submit_button("로그인", use_container_width=True)
        
        if btn_login:
            if login_id in st.session_state.users and st.session_state.users[login_id]["pw"] == login_pw:
                user_status = st.session_state.users[login_id].get("status", "approved")
                if user_status == "pending" and login_id != "admin":
                    st.sidebar.warning("⏳ 관리자 승인 대기 중인 계정입니다.")
                else:
                    st.session_state.logged_in_user = login_id
                    st.success("로그인 성공!")
                    st.rerun()
            else:
                st.sidebar.error("⚠️ 아이디 또는 비밀번호가 올바르지 않습니다.")
                
    if st.sidebar.button("📝 회원가입 하기", use_container_width=True):
        st.session_state.show_register = True
        st.rerun()

else:
    user_data = st.session_state.users[current_id]
    st.sidebar.markdown(f"👤 **{user_data['name']}**님 환영합니다!")
    if is_admin:
        st.sidebar.markdown("🛡️ **[권한: 최고 관리자]**")
    else:
        st.sidebar.markdown(f"🏷️ 학년: {user_data.get('grade', '-')}")
        st.sidebar.markdown(f"💳 학원비: **{user_data.get('pay_status', '미납')}**")
        
    if st.sidebar.button("⚙️ 내 정보 수정", use_container_width=True):
        st.session_state.show_profile_edit = True
        st.rerun()
        
    if st.sidebar.button("로그아웃", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

st.sidebar.write("---")
main_menu = st.sidebar.radio(
    "메뉴 선택",
    ["1. 기록 측정 및 랭킹", "2. 대회 사진첩", "3. 건의사항", "4. 👥 회원 승인 및 관리 (관리자 전용)"]
)

# 대회 사진첩 선택을 위한 사이드바 확장 요소
selected_event = None
if main_menu == "2. 대회 사진첩":
    st.sidebar.write("---")
    st.sidebar.markdown("### 📂 대회 폴더 선택")
    if st.session_state.event_folders:
        selected_event = st.sidebar.selectbox("조회할 대회 선택", st.session_state.event_folders)

# ==========================================
# 3. 메인 콘텐츠 영역 (메뉴별 기능 구현)
# ==========================================

if main_menu == "1. 기록 측정 및 랭킹":
    st.title("⏱️ 클럽원 랩타임 기록 측정 및 랭킹 시스템")
    st.write("우리 클럽 선수들의 종목별 기록을 측정하고 전국 기준 데이터와 비교해 보세요!")
    st.write("---")
    
    created_tabs = st.tabs(["⏱️ 개인 기록 측정", "📊 전체 랭킹 조회", "📚 기준 기록표"])
    
    with created_tabs[0]:
        st.markdown("### 🚀 실시간 랩타임 기록 입력")
        if not st.session_state.logged_in_user:
            st.warning("🔒 기록을 측정하고 등록하려면 로그인이 필요합니다.")
        else:
            with st.form("record_form", clear_on_submit=True):
                rec_col1, rec_col2 = st.columns(2)
                with rec_col1:
                    target_member_id = st.selectbox(
                        "측정 대상 회원", 
                        [current_id] if not is_admin else list(st.session_state.users.keys()),
                        format_func=lambda x: f"{st.session_state.users[x]['name']} ({x})"
                    )
                with rec_col2:
                    rec_event = st.selectbox("종목 선택", ["100m", "200m", "300m", "500m", "1,000m", "1,500m"])
                
                rec_time = st.number_input("측정 기록 (초 단위, 예: 14.52)", min_value=1.0, max_value=300.0, step=0.01)
                
                btn_save_rec = st.form_submit_button("💾 기록 저장하기", use_container_width=True)
                if btn_save_rec:
                    m_data = st.session_state.users[target_member_id]
                    new_row = pd.DataFrame([{
                        "ID": target_member_id,
                        "이름": m_data["name"],
                        "학년": m_data.get("grade", "초등 1학년"),
                        "성별": m_data.get("gender", "남"),
                        "종목": rec_event,
                        "기록": float(rec_time),
                        "입력 날짜": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }])
                    st.session_state.lab_records = pd.concat([st.session_state.lab_records, new_row], ignore_index=True)
                    save_records() # 영구 저장
                    st.success(f"✅ [{m_data['name']}] 선수의 {rec_event} 기록({rec_time}초)이 성공적으로 저장되었습니다!")
                    st.rerun()

    with created_tabs[1]:
        st.markdown("### 📊 클럽 종합 랭킹 보드")
        if not st.session_state.lab_records.empty:
            display_records = st.session_state.lab_records.copy()
            
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                g_f = st.selectbox("학년 필터", ["전체"] + list(display_records["학년"].unique()))
            with f_col2:
                s_f = st.selectbox("성별 필터", ["전체"] + list(display_records["성별"].unique()))
                
            table_df = display_records.copy()
            if g_f != "전체":
                table_df = table_df[table_df["학년"] == g_f]
            if s_f != "전체":
                table_df = table_df[table_df["성별"] == s_f]
            st.dataframe(table_df, use_container_width=True)
            
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
                    save_records() # 영구 저장
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
                        save_folders()
                        save_gallery()
                        save_winners()
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
                            st.session_state.gallery_photos[clean_rename] = st.session_state.gallery_photos.pop(target_rename, [])
                            if target_rename in st.session_state.competition_winners:
                                st.session_state.competition_winners[clean_rename] = st.session_state.competition_winners.pop(target_rename)
                            else:
                                st.session_state.competition_winners[clean_rename] = []
                            save_folders()
                            save_gallery()
                            save_winners()
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
                        save_folders()
                        save_gallery()
                        save_winners()
                        st.success(f"🗑️ [{target_del}] 폴더가 삭제되었습니다.")
                        st.rerun()
                else:
                    st.info("삭제할 폴더가 없습니다.")
        st.write("---")

    if not selected_event:
        st.info("📂 왼쪽 사이드바에서 조회할 대회 폴더를 선택해 주세요.")
        st.stop()

    st.subheader(f"📂 현재 선택된 대회: {selected_event}")

    folder_tabs = st.tabs(["📸 대회 현장 사진첩", "🏆 대회 입상자 명단"])

    with folder_tabs[0]:
        st.markdown("#### 📤 사진 등록하기")
        uploaded_files = st.file_uploader(f"[{selected_event}] 폴더에 사진 추가", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key=f"uploader_{selected_event}")
        if uploaded_files:
            if st.button("선택한 사진 등록", key=f"btn_upload_{selected_event}"):
                uploader_name = st.session_state.users[current_id]["name"]
                if selected_event not in st.session_state.gallery_photos:
                    st.session_state.gallery_photos[selected_event] = []
                for uploaded_file in uploaded_files:
                    st.session_state.gallery_photos[selected_event].append({
                        "bytes": uploaded_file.getvalue(),
                        "filename": uploaded_file.name,
                        "uploader": uploader_name,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                save_gallery() # 영구 저장
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
                            save_gallery() # 영구 저장
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
                        if selected_event not in st.session_state.competition_winners:
                            st.session_state.competition_winners[selected_event] = []
                        st.session_state.competition_winners[selected_event].append({
                            "이름": w_name,
                            "순위": w_award,
                            "종목": w_event,
                            "등록일": datetime.now().strftime("%Y-%m-%d")
                        })
                        save_winners() # 영구 저장
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
                    save_winners() # 영구 저장
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
                            save_suggestions() # 영구 저장
                            st.success("피드백이 저장되었습니다.")
                            st.rerun()
                    with c_btn2:
                        if st.button(f"🗑️ 건의사항 삭제", key=f"del_sug_{idx}", use_container_width=True):
                            st.session_state.suggestions.pop(idx)
                            save_suggestions() # 영구 저장
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
                            save_suggestions() # 영구 저장
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
    pending_users = [uid for uid, udata in st.session_state.users.items() if udata.get("status") == "pending"]
    
    if pending_users:
        p_col1, p_col2 = st.columns([3, 1])
        selected_p_user = p_col1.selectbox("승인할 회원을 선택하세요:", pending_users, format_func=lambda x: f"ID: {x} | 이름: {st.session_state.users[x]['name']} ({st.session_state.users[x].get('gender', '-')}/{st.session_state.users[x].get('grade', '-')}) | 연락처: {st.session_state.users[x].get('phone')}")
        if p_col2.button("✅ 선택 회원 승인", use_container_width=True):
            st.session_state.users[selected_p_user]["status"] = "approved"
            save_users() # 영구 저장
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
                save_users() # 영구 저장
                st.success(f"✅ [{m_user_info['name']}] 회원의 학원비 납부 상태가 [{new_pay_status}](으)로 변경되었습니다.")
                st.rerun()
    else:
        st.info("등록된 승인 회원이 없습니다.")

    st.write("---")
    
    st.markdown("### 🗑️ 3. 회원 강제 탈퇴 및 삭제 (관리자 전용)")
    all_registered_users = [uid for uid, udata in st.session_state.users.items() if udata.get("role") != "admin"]
    
    if all_registered_users:
        selected_del_user = st.selectbox(
            "삭제할 회원을 선택하세요:", 
            all_registered_users, 
            format_func=lambda x: f"ID: {x} | 이름: {st.session_state.users[x]['name']} ({st.session_state.users[x].get('grade', '-')}) | 상태: {st.session_state.users[x].get('status')}"
        )
        
        if st.button("⚠️ 선택한 회원 강제 탈퇴 (계정 삭제)", use_container_width=True):
            del_name = st.session_state.users[selected_del_user]["name"]
            del st.session_state.users[selected_del_user]
            save_users() # 영구 저장
            
            if not st.session_state.lab_records.empty:
                st.session_state.lab_records = st.session_state.lab_records[st.session_state.lab_records["ID"] != selected_del_user].reset_index(drop=True)
                save_records() # 영구 저장
            
            st.success(f"🗑️ [{del_name}] 회원의 계정 및 관련 데이터가 영구 삭제되었습니다.")
            st.rerun()
    else:
        st.info("삭제할 수 있는 일반 회원이 없습니다.")
