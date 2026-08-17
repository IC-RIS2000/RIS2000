from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="Rising Inline Club", page_icon="⛸️", layout="wide"
)

# ---------------------------------------------------------
# 1. Session State 초기화
# ---------------------------------------------------------
if "users" not in st.session_state:
  st.session_state.users = {
      "admin": {
          "name": "관리자",
          "password": "admin1234",
          "role": "admin",
          "status": "approved",
          "gender": "-",
          "grade": "-",
          "phone": "010-0000-0000",
          "pay_status": "-",
      }
  }

if "logged_in_user" not in st.session_state:
  st.session_state.logged_in_user = None

if "benchmark_db" not in st.session_state:
  st.session_state.benchmark_db = {
      "초등학교 1학년": {
          "100m": {"최정상": 15.0, "정상": 17.0},
          "200m": {"최정상": 31.0, "정상": 35.0},
      },
      "초등학교 2학년": {
          "100m": {"최정상": 14.5, "정상": 16.5},
          "200m": {"최정상": 29.5, "정상": 33.0},
          "300m": {"최정상": 43.0, "정상": 48.0},
      },
      "초등학교 3학년": {
          "100m": {"최정상": 14.0, "정상": 16.0},
          "200m": {"최정상": 28.0, "정상": 31.0},
          "300m": {"최정상": 41.0, "정상": 46.0},
          "500m": {"최정상": 55.0, "정상": 62.0},
      },
      "초등학교 4학년": {
          "100m": {"최정상": 13.5, "정상": 15.2},
          "200m": {"최정상": 26.5, "정상": 29.5},
          "300m": {"최정상": 39.0, "정상": 43.5},
          "500m": {"최정상": 52.0, "정상": 59.0},
      },
      "초등학교 5학년": {
          "100m": {"최정상": 13.0, "정상": 14.5},
          "200m": {"최정상": 25.0, "정상": 28.0},
          "300m": {"최정상": 37.0, "정상": 41.0},
          "500m": {"최정상": 50.0, "정상": 56.0},
          "1,000m": {"최정상": 110.0, "정상": 125.0},
      },
      "초등학교 6학년": {
          "100m": {"최정상": 12.5, "정상": 14.0},
          "200m": {"최정상": 24.0, "정상": 27.0},
          "300m": {"최정상": 35.0, "정상": 39.0},
          "500m": {"최정상": 48.0, "정상": 54.0},
          "1,000m": {"최정상": 105.0, "정상": 118.0},
      },
      "중/고등부 또는 성인": {
          "100m": {"최정상": 12.0, "정상": 13.5},
          "300m": {"최정상": 34.0, "정상": 38.0},
          "500m": {"최정상": 47.0, "정상": 52.0},
          "1,000m": {"최정상": 102.0, "정상": 115.0},
          "1,500m": {"최정상": 170.0, "정상": 190.0},
      },
  }

if "lap_records" not in st.session_state:
  st.session_state.lap_records = {}

if "event_photos" not in st.session_state:
  st.session_state.event_photos = {}

if "competition_winners" not in st.session_state:
  st.session_state.competition_winners = {}

if "suggestions" not in st.session_state:
  st.session_state.suggestions = []


# ---------------------------------------------------------
# 2. 사이드바 (로그인 및 네비게이션)
# ---------------------------------------------------------
st.sidebar.title("⛸️ Rising Inline Club")
st.sidebar.write("클럽 전용 기록 관리 시스템")
st.sidebar.write("---")

