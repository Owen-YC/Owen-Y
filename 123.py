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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* 헤더 스타일 */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: slideInDown 1s ease-out, gentleFloat 6s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes gentleFloat {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-5px) rotate(0.5deg); }
        50% { transform: translateY(-8px) rotate(0deg); }
        75% { transform: translateY(-3px) rotate(-0.5deg); }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-50px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* 타이틀 스타일 */
    .main-title {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        animation: fadeInUp 1.2s ease-out 0.3s both, gradientMove 5s ease-in-out infinite, textGlow 2s ease-in-out infinite alternate;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
        letter-spacing: 2px;
    }
    
    @keyframes gradientMove {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes textGlow {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.2); }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
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
        font-size: 1.3rem;
        animation: fadeInUp 1.2s ease-out 0.6s both;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* 채팅 컨테이너 스타일 */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        animation: slideInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .chat-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 70px rgba(0, 0, 0, 0.15);
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* 사용자 메시지 스타일 */
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        animation: slideInRight 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .user-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: messageShimmer 2s infinite;
    }
    
    @keyframes messageShimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 어시스턴트 메시지 스타일 */
    .assistant-message {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        color: #495057;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: slideInLeft 0.6s ease-out;
        border-left: 5px solid #667eea;
        position: relative;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 입력창 스타일 */
    .stTextInput > div > div > input {
        border-radius: 30px;
        border: 3px solid #e9ecef;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        transition: all 0.4s ease;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 5px rgba(102, 126, 234, 0.2), 0 10px 30px rgba(0, 0, 0, 0.15);
        outline: none;
        transform: scale(1.02);
    }
    
    /* 로딩 애니메이션 */
    .loading-dots {
        display: inline-block;
        position: relative;
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 2s infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* 타이핑 애니메이션 */
    .typing-animation {
        border-right: 3px solid #667eea;
        animation: blink 1.2s infinite;
    }
    
    @keyframes blink {
        0%, 50% { border-color: #667eea; }
        51%, 100% { border-color: transparent; }
    }
    
    /* 부드러운 전환 효과 */
    .smooth-transition {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* 상태 표시 */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 10px rgba(40, 167, 69, 0.5);
    }
    
    .status-online {
        background: linear-gradient(45deg, #28a745, #20c997);
    }
    
    .status-thinking {
        background: linear-gradient(45deg, #ffc107, #fd7e14);
    }
    
    @keyframes pulse {
        0% { 
            opacity: 1; 
            transform: scale(1);
        }
        50% { 
            opacity: 0.7; 
            transform: scale(1.1);
        }
        100% { 
            opacity: 1; 
            transform: scale(1);
        }
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
    
    /* 사이드바 스타일 */
    .stSidebar {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(248, 249, 250, 0.95));
        backdrop-filter: blur(20px);
    }
    
    .stSidebar .stButton > button {
        background: linear-gradient(135deg, #28a745, #20c997);
        border-radius: 15px;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .stSidebar .stButton > button:hover {
        background: linear-gradient(135deg, #218838, #1ea085);
        transform: translateY(-2px);
    }
    
    /* 다운로드 버튼 스타일 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #17a2b8, #138496);
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #138496, #117a8b);
        transform: translateY(-2px);
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .header-container, .chat-container {
            padding: 1.5rem;
            margin: 0.8rem;
        }
        
        .stButton > button {
            font-size: 0.9rem;
            padding: 0.8rem 1.5rem;
        }
    }
    
    /* 스크롤바 스타일 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # CSS 로드
    load_css()
    
    # --- Streamlit 페이지 설정 ---
    st.set_page_config(
        page_title="SCM AI Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 헤더 컨테이너
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">SCM AI Agent</h1>
        <p class="subtitle">AI Agent suggests SCM risk scenario strategies with real-time analysis</p>
    </div>
    """, unsafe_allow_html=True)

    # --- API 키 하드코딩 ---
    API_KEY = "AIzaSyCJ1F-HMS4NkQ64f1tDRqJV_N9db0MmKpI"

    # --- 챗봇 대화 내역 초기화 ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 2rem; font-size: 1.5rem;">⚙️ Settings</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 대화 초기화 버튼
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
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
        <div style="text-align: center; margin: 2rem 0;">
            <span class="status-indicator status-online"></span>
            <span style="color: #28a745; font-weight: 600; font-size: 1.1rem;">Online</span>
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

    # --- 사용자 입력 처리 ---
    if prompt := st.chat_input("Ask about countries, risks, strategies, etc.", key="main_input"):
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
        <div style="text-align: center; margin: 1.5rem 0;">
            <span class="status-indicator status-thinking"></span>
            <span style="color: #ffc107; font-weight: 600; font-size: 1.1rem;">Analyzing...</span>
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
            <div style="text-align: center; margin: 1.5rem 0;">
                <span class="status-indicator status-online"></span>
                <span style="color: #28a745; font-weight: 600; font-size: 1.1rem;">Online</span>
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
            <div style="text-align: center; margin: 1.5rem 0;">
                <span class="status-indicator status-online"></span>
                <span style="color: #28a745; font-weight: 600; font-size: 1.1rem;">Online</span>
            </div>
            """, unsafe_allow_html=True)
        
        # 완성된 전체 응답을 대화 내역에 저장합니다.
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # 메인 컨텐츠 영역 닫기
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 하단 정보
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; color: #6c757d;">
        <p style="font-size: 1.1rem;">💡 <strong>Tip:</strong> Include specific country names or risk types in your questions for more accurate analysis.</p>
        <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.8;">Powered by Google Gemini AI • Latest Information Search Support</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
