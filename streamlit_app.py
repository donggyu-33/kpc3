import streamlit as st
from openai import OpenAI
import tempfile
import os
import time
import re 
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="강의 음성 피드백 챗봇", # 페이지 제목 수정
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🌟 블랙 톤 UI 스타일 🌟
st.markdown("""
<style>
    /* 전체 배경 및 기본 색상 */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* 메인 타이틀 */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 구분선 */
    hr {
        border-color: #333333 !important;
        margin: 2rem 0 !important;
    }
    
    /* 카드/컨테이너 스타일 */
    .element-container, .stMarkdown, div[data-testid="stMarkdownContainer"] {
        color: #e0e0e0 !important;
    }
    
    /* 분석하기 버튼 (Primary) */
    div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    /* 분석하기 버튼의 모든 자식 요소 */
    div[data-testid="column"]:nth-of-type(1) button * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    /* 분석하기 버튼 hover */
    div[data-testid="column"]:nth-of-type(1) button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* 분석하기 버튼 hover의 모든 자식 요소 */
    div[data-testid="column"]:nth-of-type(1) button:hover * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    /* 초기화 버튼 */
    div[data-testid="column"]:nth-of-type(2) button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #999999 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        caret-color: #000000 !important;
    }
    
    /* 초기화 버튼의 모든 자식 요소 - 더 강력하게 */
    div[data-testid="column"]:nth-of-type(2) button,
    div[data-testid="column"]:nth-of-type(2) button *,
    div[data-testid="column"]:nth-of-type(2) button *::before,
    div[data-testid="column"]:nth-of-type(2) button *::after {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
        text-shadow: none !important;
    }
    
    /* 초기화 버튼 내 텍스트 노드 */
    div[data-testid="column"]:nth-of-type(2) button div,
    div[data-testid="column"]:nth-of-type(2) button p,
    div[data-testid="column"]:nth-of-type(2) button span,
    div[data-testid="column"]:nth-of-type(2) button svg {
        color: #000000 !important;
        fill: #000000 !important;
    }
    
    /* 초기화 버튼 hover */
    div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #f0f0f0 !important;
        border-color: #667eea !important;
        color: #000000 !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* 초기화 버튼 hover의 모든 자식 요소 - 더 강력하게 */
    div[data-testid="column"]:nth-of-type(2) button:hover,
    div[data-testid="column"]:nth-of-type(2) button:hover *,
    div[data-testid="column"]:nth-of-type(2) button:hover *::before,
    div[data-testid="column"]:nth-of-type(2) button:hover *::after {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
    }
    
    /* 초기화 버튼 active */
    div[data-testid="column"]:nth-of-type(2) button:active {
        background-color: #e0e0e0 !important;
        color: #000000 !important;
    }
    
    /* 초기화 버튼 active의 모든 자식 요소 */
    div[data-testid="column"]:nth-of-type(2) button:active,
    div[data-testid="column"]:nth-of-type(2) button:active * {
        color: #000000 !important;
        fill: #000000 !important;
    }
    
    /* 초기화 버튼 active의 모든 자식 요소 */
    div[data-testid="column"]:nth-of-type(2) button:active * {
        color: #000000 !important;
        fill: #000000 !important;
    }
    
    /* 파일 업로더 스타일 */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #1a1a1a !important;
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        padding: 2rem !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #764ba2 !important;
        background-color: #252525 !important;
    }
    
    /* 알림 박스 스타일 */
    .stAlert {
        background-color: #1a1a1a !important;
        border-left: 4px solid #667eea !important;
        color: #e0e0e0 !important;
    }
    
    /* Warning */
    div[data-baseweb="notification"][kind="warning"] {
        background-color: #2a1a0a !important;
        border-left: 4px solid #ff9800 !important;
    }
    
    /* Success */
    div[data-baseweb="notification"][kind="success"] {
        background-color: #0a2a1a !important;
        border-left: 4px solid #4caf50 !important;
    }
    
    /* Error */
    div[data-baseweb="notification"][kind="error"] {
        background-color: #2a0a0a !important;
        border-left: 4px solid #f44336 !important;
    }
    
    /* Info */
    div[data-baseweb="notification"][kind="info"] {
        background-color: #0a1a2a !important;
        border-left: 4px solid #667eea !important;
    }
    
    /* 텍스트 영역 */
    textarea {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* 읽기전용 textarea */
    textarea[disabled] {
        color: #b0b0b0 !important;
        -webkit-text-fill-color: #b0b0b0 !important;
        opacity: 1 !important;
        cursor: text !important;
        background-color: #0f0f0f !important;
    }
    
    /* 입력 필드 */
    input {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* 채팅 메시지 */
    .stChatMessage {
        background-color: #1a1a1a !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    /* 사용자 메시지 */
    div[data-testid="stChatMessageContent"][data-role="user"] {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%) !important;
        border-left: 3px solid #667eea !important;
    }
    
    /* 어시스턴트 메시지 */
    div[data-testid="stChatMessageContent"][data-role="assistant"] {
        background-color: #1a1a1a !important;
        border-left: 3px solid #4caf50 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: #252525 !important;
        border-color: #667eea !important;
    }
    
    /* 전송 버튼 (form 내부) */
    .stForm button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    /* 모든 버튼의 텍스트 색상 (흰 배경 대비) */
    button {
        color: #000000 !important;
    }
    
    /* Streamlit 버튼 내부 엘리먼트 */
    div[data-testid="column"]:nth-of-type(2) button p {
        color: #000000 !important;
    }
    div[data-testid="column"]:nth-of-type(2) button span {
        color: #000000 !important;
    }
    
    /* Primary 버튼 텍스트 색상 (검은 배경 및 그라디언트) */
    button[kind="primary"],
    .stButton > button {
        color: #000000 !important;
    }
    
    /* 특정 Primary 버튼 (분석하기) - 흰 글씨 유지 */
    div[data-testid="column"]:nth-of-type(1) button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
    }
    div[data-testid="column"]:nth-of-type(1) button p,
    div[data-testid="column"]:nth-of-type(1) button span {
        color: #ffffff !important;
    }
    
    /* Form 전송 버튼 */
    .stForm button {
        color: #000000 !important;
    }
    }
    
    /* Secondary 버튼 */
    button[kind="secondary"] {
        color: #000000 !important;
    }
    
    /* File uploader 버튼 */
    section[data-testid="stFileUploadDropzone"] button {
        color: #000000 !important;
    }
    
    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #0f0f0f !important;
        border-right: 1px solid #333333 !important;
    }
    section[data-testid="stSidebar"] button {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
    }
    section[data-testid="stSidebar"] button:hover {
        background-color: #2a2a2a !important;
        border-color: #667eea !important;
    }
    
    /* 캡션 */
    .css-1v0mbdj, .stCaptionContainer {
        color: #888888 !important;
    }
    
    /* Markdown 리스트 */
    li {
        color: #e0e0e0 !important;
    }
    
    /* 코드 블록 */
    code {
        background-color: #1a1a1a !important;
        color: #667eea !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }
    
    /* 링크 */
    a {
        color: #667eea !important;
    }
    a:hover {
        color: #764ba2 !important;
    }
</style>
<script>
    function updateFileUploaderText() {
        const dropzone = document.querySelector('section[data-testid="stFileUploadDropzone"]');
        
        if (dropzone) {
            // 1. "Limit..." 텍스트를 담고 있는 small 태그 찾기
            const limitElement = dropzone.querySelector('small');
            
            if (limitElement && limitElement.textContent.includes('Limit')) {
                limitElement.textContent = '최대 10MB • MP3, WAV, M4A, AAC'; 
            }

            // 2. "Drag and drop file here" 텍스트를 담고 있는 p 태그 찾기
            const dragText = dropzone.querySelector('div[data-testid="stMarkdownContainer"] p');
            if (dragText && dragText.textContent.includes('Drag')) {
                dragText.textContent = '여기에 음성 파일을 드래그하여 업로드하세요'; 
            }
            
            if (limitElement && !limitElement.textContent.includes('Limit')) {
                return true; 
            }
        }
        return false; 
    }

    updateFileUploaderText(); 
    
    const intervalId = setInterval(() => {
        const success = updateFileUploaderText();
        if (success) {
            clearInterval(intervalId);
        }
    }, 500); 
</script>
""", unsafe_allow_html=True)
# --- CSS 및 JS 끝 ---

