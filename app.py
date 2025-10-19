import random
import time
import pandas as pd
import streamlit as st

# ================== 기본 설정 ==================
st.set_page_config(page_title="기억 폭 확장 훈련 ver.2", page_icon="🧠", layout="centered")

# 참/거짓 문장 풀(정답: True=참, False=거짓)
TRUE_STMTS = [
    "바다는 소금물이다.",
    "고양이는 포유류이다.",
    "서울은 대한민국의 수도이다.",
    "얼음은 물보다 가볍다.",
    "나무는 광합성을 한다.",
    "사람의 심장은 좌측 흉부 쪽에 있다.",
]
FALSE_STMTS = [
    "해는 서쪽에서 뜬다.",
    "달은 낮에만 뜬다.",
    "물의 끓는점은 50도이다.",
    "사람은 잠을 자지 않아도 산다.",
    "고양이는 파충류이다.",
    "서울은 일본의 수도이다.",
]

# 짝수(단어 제시) 단어 풀
WORD_POOL = [
    "나무", "구름", "연필", "시계", "바다", "달", "책", "꽃", "고래", "바람",
    "산", "강", "도시", "별", "비", "눈", "모래", "우산", "사과", "해바라기",
]

TOTAL = 10  # 총 문항 수 (고정: 10)
EVEN_INDEXES = [2, 4, 6, 8, 10]  # 짝수 문항 번호

# ================== 유틸 함수 ==================
def make_quiz(seed=None):
    """10문제 구성: 홀수=판단, 짝수=단어"""
    if seed:
        random.seed(seed)
    else:
        random.seed()

    # 홀수 5문항(판단): True/False 섞기 (true 3, false 2 예시)
    true_pick = random.sample(TRUE_STMTS, 3)
    false_pick = random.sample(FALSE_STMTS, 2)
    judge_pool = [(s, True) for s in true_pick] + [(s, False) for s in false_pick]
    random.shuffle(judge_pool)

    # 짝수 5문항(단어)
    words = random.sample(WORD_POOL, 5)

    # 1~10 구성
    problems = []
    judge_idx = 0
    word_idx = 0
    for i in range(1, TOTAL + 1):
        if i % 2 == 1:
            s, ans = judge_pool[judge_idx]
            judge_idx += 1
            problems.append({
                "no": i,
                "type": "judge",
                "prompt": s,
                "answer_bool": ans,  # True/False
            })
        else:
            w = words[word_idx]
            word_idx += 1
            problems.append({
                "no": i,
                "type": "word",
                "word": w,          # 기억할 단어
            })
    return problems

def reset_quiz(seed=None):
    st.session_state.problems = make_quiz(seed)   # ← 안전한 키 이름
    st.session_state.idx = 0
    st.session_state.history = []   # 진행 중 기록(판단 문제용)
    st.session_state.mem_words = [it["word"] for it in st.session_state.problems if it["type"] == "word"]  # 5개
    st.session_state.start_time = time.time()
    st.session_state.stage = "quiz"   # quiz -> recall -> result
    st.session_state.ans_recall = [""] * 5  # 주관식 입력 버퍼

# ================== 사이드바 ==================
with st.sidebar:
    st.header("설정")
    name = st.text_input("이름", "")
    klass = st.text_input("반(선택)", "")
    sid = st.text_input("번호(선택)", "")
    seed_val = st.text_input("랜덤 시드(선택, 동일세트 재현)", "")
    if st.button("새 퀴즈 시작"):
        reset_quiz(seed_val.strip() or None)

# 초기화
if "stage" not in st.session_state:
    reset_quiz(seed=None)

# ================== 본문 ==================
st.title("🧠 기억 폭 확장 훈련 ver.2")
st.caption("홀수 문항: 참/거짓(O/X) 선택 · 짝수 문항: 단어만 제시 → 끝나면 짝수 단어를 순서대로 입력")

if st.session_state.stage == "quiz":
    idx = st.session_state.idx
    problems = st.session_state.problems

    if idx < TOTAL:
        item = problems[idx]
        st.markdown(f"**진행:** {idx + 1} / {TOTAL}")
        st.progress(idx / TOTAL)
        st.markdown("---")

        if item["type"] == "judge":
            st.subheader(f"{item['no']}번) 참/거짓 판단")
            st.markdown(f"### {item['prompt']}")

            cols = st.columns(2)
            # O = True, X = False
            if cols[0].button("⭕ O (참) / True", use_container_width=True):
                correct = item["answer_bool"] is True
                st.session_state.history.append({
                    "문항": item["no"],
                    "유형": "판단",
                    "문장": item["prompt"],
                    "선택": "O",
                    "정답": "O" if item["answer_bool"] else "X",
                    "결과": "정답" if correct else "오답"
                })
                st.session_state.idx += 1
                st.rerun()

            if cols[1].button("❌ X (거짓) / False", use_container_width=True):
                co
