import streamlit as st
from openai import OpenAI
import tempfile
import os
import time
import re 
from streamlit_echarts import st_echarts # 시각화 라이브러리 추가

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
    div[data-testid="column"]:nth-of-type(1) button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* 초기화 버튼 */
    div[data-testid="column"]:nth-of-type(2) button {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #333333 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="column"]:nth-of-type(2) button:hover {
        background-color: #2a2a2a !important;
        border: 1px solid #667eea !important;
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
            response_format="verbose_json"
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
- 어떤 기준의 점수가 **4.0 미만**이면, 해당 기준의 정성 피드백에는 반드시 **구체적인 약점**과 **개선 제안**을 최소 1개 이상 포함하세요.

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
- 약점을 언급할 때는 **반드시 자막에서 해당 부분의 실제 텍스트를 인용**하세요.
- 예시: "'여기서 중요한 건... 음... 그러니까...'라는 부분에서 군말이 과도하게 사용됨"
- 예시: "'첫 번째로 설명드릴 내용은...'부터 약 2분간 서론이 지나치게 길어 본론 진입이 늦어짐"
- 구체적인 증거 없이 추상적으로만 약점을 언급하지 마세요.

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

#### 🎯 청중 적합성 및 목표 달성
[구체적 강점 및 약점 분석]

#### 📢 음성 및 발음 명료도
[구체적 강점 및 약점 분석, 군말 사용 언급]

#### ⏱️ 속도 및 완급 조절
[구체적 강점 및 약점 분석]

#### 🏗️ 강의 구조 및 흐름
[구체적 강점 및 약점 분석]

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
        
        이 피드백과 자막을 참고하여 구체적이고 실용적인 조언을 제공하세요. 
        사용자가 특정 부분에 대해 질문하면 자막에서 해당 부분을 찾아 인용하며 답변하세요.
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
st.markdown("이 어플리케이션은 한국생산성본부 사내강사양성(기본)과정 수강생을 위하여 개발되었습니다. 교육을 수강하고 귀가 후 본인의 강의에 대한 추가적인 피드백이 필요할때, 시연강의를 녹음하여 업로드하면 생성형 AI 기반으로 시연 강의를 분석하여 드립니다. :)")
st.markdown("---")

# 1. 음성 파일 업로드 섹션
st.header("👨‍🏫 시연강의 업로드")
# JS로 텍스트를 변경하므로, Python의 st.warning은 간결하게 유지
st.warning("⚠️ 필수: 음성 파일은 10MB 이하로 업로드해주세요.")
uploaded_file = st.file_uploader("분석할 강의 시연 음성 파일을 업로드하세요 (mp3, wav, m4a 등)", type=["mp3", "wav", "m4a", "aac"])

# 분석 중 상태 표시
if st.session_state.get('analyzing', False):
    st.info("🔄 분석 중입니다... 잠시만 기다려주세요.")

if uploaded_file:
    file_size_mb = uploaded_file.size / 1024 / 1024
    st.caption(f"📎 업로드된 파일: {uploaded_file.name} ({file_size_mb:.2f}MB)")
    if file_size_mb > 10:
        st.error(f"⚠️ 파일 크기가 {file_size_mb:.2f}MB로 10MB를 초과합니다. 10MB 이하의 파일을 업로드해주세요.")

col1, col2 = st.columns([1, 1])
with col1:
    analyze_button = st.button("분석하기", type="primary", use_container_width=True, disabled=st.session_state.get('analyzing', False))
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
    st.rerun()


# 음성 분석 처리
if analyze_button and uploaded_file:
    # 분석 중 상태로 설정
    st.session_state.analyzing = True
    
    # 파일 크기 체크 (10MB = 10485760 bytes)
    file_size = uploaded_file.size
    file_size_mb = file_size / 1024 / 1024
    
    if file_size > 10485760:  # 10MB
        st.error(f"⚠️ 파일 크기가 {file_size_mb:.2f}MB로 너무 큽니다. 10MB 이하의 파일을 업로드해주세요.")
        st.stop()
    
    try:
        # tempfile을 사용하여 업로드된 파일의 확장자를 유지
        temp_suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=temp_suffix) as tmp_audio:
            tmp_audio.write(uploaded_file.read())
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
    
    # 🌟 1. 평가 기준 안내 🌟
    st.subheader("1. 평가 기준")
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
    if st.session_state.scores:
        st.subheader("2. 정량 평가")
        
        # 점수 데이터 준비
        categories = list(st.session_state.scores.keys())
        values = list(st.session_state.scores.values())
        
        # ECharts 오각형(레이더) 차트 옵션 - 블랙 톤
        option = {
            "backgroundColor": "#0a0a0a",
            "title": {
                "text": "5가지 평가 기준 점수",
                "left": "center",
                "textStyle": {
                    "color": "#ffffff",
                    "fontSize": 20,
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "backgroundColor": "#1a1a1a",
                "borderColor": "#667eea",
                "textStyle": {
                    "color": "#e0e0e0"
                }
            },
            "radar": {
                "indicator": [
                    {"name": cat, "max": 5} for cat in categories
                ],
                "radius": 120,
                "splitNumber": 5,
                "axisName": {
                    "color": "#e0e0e0",
                    "fontSize": 12,
                    "fontWeight": "bold"
                },
                "splitLine": {
                    "lineStyle": {
                        "color": "#333333"
                    }
                },
                "splitArea": {
                    "areaStyle": {
                        "color": ["#1a1a1a", "#0f0f0f"]
                    }
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "#667eea"
                    }
                }
            },
            "series": [{
                "name": "평가 점수",
                "type": "radar",
                "data": [{
                    "value": values,
                    "name": "점수",
                    "label": {
                        "show": True,
                        "formatter": "{c}",
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "color": "#667eea"
                    },
                    "areaStyle": {
                        "color": "rgba(102, 126, 234, 0.3)"
                    },
                    "lineStyle": {
                        "color": "#667eea",
                        "width": 3
                    },
                    "itemStyle": {
                        "color": "#764ba2",
                        "borderWidth": 3,
                        "borderColor": "#667eea"
                    }
                }]
            }]
        }
        
        st_echarts(options=option, height="450px")
        
        # 정량 평가 근거 표시 (항목별 의견)
        if 'rationales' in st.session_state and st.session_state.rationales:
            st.markdown("**항목별 점수 근거:**")
            for cat in categories:
                rationale = st.session_state.rationales.get(cat, "")
                if rationale:
                    st.markdown(f"- **{cat}**: {rationale}")
    
    st.markdown("---")
    
    # 🌟 3. 정성 평가 (상세 피드백) 🌟
    st.subheader("3. 정성 평가")
    
    # GPT 피드백에서 "### 1. 정량 평가 (점수)" 섹션 제거
    feedback_text = st.session_state.feedback
    # "### 1. 정량 평가 (점수)" 부터 "### 2. 정성 피드백" 직전까지 제거
    feedback_text = re.sub(r'###\s*1\.\s*정량\s*평가.*?(?=###\s*2\.\s*정성)', '', feedback_text, flags=re.DOTALL)
    # "### 2. 정성 피드백" 헤더도 제거
    feedback_text = re.sub(r'###\s*2\.\s*정성\s*피드백\s*', '', feedback_text)
    
    st.markdown(feedback_text)
    
    with st.expander("🔎 나의 스크립트 보기"):
        st.text_area("자막", value=st.session_state.transcript, height=200, disabled=True)
    st.markdown("---")
    
    # 🌟 4. 피드백 관련 채팅 🌟
    st.subheader("4. GPT와 채팅하기")
    st.markdown("피드백에 대해 추가적인 조언을 받아보세요.")
    
    # 채팅 메시지 표시
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if i == 0: 
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 채팅 입력창 (form 사용하여 엔터키 지원 + 자동 초기화)
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