@st.cache_resource
def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
        st.stop()
    return OpenAI(api_key=api_key)

client = get_openai_client()

# 세션 상태 초기화 (유지)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_analyzed" not in st.session_state:
    st.session_state.video_analyzed = False
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "scores" not in st.session_state: 
    st.session_state.scores = {}
if "analyzing" not in st.session_state:
    st.session_state.analyzing = False
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "uploaded_file_size" not in st.session_state:
    st.session_state.uploaded_file_size = None


# --- 핵심 함수 영역 ---

# Whisper API로 오디오를 텍스트 및 segment 정보로 변환 (유지)
def transcribe_audio(audio_path):
    # 파일 크기 확인 (Whisper API는 25MB 제한)
    file_size = os.path.getsize(audio_path)
    max_whisper_size = 25 * 1024 * 1024  # 25MB
    
    if file_size > max_whisper_size:
        raise Exception(f"파일이 너무 큽니다 ({file_size / 1024 / 1024:.1f}MB). 25MB 이하의 파일을 업로드해주세요.")
    
    with open(audio_path, "rb") as audio_file:
        transcript_json = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            language="ko"
        )
    
    transcript = transcript_json.text if hasattr(transcript_json, 'text') else ""
    segments = transcript_json.segments if hasattr(transcript_json, 'segments') else []
    
    return transcript, segments