if st.session_state.logged_in_user is None:
  st.sidebar.subheader("🔑 로그인 / 회원가입")
  auth_mode = st.sidebar.radio(
      "모드 선택", ["로그인", "회원가입"], key="auth_mode_radio"
  )

  if auth_mode == "로그인":
    with st.sidebar.form("login_form"):
      login_id = st.text_input("아이디")
      login_pw = st.text_input("비밀번호", type="password")
      btn_login = st.form_submit_button("로그인", use_container_width=True)

      if btn_login:
        user_info = st.session_state.users.get(login_id)
        if user_info and user_info["password"] == login_pw:
          if user_info["status"] == "approved":
            st.session_state.logged_in_user = login_id
            st.success(f"환영합니다, {user_info['name']}님!")
            st.rerun()
          else:
            st.warning("⏳ 가입 승인 대기 중입니다.")
        else:
          st.error("아이디 또는 비밀번호가 잘못되었습니다.")
  else:
    with st.sidebar.form("signup_form"):
      new_id = st.text_input("사용할 아이디")
      new_pw = st.text_input("비밀번호", type="password")
      new_name = st.text_input("이름")
      new_gender = st.selectbox("성별", ["남", "여"])

      current_year = datetime.now().year
      birth_years = list(range(current_year - 22, current_year - 5, 1))
      selected_birth_year = st.selectbox(
          "출생년도", birth_years, index=len(birth_years) - 9
      )

      age_diff = current_year - selected_birth_year
      grade_num = age_diff - 7

      if grade_num == 1:
        auto_grade = "초등학교 1학년"
      elif grade_num == 2:
        auto_grade = "초등학교 2학년"
      elif grade_num == 3:
        auto_grade = "초등학교 3학년"
      elif grade_num == 4:
        auto_grade = "초등학교 4학년"
      elif grade_num == 5:
        auto_grade = "초등학교 5학년"
      elif grade_num == 6:
        auto_grade = "초등학교 6학년"
      elif grade_num > 6:
        auto_grade = "중/고등부 또는 성인"
      else:
        auto_grade = "초등학교 1학년"

      st.info(f"📚 자동 산출된 학년: **{auto_grade}**")
      new_phone = st.text_input("연락처 (예: 010-1234-5678)")
      btn_signup = st.form_submit_button("가입 신청", use_container_width=True)

      if btn_signup:
        if not new_id or not new_pw or not new_name:
          st.warning("아이디, 비밀번호, 이름은 필수 입력 항목입니다.")
        elif new_id in st.session_state.users:
          st.warning("이미 존재하는 아이디입니다.")
        else:
          st.session_state.users[new_id] = {
              "name": new_name,
              "password": new_pw,
              "role": "member",
              "status": "pending",
              "gender": new_gender,
              "grade": auto_grade,
              "phone": new_phone,
              "pay_status": "미납",
          }
          st.success("🎉 가입 신청이 완료되었습니다.")
else:
  current_id = st.session_state.logged_in_user
  current_user = st.session_state.users.get(current_id, {})

  # 3항 연산자를 f-string 밖으로 분리하여 SyntaxError 해결
  role_str = "관리자" if current_user.get("role") == "admin" else "회원"

  st.sidebar.markdown(
      f"👤 **{current_user.get('name')}**님 환영합니다! ({role_str})"
  )
  if st.sidebar.button("로그아웃", use_container_width=True):
    st.session_state.logged_in_user = None
    st.rerun()

st.sidebar.write("---")
main_menu = st.sidebar.radio(
    "메인 메뉴",
    [
        "1. 📊 랩타임 및 기록실",
        "2. 🏆 대회 정보 및 입상자",
        "3. 💡 건의사항",
        "4. 👥 회원 승인 및 관리 (관리자 전용)",
    ],
)

current_id = st.session_state.logged_in_user
is_admin = (
    current_id
    and st.session_state.users.get(current_id, {}).get("role") == "admin"
)


# ---------------------------------------------------------
# 3. 메인 메뉴별 화면 구현
# ---------------------------------------------------------

