import streamlit as st
from openai import OpenAI
import re
from urllib.parse import urlparse, parse_qs

# 페이지 설정
st.set_page_config(
    page_title="강의 영상 피드백 챗봇",
    page_icon="🎓",
    layout="wide"
)

# OpenAI 클라이언트 초기화
@st.cache_resource
def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
        st.stop()
    return OpenAI(api_key=api_key)

client = get_openai_client()

# 세션 스테이트 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_analyzed" not in st.session_state:
    st.session_state.video_analyzed = False
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "feedback" not in st.session_state:
    st.session_state.feedback = ""

# 유튜브 비디오 ID 추출 함수
def extract_youtube_id(url):
    """유튜브 URL에서 비디오 ID를 추출합니다."""
    if not url:
        return None
    
    # 다양한 유튜브 URL 형식 지원
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^?]+)',
        r'(?:https?://)?(?:www\.)?youtu\.be/([^?]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

# 영상 분석 및 피드백 생성 함수
def analyze_video(video_url, video_id):
    """유튜브 영상을 분석하고 피드백을 생성합니다."""
    
    system_prompt = """당신은 전문 강의 컨설턴트입니다. 
강사들의 강의 영상을 분석하고 개선점을 제시하는 역할을 합니다.
다음 관점에서 피드백을 제공해주세요:

1. 강의 구조 및 내용 전달
2. 발표 스킬 (목소리, 속도, 명확성)
3. 시각 자료 활용
4. 학습자 참여 유도
5. 개선 제안

현재는 URL만 제공되므로, 일반적인 강의 영상 피드백 가이드라인을 제공하고,
실제 영상 분석을 위해서는 추가 정보가 필요함을 안내해주세요."""

    user_prompt = f"""다음 유튜브 영상에 대한 피드백을 제공해주세요:
URL: {video_url}
Video ID: {video_id}

현재 단계에서는 URL 정보만 제공되었으므로, 강의 영상 분석을 위한 일반적인 피드백 프레임워크와
개선 체크리스트를 제공해주세요. 그리고 더 구체적인 피드백을 위해 어떤 정보가 필요한지 안내해주세요."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"피드백 생성 중 오류가 발생했습니다: {str(e)}"

# 챗봇 응답 생성 함수
def get_chat_response(messages):
    """GPT-4o-mini를 사용하여 챗봇 응답을 생성합니다."""
    
    system_message = {
        "role": "system",
        "content": """당신은 강의 개선을 돕는 전문 컨설턴트입니다. 
강사들이 자신의 강의를 개선할 수 있도록 구체적이고 실용적인 조언을 제공합니다.
친절하고 전문적인 톤으로 대화하며, 강사의 질문에 명확하게 답변해주세요."""
    }
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_message] + messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"응답 생성 중 오류가 발생했습니다: {str(e)}"

# 메인 UI
st.title("🎓 강의 영상 피드백 챗봇")
st.markdown("---")

# 1. 유튜브 URL 입력 섹션
st.header("📹 강의 영상 URL 입력")
col1, col2 = st.columns([4, 1])

with col1:
    video_url_input = st.text_input(
        "유튜브 영상 URL을 입력하세요",
        value=st.session_state.video_url,
        placeholder="예: https://www.youtube.com/watch?v=VIDEO_ID"
    )

with col2:
    analyze_button = st.button("분석하기", type="primary", use_container_width=True)

# 영상 분석 처리
if analyze_button and video_url_input:
    video_id = extract_youtube_id(video_url_input)
    
    if video_id:
        st.session_state.video_url = video_url_input
        
        with st.spinner("영상을 분석하고 피드백을 생성하는 중..."):
            feedback = analyze_video(video_url_input, video_id)
            st.session_state.feedback = feedback
            st.session_state.video_analyzed = True
            
            # 피드백을 챗봇 히스토리에 추가
            st.session_state.messages = [
                {"role": "assistant", "content": f"**[영상 분석 피드백]**\n\n{feedback}"}
            ]
        
        st.success("분석이 완료되었습니다!")
        st.rerun()
    else:
        st.error("유효한 유튜브 URL을 입력해주세요.")

# 2. 피드백 표시 섹션
if st.session_state.video_analyzed and st.session_state.video_url:
    st.markdown("---")
    st.header("📊 영상 피드백")
    
    # 유튜브 비디오 임베드
    video_id = extract_youtube_id(st.session_state.video_url)
    if video_id:
        st.video(f"https://www.youtube.com/watch?v={video_id}")
    
    st.markdown("---")

# 3. 챗봇 섹션
if st.session_state.video_analyzed:
    st.header("💬 피드백 관련 채팅")
    st.markdown("피드백에 대해 궁금한 점을 질문하거나, 추가 조언을 받아보세요.")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 어시스턴트 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                response = get_chat_response(st.session_state.messages)
                st.markdown(response)
        
        # 어시스턴트 응답 추가
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

else:
    st.info("👆 먼저 유튜브 영상 URL을 입력하고 '분석하기' 버튼을 클릭해주세요.")

# 사이드바: 추가 정보 및 옵션
with st.sidebar:
    st.header("ℹ️ 사용 방법")
    st.markdown("""
    1. 강의 영상의 유튜브 URL을 입력하세요
    2. '분석하기' 버튼을 클릭하세요
    3. AI가 생성한 피드백을 확인하세요
    4. 피드백에 대해 질문하거나 추가 조언을 받으세요
    """)
    
    st.markdown("---")
    
    if st.session_state.video_analyzed:
        st.success(f"✅ 분석 완료")
        if st.button("새로운 영상 분석하기"):
            st.session_state.messages = []
            st.session_state.video_analyzed = False
            st.session_state.video_url = ""
            st.session_state.feedback = ""
            st.rerun()
    
    st.markdown("---")
    st.caption("Powered by OpenAI GPT-4o-mini")
