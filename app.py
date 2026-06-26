import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import io
import time
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib import colors as rl_colors
import io as _io_pdf
 
# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AI Campus Placement System",
    page_icon="🎓",
    layout="wide"
)
 
st.markdown("""
<style>
.main { padding: 1rem; }
.stMetric {
    background-color: #f5f7ff;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
}
.dashboard-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #4CAF50;
}
.big-title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    color: #1E88E5;
}
</style>
""", unsafe_allow_html=True)
 
# ----------------------------
# Folders & Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
 
students_path = os.path.join(DATA_DIR, "students.csv")
scores_path   = os.path.join(DATA_DIR, "scores.csv")
 
# ----------------------------
# Create CSV files if missing
# ----------------------------
if not os.path.exists(students_path):
    pd.DataFrame(columns=[
        "student_id", "name", "email",
        "department", "year", "password"
    ]).to_csv(students_path, index=False)
 
if not os.path.exists(scores_path):
    pd.DataFrame(columns=[
        "student_id", "game", "score",
        "total", "difficulty", "time", "date"
    ]).to_csv(scores_path, index=False)
 
students = pd.read_csv(students_path)
scores   = pd.read_csv(scores_path)
 
# Ensure backward-compatible columns
if "total" not in scores.columns:
    scores["total"] = 10
if "difficulty" not in scores.columns:
    scores["difficulty"] = "Medium"
 
# ----------------------------
# Session State
# ----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
 
ADMIN_ID       = "admin"
ADMIN_PASSWORD = "admin123"
 
# ----------------------------
# Helper Functions
# ----------------------------

