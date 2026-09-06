import os
import json
from datetime import datetime
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# --- 1. AI OCR 분석 함수 ---
def extract_lab_records_from_image(image_bytes):
    """
    업로드된 수기 기록지 사진에서 인라인 랩타임 데이터를 AI로 추출합니다.
    """
    api_key = "AQ.Ab8RN6IOZwJSyzVUc78D2ov1KqV5wIRnV5x7_H8pYAOejbacgQ"
    
    if not api_key:
        return None, "API Key가 입력되지 않았습니다."
    
    client = genai.Client(api_key=api_key)
    
    prompt = """
    이 사진은 인라인 스케이팅 훈련 수기 랩타임 기록지입니다. 
    사진에 적힌 데이터(이름, 종목, 기록, 측정 회차, 학년, 성별 등)를 읽어서 정확히 추출해주세요.
    반드시 아래의 JSON 배열 형식으로만 응답해주세요. 다른 텍스트는 포함하지 마세요.
    [
      {
        "이름": "홍길동",
        "종목": "200m 타임트라이얼",
        "기록": 28.52,
        "측정 회차": "1회차",
        "학년": "4학년",
        "성별": "남자"
      }
    ]
    * 종목은 다음 중 하나로 매칭해주세요: ['200m 타임트라이얼', '500m 스프린트', '1000m', '3000m 포인트', '마라톤']
    * 기록은 숫자(초 단위, 예: 28.52)로 변환해주세요.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()
            
        parsed_data = json.loads(text_response)
        return parsed_data, None
    except Exception as e:
        return None, str(e)


# --- 2. 세션 상태 및 데이터 초기화 예시 ---
if "lab_records" not in st.session_state:
    st.session_state.lab_records = pd.DataFrame(columns=["ID", "입력 날짜", "측정 회차", "이름", "학년", "성별", "종목", "기록"])

# 예시용 변수 (기존 코드에 맞게 유지)
current_id = st.session_state.get("current_user_id", "test_user") 

def save_records_to_disk():
    # 파일 저장 로직이 있다면 여기에 유지됩니다.
    pass


# --- 3. 메인 메뉴 로직 ---
main_menu = st.sidebar.selectbox("메뉴 선택", ["1. 개인별 LAB Time Recorder", "기타 메뉴"])

if main_menu == "1. 개인별 LAB Time Recorder":
    st.title("⏱️ 개인별 LAB Time Recorder")
    st.markdown("인라인 스케이팅 기록을 측정하고 회차별 성장 추이를 확인하세요.")
    
    # 탭을 4개로 확장 (조회, 직접입력, 사진OCR, 순위표)
    tab_rec1, tab_rec2, tab_rec3, tab_rec4 = st.tabs(["📊 기록 조회 및 그래프", "📝 직접 입력", "📸 수기 기록 사진 자동 업로드(OCR)", "🏆 기록 순위표"])
    
    df_records = st.session_state.lab_records
    
    with tab_rec1:
        st.subheader("📊 기록 조회 및 그래프")
        st.write("등록된 기록 조회 화면입니다.")

    with tab_rec2:
        st.subheader("📝 직접 입력")
        st.write("직접 기록을 입력하는 폼 화면입니다.")

    with tab_rec3:
        st.subheader("📸 수기 기록지 사진으로 자동 업로드")
        st.markdown("수기로 작성된 랩타임 기록지 사진을 업로드하면 AI가 자동으로 읽어서 데이터베이스에 등록해 줍니다.")
        
        if not current_id:
            st.warning("기록을 업로드하려면 로그인이 필요합니다.")
        else:
            uploaded_record_image = st.file_uploader("수기 기록지 사진 선택 (JPG, PNG)", type=["jpg", "jpeg", "png"])
            
            if uploaded_record_image is not None:
                st.image(uploaded_record_image, caption="업로드한 기록지 사진", use_column_width=True)
                
                if st.button("🤖 AI로 기록 자동 분석 및 추출하기"):
                    with st.spinner("사진에서 기록을 읽어오는 중입니다... 잠시만 기다려주세요."):
                        image_bytes = uploaded_record_image.getvalue()
                        extracted_items, error_msg = extract_lab_records_from_image(image_bytes)
                        
                        if error_msg:
                            st.error(f"분석 중 오류가 발생했습니다: {error_msg}")
                        elif extracted_items:
                            st.success(f"총 {len(extracted_items)}개의 기록을 성공적으로 읽어왔습니다!")
                            st.session_state["temp_ocr_records"] = extracted_items
                        else:
                            st.warning("사진에서 텍스트를 감지하지 못했습니다. 더 선명한 사진을 올려주세요.")
            
            # AI가 읽어온 데이터를 표 형태로 확인하고 수정할 수 있는 공간
            if "temp_ocr_records" in st.session_state and st.session_state["temp_ocr_records"]:
                st.markdown("---")
                st.markdown("### 📋 추출된 기록 확인 및 수정")
                st.info("아래 내용을 확인하신 후 오타가 있다면 수정하고 'DB에 최종 반영하기' 버튼을 눌러주세요.")
                
                ocr_df = pd.DataFrame(st.session_state["temp_ocr_records"])
                edited_ocr_df = st.data_editor(ocr_df, num_rows="dynamic", use_container_width=True)
                
                if st.button("💾 DB에 최종 반영하기"):
                    today_date_str = datetime.now().strftime("%Y-%m-%d")
                    new_rows = []
                    for _, row in edited_ocr_df.iterrows():
                        new_rows.append({
                            "ID": current_id,
                            "입력 날짜": today_date_str,
                            "측정 회차": row.get("측정 회차", "1회차"),
                            "이름": row.get("이름", "알수없음"),
                            "학년": row.get("학년", "성인부"),
                            "성별": row.get("성별", "남자"),
                            "종목": row.get("종목", "200m 타임트라이얼"),
                            "기록": float(row.get("기록", 0.0))
                        })
                    
                    st.session_state.lab_records = pd.concat([st.session_state.lab_records, pd.DataFrame(new_rows)], ignore_index=True)
                    save_records_to_disk()
                    del st.session_state["temp_ocr_records"]
                    st.success("모든 기록이 성공적으로 저장되었습니다!")
                    st.rerun()

    with tab_rec4:
        st.subheader("🏆 기록 순위표")
        st.write("명예의 전당 및 순위표 화면입니다.")
