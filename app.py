import streamlit as st
import google.generativeai as genai
import time

# 페이지 설정
st.set_page_config(
    page_title="🔮결정장애 고민 해결 챗봇 - 매직북",
    layout="centered"
)

# 커스텀 CSS 스타일
st.markdown("""
<style>
    .main-header {
        font-family: 'Pretendard', sans-serif;
        font-size: 2.5rem;
        font-weight: 600;
        color: #1E1E1E;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #7B2CBF 0%, #9D4EDD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subheader {
        font-family: 'Pretendard', sans-serif;
        font-size: 1.2rem;
        font-weight: 400;
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-bubble {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .user-bubble {
        background-color: #9D4EDD;
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .stButton>button {
        background-color: #7B2CBF;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #9D4EDD;
        transform: translateY(-2px);
    }
    .stTextInput>div>div>input {
        border-radius: 50px;
        border: 2px solid #E6E6E6;
        padding: 1rem;
        font-size: 1rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #7B2CBF;
        box-shadow: 0 0 0 2px rgba(123, 44, 191, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 헤더 표시
st.markdown("<h1 class='main-header'>🔮 매직북 - 결정장애 해결사</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>결정하기 어려운 순간, 매직북과 함께 해결해보세요.</p>", unsafe_allow_html=True)

# Gemini API 설정
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except KeyError:
    st.error("🚨 Google API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일에 API 키를 설정해주세요.")
    st.stop()

# Gemini 모델 초기화
model = genai.GenerativeModel('gemini-1.5-flash')

# 세션 상태 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "shared_solutions" not in st.session_state:
    st.session_state.shared_solutions = []
if "conversation_stage" not in st.session_state:
    st.session_state.conversation_stage = 0
if "user_original_problem" not in st.session_state:
    st.session_state.user_original_problem = ""
if "solution_feedback" not in st.session_state:
    st.session_state.solution_feedback = {}

# 탭 생성
solve_tab, shared_tab = st.tabs(["고민 해결하기", "공유된 해결책"])

# ----------------- 고민 해결하기 탭 ----------------- #
with solve_tab:
    # 채팅 메시지를 위한 플레이스홀더
    chat_placeholder = st.empty()

    # 채팅 히스토리 표시
    with chat_placeholder.container():
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f"<div class='user-bubble'>🗣️ {chat['parts']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble'>✨ {chat['parts']}</div>", unsafe_allow_html=True)
            time.sleep(0.02)

    # 초기 대화 시작
    if not st.session_state.chat_history and st.session_state.conversation_stage == 0:
        initial_message = "안녕하세요! 당신의 고민을 알려주세요. 어떤 일로 망설이고 계신가요?"
        st.session_state.chat_history.append({"role": "model", "parts": initial_message})
        st.session_state.conversation_stage = 1
        st.rerun()

    # 사용자 입력 처리
    user_input = st.chat_input("여기에 고민을 입력해주세요...")
    
    if user_input:
        # 사용자 메시지 추가
        st.session_state.chat_history.append({"role": "user", "parts": user_input})
        
        # 사용자 메시지 즉시 표시
        with chat_placeholder.container():
            for chat in st.session_state.chat_history:
                if chat["role"] == "user":
                    st.markdown(f"<div class='user-bubble'>🗣️ {chat['parts']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-bubble'>✨ {chat['parts']}</div>", unsafe_allow_html=True)
                time.sleep(0.02)

        # 대화 단계별 로직
        if st.session_state.conversation_stage == 1:
            # 첫 번째 질문 단계
            st.session_state.user_original_problem = user_input
            
            with st.spinner("생각 중... 잠시만 기다려주세요."):
                prompt = f"""
                당신은 사용자의 고민을 해결해주는 따뜻하고 공감적인 상담사입니다.
                사용자의 고민을 더 깊이 이해하기 위해 하나의 질문만 해주세요.
                
                질문 작성 가이드라인:
                1. 친근하고 부드러운 말투를 사용하세요
                2. 공감하는 톤으로 질문하세요
                3. 핵심을 파악하기 위한 구체적인 질문을 하세요
                4. 질문은 반드시 하나만 해주세요
                
                질문 예시:
                - "~하시다니 많이 고민되셨겠어요. 구체적으로 어떤 점이 가장 망설여지시나요?"
                - "그런 상황이시군요. 결정을 내리기 어려운 가장 큰 이유는 무엇인가요?"
                
                사용자의 고민: {user_input}
                """
                
                response = model.generate_content(prompt)
                chatbot_response = response.text
                
                st.session_state.chat_history.append({"role": "model", "parts": chatbot_response})
                st.session_state.conversation_stage = 2
                st.rerun()

        elif st.session_state.conversation_stage == 2:
            # 두 번째 질문 또는 해결책 제시 단계
            with st.spinner("생각 중... 잠시만 기다려주세요."):
                # 전체 대화 내용 구성
                full_conversation = "\n".join([
                    f"{'사용자' if chat['role'] == 'user' else '상담사'}: {chat['parts']}"
                    for chat in st.session_state.chat_history
                ])
                
                prompt = f"""
                당신은 사용자의 고민을 해결해주는 따뜻하고 공감적인 상담사입니다.
                지금까지의 대화를 바탕으로, 다음 두 가지 중 하나를 선택하세요:

                1. 고민의 핵심을 아직 완전히 파악하지 못했다면:
                   - 마지막 한 개의 질문을 더 해주세요 (최대 2개 질문)
                   - 질문은 친근하고 공감적인 톤으로 작성해주세요

                2. 고민의 핵심을 충분히 파악했다면:
                   - 다음 구조로 해결책을 제시해주세요:
                   [상황해석]: 현재 상황에 대한 객관적 분석
                   [핵심 쟁점]: 고민의 실제 핵심
                   [추천 액션]: 구체적인 해결 방안

                지금까지의 대화:
                {full_conversation}
                """
                
                response = model.generate_content(prompt)
                chatbot_response = response.text
                
                # 해결책이 포함되어 있는지 확인
                is_solution = all(keyword in chatbot_response for keyword in ['상황해석:', '핵심 쟁점:', '추천 액션:'])
                
                st.session_state.chat_history.append({"role": "model", "parts": chatbot_response})
                st.session_state.conversation_stage = 3  # 다음 단계로 진행
                st.rerun()

        elif st.session_state.conversation_stage == 3:
            # 마지막 메시지가 구조화된 해결책이 아닌 경우에만 실행
            if not any(keyword in st.session_state.chat_history[-1]["parts"] 
                      for keyword in ['상황해석:', '핵심 쟁점:', '추천 액션:']):
                with st.spinner("해결책을 생성 중입니다..."):
                    # 전체 대화 내용 구성
                    full_conversation = "\n".join([
                        f"{'사용자' if chat['role'] == 'user' else '상담사'}: {chat['parts']}"
                        for chat in st.session_state.chat_history
                    ])
                    
                    prompt = f"""
                    당신은 사용자의 고민을 해결해주는 따뜻하고 공감적인 상담사입니다.
                    지금까지의 대화를 바탕으로 최종 해결책을 제시해주세요.

                    해결책은 반드시 다음 구조로 작성해주세요:
                    상황해석: (현재 상황에 대한 객관적이고 통찰력 있는 분석)
                    핵심 쟁점: (고민의 실제 핵심과 근본 원인)
                    추천 액션: (구체적이고 실행 가능한 해결 방안)

                    작성 시 주의사항:
                    1. 친근하고 공감적인 톤을 유지하세요
                    2. 실용적이고 구체적인 조언을 제공하세요
                    3. 긍정적이고 희망적인 메시지로 마무리하세요

                    지금까지의 대화:
                    {full_conversation}

                    원래 고민:
                    {st.session_state.user_original_problem}
                    """
                    
                    response = model.generate_content(prompt)
                    chatbot_response = response.text
                    
                    st.session_state.chat_history.append({"role": "model", "parts": chatbot_response})
                    st.rerun()

    # 해결책 공유 버튼 표시
    if (st.session_state.conversation_stage == 3 and 
        "상황해석:" in st.session_state.chat_history[-1]["parts"]):
        
        st.markdown("---")
        if st.button("✨ 해결책 공유하기"):
            shared_data = {
                "고민": st.session_state.user_original_problem,
                "해결책": st.session_state.chat_history[-1]["parts"]
            }
            
            if "shared_solutions" not in st.session_state:
                st.session_state.shared_solutions = []
            
            st.session_state.shared_solutions.append(shared_data)
            st.success("해결책이 공유되었습니다!")
            
            # 채팅 초기화
            st.session_state.chat_history = []
            st.session_state.conversation_stage = 0
            st.session_state.user_original_problem = ""
            
            st.rerun()

# ----------------- 공유된 해결책 탭 ----------------- #
with shared_tab:
    st.markdown("<h2 class='subheader'>✨ 모든 사용자의 공유된 해결책</h2>", unsafe_allow_html=True)
    
    if not st.session_state.shared_solutions:
        st.info("아직 공유된 해결책이 없습니다. 첫 번째 탭에서 고민을 해결하고 공유해보세요!")
    else:
        for i, solution in enumerate(st.session_state.shared_solutions):
            st.markdown("---")
            st.markdown(f"**고민:** {solution['고민']}")
            st.markdown("**해결책:**")
            st.markdown(solution['해결책'])
            
            # 해결책의 피드백 상태 초기화
            if i not in st.session_state.solution_feedback:
                st.session_state.solution_feedback[i] = {"likes": 0, "dislikes": 0}
            
            # 공감/비공감 버튼 및 카운트 표시
            col1, col2, col3, col4 = st.columns([1, 1, 0.5, 0.5])
            
            # 공감 버튼
            if col1.button(
                f"👍 공감 ({st.session_state.solution_feedback[i]['likes']})", 
                key=f"like_{i}"
            ):
                st.session_state.solution_feedback[i]['likes'] += 1
                st.rerun()
            
            # 비공감 버튼
            if col2.button(
                f"👎 비공감 ({st.session_state.solution_feedback[i]['dislikes']})", 
                key=f"dislike_{i}"
            ):
                st.session_state.solution_feedback[i]['dislikes'] += 1
                st.rerun()