# --- 메뉴 1: 랩타임 및 기록실 ---
if main_menu == "1. 📊 랩타임 및 기록실":
  st.title("📊 랩타임 측정 및 개인별 비교 기록실")
  st.write(
      "학생 선택 시 정확한 학년 정보가 연동되며, 해당 학년의 '최정상' 및"
      " '정상' 기준과 본인 기록을 스크롤 없는 한눈에 보는 꺾은선형 그래프로"
      " 비교합니다."
  )
  st.write("---")

  tab_lap1, tab_lap2, tab_lap3 = st.tabs([
      "⏱️ 날짜별 랩타임 측정 및 등록",
      "👤 개인별 기록 조회 및 비교",
      "📈 벤치마크 기준 관리",
  ])

  # [탭 1] 날짜별 랩타임 측정 및 등록
  with tab_lap1:
    st.subheader("⏱️ 훈련 랩타임 신규 등록")
    approved_members = [
        udata["name"]
        for uid, udata in st.session_state.users.items()
        if udata.get("status") == "approved" and udata.get("role") != "admin"
    ]
    if not approved_members:
      approved_members = ["등록된 회원 없음"]

    with st.form("lap_record_form", clear_on_submit=True):
      r_col1, r_col2, r_col3, r_col4 = st.columns(4)
      with r_col1:
        sel_member = st.selectbox("선수 선택", approved_members)
      with r_col2:
        sel_date = st.date_input("측정 일자", value=datetime.today())
      with r_col3:
        sel_distance = st.selectbox(
            "측정 종목", ["100m", "200m", "300m", "500m", "1,000m", "1,500m"]
        )
      with r_col4:
        sel_sec = st.number_input(
            "기록 (초 단위, 예: 45.2)", min_value=0.0, format="%.2f"
        )

      btn_save_lap = st.form_submit_button(
          "💾 랩타임 기록 저장", use_container_width=True
      )
      if btn_save_lap:
        if sel_member != "등록된 회원 없음" and sel_sec > 0:
          if sel_member not in st.session_state.lap_records:
            st.session_state.lap_records[sel_member] = []

          st.session_state.lap_records[sel_member].append({
              "날짜": sel_date.strftime("%Y-%m-%d"),
              "종목": sel_distance,
              "기록(초)": sel_sec,
          })
          st.success(
              f"✅ [{sel_member}] 선수의 {sel_distance} 기록 ({sel_sec}초)이"
              " 저장되었습니다!"
          )
          st.rerun()
        else:
          st.warning("⚠️ 올바른 선수 이름과 0보다 큰 기록을 입력해 주세요.")

  # [탭 2] 개인별 기록 조회 및 최정상/정상 비교 및 고정형 꺾은선형 그래프
  with tab_lap2:
    st.subheader("👤 개인별 기록 조회 및 학년별 맞춤 비교")

    if st.session_state.lap_records:
      all_recorded_members = list(st.session_state.lap_records.keys())
      view_member = st.selectbox(
          "조회할 학생(선수)을 선택하세요:", all_recorded_members
      )

      member_grade = "초등학교 5학년"
      for uid, udata in st.session_state.users.items():
        if udata.get("name") == view_member:
          member_grade = udata.get("grade", "초등학교 5학년")
          break

      st.info(
          f"ℹ️ **[{view_member}]** 선수의 소속 학년: **{member_grade}**"
      )

      member_data = st.session_state.lap_records[view_member]
      df_member = pd.DataFrame(member_data)

      st.markdown(f"### 📋 [{view_member}] 선수의 전체 훈련 기록")
      st.dataframe(df_member, use_container_width=True)

      st.write("---")
      st.markdown(
          f"### 🔍 [{member_grade}] '최정상'·'정상' 기준 비교 및 성장 추이 그래프"
      )

      unique_events_in_rec = df_member["종목"].unique().tolist()
      comp_event = st.selectbox(
          "비교 및 그래프로 확인할 종목:", unique_events_in_rec
      )

      sub_df = df_member[df_member["종목"] == comp_event].copy()
      if not sub_df.empty:
        my_latest_record = sub_df.iloc[-1]["기록(초)"]
        my_best_record = sub_df["기록(초)"].min()

        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.metric(label="내 최근 기록", value=f"{my_latest_record} 초")
        col_c2.metric(label="내 개인 최고 기록(PB)", value=f"{my_best_record} 초")

        grade_bm = st.session_state.benchmark_db.get(member_grade, {})
        event_bm = grade_bm.get(comp_event, {"최정상": 0, "정상": 0})
        top_record = event_bm.get("최정상", 0)
        normal_record = event_bm.get("정상", 0)

        col_c3.markdown(
            f"**🏆 [{member_grade}] {comp_event} 기준**<br>"
            f"- 최정상: **{top_record}초**<br>"
            f"- 정상: **{normal_record}초**",
            unsafe_allow_html=True,
        )

        if top_record > 0:
          if my_best_record <= top_record:
            st.success(
                "🌟 대단합니다! 해당 학년 '최정상' 기준 기록을 달성했습니다!"
            )
          elif my_best_record <= normal_record:
            st.info(
                "👍 해당 학년 '정상' 수준의 훌륭한 기록입니다! 최정상 도약을"
                " 향해 화이팅!"
            )
          else:
            st.warning(
                "💪 꾸준한 훈련을 통해 정상 기록 진입을 목표로 도전해 봅시다!"
            )
        else:
          st.info(
              "💡 해당 종목의 학년별 벤치마크 기준이 아직 설정되지 않았습니다."
          )

        st.write("")
        st.markdown(
            f"#### 📈 [{view_member}] 선수의 [{comp_event}] 성장 꺾은선형"
            " 그래프"
        )

        # Plotly를 이용해 스크롤/커서 없이 화면 폭에 맞춘 깔끔한 꺾은선형 그래프 구현
        fig = px.line(
            sub_df,
            x="날짜",
            y="기록(초)",
            markers=True,
            title=f"[{view_member}] {comp_event} 기록 추이",
        )

        # 기준선 추가 (최정상, 정상)
        if top_record > 0:
          fig.add_hline(
              y=top_record,
              line_dash="dash",
              line_color="red",
              annotation_text=f"최정상 기준 ({top_record}초)",
              annotation_position="bottom right",
          )
          fig.add_hline(
              y=normal_record,
              line_dash="dash",
              line_color="orange",
              annotation_text=f"정상 기준 ({normal_record}초)",
              annotation_position="bottom right",
          )

        # 레이아웃 고정 (스크롤바 및 커서 방지, 한 페이지에 꽉 차게 고정)
        fig.update_layout(
            xaxis=dict(type="category"),  # 날짜를 고정 간격 카테고리로 처리
            margin=dict(l=40, r=40, t=40, b=40),
            height=400,
            autosize=True,
        )

        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "※ 모든 데이터가 스크롤 없이 한 화면에 고정되어 렌더링됩니다."
        )

      if is_admin:
        st.write("---")
        if st.button(f"🗑️ [{view_member}] 선수의 전체 기록 초기화"):
          del st.session_state.lap_records[view_member]
          st.success(f"[{view_member}] 선수의 모든 기록이 삭제되었습니다.")
          st.rerun()
    else:
      st.info("💡 아직 저장된 랩타임 기록이 없습니다.")

  # [탭 3] 벤치마크 기준 관리
  with tab_lap3:
    st.subheader("📈 학년별·종목별 벤치마크 기준 관리")
    bm_list = []
    for grp, evs in st.session_state.benchmark_db.items():
      for ev, vals in evs.items():
        bm_list.append({
            "학년/그룹": grp,
            "종목": ev,
            "최정상(초)": vals["최정상"],
            "정상(초)": vals["정상"],
        })
    st.dataframe(pd.DataFrame(bm_list), use_container_width=True)

    if is_admin:
      st.write("---")
      st.markdown("#### ➕ 벤치마크 기준 수정/등록 (관리자 전용)")
      with st.form("bm_edit_form"):
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
          b_grp = st.selectbox(
              "학년/그룹",
              [
                  "초등학교 1학년",
                  "초등학교 2학년",
                  "초등학교 3학년",
                  "초등학교 4학년",
                  "초등학교 5학년",
                  "초등학교 6학년",
                  "중/고등부 또는 성인",
              ],
          )
        with b_col2:
          b_ev = st.selectbox(
              "종목", ["100m", "200m", "300m", "500m", "1,000m", "1,500m"]
          )
        with b_col3:
          b_top = st.number_input(
              "최정상 기준 (초)", value=13.5, format="%.1f"
          )
        with b_col4:
          b_normal = st.number_input("정상 기준 (초)", value=15.0, format="%.1f")

        btn_bm_save = st.form_submit_button(
            "기준 기록 업데이트", use_container_width=True
        )
        if btn_bm_save:
          if b_grp not in st.session_state.benchmark_db:
            st.session_state.benchmark_db[b_grp] = {}
          st.session_state.benchmark_db[b_grp][b_ev] = {
              "최정상": b_top,
              "정상": b_normal,
          }
          st.success("✅ 벤치마크 기준이 업데이트되었습니다!")
          st.rerun()


