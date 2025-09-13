import streamlit as st
from google import genai
from google.genai import types
import time

# CSS 스타일 정의 (제목에만 UI/UX 효과)
def load_css():
    st.markdown("""
    <style>
    /* 타이틀 스타일 - Gray/White 그라데이션 */
    .main-title {
        background: linear-gradient(45deg, #495057, #6c757d, #adb5bd, #6c757d);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        animation: gradientMove 4s ease-in-out infinite, textGlow 2s ease-in-out infinite alternate;
        text-shadow: 0 0 20px rgba(108, 117, 125, 0.3);
        letter-spacing: 1px;
    }
    
    @keyframes gradientMove {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    @keyframes textGlow {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.1); }
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
        layout="centered"
    )
    
    # 제목 (UI/UX 효과 적용)
    st.markdown("""
    <h1 class="main-title">SCM AI Agent</h1>
    """, unsafe_allow_html=True)
    st.caption("Google 검색을 통해 최신 정보를 반영하여 SCM 리스크 시나리오 전략을 제안합니다.")

    # --- API 키 하드코딩 ---
    API_KEY = "AIzaSyCJ1F-HMS4NkQ64f1tDRqJV_N9db0MmKpI"

    # --- 챗봇 대화 내역 초기화 ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! SCM 리스크 전략에 대해 무엇이든 물어보세요."}
        ]

    # --- 이전 대화 내역 출력 ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- 사용자 입력 처리 ---
    if prompt := st.chat_input("국가, 리스크, 전략 등 궁금한 점을 질문하세요."):
        # 사용자의 메시지를 대화 내역에 추가하고 화면에 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- UI/UX 개선: 동적 애니메이션으로 답변 생성 상태 표시 ---
        with st.chat_message("assistant"):
            # 답변이 스트리밍될 빈 공간(placeholder)을 만듭니다.
            message_placeholder = st.empty()
            # "생성 중"을 나타낼 애니메이션 프레임
            animation_frames = ["", " .", " ..", " ..."]
            animation_index = 0
            full_response = ""

            # API 호출 전, 사용자에게 즉각적인 피드백을 줍니다.
            message_placeholder.markdown("생각 중...")

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
                        # 현재까지의 답변 + 애니메이션 프레임을 placeholder에 업데이트합니다.
                        animation_char = animation_frames[animation_index % len(animation_frames)]
                        message_placeholder.markdown(full_response + animation_char)
                        animation_index += 1
                        # 아주 짧은 딜레이를 주어 애니메이션이 보이도록 합니다.
                        time.sleep(0.05)
                
                # 답변 생성이 완료되면 애니메이션 없이 최종 결과만 표시합니다.
                message_placeholder.markdown(full_response)

            except Exception as e:
                # 에러 발생 시, placeholder에 에러 메시지를 표시합니다.
                st.error(f"API 호출 중 오류가 발생했습니다: {e}")
                full_response = "죄송합니다, 답변을 생성하는 동안 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                message_placeholder.markdown(full_response)
            
            # 완성된 전체 응답을 대화 내역에 저장합니다.
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