# 🌟 analyze_transcript 복구: 5가지 기준 및 JSON 출력 로직 통합 🌟
def analyze_transcript(transcript, segments):
    # 말의 속도(분당 단어 수) 계산 (유지)
    wpm = "N/A"
    try:
        if segments:
            total_words = 0
            for seg in segments:
                if hasattr(seg, 'text'):
                    total_words += len(seg.text.split())
            
            start_time = segments[0].start
            end_time = segments[-1].end
            
            total_time = end_time - start_time
            if total_time > 0:
                wpm = round(total_words / (total_time / 60), 2)
    except Exception as e:
        wpm = "N/A"

    
    # 🌟 5가지 평가 기준을 반영한 시스템 프롬프트 (복구) 🌟
    system_prompt = f"""당신은 한국생산성본부(KPC)의 사내 강사 육성 전문 코치입니다. 
강의 음성 파일의 자막을 바탕으로 청각적 전달력과 내용 구조에 초점을 맞춘 5가지 핵심 평가 기준에 따라 강의를 분석하고 평가합니다.

평가 기준은 다음과 같습니다 (총점 5점 만점):
1. **🎯 청중 적합성 및 목표 달성**: 강의 내용, 용어, 난이도가 청중의 니즈에 적합한가?
2. **📢 음성 및 발음 명료도**: 발음 정확성, 전달력이 명확하며, **군말(Filler Words)** 사용이 적절히 억제되었는가?
3. **⏱️ 속도 및 완급 조절**: 강의 속도(약 {wpm} WPM)가 적절하며, 내용의 중요도에 따라 완급 조절이 효과적인가?
4. **🏗️ 강의 구조 및 흐름**: 기승전결(서론, 본론, 결론)이 명확하고, 내용 간의 논리적 연결(스트로크)이 체계적인가?
5. **🔥 몰입 유도 및 흥미도**: 청중의 집중력을 높이는 기법(질문, 비유, 흥미로운 예시, 에너지 변화)이 효과적으로 활용되었는가?

피드백은 반드시 다음의 세 부분으로 구성되어야 합니다:

**A. 정량 평가 (JSON 형식):** 각 기준에 대해 5점 만점의 점수를 부여하고, 점수와 기준을 담아 JSON 오브젝트만 반환합니다.
**B. 정량 평가 근거 (JSON 형식):** 각 기준 점수에 대한 간결한 근거/의견을 항목별로 JSON으로 반환합니다.
**C. 정성 피드백 (Markdown 형식):** 각 기준에 대한 구체적인 강점/약점 분석 및 개선 제안을 마크다운 형식으로 작성합니다.

일관성 규칙:
- 어떤 기준의 점수가 **4.0 미만**이면, 해당 기준의 정성 피드백에는 반드시 **구체적인 약점**과 **개선 제안**을 최소 2개 이상 포함하세요.
- 점수가 3.0 이하인 항목은 특히 집중적으로 분석하고, 약점 섹션에서 최소 3개 이상의 구체적 사례를 제시하세요.
- 정성 피드백의 강점/약점 분석이 정량 점수와 일치해야 합니다 (높은 점수 항목은 강점 중심, 낮은 점수 항목은 약점 중심).

반드시 정량 평가와 정성 피드백을 구분하여 출력해야 합니다.
"""

    user_prompt = f"""다음은 강의 시연 음성의 전체 자막(음성 인식 결과)입니다. 이 내용을 바탕으로 강의를 분석하고 평가해주세요.

---
자막:
{transcript}
---

**중요 평가 지침:**
- 점수는 **0.1점 단위로 정밀하게** 부여하세요 (예: 3.2, 4.7 등).
- 후한 점수보다 **정확하고 객관적인 피드백**을 우선하세요.
- 완벽한 강의(5.0점)는 극히 드물며, 대부분의 강의는 개선의 여지가 있습니다.
- 평균적인 강의는 3.0~3.5점 수준이며, 우수한 강의는 4.0~4.5점입니다.

**약점 및 개선 제안 작성 시 필수 사항:**
- 약점을 언급할 때는 **반드시 자막에서 해당 부분의 실제 텍스트를 직접 인용**하세요.
- 예시: "약점: '여기서 중요한 건... 음... 그러니까...'라는 부분에서 군말이 과도하게 사용되고 있습니다."
- 예시: "약점: '첫 번째로 설명드릴 내용은...'부터 약 2분간 서론이 지나치게 길어 본론 진입이 늦어집니다."
- 각 약점마다 **구체적인 자막 인용**을 포함해야 하며, 추상적으로만 언급하지 마세요.
- 강점과 약점, 개선제안을 명확하게 구분하여 작성하세요.

규정된 5가지 기준에 따라 1.0점부터 5.0점까지 점수를 부여하고, 아래와 같은 형식으로 결과를 출력해주세요.

### 1. 정량 평가 (점수)
```json
{{
    "청중 적합성 및 목표 달성": [점수],
    "음성 및 발음 명료도": [점수],
    "속도 및 완급 조절": [점수],
    "강의 구조 및 흐름": [점수],
    "몰입 유도 및 흥미도": [점수]
}}
```

### 1-1. 정량 평가 근거 (항목별 의견)
```json
{{
    "청중 적합성 및 목표 달성": "[근거/의견]",
    "음성 및 발음 명료도": "[근거/의견]",
    "속도 및 완급 조절": "[근거/의견]",
    "강의 구조 및 흐름": "[근거/의견]",
    "몰입 유도 및 흥미도": "[근거/의견]"
}}
```

### 2. 정성 피드백

**정성 피드백 작성 규칙:**
각 평가 기준마다 아래 형식을 따라 작성하세요:
1. **강점**: 현재 강의에서 잘한 부분 (구체적 사례 포함)
2. **약점**: 개선이 필요한 부분 (반드시 자막에서 직접 인용한 사례와 함께 설명)
3. **개선제안**: 구체적이고 실행 가능한 개선 방안

#### 🎯 청중 적합성 및 목표 달성
**강점:** [구체적인 강점 사항]

**약점:** [약점 설명 + 자막 인용 예시: "예: '내용' 부분에서 ..."]

**개선제안:** [구체적인 개선 방안]

#### 📢 음성 및 발음 명료도
**강점:** [구체적인 강점 사항]

**약점:** [약점 설명 + 군말/발음 문제 자막 인용 예시: "예: '...음... ...'와 같이 군말 사용"]

**개선제안:** [구체적인 개선 방안]

#### ⏱️ 속도 및 완급 조절
**강점:** [구체적인 강점 사항]

**약점:** [약점 설명 + 속도/완급 문제 자막 인용 예시]

**개선제안:** [구체적인 개선 방안]

#### 🏗️ 강의 구조 및 흐름
**강점:** [구체적인 강점 사항]

**약점:** [약점 설명 + 구조 문제 자막 인용 예시: "예: '...' 부분부터 약 X분간 ..."]

**개선제안:** [구체적인 개선 방안]

#### 🔥 몰입 유도 및 흥미도
**강점:** [구체적인 강점 사항]

**약점:** [약점 설명 + 몰입도 부족 자막 인용 예시]

**개선제안:** [구체적인 개선 방안]

#### 🔥 몰입 유도 및 흥미도
[구체적 강점 및 약점 분석]

#### 💡 종합 개선 제안
[우선순위가 높은 개선 사항 3가지]
"""

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


