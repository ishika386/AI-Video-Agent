import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────────
# Modern, vibrant, dark SaaS aesthetic.
# Palette: deep indigo-black base, electric indigo + hot pink + teal accents.
# Type: Plus Jakarta Sans (display/UI) + Inter (body) + JetBrains Mono (transcript data)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0b0b14;
    --surface: #14141f;
    --surface-2: #1b1b2a;
    --border: #2a2a3d;
    --accent: #7c6cff;
    --accent-2: #ff5fa2;
    --accent-3: #17e3c4;
    --gradient: linear-gradient(135deg, #7c6cff 0%, #ff5fa2 100%);
    --text: #f5f5fb;
    --text-muted: #8d8da8;
    --danger: #ff5470;
    --success: #17e3c4;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

/* soft ambient glow blobs, fixed in background */
.stApp::before {
    content: '';
    position: fixed;
    top: -10%; left: -5%;
    width: 40vw; height: 40vw;
    background: radial-gradient(circle, rgba(124,108,255,0.16), transparent 70%);
    pointer-events: none;
    z-index: 0;
}
.stApp::after {
    content: '';
    position: fixed;
    bottom: -15%; right: -10%;
    width: 45vw; height: 45vw;
    background: radial-gradient(circle, rgba(255,95,162,0.12), transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

.side-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.2rem;
}
.side-brand-mark {
    width: 34px; height: 34px;
    border-radius: 9px;
    background: var(--gradient);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.side-brand-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.05rem;
    line-height: 1.15;
}
.side-brand-sub {
    color: var(--text-muted);
    font-size: 0.72rem;
    margin: 0.15rem 0 1.2rem 0.05rem;
}

.field-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1rem 0 0.4rem 0;
}

/* ── Headings ── */
h1, h2, h3, h4, h5, h6 { font-family: 'Plus Jakarta Sans', sans-serif !important; color: var(--text) !important; }

/* ── Hero ── */
.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--accent);
    background: rgba(124,108,255,0.12);
    border: 1px solid rgba(124,108,255,0.28);
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
}
.eyebrow-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--gradient); }

.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.1rem, 4.4vw, 3.4rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.02em;
    margin: 0.7rem 0 0.5rem 0;
    background: linear-gradient(135deg, #ffffff 20%, var(--accent) 65%, var(--accent-2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 0.98rem;
    color: var(--text-muted);
    max-width: 560px;
    line-height: 1.6;
    margin-bottom: 1.4rem;
}

/* ── Cards ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    transition: border-color 0.2s, transform 0.2s;
}
.card:hover { border-color: rgba(124,108,255,0.4); }

.card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.85rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title .icon-chip {
    width: 26px; height: 26px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    background: rgba(124,108,255,0.14);
}

.card-content {
    font-size: 0.9rem;
    line-height: 1.75;
    color: var(--text-muted);
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.22rem 0.65rem;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-violet { background: rgba(124,108,255,0.14); color: #a79cff; border: 1px solid rgba(124,108,255,0.3); }
.badge-pink   { background: rgba(255,95,162,0.14);  color: #ff8fc2; border: 1px solid rgba(255,95,162,0.3); }
.badge-teal   { background: rgba(23,227,196,0.14);  color: #5cf0da; border: 1px solid rgba(23,227,196,0.3); }

/* ── Inputs & buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,108,255,0.18) !important;
}

.stButton > button {
    background: var(--gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 28px rgba(124,108,255,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
}

/* ── Pipeline step pills ── */
.step-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 0.75rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin: 0.35rem 0;
    font-size: 0.8rem;
}
.step-icon {
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem;
    flex-shrink: 0;
    background: var(--border);
    color: var(--text-muted);
}
.step-pending .step-icon { background: var(--border); color: var(--text-muted); }
.step-active  .step-icon { background: var(--gradient); color: white; animation: softpulse 1.3s ease-in-out infinite; }
.step-done    .step-icon { background: rgba(23,227,196,0.2); color: var(--success); }
@keyframes softpulse { 0%,100% { opacity: 1; } 50% { opacity: 0.55; } }
.step-pending .step-text { color: var(--text-muted); }
.step-active  .step-text { color: var(--text); font-weight: 600; }
.step-done    .step-text { color: var(--text); }

/* ── Chat ── */
.chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-msg { margin-bottom: 1.1rem; display: flex; flex-direction: column; gap: 0.3rem; }
.chat-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
}
.user-label { color: var(--accent-2); }
.bot-label  { color: var(--accent-3); }