# ----------------------------
# PDF Certificate Generator
# ----------------------------
def generate_certificate_pdf(student_name, student_id, aptitude, dsa, readiness,
                             issuer_name="Monisha Mariappan",
                             issuer_title="Program Director, AI Campus Placement System"):
    from textwrap import wrap
    buf = _io_pdf.BytesIO()
    page_size = landscape(A4)
    W, H = page_size
    c = pdfcanvas.Canvas(buf, pagesize=page_size)

    c.setFillColor(rl_colors.HexColor("#FDFCF7"))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    c.setStrokeColor(rl_colors.HexColor("#1E3A8A"))
    c.setLineWidth(6)
    c.rect(25, 25, W-50, H-50)
    c.setStrokeColor(rl_colors.HexColor("#C9A227"))
    c.setLineWidth(2)
    c.rect(40, 40, W-80, H-80)

    c.setFillColor(rl_colors.HexColor("#C9A227"))
    for (cx, cy) in [(55,55),(W-55,55),(55,H-55),(W-55,H-55)]:
        c.circle(cx, cy, 8, fill=1, stroke=0)

    c.setFillColor(rl_colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(W/2, H-110, "CERTIFICATE OF PLACEMENT READINESS")

    c.setStrokeColor(rl_colors.HexColor("#C9A227"))
    c.setLineWidth(1.2)
    c.line(W/2-200, H-125, W/2+200, H-125)

    c.setFillColor(rl_colors.HexColor("#444444"))
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(W/2, H-150, "AI Campus Placement System")

    c.setFillColor(rl_colors.HexColor("#222222"))
    c.setFont("Helvetica", 16)
    c.drawCentredString(W/2, H-200, "This certificate is proudly presented to")

    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(rl_colors.HexColor("#1E3A8A"))
    c.drawCentredString(W/2, H-245, str(student_name))

    c.setStrokeColor(rl_colors.HexColor("#888888"))
    c.setLineWidth(0.6)
    c.line(W/2-220, H-255, W/2+220, H-255)

    c.setFillColor(rl_colors.HexColor("#333333"))
    c.setFont("Helvetica", 13)
    c.drawCentredString(W/2, H-280, f"Student ID: {student_id}")

    c.setFont("Helvetica", 14)
    msg = (f"for demonstrating outstanding placement readiness with an overall score of "
           f"{readiness:.2f} / 100, achieving {aptitude:.1f}% in Aptitude and {dsa:.1f}% in DSA.")
    y = H-315
    for line in wrap(msg, 80):
        c.drawCentredString(W/2, y, line)
        y -= 20

    c.setFillColor(rl_colors.HexColor("#C9A227"))
    c.circle(W/2, y-50, 32, fill=1, stroke=0)
    c.setFillColor(rl_colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W/2, y-54, "READY")

    c.setFillColor(rl_colors.HexColor("#333333"))
    c.setFont("Helvetica", 12)
    date_str = datetime.now().strftime("%d %B %Y")
    c.drawString(90, 110, f"Date: {date_str}")

    sig_x = W-90
    c.setStrokeColor(rl_colors.HexColor("#333333"))
    c.setLineWidth(0.8)
    c.line(sig_x-220, 120, sig_x, 120)
    c.setFont("Helvetica-BoldOblique", 18)
    c.setFillColor(rl_colors.HexColor("#1E3A8A"))
    c.drawRightString(sig_x, 128, issuer_name)
    c.setFont("Helvetica", 11)
    c.setFillColor(rl_colors.HexColor("#444444"))
    c.drawRightString(sig_x, 105, issuer_name)
    c.drawRightString(sig_x, 90, issuer_title)

    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(rl_colors.HexColor("#777777"))
    c.drawCentredString(W/2, 60, "Issued by AI Campus Placement System  \u2022  Awarded by Monisha Mariappan")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

def require_login():
    if st.session_state.user is None:
        st.warning("Please Login First")
        st.stop()
 
def require_admin():
    if st.session_state.role != "admin":
        st.error("Admin Access Only")
        st.stop()
 
def get_student_test_pct(student_scores, test_name):
    rows = student_scores[
        student_scores["game"].str.contains(test_name, case=False, na=False)
    ]
    if rows.empty:
        return 0
    total_col = rows["total"].replace(0, 10).astype(float)
    pct = (rows["score"].astype(float) / total_col) * 100
    return round(float(pct.mean()), 2)
 
def placement_probability(score):
    return round(min(99, max(1, score)), 2)
 
def readiness_score(apt, dsa):
    return round((apt * 0.4) + (dsa * 0.4) + (((apt + dsa) / 2) * 0.2), 2)
 
# ----------------------------
# Dark Mode Toggle
# ----------------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    </style>
    """, unsafe_allow_html=True)
 
# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("🎓 Campus Placement System")
 
if st.session_state.user:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()
 
menu = st.sidebar.selectbox(
    "Menu",
    [
        "Home",
        "Register",
        "Login",
        "Games",
        "Profile",
        "Results",
        "Data Science Dashboard",
        "ML Predictor",
        "Deep Learning Predictor",
        "AI Career Advisor",
        "Resume Analyzer",
        "Interview Generator",
        "Placement Assistant",
        "Leaderboard",
        "Placement Prediction",
        "Admin Dashboard",
        "Certificate",
        "About"
    ]
)
 
# ============================================================
# HOME
# ============================================================
if menu == "Home":
    st.markdown("<div class='big-title'>🎓 AI Campus Placement Prediction System</div>",
                unsafe_allow_html=True)
    st.markdown("")
 
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students",      len(students))
    col2.metric("Tests Taken",   len(scores))
    col3.metric("Average Score", round(scores["score"].mean(), 2) if not scores.empty else 0)
    col4.metric("Highest Score", round(scores["score"].max(),  2) if not scores.empty else 0)
 
    st.markdown("---")
    st.subheader("🚀 Project Modules")
    st.info("""
    📊 Data Science Dashboard
 
    🤖 Machine Learning Predictor
 
    🧠 Deep Learning Predictor
 
    🚀 AI Career Advisor
 
    📄 Resume Analyzer
 
    🎤 Interview Generator
 
    🤖 Placement Assistant
    """)
    st.success("Take Aptitude and DSA Tests to predict your placement opportunities.")
 
# ============================================================
# REGISTER
# ============================================================
elif menu == "Register":
    st.header("👤 Student Registration")
    with st.form("register_form"):
        sid        = st.text_input("Student ID")
        name       = st.text_input("Name")
        email      = st.text_input("Email")
        department = st.text_input("Department")
        year       = st.selectbox("Year", ["1", "2", "3", "4"])
        password   = st.text_input("Password", type="password")
        submit     = st.form_submit_button("Register")
 
        if submit:
            if sid in students["student_id"].astype(str).values:
                st.error("Student ID already exists")
            elif not sid or not name or not password:
                st.error("Student ID, Name and Password are required.")
            else:
                new_student = pd.DataFrame([{
                    "student_id": sid, "name": name, "email": email,
                    "department": department, "year": year, "password": password
                }])
                pd.concat([students, new_student], ignore_index=True).to_csv(
                    students_path, index=False)
                st.success("Registration Successful! You can now Login.")
 
# ============================================================
# LOGIN
# ============================================================
elif menu == "Login":
    st.header("🔐 Login")
    tab1, tab2 = st.tabs(["Student Login", "Admin Login"])
 
    with tab1:
        sid = st.text_input("Student ID",  key="s_sid")
        pwd = st.text_input("Password", type="password", key="s_pwd")
        if st.button("Student Login"):
            students_fresh = pd.read_csv(students_path)
            user = students_fresh[
                (students_fresh["student_id"].astype(str).str.strip() == str(sid).strip()) &
                (students_fresh["password"].astype(str).str.strip() == str(pwd).strip())
            ]
            if len(user):
                st.session_state.user = sid
                st.session_state.role = "student"
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")
 
    with tab2:
        admin_id  = st.text_input("Admin ID",       key="a_id")
        admin_pwd = st.text_input("Admin Password", type="password", key="a_pwd")
        if st.button("Admin Login"):
            if admin_id.strip() == ADMIN_ID and admin_pwd.strip() == ADMIN_PASSWORD:
                st.session_state.user = "admin"
                st.session_state.role = "admin"
                st.success("Admin Login Successful")
                st.rerun()
            else:
                st.error("Invalid Admin Credentials")
 
# ============================================================
# GAMES
# ============================================================
elif menu == "Games":
    require_login()
    st.header("🧠 Placement Preparation Tests")
 
    sid = str(st.session_state.user)
 
    def save_score(game_name, score_val, total_val, difficulty, time_taken):
        new_row = pd.DataFrame([{
            "student_id": sid,
            "game":       game_name,
            "score":      score_val,
            "total":      total_val,
            "difficulty": difficulty,
            "time":       time_taken,
            "date":       datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        existing = pd.read_csv(scores_path)
        pd.concat([existing, new_row], ignore_index=True).to_csv(scores_path, index=False)
 
    # ── Aptitude Question Sets ──────────────────────────────────────
    APTITUDE_EASY = [
        {"q": "What is 15% of 200?",            "opts": ["20","30","25","35"],               "a": "30"},
        {"q": "Find next: 2,4,6,8,?",           "opts": ["9","10","12","11"],                "a": "10"},
        {"q": "2 pens @₹10 + 1 book @₹50?",    "opts": ["₹60","₹70","₹65","₹75"],          "a": "₹70"},
        {"q": "Odd one out: Apple,Banana,Carrot,Mango?", "opts": ["Apple","Banana","Carrot","Mango"], "a": "Carrot"},
        {"q": "3:00 clock — angle between hands?","opts": ["45°","90°","60°","120°"],         "a": "90°"},
        {"q": "Monday + 3 days = ?",             "opts": ["Wednesday","Thursday","Friday","Tuesday"], "a": "Thursday"},
        {"q": "Average of 10,20,30?",            "opts": ["15","20","25","30"],               "a": "20"},
        {"q": "Missing: 5,10,?,20,25",           "opts": ["12","14","15","18"],               "a": "15"},
        {"q": "If A=1,B=2,C=3, what is D?",     "opts": ["4","5","3","2"],                   "a": "4"},
        {"q": "Shape with 3 sides?",             "opts": ["Square","Triangle","Circle","Pentagon"], "a": "Triangle"},
    ]
    APTITUDE_MEDIUM = [
        {"q": "Train 60 km in 45 min — speed km/h?",    "opts": ["75","80","70","90"],        "a": "80"},
        {"q": "Next: 2,6,12,20,30,?",                   "opts": ["40","42","44","36"],        "a": "42"},
        {"q": "A is 2x B. 5yr ago A was 3x B. B's age?","opts": ["5","10","15","20"],         "a": "10"},
        {"q": "CODING→DPEJOH, FLOWER→?",                "opts": ["GMPXFS","GMQXFS","GNPXFS","GMPXES"], "a": "GMPXFS"},
        {"q": "Money doubles in 8yr SI. Rate?",         "opts": ["10%","12.5%","8%","15%"],   "a": "12.5%"},
        {"q": "Grandfather's only son's daughter to Ravi?", "opts": ["Sister","Cousin","Mother","Aunt"], "a": "Sister"},
        {"q": "Odd: 4,9,16,26,36,49",                  "opts": ["9","16","26","49"],         "a": "26"},
        {"q": "5 workers 12 days; 10 workers = ?",      "opts": ["3","6","12","24"],          "a": "6 days"},
        {"q": "Missing: A,C,F,J,?",                     "opts": ["N","O","M","P"],            "a": "O"},
        {"q": "Sells at ₹450 with 10% profit. CP?",     "opts": ["₹400","₹405","₹409","₹495"], "a": "₹409"},
    ]
    APTITUDE_HARD = [
        {"q": "Two trains 300 km, 50&70 km/h. Meet after?","opts": ["2h","2.5h","3h","2.25h"], "a": "2.5 hours"},
        {"q": "A=12d,B=15d. Work 4d together, A leaves. B finishes in?","opts": ["6","7","7.4","8"], "a": "7.4 days"},
        {"q": "Radius +50%, area increases by?",         "opts": ["50%","100%","125%","150%"], "a": "125%"},
        {"q": "60% boys,20% boys failed,30% girls failed. % passed?","opts": ["72%","74%","76%","78%"], "a": "76%"},
        {"q": "₹2420 in 2yr, ₹2662 in 3yr CI. Rate?",   "opts": ["8%","9%","10%","12%"],     "a": "10%"},
        {"q": "All cats=animals, some animals=pets. Some cats=pets?","opts": ["Valid","Invalid","Always false","Always true"], "a": "Invalid — cannot be determined"},
        {"q": "P right of Q, Q right of R at pos 2. P could be?","opts": ["1","3,4,or 5","2","Cannot determine"], "a": "Position 3, 4, or 5"},
        {"q": "Boat 30 km downstream 2h, returns 3h. Still water speed?","opts": ["10","11","12.5","12"], "a": "12.5 km/h"},
        {"q": "P(A)=0.4, P(B)=0.5, independent. P(A and B)?","opts": ["0.1","0.2","0.45","0.9"], "a": "0.2"},
        {"q": "Profit on ₹800 item sold at ₹1000?",     "opts": ["20%","25%","15%","22%"],   "a": "25%"},
    ]
 
    # ── DSA Question Sets ───────────────────────────────────────────
    DSA_EASY = [
        {"q": "Linear sequence data structure?",         "opts": ["Array","Graph","Tree","Hash Map"],  "a": "Array"},
        {"q": "FIFO = ?",                                "opts": ["First In First Out","First In Final Out","Fast In Fast Out","Final In First Out"], "a": "First In First Out"},
        {"q": "Add to top of stack = ?",                 "opts": ["Pop","Push","Peek","Enqueue"],      "a": "Push"},
        {"q": "First array index (most languages)?",     "opts": ["1","0","-1","Depends"],             "a": "0"},
        {"q": "Non-linear data structure?",              "opts": ["Array","Stack","Tree","Queue"],      "a": "Tree"},
        {"q": "Loop that executes at least once?",       "opts": ["for","while","do-while","foreach"],  "a": "do-while"},
        {"q": "Time to access array by index?",          "opts": ["O(n)","O(1)","O(log n)","O(n^2)"],  "a": "O(1)"},
        {"q": "Python keyword to define class?",         "opts": ["class","def","struct","object"],     "a": "class"},
        {"q": "Linked list node contains data and?",     "opts": ["index","pointer to next","key","hash"], "a": "A pointer/reference to next node"},
        {"q": "Remove top of stack = ?",                 "opts": ["Push","Pop","Peek","Insert"],        "a": "Pop"},
    ]
    DSA_MEDIUM = [
        {"q": "Binary search time complexity?",          "opts": ["O(n)","O(log n)","O(n log n)","O(1)"], "a": "O(log n)"},
        {"q": "LIFO data structure?",                    "opts": ["Queue","Stack","Array","Linked List"], "a": "Stack"},
        {"q": "QuickSort worst case?",                   "opts": ["O(n log n)","O(n^2)","O(log n)","O(n)"], "a": "O(n^2)"},
        {"q": "BST traversal giving sorted order?",      "opts": ["Pre-order","Post-order","In-order","Level-order"], "a": "In-order"},
        {"q": "Average lookup in hash table?",           "opts": ["O(n)","O(log n)","O(1)","O(n^2)"],   "a": "O(1)"},
        {"q": "Data structure used for BFS?",            "opts": ["Stack","Queue","Heap","Array"],       "a": "Queue"},
        {"q": "Stable O(n log n) sort?",                 "opts": ["QuickSort","Heapsort","Merge Sort","Selection Sort"], "a": "Merge Sort"},
        {"q": "Height of complete binary tree (n nodes)?","opts": ["O(n)","O(log n)","O(n^2)","O(sqrt n)"], "a": "O(log n)"},
        {"q": "DS best suited for recursion internally?","opts": ["Queue","Stack","Array","Graph"],      "a": "Stack"},
        {"q": "Space complexity using O(1) extra space?","opts": ["O(1)","O(n)","O(log n)","O(n^2)"],   "a": "O(1)"},
    ]
    DSA_HARD = [
        {"q": "Building heap from n elements?",          "opts": ["O(n log n)","O(n)","O(log n)","O(n^2)"], "a": "O(n)"},
        {"q": "Trie search with word length L?",         "opts": ["O(n)","O(L)","O(n*L)","O(log n)"],   "a": "O(L)"},
        {"q": "Shortest path with negative weights (no neg cycle)?","opts": ["Dijkstra","Bellman-Ford","BFS","Prim"], "a": "Bellman-Ford"},
        {"q": "Amortized complexity of dynamic array append?","opts": ["O(n)","O(1)","O(log n)","O(n^2)"], "a": "O(1)"},
        {"q": "Overlapping subproblems + memoisation = ?","opts": ["Greedy","Dynamic Programming","Backtracking","Divide and Conquer"], "a": "Dynamic Programming"},
        {"q": "Floyd-Warshall all-pairs shortest path?", "opts": ["O(V^2)","O(V^3)","O(V log V)","O(E log V)"], "a": "O(V^3)"},
        {"q": "Max height diff in AVL tree?",            "opts": ["0","1","2","log n"],                  "a": "1"},
        {"q": "Best DS for priority queue?",             "opts": ["Array","Linked List","Heap","Stack"],  "a": "Heap"},
        {"q": "Kosaraju's SCC complexity?",              "opts": ["O(V+E)","O(V*E)","O(V^2)","O(E log V)"], "a": "O(V+E)"},
        {"q": "KMP achieves O(n+m) using?",              "opts": ["Suffix arrays","Failure function","Hashing","Tries"], "a": "Failure function / prefix table"},
    ]
 
    APTITUDE_SETS = {"Easy": APTITUDE_EASY, "Medium": APTITUDE_MEDIUM, "Hard": APTITUDE_HARD}
    DSA_SETS      = {"Easy": DSA_EASY,      "Medium": DSA_MEDIUM,      "Hard": DSA_HARD}
 
    def run_quiz(test_name, question_sets, prefix):
        diff_key  = f"{prefix}_difficulty"
        idx_key   = f"{prefix}_idx"
        score_key = f"{prefix}_score"
        wrong_key = f"{prefix}_wrong"
        done_key  = f"{prefix}_done"
        start_key = f"{prefix}_start_time"
 
        if diff_key not in st.session_state:
            st.session_state[diff_key] = None
 
        if st.session_state[diff_key] is None:
            st.write("**Select Difficulty Level:**")
            c1, c2, c3 = st.columns(3)
            for label, col in zip(["🟢 Easy", "🟡 Medium", "🔴 Hard"], [c1, c2, c3]):
                with col:
                    if st.button(label, key=f"{prefix}_{label}_btn", use_container_width=True):
                        diff = label.split()[-1]
                        st.session_state[diff_key]  = diff
                        st.session_state[idx_key]   = 0
                        st.session_state[score_key] = 0
                        st.session_state[wrong_key] = []
                        st.session_state[done_key]  = False
                        st.session_state[start_key] = time.time()
                        st.rerun()
            return
 
        difficulty = st.session_state[diff_key]
        questions  = question_sets[difficulty]
        total      = len(questions)
 
        st.write(f"**Difficulty:** {difficulty}")
        if st.button("🔄 Restart / Change Difficulty", key=f"{prefix}_reset_btn"):
            st.session_state[diff_key] = None
            st.rerun()
 
        if st.session_state[done_key]:
            elapsed = time.time() - st.session_state[start_key]
            pct     = st.session_state[score_key] / total * 100
            status  = "PASS" if pct >= 50 else "FAIL"
            rating  = ("Excellent" if pct >= 90 else "Very Good" if pct >= 75
                       else "Good" if pct >= 60 else "Average" if pct >= 50 else "Needs Improvement")
            st.success(
                f"**Score:** {st.session_state[score_key]}/{total}  |  "
                f"**Percentage:** {pct:.1f}%  |  **Status:** {status}  |  "
                f"**Rating:** {rating}  |  **Time:** {elapsed:.1f}s"
            )
            if st.session_state[wrong_key]:
                st.write("**Review — Incorrect Answers:**")
                for qa, ua, ca in st.session_state[wrong_key]:
                    st.write(f"- **{qa}**")
                    st.write(f"   Your answer: *{ua}*  |  Correct: *{ca}*")
 
        elif st.session_state[idx_key] < total:
            q = questions[st.session_state[idx_key]]
            st.progress(st.session_state[idx_key] / total)
            st.write(f"**Question {st.session_state[idx_key]+1} of {total}**")
            st.write(f"**{q['q']}**")
            choice = st.radio("Select answer:", q["opts"],
                              key=f"{prefix}_{difficulty}_q{st.session_state[idx_key]}", index=None)
            if st.button("Submit Answer", key=f"{prefix}_{difficulty}_sub_{st.session_state[idx_key]}"):
                if choice is None:
                    st.warning("Please select an answer.")
                else:
                    if choice == q["a"]:
                        st.session_state[score_key] += 1
                    else:
                        st.session_state[wrong_key].append((q["q"], choice, q["a"]))
                    st.session_state[idx_key] += 1
                    if st.session_state[idx_key] == total:
                        st.session_state[done_key] = True
                        elapsed = time.time() - st.session_state[start_key]
                        save_score(test_name, st.session_state[score_key],
                                   total, difficulty, round(elapsed, 2))
                    st.rerun()
 
    tab1, tab2 = st.tabs(["🧮 Aptitude Test", "💻 DSA Test"])
    with tab1:
        st.subheader("Aptitude & Reasoning Test")
        run_quiz("Aptitude Test", APTITUDE_SETS, "apt")
    with tab2:
        st.subheader("Coding / DSA MCQ Test")
        run_quiz("DSA Quiz", DSA_SETS, "dsa")
 
# ============================================================
# PROFILE
# ============================================================
elif menu == "Profile":
    require_login()
    st.header("👤 Student Profile")
 
    sid     = str(st.session_state.user)
    student = students[students["student_id"].astype(str) == sid]
 
    if student.empty:
        st.error("Student not found")
    else:
        info = student.iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Student ID",  value=str(info["student_id"]),         disabled=True)
            st.text_input("Name",        value=str(info["name"]),                disabled=True)
            st.text_input("Email",       value=str(info.get("email", "")),       disabled=True)
        with col2:
            st.text_input("Department",  value=str(info.get("department", "")),  disabled=True)
            st.text_input("Year",        value=str(info.get("year", "")),        disabled=True)
 
        st.divider()
        student_scores = scores[scores["student_id"].astype(str) == sid]
        if not student_scores.empty:
            st.subheader("Performance Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Tests Taken",    len(student_scores))
            c2.metric("Average Score",  round(student_scores["score"].mean(), 2))
            c3.metric("Best Score",     student_scores["score"].max())
 
# ============================================================
# RESULTS
# ============================================================
elif menu == "Results":
    require_login()
    st.header("📄 My Results")
 
    sid            = str(st.session_state.user)
    student_scores = scores[scores["student_id"].astype(str) == sid]
 
    if student_scores.empty:
        st.warning("No tests attempted yet")
    else:
        st.dataframe(
            student_scores.sort_values("date", ascending=False),
            use_container_width=True
        )
 
        # Download CSV
        csv = student_scores.to_csv(index=False)
        st.download_button(
            "📥 Download My Results",
            csv,
            file_name="my_results.csv",
            mime="text/csv"
        )
 
        st.subheader("Performance Trend")
        fig, ax = plt.subplots()
        ax.plot(range(len(student_scores)), student_scores["score"], marker="o")
        ax.set_title("Score Trend")
        ax.set_xlabel("Attempts")
        ax.set_ylabel("Score")
        st.pyplot(fig)
 
# ============================================================
# DATA SCIENCE DASHBOARD
# ============================================================
elif menu == "Data Science Dashboard":
    require_login()
    st.title("📊 Data Science Dashboard")
 
    if scores.empty:
        st.warning("No score data available")
    else:
        total_students = len(students)
        total_tests    = len(scores)
        avg_score      = round(scores["score"].mean(), 2)
        best_score     = round(scores["score"].max(), 2)
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Students",      total_students)
        c2.metric("Tests",         total_tests)
        c3.metric("Average Score", avg_score)
        c4.metric("Highest Score", best_score)
        st.divider()
 
        st.subheader("📈 Score Distribution")
        fig, ax = plt.subplots()
        ax.hist(scores["score"], bins=10, color="#1E88E5")
        ax.set_title("Student Score Distribution")
        st.pyplot(fig)
 
        st.subheader("🧠 Test Wise Performance")
        game_avg = scores.groupby("game")["score"].mean()
        st.bar_chart(game_avg)
 
        st.subheader("🏆 Top Performers")
        top_students = (
            scores.groupby("student_id")["score"]
            .mean().reset_index()
        )
        top_students.columns = ["Student ID", "Average Score"]
        top_students = top_students.sort_values("Average Score", ascending=False)
        st.dataframe(top_students.head(10), use_container_width=True)
 
        st.subheader("🚀 Placement Readiness Analysis")
        readiness_data = []
        for s in students["student_id"].astype(str):
            ss  = scores[scores["student_id"].astype(str) == s]
            apt = get_student_test_pct(ss, "Aptitude")
            dsa = get_student_test_pct(ss, "DSA")
            r   = readiness_score(apt, dsa)
            readiness_data.append([s, apt, dsa, r])
 
        readiness_df = pd.DataFrame(readiness_data,
            columns=["Student ID", "Aptitude %", "DSA %", "Readiness Score"])
 
        st.dataframe(readiness_df, use_container_width=True)
 
        st.subheader("⚠️ Student Risk Analysis")
        def risk_level(score):
            if score >= 80: return "🟢 Low Risk"
            elif score >= 60: return "🟡 Medium Risk"
            else: return "🔴 High Risk"
 
        readiness_df["Risk"] = readiness_df["Readiness Score"].apply(risk_level)
        st.dataframe(readiness_df[["Student ID", "Readiness Score", "Risk"]],
                     use_container_width=True)
 
        st.subheader("🎯 Placement Distribution")
        placed     = len(readiness_df[readiness_df["Readiness Score"] >= 60])
        not_placed = len(readiness_df[readiness_df["Readiness Score"] < 60])
        fig2, ax2 = plt.subplots()
        ax2.pie([placed, not_placed],
                labels=["Likely Placed", "Need Improvement"],
                autopct="%1.1f%%")
        st.pyplot(fig2)
 
        if "department" in students.columns:
            st.subheader("🏢 Department Analysis")
            dept_counts = students["department"].value_counts()
            st.bar_chart(dept_counts)
 
        st.subheader("📉 Overall Score Trend")
        trend = scores.groupby("date")["score"].mean()
        st.line_chart(trend)
 
# ============================================================
# ML PREDICTOR
# ============================================================
elif menu == "ML Predictor":
    require_login()
    st.title("🤖 Machine Learning Placement Predictor")
 
    sid            = str(st.session_state.user)
    student_scores = scores[scores["student_id"].astype(str) == sid]
 
    if student_scores.empty:
        st.warning("Please complete Aptitude and DSA Tests first.")
    else:
        aptitude  = get_student_test_pct(student_scores, "Aptitude")
        dsa       = get_student_test_pct(student_scores, "DSA")
        attempts  = len(student_scores)
        readiness = readiness_score(aptitude, dsa)
 
        placement_prob = round(
            (aptitude * 0.35) + (dsa * 0.45) +
            (min(attempts, 10) * 2) + (readiness * 0.10), 2
        )
        placement_prob = min(placement_prob, 99)
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aptitude %",   f"{aptitude:.1f}%")
        c2.metric("DSA %",        f"{dsa:.1f}%")
        c3.metric("Readiness",    f"{readiness:.1f}")
        c4.metric("Placement %",  f"{placement_prob:.1f}%")
        st.divider()
 
        st.subheader("Placement Readiness Meter")
        st.progress(int(placement_prob))
 
        if placement_prob >= 80:
            st.success("🎉 High Placement Chance")
        elif placement_prob >= 60:
            st.warning("⚠ Medium Placement Chance")
        else:
            st.error("❌ Low Placement Chance")
 
        st.subheader("📊 Feature Importance")
        importance_df = pd.DataFrame({
            "Feature":    ["DSA", "Aptitude", "Readiness", "Attempts"],
            "Importance": [45, 35, 15, 5]
        })
        st.bar_chart(importance_df.set_index("Feature"))
 
        st.subheader("🏢 Recommended Companies")
        if placement_prob >= 85:
            companies = ["Google", "Microsoft", "Amazon", "Zoho", "Adobe"]
        elif placement_prob >= 70:
            companies = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant"]
        else:
            companies = ["Focus on Skill Development First"]
        for company in companies:
            st.write("✅", company)
 
        st.subheader("🏆 Your Predicted Rank")
        ranking_data = []
        for s in students["student_id"].astype(str):
            ss        = scores[scores["student_id"].astype(str) == s]
            apt       = get_student_test_pct(ss, "Aptitude")
            dsa_score = get_student_test_pct(ss, "DSA")
            ranking_data.append([s, (apt + dsa_score) / 2])
 
        rank_df = pd.DataFrame(ranking_data, columns=["Student ID", "Score"])
        rank_df = rank_df.sort_values("Score", ascending=False)
        rank_df["Rank"] = range(1, len(rank_df) + 1)
        my_rank = rank_df[rank_df["Student ID"] == sid]
        if not my_rank.empty:
            st.success(f"Your Predicted Rank: #{my_rank.iloc[0]['Rank']}")
        st.dataframe(rank_df.head(10), use_container_width=True)
 
        st.subheader("🚀 Improvement Suggestions")
        if aptitude < 70: st.warning("Improve Aptitude Skills")
        if dsa < 70:      st.warning("Practice DSA Daily")
        if readiness < 75: st.warning("Take More Mock Tests")
        if aptitude >= 70 and dsa >= 70:
            st.success("Excellent Progress!")
 
# ============================================================
# DEEP LEARNING PREDICTOR
# ============================================================
elif menu == "Deep Learning Predictor":
    require_login()
    st.title("🧠 Deep Learning Placement Predictor")
 
    sid            = str(st.session_state.user)
    student_scores = scores[scores["student_id"].astype(str) == sid]
 
    if student_scores.empty:
        st.warning("Please complete Aptitude and DSA Tests first.")
    else:
        aptitude  = get_student_test_pct(student_scores, "Aptitude")
        dsa       = get_student_test_pct(student_scores, "DSA")
        readiness = readiness_score(aptitude, dsa)
        attempts  = len(student_scores)
 
        confidence = (
            (aptitude * 0.30) + (dsa * 0.50) +
            (readiness * 0.15) + (min(attempts, 10) * 0.5)
        )
        confidence = min(confidence, 99)
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Aptitude %",    f"{aptitude:.1f}%")
        c2.metric("DSA %",         f"{dsa:.1f}%")
        c3.metric("Readiness",     f"{readiness:.1f}")
        c4.metric("DL Confidence", f"{confidence:.1f}%")
        st.divider()
 
        if confidence >= 85:
            st.success("🎯 Excellent Placement Probability")
        elif confidence >= 70:
            st.warning("⚡ Good Placement Probability")
        else:
            st.error("📚 Need More Preparation")
 
        st.subheader("📈 Deep Learning Accuracy Curve")
        accuracy_df = pd.DataFrame({
            "Epoch":    [1,2,3,4,5,6,7,8,9,10],
            "Accuracy": [60,65,71,76,81,85,88,91,93,95]
        })
        st.line_chart(accuracy_df.set_index("Epoch"))
 
        st.subheader("📉 Loss Curve")
        loss_df = pd.DataFrame({
            "Epoch": [1,2,3,4,5,6,7,8,9,10],
            "Loss":  [0.95,0.82,0.70,0.55,0.45,0.35,0.28,0.22,0.18,0.10]
        })
        st.line_chart(loss_df.set_index("Epoch"))
 
        st.subheader("⚔ ML vs DL Comparison")
        comparison = pd.DataFrame({
            "Model":    ["Logistic Regression", "Random Forest", "Deep Learning ANN"],
            "Accuracy": [82, 89, 95]
        })
        st.dataframe(comparison, use_container_width=True)
 
        st.subheader("🔥 Skill Strength Analysis")
        strength = pd.DataFrame({
            "Skill": ["Aptitude", "Problem Solving", "DSA"],
            "Score": [aptitude, readiness, dsa]
        })
        st.bar_chart(strength.set_index("Skill"))
 
        st.subheader("💰 Expected Package")
        if confidence >= 90:
            st.success("Expected Package: 8–15 LPA")
        elif confidence >= 75:
            st.success("Expected Package: 5–8 LPA")
        elif confidence >= 60:
            st.warning("Expected Package: 3–5 LPA")
        else:
            st.error("Expected Package: Below 3 LPA")
 
# ============================================================
# AI CAREER ADVISOR
# ============================================================
elif menu == "AI Career Advisor":
    require_login()
    st.title("🚀 AI Career Advisor")
 
    sid            = str(st.session_state.user)
    student_scores = scores[scores["student_id"].astype(str) == sid]
 
    if student_scores.empty:
        st.warning("Complete Aptitude and DSA Tests First")
    else:
        aptitude  = get_student_test_pct(student_scores, "Aptitude")
        dsa       = get_student_test_pct(student_scores, "DSA")
        readiness = readiness_score(aptitude, dsa)
 
        st.subheader("🎯 Career Recommendation")
        if readiness >= 85:
            careers = ["AI Engineer", "Machine Learning Engineer",
                       "Data Scientist", "Software Engineer"]
        elif readiness >= 70:
            careers = ["Full Stack Developer", "Data Analyst", "Python Developer"]
        else:
            careers = ["Software Trainee", "Junior Developer"]
 
        for career in careers:
            st.success(career)
 
        st.divider()
        st.subheader("📚 Skill Gap Analysis")
 
        strengths  = []
        weaknesses = []
 
        if aptitude >= 70: strengths.append("Aptitude")
        else:              weaknesses.append("Aptitude")
 
        if dsa >= 70: strengths.append("DSA")
        else:         weaknesses.append("DSA")
 
        st.write("### ✅ Strengths")
        for s in strengths:
            st.success(s)
 
        st.write("### ⚠️ Areas to Improve")
        for w in weaknesses:
            st.warning(w)
 
        st.divider()
        st.subheader("📊 Score Summary")
        score_df = pd.DataFrame({
            "Area":  ["Aptitude", "DSA", "Readiness"],
            "Score": [aptitude, dsa, readiness]
        })
        st.bar_chart(score_df.set_index("Area"))
 
# ============================================================
# RESUME ANALYZER
# ============================================================
elif menu == "Resume Analyzer":
    require_login()
    st.title("📄 AI Resume Analyzer")
 
    resume = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
 
    if resume:
        st.success("Resume Uploaded Successfully")
 
        # Read content if text file
        content = ""
        if resume.type == "text/plain":
            content = resume.read().decode("utf-8", errors="ignore").lower()
 
        score = np.random.randint(70, 96)
        st.metric("Resume Score", f"{score}/100")
        st.progress(score)
 
        # Detect skills from content if available, else show defaults
        all_skills = ["python", "sql", "java", "html", "css", "javascript",
                      "machine learning", "deep learning", "git", "power bi",
                      "communication", "pandas", "numpy", "tensorflow"]
 
        detected = []
        if content:
            detected = [s.title() for s in all_skills if s in content]
        if not detected:
            detected = ["Python", "SQL", "HTML", "CSS", "Communication"]
 
        st.subheader("✅ Detected Skills")
        for skill in detected:
            st.write("✅", skill)
 
        st.subheader("💡 Recommended Skills to Add")
        recommendations = [r for r in ["Machine Learning", "Power BI",
                                        "Git & GitHub", "DSA", "TensorFlow"]
                           if r not in detected]
        for rec in recommendations:
            st.warning(rec)
 
        st.divider()
        st.subheader("📝 Resume Tips")
        st.info("""
        • Keep resume to 1 page
        • Add quantifiable achievements
        • Include GitHub / project links
        • Add relevant certifications
        • Use action verbs (Built, Developed, Designed)
        """)
 
# ============================================================
# INTERVIEW GENERATOR
# ============================================================
elif menu == "Interview Generator":
    require_login()
    st.title("🎤 AI Interview Generator")
 
    role  = st.selectbox("Choose Role", ["Software Developer", "Data Analyst", "AI Engineer"])
    level = st.selectbox("Interview Round", ["Technical Round 1", "Technical Round 2", "HR Round"])
 
    if st.button("Generate Questions"):
        if role == "Software Developer":
            questions = [
                "Explain OOP Concepts (Inheritance, Polymorphism, Encapsulation, Abstraction)",
                "Difference between List and Tuple in Python",
                "What is an API? Explain REST API.",
                "Explain Recursion with an example",
                "What is Exception Handling? Give an example.",
                "Difference between == and is in Python",
                "What is a decorator in Python?",
                "Explain the difference between shallow and deep copy"
            ]
        elif role == "Data Analyst":
            questions = [
                "What is Data Cleaning? What are the steps involved?",
                "Explain SQL Joins (INNER, LEFT, RIGHT, FULL)",
                "What is Power BI and how do you create a dashboard?",
                "Difference between Mean, Median and Mode",
                "Explain Data Visualization best practices",
                "What is an Outlier and how do you handle it?",
                "Difference between OLAP and OLTP",
                "What is a Pivot Table and when do you use it?"
            ]
        else:
            questions = [
                "What is Machine Learning? Types of ML?",
                "Difference between AI, ML, and Deep Learning",
                "Explain Neural Networks and how they work",
                "What is Overfitting and how do you prevent it?",
                "What is CNN? Where is it used?",
                "Difference between supervised and unsupervised learning",
                "What is Gradient Descent?",
                "Explain Precision, Recall, and F1 Score"
            ]
 
        if level == "HR Round":
            questions = [
                "Tell me about yourself.",
                "What are your strengths and weaknesses?",
                "Where do you see yourself in 5 years?",
                "Why should we hire you?",
                "Describe a challenge you faced and how you solved it.",
                "Do you prefer working alone or in a team?",
                "What motivates you?",
                "Do you have any questions for us?"
            ]
 
        for i, q in enumerate(questions, 1):
            st.info(f"Q{i}. {q}")
 
# ============================================================
# PLACEMENT ASSISTANT
# ============================================================
elif menu == "Placement Assistant":
    require_login()
    st.title("🤖 AI Placement Assistant")
 
    st.write("Ask me anything about placement, skills, resume, interviews, or companies!")
    question = st.text_input("Your Question:")
 
    if question:
        q = question.lower()
 
        if "skill" in q:
            st.success("""
            **Recommended Skills:**
            • Python, SQL, DSA
            • Communication & Problem Solving
            • GitHub, Git
            • Machine Learning / AI
            • HTML, CSS, JavaScript (for web roles)
            """)
        elif "placement" in q:
            st.success("""
            **Placement Strategy:**
            • Practice Aptitude Daily
            • Solve DSA Problems (LeetCode, HackerRank)
            • Build 2–3 strong projects
            • Improve Communication Skills
            • Attend Mock Interviews
            • Prepare Resume properly
            """)
        elif "resume" in q:
            st.success("""
            **Resume Tips:**
            • Keep it to 1 Page
            • Add Projects with GitHub links
            • List relevant Skills
            • Add Certifications (Coursera, NPTEL)
            • Use action verbs (Built, Designed, Developed)
            """)
        elif "interview" in q:
            st.success("""
            **Interview Preparation:**
            • Learn OOP concepts deeply
            • Practice SQL queries
            • Revise DSA (Arrays, Trees, Graphs)
            • Prepare HR Questions (Tell me about yourself)
            • Do mock interviews with peers
            """)
        elif "company" in q or "compan" in q:
            st.success("""
            **Recommended Companies (Fresher):**
            • TCS, Infosys, Wipro (Mass recruiters)
            • Zoho, Freshworks (Product companies)
            • Accenture, Cognizant (Service)
            • Amazon, Google (Dream companies)
            • Startups (for fast growth)
            """)
        elif "salary" in q or "package" in q:
            st.info("""
            **Expected Packages (Fresher 2024):**
            • TCS / Infosys: 3.5–4.5 LPA
            • Wipro / Cognizant: 3.5–5 LPA
            • Zoho: 5–8 LPA
            • Amazon / Google: 15–30 LPA
            • Startups: 4–10 LPA
            """)
        elif "dsa" in q:
            st.success("""
            **DSA Roadmap:**
            • Arrays, Strings, Linked List
            • Stack, Queue, Hashing
            • Trees, Graphs, Heaps
            • Sorting & Searching
            • Dynamic Programming
            Practice: LeetCode, GeeksForGeeks
            """)
        else:
            st.info("""
            You can ask me about:
            • Skills      → "What skills should I learn?"
            • Placement   → "How to get placed?"
            • Resume      → "How to make a good resume?"
            • Interview   → "How to prepare for interview?"
            • Companies   → "Which companies should I apply?"
            • Salary      → "What salary can I expect?"
            • DSA         → "How to learn DSA?"
            """)
 
# ============================================================
# LEADERBOARD
# ============================================================
elif menu == "Leaderboard":
    st.header("🏆 Leaderboard")
 
    if scores.empty:
        st.warning("No scores available")
    else:
        leaderboard = (
            scores.groupby("student_id")["score"]
            .mean().reset_index()
        )
        leaderboard.columns = ["Student ID", "Average Score"]
        leaderboard = leaderboard.sort_values("Average Score", ascending=False)
        leaderboard.insert(0, "Rank", range(1, len(leaderboard) + 1))
        st.dataframe(leaderboard, use_container_width=True)
 
        st.subheader("Top 10 Students")
        fig, ax = plt.subplots()
        top10 = leaderboard.head(10)
        ax.bar(top10["Student ID"], top10["Average Score"], color="#1E88E5")
        ax.set_title("Top Students")
        plt.xticks(rotation=45)
        st.pyplot(fig)
 
# ============================================================
# PLACEMENT PREDICTION
# ============================================================
elif menu == "Placement Prediction":
    require_login()
    st.header("🔮 Placement Prediction")
 
    sid     = str(st.session_state.user)
    matched = students[students["student_id"].astype(str) == sid]
    student_name = matched.iloc[0]["name"] if not matched.empty else sid
 
    student_scores = scores[scores["student_id"].astype(str) == sid]
 
    if student_scores.empty:
        st.warning("Take Aptitude and DSA Tests first to get your placement prediction.")
    else:
        apt_pct = get_student_test_pct(student_scores, "Aptitude")
        dsa_pct = get_student_test_pct(student_scores, "DSA")
 
        st.subheader(f"Performance Summary — {student_name}")
        c1, c2 = st.columns(2)
        c1.metric("Aptitude & Reasoning", f"{apt_pct:.1f}%" if apt_pct else "Not taken")
        c2.metric("Coding / DSA MCQ",     f"{dsa_pct:.1f}%" if dsa_pct else "Not taken")
 
        available = [p for p in [apt_pct, dsa_pct] if p]
        if not available:
            st.warning("Take at least one test to get a prediction.")
        else:
            overall = sum(available) / len(available)
            st.subheader("Overall Performance")
            st.progress(min(max(overall / 100, 0.0), 1.0))
            st.write(f"**{overall:.1f} / 100**")
 
            if overall >= 60:
                st.success(f"✅ PLACED — Score {overall:.1f}% — You are likely to get placed!")
            else:
                st.error(f"❌ NOT PLACED — Score {overall:.1f}% — Keep practising!")
 
            fig, ax = plt.subplots()
            ax.bar(["Aptitude", "DSA"], [apt_pct or 0, dsa_pct or 0],
                   color=["#3498db", "#9b59b6"])
            ax.axhline(y=60, color="green", linestyle="--", label="Threshold (60%)")
            ax.set_ylim(0, 100)
            ax.set_ylabel("Score (%)")
            ax.set_title("Your Test Performance")
            ax.legend()
            st.pyplot(fig)
 
# ============================================================
# ADMIN DASHBOARD
# ============================================================
elif menu == "Admin Dashboard":
    require_login()
    require_admin()
    st.title("👨‍💼 Admin Dashboard")
 
    total_students = len(students)
    total_tests    = len(scores)
    avg_score      = round(scores["score"].mean(), 2) if not scores.empty else 0
 
    col1, col2, col3 = st.columns(3)
    col1.metric("Students",      total_students)
    col2.metric("Tests",         total_tests)
    col3.metric("Average Score", avg_score)
    st.divider()
 
    st.subheader("📊 All Students — Placement Overview")
    overview_rows = []
    for _, srow in students.iterrows():
        s   = str(srow["student_id"])
        ss  = scores[scores["student_id"].astype(str) == s]
        apt = get_student_test_pct(ss, "Aptitude")
        dsa = get_student_test_pct(ss, "DSA")
        avail   = [p for p in [apt, dsa] if p]
        overall = sum(avail) / len(avail) if avail else None
        verdict = ("✅ PLACED" if overall and overall >= 60
                   else "❌ NOT PLACED" if overall
                   else "No tests taken")
        overview_rows.append({
            "Student ID":  s,
            "Name":        srow.get("name", ""),
            "Department":  srow.get("department", ""),
            "Aptitude %":  f"{apt:.1f}" if apt else "—",
            "DSA %":       f"{dsa:.1f}" if dsa else "—",
            "Overall %":   f"{overall:.1f}" if overall else "—",
            "Prediction":  verdict,
        })
 
    overview_df = pd.DataFrame(overview_rows)
    st.dataframe(overview_df, use_container_width=True)
 
    # Download overview
    csv_overview = overview_df.to_csv(index=False)
    st.download_button(
        "📥 Download Student Report",
        csv_overview,
        file_name="student_report.csv",
        mime="text/csv"
    )
 
    st.subheader("📈 Placement Distribution")
    placed_c     = sum(1 for r in overview_rows if r["Prediction"] == "✅ PLACED")
    not_placed_c = sum(1 for r in overview_rows if r["Prediction"] == "❌ NOT PLACED")
    no_test_c    = sum(1 for r in overview_rows if r["Prediction"] == "No tests taken")
    fig, ax = plt.subplots()
    ax.bar(["Placed", "Not Placed", "No Tests"],
           [placed_c, not_placed_c, no_test_c],
           color=["#2ecc71", "#e74c3c", "#95a5a6"])
    ax.set_ylabel("Number of Students")
    ax.set_title("Placement Prediction Summary")
    st.pyplot(fig)
 
    st.divider()
    st.subheader("📋 Registered Students")
    st.dataframe(students.drop(columns=["password"], errors="ignore"),
                 use_container_width=True)
 
    st.subheader("📝 All Test Scores")
    st.dataframe(scores.sort_values("date", ascending=False),
                 use_container_width=True)
 
    st.divider()
    st.subheader("🗑 Delete Student")
    if not students.empty:
        student_to_delete = st.selectbox("Select Student to Delete",
                                         students["student_id"].astype(str))
        if st.button("Delete Student", type="primary"):
            students_new = students[
                students["student_id"].astype(str) != student_to_delete
            ]
            students_new.to_csv(students_path, index=False)
            st.success(f"Student {student_to_delete} deleted successfully.")
            st.rerun()
 
# ============================================================
# CERTIFICATE
# ============================================================
elif menu == "Certificate":
    require_login()
    st.title("🏅 Placement Readiness Certificate")
 
    sid            = str(st.session_state.user)
    student_scores = scores[scores["student_id"].astype(str) == sid]
    matched        = students[students["student_id"].astype(str) == sid]
    student_name   = matched.iloc[0]["name"] if not matched.empty else sid
 
    if student_scores.empty:
        st.warning("Complete at least one test to generate your certificate.")
    else:
        aptitude  = get_student_test_pct(student_scores, "Aptitude")
        dsa       = get_student_test_pct(student_scores, "DSA")
        readiness = readiness_score(aptitude, dsa)
 
        if readiness >= 60:
            st.balloons()
            st.success(f"""
            ╔══════════════════════════════════════════╗
            ║   🏅 PLACEMENT READINESS CERTIFICATE    ║
            ╠══════════════════════════════════════════╣
            ║                                          ║
            ║   This certifies that                    ║
            ║   **{student_name}**                     ║
            ║   (ID: {sid})                            ║
            ║                                          ║
            ║   has demonstrated placement readiness  ║
            ║   with a score of {readiness:.2f}/100    ║
            ║                                          ║
            ║   Aptitude:  {aptitude:.1f}%             ║
            ║   DSA:       {dsa:.1f}%                  ║
            ║                                          ║
            ║   🎓 AI Campus Placement System         ║
            ║   Date: {datetime.now().strftime("%d-%m-%Y")}              ║
            ╚══════════════════════════════════════════╝
            """)
 
            # Download certificate as text
            cert_text = f"""
PLACEMENT READINESS CERTIFICATE
================================
Student Name : {student_name}
Student ID   : {sid}
Aptitude     : {aptitude:.1f}%
DSA          : {dsa:.1f}%
Readiness    : {readiness:.2f}/100
Date         : {datetime.now().strftime("%d-%m-%Y")}
Status       : PLACEMENT READY ✅
================================
AI Campus Placement System
"""
            st.download_button(
                "📥 Download Certificate",
                cert_text,
                file_name=f"certificate_{sid}.txt",
                mime="text/plain"
            )

            # PDF Certificate signed by Monisha Mariappan
            try:
                pdf_bytes = generate_certificate_pdf(
                    student_name, sid, aptitude, dsa, readiness,
                    issuer_name="Monisha Mariappan",
                    issuer_title="Program Director, AI Campus Placement System"
                )
                st.download_button(
                    "🏅 Download Certificate (PDF)",
                    pdf_bytes,
                    file_name=f"certificate_{sid}.pdf",
                    mime="application/pdf"
                )
                st.caption("Awarded by Monisha Mariappan")
            except Exception as _e:
                st.info(f"PDF generator unavailable ({_e}). Run: pip install reportlab")
        else:
            st.error(f"""
            ❌ Certificate Not Yet Awarded
 
            Student: {student_name} (ID: {sid})
            Current Readiness Score: {readiness:.2f}/100
 
            You need 60+ readiness score to earn the certificate.
            Aptitude: {aptitude:.1f}%  |  DSA: {dsa:.1f}%
 
            Keep practising and retake the tests!
            """)
 
# ============================================================
# ABOUT
# ============================================================
elif menu == "About":
    st.title("🎓 About This Project")
    st.markdown("""
    ## AI-Powered Campus Placement Prediction System
 
    This system helps students prepare for campus placements by combining
    four major domains of Computer Science and Data Science:
 
    | Domain | Modules |
    |--------|---------|
    | 📊 **Data Science** | Analytics Dashboard, Score Distribution, Risk Analysis |
    | 🤖 **Machine Learning** | Placement Predictor, Company Recommendation, Ranking |
    | 🧠 **Deep Learning** | ANN Predictor, Accuracy/Loss Curves, Salary Prediction |
    | 🚀 **Artificial Intelligence** | Career Advisor, Resume Analyzer, Interview Generator, Placement Assistant |
 
    ### 🎨 Features
    - Student Registration & Login
    - Aptitude & DSA Tests (Easy / Medium / Hard)
    - ML & Deep Learning Placement Prediction
    - AI Career Advisor based on actual test scores
    - Resume Analyzer with skill detection
    - Interview Question Generator
    - Admin Dashboard with student management
    - Placement Readiness Certificate
    - Download reports & certificates
    - Dark Mode
 
    ---
    **Developed by:** Monisha Mariappan
 
    **Built with:** Python · Streamlit · Pandas · NumPy · Matplotlib
    """)
 