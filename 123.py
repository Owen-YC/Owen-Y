import streamlit as st
from google import genai
from google.genai import types
import time
import random
import json
from datetime import datetime

# CSS 스타일 정의
def load_css():
    st.markdown("""
    <style>
    /* 전체 페이지 스타일 */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        min-height: 100vh;
    }
    
    /* 헤더 스타일 */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(108, 117, 125, 0.2);
        animation: slideInDown 0.8s ease-out, gentleFloat 4s ease-in-out infinite;
    }
    
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-3px); }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 타이틀 스타일 */
    .main-title {
        background: linear-gradient(45deg, #495057, #6c757d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInUp 1s ease-out 0.2s both, subtlePulse 3s ease-in-out infinite;
    }
    
    @keyframes subtlePulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 서브타이틀 스타일 */
    .subtitle {
        color: #6c757d;
        text-align: center;
        font-size: 1.1rem;
        animation: fadeInUp 1s ease-out 0.4s both;
    }
    
    /* 채팅 컨테이너 스타일 */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInUp 0.6s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 사용자 메시지 스타일 */
    .user-message {
        background: linear-gradient(135deg, #6c757d, #495057);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(108, 117, 125, 0.3);
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 어시스턴트 메시지 스타일 */
    .assistant-message {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        color: #495057;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.6s ease-out;
        border-left: 4px solid #6c757d;
    }
    
    /* 입력창 스타일 */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6c757d;
        box-shadow: 0 0 0 3px rgba(108, 117, 125, 0.1);
        outline: none;
    }
    
    /* 로딩 애니메이션 */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 1.5s infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* 타이핑 애니메이션 */
    .typing-animation {
        border-right: 2px solid #6c757d;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { border-color: #6c757d; }
        51%, 100% { border-color: transparent; }
    }
    
    /* 부드러운 전환 효과 */
    .smooth-transition {
        transition: all 0.3s ease;
    }
    
    /* 상태 표시 */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background-color: #28a745;
    }
    
    .status-thinking {
        background-color: #ffc107;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* 다크모드 지원 */
    @media (prefers-color-scheme: dark) {
        .header-container, .chat-container {
            background: rgba(30, 30, 30, 0.95);
            color: #ffffff;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #2d3748, #4a5568);
            color: #ffffff;
        }
        
        .stTextInput > div > div > input {
            background: rgba(30, 30, 30, 0.9);
            color: #ffffff;
            border-color: #4a5568;
        }
    }
    
    /* 빠른 질문 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #6c757d, #495057);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.75rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(108, 117, 125, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6268, #343a40);
        box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
    }
    
    /* 사이드바 버튼 스타일 */
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #6c757d, #495057);
        border-radius: 10px;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #5a6268, #343a40);
    }
    
    /* 다운로드 버튼 스타일 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #6c757d, #495057);
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #5a6268, #343a40);
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .header-container, .chat-container {
            padding: 1rem;
            margin: 0.5rem;
        }
        
        .stButton > button {
            font-size: 0.9rem;
            padding: 0.6rem 0.8rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # CSS 로드
    load_css()
    
    # --- Streamlit 페이지 설정 ---
    st.set_page_config(
        page_title="SCM 리스크 전략 챗봇",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 헤더 컨테이너
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">SCM AI Agent</h1>
        <p class="subtitle">AI Agent suggests SCM risk scenario strategies.</p>
    </div>
    """, unsafe_allow_html=True)

    # --- API 키 하드코딩 ---
    API_KEY = "AIzaSyCJ1F-HMS4NkQ64f1tDRqJV_N9db0MmKpI"

    # --- 챗봇 대화 내역 초기화 ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Feel free to ask me anything about SCM risk strategies."}
        ]
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: #6c757d; margin-bottom: 1rem;">⚙️ Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 대화 초기화 버튼
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! Feel free to ask me anything about SCM risk strategies."}
            ]
            st.rerun()
        
        # 대화 내역 다운로드
        if st.session_state.messages:
            conversation_text = ""
            for msg in st.session_state.messages:
                role = "User" if msg["role"] == "user" else "AI Assistant"
                conversation_text += f"{role}: {msg['content']}\n\n"
            
            st.download_button(
                label="💾 Download Conversation",
                data=conversation_text,
                file_name=f"scm_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # 상태 표시
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <span class="status-indicator status-online"></span>
            <span style="color: #28a745; font-weight: 500;">Online</span>
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 컨텐츠 영역
    st.markdown("""
    <div style="margin-left: 1rem;">
    """, unsafe_allow_html=True)

    # --- 이전 대화 내역 출력 ---
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message smooth-transition">
                <strong>👤 User</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message smooth-transition">
                <strong>🤖 AI Assistant</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    # 빠른 질문 버튼들
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h4 style="color: #6c757d; margin-bottom: 1rem;">💬 Quick Questions</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # 빠른 질문 버튼들
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🇨🇳 China Risk Analysis", use_container_width=True):
            st.session_state.quick_question = "Please analyze China's SCM risks. Specifically, tell me about supply chain disruption risks and response strategies."
    
    with col2:
        if st.button("🌍 Global Supply Chain Strategy", use_container_width=True):
            st.session_state.quick_question = "Please suggest strategies to minimize global supply chain risks. Include diversification and alternative supplier acquisition plans."
    
    with col3:
        if st.button("⚡ Risk Hedging Methods", use_container_width=True):
            st.session_state.quick_question = "Please tell me about various methods to hedge SCM risks. Include both financial and non-financial methods."
    
    # --- 사용자 입력 처리 ---
    prompt = None
    
    # 빠른 질문이 선택된 경우 처리
    if hasattr(st.session_state, 'quick_question'):
        prompt = st.session_state.quick_question
        del st.session_state.quick_question
    
    # 일반 입력 처리
    if not prompt:
        prompt = st.chat_input("Ask about countries, risks, strategies, etc.", key="main_input")
    
    if prompt:
        # 사용자의 메시지를 대화 내역에 추가하고 화면에 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        st.markdown(f"""
        <div class="user-message smooth-transition">
            <strong>👤 User</strong><br>
            {prompt}
        </div>
        """, unsafe_allow_html=True)

        # 상태를 "생각 중"으로 변경
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0;">
            <span class="status-indicator status-thinking"></span>
            <span style="color: #ffc107; font-weight: 500;">Thinking...</span>
        </div>
        """, unsafe_allow_html=True)

        # --- UI/UX 개선: 동적 애니메이션으로 답변 생성 상태 표시 ---
        # 답변이 스트리밍될 빈 공간(placeholder)을 만듭니다.
        message_placeholder = st.empty()
        full_response = ""

        # API 호출 전, 사용자에게 즉각적인 피드백을 줍니다.
        message_placeholder.markdown("""
        <div class="assistant-message">
            <strong>🤖 AI Assistant</strong><br>
            <span class="loading-dots">Searching and analyzing latest information</span>
        </div>
        """, unsafe_allow_html=True)

        try:
            # --- Gemini API 호출 로직 (기존과 동일) ---
            client = genai.Client(api_key=API_KEY)

            system_instruction = [
                types.Part.from_text(text="""SCM 리스크 시나리오 전략을 짜줬으면 해.
                입력으로 들어갈 수 있는 걸로는 다음과 같은 것들이 있어 :
                 - 발생 국가에 대한 리스크 정도를 파악
                 - 리스크 헷지(Hedge) 방법 제안
                 - 대체 전략 제안
                ---
                답변 전에는 !!항상!! 유저가 입력한 내용과 관련된 최신 정보를 google search tool을 통해 검색한 뒤, 해당 정보 기반으로 답변할 것."""),
            ]
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            safety_settings = [
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
            ]
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                safety_settings=safety_settings,
                system_instruction=system_instruction,
                tools=[google_search_tool]
            )
            contents_for_api = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents_for_api.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                )

            model_name = "gemini-2.5-flash"
            response_stream = client.models.generate_content_stream(
                model=model_name,
                contents=contents_for_api,
                config=generate_content_config,
            )

            # 스트리밍 응답을 처리하며 동적 애니메이션을 추가합니다.
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    # 현재까지의 답변을 타이핑 애니메이션과 함께 표시
                    message_placeholder.markdown(f"""
                    <div class="assistant-message">
                        <strong>🤖 AI Assistant</strong><br>
                        <span class="typing-animation">{full_response}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    # 부드러운 타이핑 효과를 위한 딜레이
                    time.sleep(0.02)
            
            # 답변 생성이 완료되면 타이핑 애니메이션 없이 최종 결과만 표시합니다.
            message_placeholder.markdown(f"""
            <div class="assistant-message smooth-transition">
                <strong>🤖 AI Assistant</strong><br>
                {full_response}
            </div>
            """, unsafe_allow_html=True)
            
            # 상태를 "온라인"으로 복원
            st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
                <span class="status-indicator status-online"></span>
                <span style="color: #28a745; font-weight: 500;">Online</span>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            # 에러 발생 시, placeholder에 에러 메시지를 표시합니다.
            full_response = "Sorry, an error occurred while generating the response. Please try again later."
            message_placeholder.markdown(f"""
            <div class="assistant-message" style="border-left-color: #dc3545; background: linear-gradient(135deg, #f8d7da, #f5c6cb);">
                <strong>🤖 AI Assistant</strong><br>
                {full_response}
            </div>
            """, unsafe_allow_html=True)
            
            # 상태를 "온라인"으로 복원
            st.markdown("""
            <div style="text-align: center; margin: 1rem 0;">
                <span class="status-indicator status-online"></span>
                <span style="color: #28a745; font-weight: 500;">Online</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 완성된 전체 응답을 대화 내역에 저장합니다.
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # 메인 컨텐츠 영역 닫기
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 하단 정보
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #6c757d;">
        <p>💡 <strong>Tip:</strong> Include specific country names or risk types in your questions for more accurate analysis.</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Powered by Google Gemini AI • Latest Information Search Support</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