.chat-bubble {
    display: inline-block;
    padding: 0.65rem 1rem;
    border-radius: 14px;
    font-size: 0.88rem;
    line-height: 1.6;
    max-width: 90%;
}
.user-bubble { background: rgba(255,95,162,0.1); border: 1px solid rgba(255,95,162,0.22); align-self: flex-end; border-bottom-right-radius: 4px; }
.bot-bubble  { background: rgba(23,227,196,0.08); border: 1px solid rgba(23,227,196,0.2); align-self: flex-start; border-bottom-left-radius: 4px; }

/* ── Transcript box ── */
.transcript-box {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.85;
    max-height: 300px;
    overflow-y: auto;
    color: var(--text-muted);
    white-space: pre-wrap;
    word-break: break-word;
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.6rem 0 !important; }

.stProgress > div > div > div { background: var(--gradient) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }
label { color: var(--text-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ────────────────────────────────────────────────────────────────────
def step_css(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "active": return "step-active"
    if s == "done":   return "step-done"
    return "step-pending"

def step_icon_char(steps: dict, key: str) -> str:
    s = steps.get(key, "pending")
    if s == "done": return "✓"
    if s == "active": return "●"
    return "○"

def render_step(label: str, key: str):
    css = step_css(st.session_state.pipeline_steps, key)
    icon = step_icon_char(st.session_state.pipeline_steps, key)
    st.markdown(f"""
    <div class="step-row {css}">
        <div class="step-icon">{icon}</div>
        <span class="step-text">{label}</span>
    </div>""", unsafe_allow_html=True)

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="side-brand">
        <div class="side-brand-mark">✦</div>
        <div class="side-brand-text">AI Video<br>Assistant</div>
    </div>
    <div class="side-brand-sub">Meeting intelligence, in one place</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="field-label">Input source</div>', unsafe_allow_html=True)
    source = st.text_input("YouTube URL or File Path", placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4", label_visibility="collapsed")

    st.markdown('<div class="field-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("✦  Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown("---")
        st.markdown('<div class="field-label">Pipeline status</div>', unsafe_allow_html=True)
        for step, label in [
            ("audio",      "Audio processing"),
            ("transcript", "Transcription"),
            ("title",      "Title generation"),
            ("summary",    "Summarisation"),
            ("extract",    "Extraction"),
            ("rag",        "RAG engine"),
        ]:
            render_step(label, step)

# ─── Main Area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="eyebrow"><span class="eyebrow-dot"></span> AI-Powered Meeting Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Turn any recording<br>into instant clarity</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Drop in a YouTube link or a local file — get a clean transcript, summary, action items, and a chat interface to query the whole meeting.</div>', unsafe_allow_html=True)
st.markdown("---")

# ── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Please enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("Pipeline running — see sidebar for live status…")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items  = extract_action_items(transcript)
            decisions     = extract_key_decisions(transcript)
            questions     = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("Analysis complete!")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k in ["audio","transcript","title","summary","extract","rag"]:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"Error: {e}")

# ── Results ──────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="icon-chip">📌</span> Session Title</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.4rem;font-weight:800;color:var(--text)">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top row: summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title"><span class="icon-chip">📋</span> Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    # Second row: action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title"><span class="icon-chip">✅</span> Action Items <span class="badge badge-violet">Do</span></div>
            <div class="card-content">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title"><span class="icon-chip">🔑</span> Key Decisions <span class="badge badge-pink">Locked</span></div>
            <div class="card-content">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title"><span class="icon-chip">❓</span> Open Questions <span class="badge badge-teal">Open</span></div>
            <div class="card-content">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── RAG Chat ──────────────────────────────────────────────────────────────
    st.markdown('<div class="eyebrow"><span class="eyebrow-dot"></span> Ask the meeting</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:1.3rem;font-weight:800;margin:0.6rem 0 1rem 0">Chat with your meeting</div>', unsafe_allow_html=True)

    # Chat history display
    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-end">
                    <span class="chat-label user-label">You</span>
                    <div class="chat-bubble user-bubble">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg" style="align-items:flex-start">
                    <span class="chat-label bot-label">Assistant</span>
                    <div class="chat-bubble bot-bubble">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2rem">
            <div style="font-size:1.8rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.85rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    # Chat input
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Your question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    # Empty state
    st.markdown("""
    <div class="card" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4.5rem 2rem;text-align:center">
        <div style="width:56px;height:56px;border-radius:16px;background:var(--gradient);display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin-bottom:1.2rem">✦</div>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:0.5rem">
            Ready when you are
        </div>
        <div style="color:var(--text-muted);font-size:0.9rem;max-width:380px;line-height:1.7">
            Paste a YouTube URL or local file path in the sidebar, choose your language, and hit <strong>Analyse</strong> to get started.
        </div>
        <div style="margin-top:1.8rem;display:flex;gap:0.6rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-violet">Transcription</span>
            <span class="badge badge-pink">Summarisation</span>
            <span class="badge badge-teal">RAG Chat</span>
        </div>
    </div>""", unsafe_allow_html=True)