# 챗봇 응답 생성 함수 (유지)
def get_chat_response(messages, initial_feedback, transcript=""):
    # initial_feedback과 transcript를 포함하여 시스템 메시지를 강화
    system_message = {
        "role": "system",
        "content": f"""당신은 강의 개선을 돕는 전문 컨설턴트입니다. 
        사용자(강사)는 방금 분석된 자신의 강의 피드백에 대해 질문하고 있습니다. 
        
        **분석된 강의 피드백:** 
        ---
        {initial_feedback}
        ---
        
        **강의 자막 원본:**
        ---
        {transcript}
        ---
        
        **대화 가이드:**
        1. 사용자의 질문에 답변할 때, 분석 피드백의 정성평가 섹션에서 언급된 강점/약점/개선제안을 직접 참고하세요.
        2. 사용자가 특정 항목(예: 음성 명료도, 강의 구조 등)에 대해 질문하면, 그 항목에 대한 정성평가 내용을 중심으로 답변하세요.
        3. 자막에서 해당 부분을 직접 인용하여 구체적이고 실질적인 조언을 제공하세요.
        4. 약점에 대한 질문에는 제시된 개선제안을 바탕으로 실행 가능한 방법들을 제시하세요.
        5. 정량평가의 점수가 낮은 항목에 대해서는 더욱 상세하고 집중적인 조언을 제공하세요.
        
        친절하고 전문적인 톤으로 대화하세요."""
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


# --- 메인 UI 영역 ---

# 메인 UI
st.title("🎓 시연강의 셀프분석 APP")
st.markdown("이 어플리케이션은 한국생산성본부 사내강사양성(기본)과정 수강생을 위하여 개발되었습니다.\n\n교육을 수강하고 귀가 후 본인의 강의에 대한 추가적인 피드백이 필요할때, 시연강의를 녹음하여 업로드하면 생성형 AI 기반으로 시연 강의를 분석하여 드립니다. :)")
st.markdown("---")

# 1. 음성 파일 업로드 섹션
st.header("👨‍🏫 시연강의 업로드")
# JS로 텍스트를 변경하므로, Python의 st.warning은 간결하게 유지
st.warning("⚠️ 필수: 음성 파일은 10MB 이하로 업로드해주세요.")

# 초기화 후 파일 업로더 상태를 초기화하기 위해 key 사용
uploaded_file = st.file_uploader(
    "분석할 강의 시연 음성 파일을 업로드하세요 (mp3, wav, m4a 등)", 
    type=["mp3", "wav", "m4a", "aac"],
    key=f"file_uploader_{st.session_state.video_analyzed}"  # 분석 상태에 따라 key 변경
)

# 분석 중 상태 표시
if st.session_state.get('analyzing', False):
    st.info("🔄 분석 중입니다... 잠시만 기다려주세요.")

# 업로드된 파일 정보 저장 및 표시
if uploaded_file:
    # 새로운 파일이 업로드되었을 때 session state에 저장
    st.session_state.uploaded_file_name = uploaded_file.name
    st.session_state.uploaded_file_size = uploaded_file.size / 1024 / 1024
    
    file_size_mb = uploaded_file.size / 1024 / 1024
    st.caption(f"📎 업로드된 파일: {uploaded_file.name} ({file_size_mb:.2f}MB)")
    if file_size_mb > 10:
        st.error(f"⚠️ 파일 크기가 {file_size_mb:.2f}MB로 10MB를 초과합니다. 10MB 이하의 파일을 업로드해주세요.")
elif st.session_state.get('uploaded_file_name'):
    # 분석 후에도 업로드된 파일 정보 표시
    file_size_mb = st.session_state.uploaded_file_size
    st.caption(f"📎 업로드된 파일: {st.session_state.uploaded_file_name} ({file_size_mb:.2f}MB)")

col1, col2 = st.columns([1, 1])
with col1:
    # "분석하기" 버튼: 파일이 업로드되었거나 이전에 파일이 있었을 때 활성화
    analyze_button = st.button(
        "분석하기", 
        type="primary", 
        use_container_width=True, 
        disabled=st.session_state.get('analyzing', False) or (not uploaded_file and not st.session_state.get('uploaded_file_name'))
    )
with col2:
    reset_button = st.button("초기화", use_container_width=True)

# 초기화 버튼 처리
if reset_button:
    st.session_state.messages = []
    st.session_state.video_analyzed = False
    st.session_state.feedback = ""
    st.session_state.transcript = ""
    st.session_state.segments = []
    st.session_state.scores = {}
    st.session_state.analyzing = False
    st.session_state.uploaded_file_name = None  # 업로드된 파일 정보 초기화
    st.session_state.uploaded_file_size = None
    # 파일 업로더 상태도 초기화되도록 rerun 호출
    st.rerun()


# 음성 분석 처리
if analyze_button and (uploaded_file or st.session_state.get('uploaded_file_name')):
    # 분석 중 상태로 설정
    st.session_state.analyzing = True
    
    # 새로운 파일이 업로드된 경우 또는 기존 파일로 재분석하는 경우
    current_file = uploaded_file if uploaded_file else None
    
    if not current_file and st.session_state.get('uploaded_file_name'):
        # 재분석: 기존 파일로 다시 분석하려고 함
        # 이 경우 임시 파일을 다시 생성할 수 없으므로 사용자에게 파일을 다시 업로드하도록 요청
        st.warning("재분석을 위해서는 파일을 다시 업로드해주세요.")
        st.session_state.analyzing = False
        st.stop()
    
    # 파일 크기 체크 (10MB = 10485760 bytes)
    file_size = current_file.size
    file_size_mb = file_size / 1024 / 1024
    
    if file_size > 10485760:  # 10MB
        st.error(f"⚠️ 파일 크기가 {file_size_mb:.2f}MB로 너무 큽니다. 10MB 이하의 파일을 업로드해주세요.")
        st.session_state.analyzing = False
        st.stop()
    
    try:
        # tempfile을 사용하여 업로드된 파일의 확장자를 유지
        temp_suffix = os.path.splitext(current_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=temp_suffix) as tmp_audio:
            tmp_audio.write(current_file.read())
            tmp_audio_path = tmp_audio.name
        
        st.info(f"📤 파일 업로드 완료 ({file_size_mb:.2f}MB)")
        
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # 🎙️ 1단계: Whisper 음성 인식
        progress_placeholder.info("🎙️음성 인식 중입니다...")
        status_placeholder.caption("⏳ Whisper API 처리 중 (파일 크기에 따라 20초~2분 소요)")
        
        transcript, segments = transcribe_audio(tmp_audio_path)
        st.session_state.transcript = transcript
        st.session_state.segments = segments
        
        # 🤖 2단계: GPT 분석
        progress_placeholder.info("🤖 GPT 분석 중입니다...")
        status_placeholder.caption("⏳ AI 피드백 생성 중 (약 15~30초 소요)")
        
        feedback = analyze_transcript(transcript, segments)
        
        status_placeholder.empty()
        
        # 🌟 점수 추출 로직 추가 🌟
        try:
            # JSON 블록 추출
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', feedback, re.DOTALL)
            if json_match:
                import json
                scores_data = json.loads(json_match.group(1))
                st.session_state.scores = scores_data

            # 근거 JSON 추출 (두 번째 JSON 블록 또는 "정량 평가 근거" 직후 블록)
            rationale_match = None
            # 우선 "정량 평가 근거" 제목 이후의 첫 번째 JSON을 찾기
            rationale_section = re.search(r'정량\s*평가\s*근거[\s\S]*?```json\s*(\{.*?\})\s*```', feedback, re.IGNORECASE)
            if rationale_section:
                rationale_match = rationale_section
            else:
                # 아니면 두 번째 코드 블록을 시도
                code_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', feedback, re.DOTALL)
                if len(code_blocks) >= 2:
                    rationale_json_text = code_blocks[1]
                    import json
                    st.session_state.rationales = json.loads(rationale_json_text)
            if rationale_section:
                import json
                st.session_state.rationales = json.loads(rationale_section.group(1))
        except Exception as e:
            st.session_state.scores = {}
            st.session_state.rationales = {}
        
        progress_placeholder.empty()
        status_placeholder.empty()
        
        st.session_state.feedback = feedback
        st.session_state.video_analyzed = True
        st.session_state.analyzing = False  # 분석 완료
        st.session_state.messages = [
            {"role": "assistant", "content": f"**[음성 분석 피드백]**\n\n{feedback}"}
        ]
        
        os.remove(tmp_audio_path)
        st.success("✅ 분석이 완료되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.session_state.analyzing = False  # 오류 발생 시 상태 초기화
        st.error(f"❌ 오류 발생: {str(e)}")
        if 'tmp_audio_path' in locals() and os.path.exists(tmp_audio_path):
            try:
                os.remove(tmp_audio_path)
            except:
                pass
        st.stop()

elif analyze_button:
    st.error("분석할 음성 파일을 업로드해주세요.")


# 2. 피드백 표시 섹션
if st.session_state.video_analyzed:
    st.markdown("---")
    st.header("📊 시연강의 분석 레포트")
    st.markdown("레포트는 생성형 AI기반으로 작성되었습니다.\n\n정확하지 않을 수 있으니 참고용으로만 활용 부탁드리겠습니다")
    
    # 🌟 1. 평가 기준 안내 🌟
    with st.expander("1. 평가 기준", expanded=False):
        st.markdown("""
        **5가지 핵심 평가 기준 안내:**
        - **🎯 청중 적합성 및 목표 달성**: 강의 내용, 용어, 난이도가 청중의 니즈와 학습 목표에 부합하는지 평가
        - **📢 음성 및 발음 명료도**: 발음의 정확성, 전달력, 군말(음, 아, 그) 사용 빈도 등 음성적 명료성 평가
        - **⏱️ 속도 및 완급 조절**: 강의 진행 속도의 적절성 및 중요 내용 강조를 위한 완급 조절 능력 평가
        - **🏗️ 강의 구조 및 흐름**: 서론-본론-결론의 구조적 명확성과 내용 간 논리적 연결성 평가
        - **🔥 몰입 유도 및 흥미도**: 질문, 비유, 예시 등을 활용한 청중 집중력 유지 및 흥미 유발 능력 평가
        """)
    st.markdown("---")
    # 🌟 2. 정량 평가 (점수 시각화) 🌟
    if st.session_state.scores and len(st.session_state.scores) > 0:
        with st.expander("2. 정량 평가", expanded=False):
            try:
                # 점수 데이터 준비
                categories = list(st.session_state.scores.keys())
                values = list(st.session_state.scores.values())
                
                # 데이터 유효성 검사
                if not categories or not values or len(categories) != len(values):
                    st.warning("점수 데이터가 올바르지 않습니다.")
                else:
                    # 값이 숫자인지 확인
                    try:
                        values = [float(v) for v in values]
                    except (ValueError, TypeError):
                        st.warning("점수 값이 숫자가 아닙니다.")
                    else:
                        # Plotly를 사용한 레이더 차트
                        fig = go.Figure()
                        
                        # 폐곡선을 만들기 위해 첫 번째 점을 마지막에 추가
                        categories_closed = categories + [categories[0]]
                        values_closed = values + [values[0]]
                        text_closed = [f'{v:.1f}' for v in values] + [f'{values[0]:.1f}']
                        
                        fig.add_trace(go.Scatterpolar(
                            r=values_closed,
                            theta=categories_closed,
                            fill='toself',
                            name='평가 점수',
                            line=dict(color='#667eea', width=2),
                            fillcolor='rgba(102, 126, 234, 0.3)',
                            mode='lines+markers+text',
                            text=text_closed,  # 점수 표기
                            textposition='top center',
                            textfont=dict(color='#667eea', size=13, family='Arial Black'),
                            marker=dict(
                                size=10,
                                color='#764ba2',
                                line=dict(color='#667eea', width=2)
                            ),
                            hovertemplate='<b>%{theta}</b><br>점수: %{r:.1f}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 5],
                                    tickcolor='#666666',
                                    gridcolor='#333333',
                                    tickfont=dict(color='#e0e0e0', size=11),
                                ),
                                angularaxis=dict(
                                    tickfont=dict(color='#e0e0e0', size=12),
                                    linecolor='#666666',
                                    rotation=90  # 한 꼭지점이 상단으로 오도록 회전
                                ),
                                bgcolor='rgba(10, 10, 10, 0.5)'
                            ),
                            showlegend=False,
                            title=dict(
                                text='분석 결과',
                                font=dict(color='#ffffff', size=18),
                                x=0.5,
                                xanchor='center'
                            ),
                            paper_bgcolor='#0a0a0a',
                            plot_bgcolor='#0a0a0a',
                            font=dict(color='#e0e0e0', family='Arial'),
                            margin=dict(l=100, r=100, t=120, b=100),
                            height=550
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 점수 근거
                        st.markdown("---")
                        if 'rationales' in st.session_state and st.session_state.rationales:
                            st.markdown("**항목별 점수 근거:**")
                            for cat in categories:
                                rationale = st.session_state.rationales.get(cat, "")
                                if rationale:
                                    st.markdown(f"- **{cat}**: {rationale}")
            except Exception as e:
                st.error(f"정량 평가 렌더링 중 오류: {str(e)}")
    st.markdown("---")
    # 🌟 3. 정성 평가 (상세 피드백) 🌟
    with st.expander("3. 정성 평가", expanded=False):
        feedback_text = st.session_state.feedback
        feedback_text = re.sub(r'###\s*1\.\s*정량\s*평가.*?(?=###\s*2\.\s*정성)', '', feedback_text, flags=re.DOTALL)
        feedback_text = re.sub(r'###\s*2\.\s*정성\s*피드백\s*', '', feedback_text)
        st.markdown(feedback_text)
        with st.expander("🔎 나의 스크립트 보기", expanded=False):
            st.text_area("자막", value=st.session_state.transcript, height=200, disabled=True)
    st.markdown("---")
    # 🌟 4. GPT와 채팅하기 🌟
    with st.expander("4. GPT와 채팅하기", expanded=False):
        st.markdown("피드백에 대해 추가적인 조언을 받아보세요.")
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state.messages):
                if i == 0:
                    continue
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("메시지를 입력하세요...", key="chat_input", label_visibility="collapsed")
            submit_button = st.form_submit_button("전송", use_container_width=True)
        if submit_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("답변 생성 중..."):
                response = get_chat_response(st.session_state.messages, st.session_state.feedback, st.session_state.transcript)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# 분석 전 안내 메시지
else:
    st.info("👆 먼저 강의 시연 음성 파일을 업로드하고 '분석하기' 버튼을 클릭해주세요.")


# 사이드바: 추가 정보 및 옵션 (기존 유지)
with st.sidebar:
    if st.session_state.video_analyzed:
        st.success("✅ 분석 완료")
        if st.button("새로운 분석 시작하기"):
            st.session_state.messages = []
            st.session_state.video_analyzed = False
            st.session_state.feedback = ""
            st.session_state.transcript = ""
            st.session_state.segments = []
            st.session_state.scores = {}
            st.rerun()
        st.markdown("---")
    st.caption("Powered by OpenAI GPT-4o-mini & Whisper-1")