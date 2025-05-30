import streamlit as st
import google.generativeai as genai
import time

# Streamlit 페이지 설정
st.set_page_config(
    page_title="결정장애 고민 해결사",
    page_icon="🤔",
    layout="centered"
)

# API 키 설정
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "initial_prompt_sent" not in st.session_state:
    st.session_state.initial_prompt_sent = False

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "chat_session" not in st.session_state:
    # Gemini 모델 초기화 및 채팅 세션 시작
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.chat_session = model.start_chat(history=[])

# 헤더 디자인
st.title("🤔 결정장애 고민 해결사")

# 초기 메시지 발송 (한 번만)
if not st.session_state.initial_prompt_sent:
    initial_message = """
    안녕하세요! 저는 여러분의 고민을 함께 해결해나가는 AI 상담사입니다.
    어떤 결정을 내리기 어려운 상황이신가요? 천천히 이야기해주세요.
    """
    st.session_state.chat_history.append({
        "role": "model",
        "parts": [initial_message]
    })
    st.session_state.initial_prompt_sent = True

# 대화 기록 표시
for message in st.session_state.chat_history:
    with st.chat_message("assistant" if message["role"] == "model" else "user"):
        st.markdown(message["parts"][0])

# 사용자 입력 처리
if prompt := st.chat_input("고민이 있다면 자유롭게 이야기해주세요..."):
    # 사용자 메시지 표시 및 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.chat_history.append({
        "role": "user",
        "parts": [prompt]
    })

    try:
        # AI 응답 생성을 위한 프롬프트 설정
        full_prompt = f"""
        당신은 사용자의 결정장애 고민을 듣고, 공감하며, 그 이면에 숨겨진 진짜 마음을 이해하도록 돕는 친절한 상담사입니다.

        현재 질문 횟수: {st.session_state.question_count}

        엄격한 질문 규칙:
        1. 질문은 절대로 2회를 초과할 수 없습니다.
        2. 현재 질문 횟수가 2회 이상이면, 더 이상의 질문 없이 반드시 최종 결론을 도출해야 합니다.
        3. 각 응답에는 반드시 하나의 질문만 포함해야 합니다.

        질문 단계별 지침:
        - 첫 번째 질문 (현재 카운트가 0일 때):
          * 현재 상황을 더 자세히 이해하기 위한 구체적인 질문을 하나만 하세요.
          * 예: "구체적으로 어떤 선택지들 사이에서 고민이 되시나요?"

        - 두 번째 질문 (현재 카운트가 1일 때):
          * 고민의 근본 원인을 파악하기 위한 심층적인 질문을 하나만 하세요.
          * 예: "그 선택지들 중에서 특별히 더 끌리는 쪽이 있나요?"

        - 결론 도출 (현재 카운트가 2 이상일 때):
          반드시 다음 구조로 최종 해결책을 제시하세요:

          **현재 상황 분석**:
          (지금까지의 대화를 통해 파악한 사용자의 상황 요약)

          **고민의 핵심**:
          (질문들을 통해 파악한 진짜 고민의 원인)

          **추천 조치**:
          (구체적이고 실천 가능한 해결 방안)

        공감과 소통:
        - 각 응답은 반드시 공감 표현으로 시작하세요.
        - 따뜻하고 친근한 어조를 유지하세요.
        - 사용자의 감정에 충분히 공감하세요.

        해결책 제시 방식:
        - 사용자가 스스로 결정할 수 있도록 돕는 조언을 제공하세요.
        - 강압적인 어투는 사용하지 마세요.
        - 실천 가능한 구체적 방안을 제시하세요.

        사용자의 마지막 고민: {prompt}
        """

        # AI 응답 생성 및 실시간 표시
        response = st.session_state.chat_session.send_message(
            full_prompt,
            stream=True
        )

        # 응답 표시를 위한 컨테이너 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 응답을 실시간으로 표시
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # 임시 커서를 추가하여 타이핑 효과 생성
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
            
            # 최종 응답 표시 (커서 제거)
            message_placeholder.markdown(full_response)
            
            # 대화 기록에 저장
            st.session_state.chat_history.append({
                "role": "model",
                "parts": [full_response]
            })

            # 질문이 포함된 경우에만 카운터 증가
            if "?" in full_response and st.session_state.question_count < 2:
                st.session_state.question_count += 1

    except Exception as e:
        error_message = f"챗봇 응답 중 오류가 발생했습니다: {str(e)}. API 키를 확인하거나 잠시 후 다시 시도해주세요."
        st.error(error_message)

# 푸터 추가
st.markdown("---")
st.markdown("💡 모든 대화는 비공개로 진행되며, 안전하게 보호됩니다.")
st.markdown("<br><br><br>", unsafe_allow_html=True)
