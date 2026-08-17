from datetime import datetime
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="Rising Inline Club", page_icon="⛸️", layout="wide"
)

# ---------------------------------------------------------
# 1. Session State 초기화
# ---------------------------------------------------------
if "users" not in st.session_state:
  # 관리자 기본 계정 포함 (아이디: admin / 비밀번호: admin1234)
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
  # 학년별·종목별 세부 벤치마크 기준 기록 (예시)
  st.session_state.benchmark_db = {
      "초등 저학년부": {
          "100m": {"최상위권": 14.0, "상위권": 16.0},
          "200m": {"최상위권": 28.0, "상위권": 31.0},
          "300m": {"최상위권": 41.0, "상위권": 46.0},
          "500m": {"최상위권": 55.0, "상위권": 62.0},
      },
      "초등 고학년부": {
          "100m": {"최상위권": 13.0, "상위권": 14.5},
          "200m": {"최상위권": 25.0, "상위권": 28.0},
          "300m": {"최상위권": 37.0, "상위권": 41.0},
          "500m": {"최상위권": 50.0, "상위권": 56.0},
          "1,000m": {"최상위권": 110.0, "상위권": 125.0},
      },
      "중/고등부 또는 성인": {
          "100m": {"최상위권": 12.0, "상위권": 13.5},
          "300m": {"최상위권": 34.0, "상위권": 38.0},
          "500m": {"최상위권": 47.0, "상위권": 52.0},
          "1,000m": {"최상위권": 102.0, "상위권": 115.0},
          "1,500m": {"최상위권": 170.0, "상위권": 190.0},
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

# 로그인 상태 관리
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
            st.warning(
                "⏳ 가입 승인 대기 중입니다. 관리자의 승인을 기다려주세요."
            )
        else:
          st.error("아이디 또는 비밀번호가 잘못되었습니다.")
  else:
    with st.sidebar.form("signup_form"):
      new_id = st.text_input("사용할 아이디")
      new_pw = st.text_input("비밀번호", type="password")
      new_name = st.text_input("이름")
      new_gender = st.selectbox("성별", ["남", "여"])

      current_year = datetime.now().year
      birth_years = list(range(current_year - 25, current_year - 3, 1))
      selected_birth_year = st.selectbox(
          "출생년도", birth_years, index=len(birth_years) - 10
      )

      age_diff = current_year - selected_birth_year
      school_grade_num = age_diff - 6
      if 1 <= school_grade_num <= 3:
        auto_grade = "초등 저학년부"
      elif 4 <= school_grade_num <= 6:
        auto_grade = "초등 고학년부"
      elif school_grade_num > 6:
        auto_grade = "중/고등부 또는 성인"
      else:
        auto_grade = "초등 저학년부"

      st.info(f"📚 자동 지정 분류: **{auto_grade}**")
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
          st.success(
              "🎉 가입 신청이 완료되었습니다. 관리자 승인 후 이용 가능합니다."
          )
else:
  current_id = st.session_state.logged_in_user
  current_user = st.session_state.users.get(current_id, {})
  st.sidebar.markdown(
      f"👤 **{current_user.get('name')}**님 환영합니다! ({'관리자' if current_user.get('role') == 'admin' else '회원'})"
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
      "학생 이름을 선택하면 해당 학생의 학년 정보가 자동으로 연동되며, 학년별"
      " 최상위·상위권 선수 기준과 비교 및 성장 추이 그래프를 확인할 수"
      " 있습니다."
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
          st.warning(
              "⚠️ 올바른 선수 이름과 0보다 큰 기록(초)을 입력해 주세요."
          )

  # [탭 2] 개인별 기록 조회 및 최상위/상위권 비교 (복원된 핵심 기능)
  with tab_lap2:
    st.subheader("👤 개인별 기록 조회 및 학년별 상위권 비교")

    if st.session_state.lap_records:
      all_recorded_members = list(st.session_state.lap_records.keys())
      view_member = st.selectbox(
          "조회할 학생(선수)을 선택하세요:", all_recorded_members
      )

      # 선택한 학생의 학년 정보 찾아내기
      member_grade = "초등 고학년부"  # 기본값
      for uid, udata in st.session_state.users.items():
        if udata.get("name") == view_member:
          member_grade = udata.get("grade", "초등 고학년부")
          break

      st.info(
          f"ℹ️ **[{view_member}]** 선수의 소속 그룹(학년): **{member_grade}**"
      )

      member_data = st.session_state.lap_records[view_member]
      df_member = pd.DataFrame(member_data)

      st.markdown(f"### 📋 [{view_member}] 선수의 전체 훈련 기록")
      st.dataframe(df_member, use_container_width=True)

      st.write("---")
      st.markdown(
          f"### 🔍 [{member_grade}] 최상위권·상위권 기준 비교 및 추이 그래프"
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

        # 해당 학년 그룹의 벤치마크 기준 가져오기
        grade_bm = st.session_state.benchmark_db.get(member_grade, {})
        event_bm = grade_bm.get(comp_event, {"최상위권": 0, "상위권": 0})
        top_record = event_bm.get("최상위권", 0)
        high_record = event_bm.get("상위권", 0)

        col_c3.markdown(
            f"**🏆 [{member_grade}] {comp_event} 기준**<br>"
            f"- 최상위권: **{top_record}초**<br>"
            f"- 상위권: **{high_record}초**",
            unsafe_allow_html=True,
        )

        if top_record > 0:
          if my_best_record <= top_record:
            st.success(
                "🌟 대단합니다! 해당 학년 전국 최상위권 기록을 달성했습니다!"
            )
          elif my_best_record <= high_record:
            st.info(
                "👍 해당 학년 상위권 수준의 훌륭한 기록입니다! 최상위권 도약을"
                " 향해 화이팅!"
            )
          else:
            st.warning(
                "💪 꾸준한 훈련을 통해 상위권 기록 진입을 목표로 도전해 봅시다!"
            )
        else:
          st.info(
              "💡 해당 종목의 학년별 벤치마크 기준이 아직 설정되지 않았습니다."
          )

        st.write("")
        st.markdown(f"#### 📈 [{view_member}] 선수의 [{comp_event}] 기록 추이")
        chart_df = sub_df.set_index("날짜")[["기록(초)"]]
        st.line_chart(chart_df)

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
    st.write("학년 그룹별 종목별 최상위권 및 상위권 기준 기록입니다.")

    bm_list = []
    for grp, evs in st.session_state.benchmark_db.items():
      for ev, vals in evs.items():
        bm_list.append({
            "그룹/학년": grp,
            "종목": ev,
            "최상위권(초)": vals["최상위권"],
            "상위권(초)": vals["상위권"],
        })
    st.dataframe(pd.DataFrame(bm_list), use_container_width=True)

    if is_admin:
      st.write("---")
      st.markdown("#### ➕ 벤치마크 기준 수정/등록 (관리자 전용)")
      with st.form("bm_edit_form"):
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        with b_col1:
          b_grp = st.selectbox(
              "그룹/학년",
              ["초등 저학년부", "초등 고학년부", "중/고등부 또는 성인"],
          )
        with b_col2:
          b_ev = st.selectbox(
              "종목", ["100m", "200m", "300m", "500m", "1,000m", "1,500m"]
          )
        with b_col3:
          b_top = st.number_input(
              "최상위권 기준 (초)", value=13.5, format="%.1f"
          )
        with b_col4:
          b_high = st.number_input("상위권 기준 (초)", value=15.0, format="%.1f")

        btn_bm_save = st.form_submit_button(
            "기준 기록 업데이트", use_container_width=True
        )
        if btn_bm_save:
          if b_grp not in st.session_state.benchmark_db:
            st.session_state.benchmark_db[b_grp] = {}
          st.session_state.benchmark_db[b_grp][b_ev] = {
              "최상위권": b_top,
              "상위권": b_high,
          }
          st.success(
              f"✅ [{b_grp}] [{b_ev}] 벤치마크 기준이 업데이트되었습니다!"
          )
          st.rerun()


# --- 메뉴 2: 대회 정보 및 입상자 ---
elif main_menu == "2. 🏆 대회 정보 및 입상자":
  st.title("🏆 대회 정보 및 입상자 명단")
  st.write(
      "클럽 선수들이 출전한 대회 정보와 빛나는 입상 내역을 확인할 수 있습니다."
  )
  st.write("---")

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
    st.write("대회 일정, 장소, 출전 선수 안내 및 현장 포토 갤러리입니다.")

    if is_admin:
      st.write("---")
      st.markdown("#### 📷 현장 사진 업로드 (관리자 전용)")
      uploaded_photo = st.file_uploader(
          "대회 현장 사진 선택",
          type=["jpg", "jpeg", "png"],
          key=f"photo_up_{selected_event}",
      )
      if uploaded_photo is not None:
        if selected_event not in st.session_state.event_photos:
          st.session_state.event_photos[selected_event] = []
        st.session_state.event_photos[selected_event].append(uploaded_photo)
        st.success("사진이 성공적으로 업로드되었습니다!")

    photos = st.session_state.event_photos.get(selected_event, [])
    if photos:
      st.write("---")
      st.markdown("#### 🖼️ 대회 포토 갤러리")
      p_cols = st.columns(3)
      for idx, p in enumerate(photos):
        with p_cols[idx % 3]:
          st.image(p, caption=f"현장 사진 {idx+1}", use_container_width=True)
    else:
      st.info("💡 등록된 현장 사진이 없습니다.")

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
            "종목": w.get("종목", w.get("종목 및 부서", "-")),
            "등록일": w.get("등록일", "-"),
        })

      df_winners = pd.DataFrame(display_winners)
      st.dataframe(df_winners, use_container_width=True)
    else:
      st.info("💡 아직 등록된 입상자 정보가 없습니다.")

    if is_admin:
      st.write("---")
      st.markdown("#### ➕ 입상자 등록 (관리자 전용)")

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
              [
                  "100m",
                  "200m",
                  "300m",
                  "500m",
                  "1,000m",
                  "1,500m",
                  "초등 저학년부 500m",
                  "초등 고학년부 1,000m",
              ],
          )

        btn_add_winner = st.form_submit_button(
            "🌟 입상자 등록하기", use_container_width=True
        )
        if btn_add_winner:
          if w_name != "등록된 회원 없음":
            st.session_state.competition_winners[selected_event].append({
                "이름": w_name,
                "순위": w_award,
                "종목": w_event,
                "등록일": datetime.now().strftime("%Y-%m-%d"),
            })
            st.success(
                f"✅ [{w_name}] 선수의 입상 정보가 성공적으로 등록되었습니다!"
            )
            st.rerun()
          else:
            st.warning("⚠️ 등록된 선수가 없습니다.")

      if winners:
        st.write("")
        st.markdown("#### 🗑️ 입상자 삭제 (관리자 전용)")
        del_win_idx = st.selectbox(
            "삭제할 입상자를 선택하세요:",
            range(len(winners)),
            format_func=lambda i: (
                f"👤 {winners[i]['이름']} - 🥇 {winners[i]['순위']}"
                f" ({winners[i].get('종목', winners[i].get('종목 및 부서', '-'))})"
            ),
            key=f"del_win_select_{selected_event}",
        )
        if st.button(
            "선택 입상자 정보 삭제", key=f"btn_del_win_{selected_event}"
        ):
          st.session_state.competition_winners[selected_event].pop(del_win_idx)
          st.success("선택한 입상자 정보가 삭제되었습니다.")
          st.rerun()


# --- 메뉴 3: 건의사항 ---
elif main_menu == "3. 💡 건의사항":
  st.title("💡 무기명 건의사항함")
  st.write(
      "클럽 운영 및 시설 등 자유롭게 의견을 제출해 주세요. 작성자의 정보나"
      " 제출 시각은 전혀 기록되지 않습니다."
  )
  st.write("---")

  if is_admin:
    st.markdown("### 🔒 [관리자 전용] 건의사항 목록 및 피드백 작성")
    st.info(
        "※ 관리자 계정에서는 건의사항 작성란이 노출되지 않으며, 등록된 건의"
        " 내용 확인 및 피드백 작성만 가능합니다."
    )
    st.write("---")

    if st.session_state.suggestions:
      for idx, item in enumerate(st.session_state.suggestions):
        with st.expander(f"📌 [{idx+1}] {item['title']}"):
          st.markdown("**건의 내용:**")
          st.write(item["content"])
          st.write("---")

          fb_text = st.text_area(
              "💬 관리자 Feedback (피드백 작성)",
              value=item.get("feedback", ""),
              key=f"fb_input_{idx}",
              height=100,
          )

          c_btn1, c_btn2 = st.columns([1, 1])
          with c_btn1:
            if st.button(
                "💾 피드백 저장",
                key=f"save_fb_{idx}",
                use_container_width=True,
            ):
              st.session_state.suggestions[idx]["feedback"] = fb_text.strip()
              st.success("피드백이 저장되었습니다.")
              st.rerun()
          with c_btn2:
            if st.button(
                "🗑️ 건의사항 삭제",
                key=f"del_sug_{idx}",
                use_container_width=True,
            ):
              st.session_state.suggestions.pop(idx)
              st.success("해당 건의사항이 삭제되었습니다.")
              st.rerun()
    else:
      st.info("현재 등록된 건의사항이 없습니다.")

  else:
    if not st.session_state.logged_in_user:
      st.warning(
          "🔒 건의사항은 **로그인한 승인 회원**만 작성할 수 있습니다. 왼쪽"
          " 사이드바 하단에서 로그인해 주세요."
      )
    else:
      current_user_status = st.session_state.users[current_id].get("status")
      if current_user_status != "approved":
        st.warning(
            "⏳ 관리자 가입 승인 대기 중인 회원입니다. 승인 완료 후 건의사항을"
            " 작성하실 수 있습니다."
        )
      else:
        st.markdown("### ✍️ 건의사항 작성 (익명)")
        with st.form("suggestion_form", clear_on_submit=True):
          s_title = st.text_input(
              "제목", placeholder="건의사항 제목을 입력하세요"
          )
          s_content = st.text_area(
              "내용",
              placeholder=(
                  "개선되었으면 하는 점이나 의견을 자유롭게 작성해 주세요."
              ),
              height=150,
          )
          btn_submit_s = st.form_submit_button(
              "📩 무기명 제출하기", use_container_width=True
          )

          if btn_submit_s:
            if s_title.strip() and s_content.strip():
              st.session_state.suggestions.append({
                  "title": s_title.strip(),
                  "content": s_content.strip(),
                  "feedback": "",
              })
              st.success("✅ 건의사항이 성공적으로 제출되었습니다.")
            else:
              st.warning("⚠️ 제목과 내용을 모두 입력해 주세요.")


# --- 메뉴 4: 회원 승인 및 관리 ---
elif main_menu == "4. 👥 회원 승인 및 관리 (관리자 전용)":
  st.title("👥 회원 승인 및 학원비 관리")
  st.write(
      "회원의 가입 승인 처리, 연락처, 성별 및 **월 학원비 납부 상태**를"
      " 관리합니다."
  )
  st.write("---")

  if not is_admin:
    st.error("🔒 관리자 권한이 필요합니다.")
    st.stop()

  st.markdown("### ⏳ 1. 가입 승인 대기 목록")
  pending_users = [
      uid
      for uid, udata in st.session_state.users.items()
      if udata.get("status") == "pending"
  ]

  if pending_users:
    p_col1, p_col2 = st.columns([3, 1])
    selected_p_user = p_col1.selectbox(
        "승인할 회원을 선택하세요:",
        pending_users,
        format_func=lambda x: (
            f"ID: {x} | 이름: {st.session_state.users[x]['name']}"
            f" ({st.session_state.users[x].get('gender', '-')}/{st.session_state.users[x].get('grade', '-')})"
            f" | 연락처: {st.session_state.users[x].get('phone')}"
        ),
    )
    if p_col2.button("✅ 선택 회원 승인", use_container_width=True):
      st.session_state.users[selected_p_user]["status"] = "approved"
      st.success(
          f"🎉 [{st.session_state.users[selected_p_user]['name']}] 회원이 정상"
          " 승인되었습니다!"
      )
      st.rerun()
  else:
    st.info("현재 승인 대기 중인 신청이 없습니다.")

  st.write("---")

  st.markdown("### 💳 2. 회원별 학원비 납부 상태 관리 (관리자 전용)")
  approved_users = [
      uid
      for uid, udata in st.session_state.users.items()
      if udata.get("role") != "admin" and udata.get("status") == "approved"
  ]

  if approved_users:
    with st.form("pay_manage_form"):
      selected_m_user = st.selectbox(
          "관리할 회원을 선택하세요:",
          approved_users,
          format_func=lambda x: (
              f"이름: {st.session_state.users[x]['name']}"
              f" ({st.session_state.users[x].get('grade', '-')}) | 현재 상태:"
              f" {st.session_state.users[x].get('pay_status', '미납')}"
          ),
      )
      m_user_info = st.session_state.users[selected_m_user]

      new_pay_status = st.selectbox(
          "납부 상태 설정",
          ["완료", "미납"],
          index=0 if m_user_info.get("pay_status") == "완료" else 1,
      )

      btn_update_pay = st.form_submit_button(
          "상태 업데이트", use_container_width=True
      )
      if btn_update_pay:
        st.session_state.users[selected_m_user]["pay_status"] = new_pay_status
        st.success(
            f"✅ [{m_user_info['name']}] 회원의 학원비 납부 상태가"
            f" [{new_pay_status}](으)로 변경되었습니다."
        )
        st.rerun()
  else:
    st.info("등록된 승인 회원이 없습니다.")