# --- 메뉴 2: 대회 정보 및 입상자 ---
elif main_menu == "2. 🏆 대회 정보 및 입상자":
  st.title("🏆 대회 정보 및 입상자 명단")
  events_list = [
      "2026년 전국 인라인 스케이트 대회",
      "제1회 클럽 자체 평가전",
      "2025년 하반기 시합",
  ]
  selected_event = st.selectbox("조회할 대회를 선택하세요:", events_list)

  if selected_event not in st.session_state.competition_winners:
    st.session_state.competition_winners[selected_event] = []

  folder_tabs = st.tabs(["📁 대회 개요 및 사진", "🏆 입상자 명단"])

  with folder_tabs[0]:
    st.markdown(f"### 📌 [{selected_event}] 대회 개요")
    if is_admin:
      uploaded_photo = st.file_uploader(
          "대회 현장 사진 선택",
          type=["jpg", "jpeg", "png"],
          key=f"photo_up_{selected_event}",
      )
      if uploaded_photo is not None:
        if selected_event not in st.session_state.event_photos:
          st.session_state.event_photos[selected_event] = []
        st.session_state.event_photos[selected_event].append(uploaded_photo)
        st.success("사진이 업로드되었습니다!")

    photos = st.session_state.event_photos.get(selected_event, [])
    if photos:
      p_cols = st.columns(3)
      for idx, p in enumerate(photos):
        with p_cols[idx % 3]:
          st.image(p, caption=f"현장 사진 {idx+1}", use_container_width=True)
    else:
      st.info("💡 등록된 현장 사진이 없습니다.")

  with folder_tabs[1]:
    winners = st.session_state.competition_winners.get(selected_event, [])
    if winners:
      df_winners = pd.DataFrame(winners)
      st.dataframe(df_winners, use_container_width=True)
    else:
      st.info("💡 아직 등록된 입상자 정보가 없습니다.")

    if is_admin:
      all_club_members = [
          udata["name"]
          for uid, udata in st.session_state.users.items()
          if udata.get("name")
      ]
      if not all_club_members:
        all_club_members = ["등록된 회원 없음"]

      with st.form(f"winner_add_form_{selected_event}", clear_on_submit=True):
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
          w_name = st.selectbox("선수 이름", all_club_members)
        with w_col2:
          w_award = st.selectbox(
              "순위",
              [
                  "1위 (금메달)",
                  "2위 (은메달)",
                  "3위 (동메달)",
                  "최우수상",
                  "우수상",
                  "장려상",
                  "입상",
              ],
          )
        with w_col3:
          w_event = st.selectbox(
              "종목",
              ["100m", "200m", "300m", "500m", "1,000m", "1,500m"],
          )

        if st.form_submit_button(
            "🌟 입상자 등록하기", use_container_width=True
        ):
          if w_name != "등록된 회원 없음":
            st.session_state.competition_winners[selected_event].append({
                "이름": w_name,
                "순위": w_award,
                "종목": w_event,
                "등록일": datetime.now().strftime("%Y-%m-%d"),
            })
            st.success("등록되었습니다!")
            st.rerun()


