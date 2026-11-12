import os
import io
import sys
import contextlib
import time
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ==========================================================
# 📌 PROJECT CONFIGURATION & BRANDING
# ==========================================================
PROJECT_NAME = "CodeMentor Hub"
PROJECT_TAGLINE = "Advanced AI Studio & Python Playground"
PAGE_ICON = "🚀"
DEFAULT_MODEL = "gemini-2.5-flash"

# Load API Key from .env
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title=PROJECT_NAME, 
    page_icon=PAGE_ICON, 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN CLEAN UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .sidebar .stSidebar { background-color: #1e293b; }
    div.stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.2s ease-in-out; }
    div.stButton > button:hover { border-color: #38bdf8; color: #38bdf8; }
    .challenge-box { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        border: 1px solid #334155; 
        padding: 18px; 
        border-radius: 12px; 
        margin-bottom: 15px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stTextArea textarea { font-family: 'Fira Code', monospace; background-color: #020617; border-color: #334155; color: #e2e8f0; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("🔑 GEMINI_API_KEY is missing! Please configure your .env file or Streamlit Secrets.")

client = genai.Client(api_key=api_key)

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_challenge" not in st.session_state:
    st.session_state.current_challenge = "Two Sum Problem"
if "challenge_desc" not in st.session_state:
    st.session_state.challenge_desc = "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`."
if "code_history" not in st.session_state:
    st.session_state.code_history = "def two_sum(nums, target):\n    # Write your optimal O(N) solution here\n    pass\n\nprint(two_sum([2, 7, 11, 15], 9))"
if "test_cases" not in st.session_state:
    st.session_state.test_cases = [
        {"input": "([2, 7, 11, 15], 9)", "expected": [0, 1]},
        {"input": "([3, 2, 4], 6)", "expected": [1, 2]}
    ]
if "terminal_output" not in st.session_state:
    st.session_state.terminal_output = "Click '▶ Run Code' or '🧪 Run Tests' to begin execution."

# --- SIDEBAR: CHALLENGE GENERATOR & SETTINGS ---
with st.sidebar:
    st.markdown(f"## ⚙️ {PROJECT_NAME}")
    st.caption(PROJECT_TAGLINE)
    st.divider()
    
    st.markdown("### 🎯 AI Challenge Generator")
    user_custom_topic = st.text_input("Coding Topic / Algorithm:", placeholder="e.g., Valid Parentheses, LRU Cache")
    challenge_difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced FAANG"])
    
    if st.button("✨ Generate AI Challenge", type="primary", use_container_width=True):
        if user_custom_topic:
            with st.spinner("🧠 Generating challenge & test suites..."):
                prompt = f"""
                Create a coding challenge on the topic: '{user_custom_topic}' with difficulty '{challenge_difficulty}'.
                Return valid JSON with keys:
                - title (string)
                - description (string with markdown formatting)
                - starter_code (string python code template)
                - test_cases (list of 2 dictionaries, each having 'input' string representation and 'expected' output representation)
                """
                try:
                    response = client.models.generate_content(
                        model=DEFAULT_MODEL,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.3
                        ),
                    )
                    data = json.loads(response.text)
                    st.session_state.current_challenge = data.get("title", user_custom_topic)
                    st.session_state.challenge_desc = data.get("description", "")
                    st.session_state.code_history = data.get("starter_code", "# Write code here\n")
                    st.session_state.test_cases = data.get("test_cases", [])
                    st.success("Challenge generated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Generation error: {e}")
        else:
            st.warning("Please enter a topic.")
            
    st.divider()
    persona = st.selectbox(
        "🤖 AI Mentor Persona",
        [
            "Professional Python Expert (English)",
            "Strict Technical Interviewer (FAANG)",
            "Senior Python Code Reviewer & Optimizer"
        ]
    )
    
    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN APP HEADER ---
st.markdown(f"<h1 style='font-size: 1.8rem; margin-bottom: 5px;'>{PAGE_ICON} {PROJECT_NAME}</h1>", unsafe_allow_html=True)

# --- MAIN SPLIT LAYOUT (LEFT: CODING | RIGHT: CHAT) ---
left_col, right_col = st.columns([1.2, 0.8], gap="medium")

# ================= LEFT COLUMN: WORKSPACE & TERMINAL =================
with left_col:
    st.markdown(f"""
        <div class='challenge-box'>
            <b>📌 Challenge: {st.session_state.current_challenge}</b><br><br>
            <span style='color: #cbd5e1; font-size: 0.92rem;'>{st.session_state.challenge_desc}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("📝 Python Code Workspace")
    user_code = st.text_area(
        "Workspace Editor",
        value=st.session_state.code_history,
        height=300,
        label_visibility="collapsed"
    )
    st.session_state.code_history = user_code
    
    # Action Buttons
    c1, c2, c3, c4 = st.columns(4)
    run_btn = c1.button("▶ Run Code", type="primary", use_container_width=True)
    test_btn = c2.button("🧪 Run Tests", use_container_width=True)
    review_btn = c3.button("🤖 Code Review", use_container_width=True)
    reset_btn = c4.button("🔄 Reset", use_container_width=True)
    
    if reset_btn:
        st.session_state.code_history = "def solution():\n    pass"
        st.rerun()

    # Code Execution Handler
    if run_btn:
        output_buffer = io.StringIO()
        start_time = time.time()
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                exec_globals = {}
                exec(user_code, exec_globals)
            exec_time = (time.time() - start_time) * 1000
            val = output_buffer.getvalue()
            st.session_state.terminal_output = f"SUCCESS ({exec_time:.2f} ms)\n\n{val if val else '[No stdout output]'}"
        except Exception as e:
            st.session_state.terminal_output = f"❌ RUNTIME ERROR:\n{type(e).__name__}: {e}"

    # Automated Test Cases Runner
    if test_btn:
        test_output = []
        try:
            exec_globals = {}
            exec(user_code, exec_globals)
            func_name = [name for name, obj in exec_globals.items() if callable(obj) and not name.startswith("__")][0]
            func = exec_globals[func_name]
            
            passed = 0
            for i, tc in enumerate(st.session_state.test_cases):
                try:
                    args = eval(tc["input"])
                    if not isinstance(args, tuple):
                        args = (args,)
                    result = func(*args)
                    expected = tc["expected"]
                    if result == expected:
                        test_output.append(f"✅ Test {i+1} Passed (Input: {tc['input']} => Got: {result})")
                        passed += 1
                    else:
                        test_output.append(f"❌ Test {i+1} Failed (Input: {tc['input']} | Expected: {expected} | Got: {result})")
                except Exception as ex:
                    test_output.append(f"❌ Test {i+1} Error: {ex}")
            st.session_state.terminal_output = f"🧪 TEST RESULTS ({passed}/{len(st.session_state.test_cases)} Passed):\n" + "\n".join(test_output)
        except Exception as e:
            st.session_state.terminal_output = f"❌ Test Suite Execution Error: Could not locate testable function or syntax error.\n{e}"

    # AI Code Reviewer Trigger
    if review_btn:
        with st.spinner("🤖 AI Code Reviewer analyzing workspace..."):
            review_prompt = f"""
            Review this student Python code for challenge '{st.session_state.current_challenge}':
            ```python
            {user_code}
            ```
            Provide concise feedback on time complexity O(N), space complexity, best practices, and suggestions for optimization without directly giving away the full solution. (Respond strictly in English).
            """
            response = client.models.generate_content(model=DEFAULT_MODEL, contents=review_prompt)
            st.session_state.terminal_output = f"🤖 AI CODE REVIEW:\n\n{response.text}"

    st.subheader("🖥️ Execution Terminal & Test Results")
    st.code(st.session_state.terminal_output, language="text")


# ================= RIGHT COLUMN: AI MENTOR CHAT =================
with right_col:
    st.subheader("💬 AI Mentor Chat")
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8;'>Ask questions, request hints, or debug your code live.</p>", unsafe_allow_html=True)
    
    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.messages:
            st.info(f"👋 Hello! Welcome to {PROJECT_NAME}. Use the sidebar to generate a challenge or start coding your solution.")
            
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    persona_instructions = {
        "Professional Python Expert (English)": f"You are an expert AI programming mentor at {PROJECT_NAME}. Always respond strictly in clear English matching the language of the user's prompt. Provide conceptual hints and guidance without directly revealing the solution code.",
        "Strict Technical Interviewer (FAANG)": "You are a FAANG Senior Tech Lead conducting a rigorous technical interview. Evaluate code for time/space complexity, scalability, and edge cases strictly in English. Do not give direct solutions.",
        "Senior Python Code Reviewer & Optimizer": "You are a senior software engineer. Guide the user on clean architecture, Pythonic idioms (PEP 8), typing, and performance tuning strictly in English."
    }

    selected_instruction = persona_instructions[persona]

    if user_message := st.chat_input("Ask your mentor..."):
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        full_prompt = f"""
        System Persona & Language Rule: {selected_instruction}
        Current Challenge: {st.session_state.current_challenge}
        Description: {st.session_state.challenge_desc}

        Student Workspace Code:
        ```python
        {user_code}
        ```

        Student Question: {user_message}
        """

        try:
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=full_prompt,
            )
            ai_response = response.text
        except Exception as e:
            ai_response = f"Error communicating with Gemini API: {e}"

        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()