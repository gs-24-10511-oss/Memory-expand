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

TOTAL = 10
EVEN_INDEXES = [2, 4, 6, 8, 10]

# ================== 유틸 함수 ==================
def make_quiz(seed=None):
    if seed:
        random.seed(seed)
    else:
        random.seed()

    true_pick = random.sample(TRUE_STMTS, 3)
    false_pick = random.sample(FALSE_STMTS, 2)
    judge_pool = [(s, True) for s in true_pick] + [(s, False) for s in false_pick]
    random.shuffle(judge_pool)

    words = random.sample(WORD_POOL, 5)

    problems = []
    ji = wi = 0
    for i in range(1, TOTAL + 1):
        if i % 2 == 1:
            s, ans = judge_pool[ji]; ji += 1
            problems.append({"no": i, "type": "judge", "prompt": s, "answer_bool": ans})
        else:
            w = words[wi]; wi += 1
            problems.append({"no": i, "type": "word", "word": w})
    return problems

def reset_quiz(seed=None):
    st.session_state.problems = make_quiz(seed)
    st.session_state.idx = 0
    st.session_state.history = []
    st.session_state.mem_words = [it["word"] for it in st.session_state.problems if it["type"] == "word"]
    st.session_state.stage = "quiz"
    st.session_state.ans_recall = [""] * 5

# ================== 사이드바 ==================
with st.sidebar:
    st.header("설정")
    name = st.text_input("이름", "")
    klass = st.text_input("반(선택)", "")
    sid = st.text_input("번호(선택)", "")
    seed_val = st.text_input("랜덤 시드(선택, 동일세트 재현)", "")
    if st.button("새 퀴즈 시작"):
        reset_quiz(seed_val.strip() or None)
        st.rerun()

if "stage" not in st.session_state:
    reset_quiz(seed=None)

# ================== 렌더링 함수 ==================
def render_quiz():
    idx = st.session_state.idx
    problems = st.session_state.problems

    st.title("🧠 기억 폭 확장 훈련 ver.2")
    st.caption("홀수: 참/거짓(O/X) · 짝수: 단어 제시 → 끝나면 짝수 단어를 순서대로 입력")

    # 모든 문제 완료 → 즉시 리콜 화면으로 전환 렌더
    if idx >= TOTAL:
        st.session_state.stage = "recall"
        render_recall()   # ← rerun 없이 즉시 리콜화면 그리기
        return

    item = problems[idx]
    st.markdown(f"**진행:** {idx + 1} / {TOTAL}")
    st.progress(idx / TOTAL)
    st.markdown("---")

    if item["type"] == "judge":
        st.subheader(f"{item['no']}번) 참/거짓 판단")
        st.markdown(f"### {item['prompt']}")

        cols = st.columns(2)
        if cols[0].button("⭕ O (참)", use_container_width=True):
            correct = item["answer_bool"] is True
            st.session_state.history.append({
                "문항": item["no"], "유형": "판단", "문장": item["prompt"],
                "선택": "O", "정답": "O" if item["answer_bool"] else "X",
                "결과": "정답" if correct else "오답"
            })
            st.session_state.idx += 1
            st.rerun()

        if cols[1].button("❌ X (거짓)", use_container_width=True):
            correct = item["answer_bool"] is False
            st.session_state.history.append({
                "문항": item["no"], "유형": "판단", "문장": item["prompt"],
                "선택": "X", "정답": "O" if item["answer_bool"] else "X",
                "결과": "정답" if correct else "오답"
            })
            st.session_state.idx += 1
            st.rerun()

    else:
        st.subheader(f"{item['no']}번) 단어 기억")
        st.markdown(f"### {item['word']}")
        st.info("이 단어를 기억하세요. (선택 없음)")

        if st.button("기억했어요 → 다음", use_container_width=True):
            st.session_state.history.append({
                "문항": item["no"], "유형": "단어", "문장": "(단어 제시)",
                "선택": "(제시됨)", "정답": item["word"], "결과": "제시"
            })
            st.session_state.idx += 1
            st.rerun()

def render_recall():
    st.title("✍️ 기억 회상(짝수 문항)")
    st.subheader("2, 4, 6, 8, 10번에 제시된 단어를 **순서대로** 입력하세요.")

    labels = ["2번 단어", "4번 단어", "6번 단어", "8번 단어", "10번 단어"]
    with st.form("recall_form"):
        inputs = []
        for i, label in enumerate(labels):
            default = st.session_state.ans_recall[i]
            inputs.append(st.text_input(label, value=default))
        submitted = st.form_submit_button("채점하기")

    if submitted:
        st.session_state.ans_recall = inputs
        gold = st.session_state.mem_words
        user = [a.strip() for a in st.session_state.ans_recall]

        rows = []
        rs = 0
        for i, (g, u) in enumerate(zip(gold, user), start=1):
            ok = (u == g)
            rs += 1 if ok else 0
            rows.append({
                "순번(짝수)": EVEN_INDEXES[i - 1],
                "정답단어": g,
                "내답": u if u else "미입력",
                "결과": "정답" if ok else "오답"
            })

        st.session_state.recall_df = pd.DataFrame(rows)
        st.session_state.recall_score = rs
        st.session_state.judge_score = sum(1 for r in st.session_state.history if r["유형"] == "판단" and r["결과"] == "정답")
        st.session_state.stage = "result"
        st.rerun()

def render_result():
    st.title("📊 결과 요약")

    judge_score = st.session_state.judge_score
    recall_score = st.session_state.recall_score
    st.write(f"- 판단문항(홀수) 점수: **{judge_score} / 5**")
    st.write(f"- 기억회상(짝수) 점수: **{recall_score} / 5**")
    st.success(f"총점: **{judge_score + recall_score} / 10**")

    st.markdown("---")
    st.subheader("판단문항 기록")
    df_judge = pd.DataFrame([r for r in st.session_state.history if r["유형"] == "판단"])
    if not df_judge.empty:
        df_judge.insert(0, "이름", name if name else "미기입")
        df_judge.insert(1, "반", klass if klass else "미기입")
        df_judge.insert(2, "번호", sid if sid else "미기입")
        st.dataframe(df_judge, use_container_width=True)
    else:
        st.info("판단문항 기록이 없습니다.")

    st.subheader("기억회상(짝수) 채점표")
    df_recall = st.session_state.recall_df.copy()
    df_recall.insert(0, "이름", name if name else "미기입")
    df_recall.insert(1, "반", klass if klass else "미기입")
    df_recall.insert(2, "번호", sid if sid else "미기입")
    st.dataframe(df_recall, use_container_width=True)

    st.markdown("### 📥 결과 CSV 다운로드")
    if not df_judge.empty:
        csv_judge = df_judge.to_csv(index=False).encode("utf-8-sig")
        st.download_button("판단문항 결과 다운로드", data=csv_judge,
                           file_name=f"기폭훈련_판단_{name or '미기입'}.csv", mime="text/csv")
    csv_recall = df_recall.to_csv(index=False).encode("utf-8-sig")
    st.download_button("기억회상 결과 다운로드", data=csv_recall,
                       file_name=f"기폭훈련_회상_{name or '미기입'}.csv", mime="text/csv")

    st.markdown("---")
    if st.button("다시 시작(새 세트)"):
        reset_quiz(seed=None)
        st.rerun()

# ================== 라우팅 ==================
stage = st.session_state.stage
if stage == "quiz":
    render_quiz()
elif stage == "recall":
    render_recall()
else:
    render_result()