# --- 메뉴 3: 건의사항 ---
elif main_menu == "3. 💡 건의사항":
  st.title("💡 무기명 건의사항함")
  if is_admin:
    if st.session_state.suggestions:
      for idx, item in enumerate(st.session_state.suggestions):
        with st.expander(f"📌 [{idx+1}] {item['title']}"):
          st.write(item["content"])
          fb_text = st.text_area(
              "💬 피드백", value=item.get("feedback", ""), key=f"fb_{idx}"
          )
          if st.button("💾 저장", key=f"save_fb_{idx}"):
            st.session_state.suggestions[idx]["feedback"] = fb_text
            st.rerun()
    else:
      st.info("건의사항이 없습니다.")
  else:
    if st.session_state.logged_in_user:
      with st.form("sug_form", clear_on_submit=True):
        s_title = st.text_input("제목")
        s_content = st.text_area("내용")
        if st.form_submit_button("제출"):
          if s_title and s_content:
            st.session_state.suggestions.append(
                {"title": s_title, "content": s_content, "feedback": ""}
            )
            st.success("제출되었습니다.")
    else:
      st.warning("로그인 후 이용 가능합니다.")


# --- 메뉴 4: 회원 승인 및 관리 ---
elif main_menu == "4. 👥 회원 승인 및 관리 (관리자 전용)":
  st.title("👥 회원 승인 및 관리")
  if not is_admin:
    st.stop()
  pending = [
      k
      for k, v in st.session_state.users.items()
      if v.get("status") == "pending"
  ]
  if pending:
    sel_p = st.selectbox("승인 대기 회원", pending)
    if st.button("승인"):
      st.session_state.users[sel_p]["status"] = "approved"
      st.rerun()
  else:
    st.info("승인 대기 중인 회원이 없습니다.")
