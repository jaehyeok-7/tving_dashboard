import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="TVING Sports Dashboard v1", layout="wide")

DATA_DIR = Path("data/raw")

@st.cache_data
def load_csv(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        return None
    return pd.read_csv(path)

def to_dt(df, col):
    if df is not None and col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

st.title("스포츠 이용자 이탈 위험 대시보드 (v1)")

# 여기 파일명이 너 폴더에 있는 파일명이랑 같아야 함
churn = load_csv("churn_final_data.csv")
watch = load_csv("watch_data.csv")
search = load_csv("search_data.csv")
reco  = load_csv("recommend_data.csv")

missing = [name for name, df in [
    ("churn_final_data.csv", churn),
    ("watch_data.csv", watch),
    ("search_data.csv", search),
    ("recommend_data.csv", reco),
] if df is None]

if missing:
    st.warning("배포 환경에 data/raw CSV가 없어 데모 모드로 실행합니다.")
    churn = pd.DataFrame({"user_id":[1,2,3], "churn_status":[0,1,0]})
    watch = pd.DataFrame({"user_id":[1,2,3], "timestamp": pd.to_datetime(["2026-02-01","2026-02-02","2026-02-03"]),
                          "watch_duration_minutes":[30,10,50]})
    search = pd.DataFrame({"user_id":[1], "timestamp": pd.to_datetime(["2026-02-01"])})
    reco  = pd.DataFrame({"user_id":[1], "timestamp": pd.to_datetime(["2026-02-01"])})

watch = to_dt(watch, "timestamp")
search = to_dt(search, "timestamp")
reco = to_dt(reco, "timestamp")

st.sidebar.header("필터")

# 주차 필터(가능하면)
if "timestamp" in watch.columns:
    watch["week"] = watch["timestamp"].dt.to_period("W").astype(str)
    week_list = ["all"] + sorted(watch["week"].dropna().unique().tolist())
else:
    week_list = ["all"]

selected_week = st.sidebar.selectbox("주차", week_list)

w = watch.copy()
if selected_week != "all" and "week" in w.columns:
    w = w[w["week"] == selected_week]

# 위험군 정의(v1)
risk_col = None
if "churn_risk_score" in churn.columns:
    risk_col = "churn_risk_score"
elif "churn_status" in churn.columns:
    risk_col = "churn_status"

st.subheader("Overview: 얼마나 위험한가")

c1, c2, c3 = st.columns(3)

if risk_col == "churn_risk_score":
    thr = st.sidebar.slider("위험 점수 임계값", 0.0, 1.0, 0.7, 0.05)
    churn["is_risk"] = (churn[risk_col] >= thr).astype(int)
    c1.metric("위험군 비율", f"{churn['is_risk'].mean():.1%}")
elif risk_col == "churn_status":
    churn["is_risk"] = churn[risk_col].astype(int)
    c1.metric("위험군 비율", f"{churn['is_risk'].mean():.1%}")
else:
    c1.metric("위험군 비율", "risk 컬럼 없음")

if "user_id" in w.columns:
    c2.metric("활성 사용자 수(시청)", f"{w['user_id'].nunique():,}")
else:
    c2.metric("활성 사용자 수", "user_id 없음")

watch_time_col = None
for cand in ["watch_duration_minutes", "watch_minutes", "watch_hours", "watch_time"]:
    if cand in w.columns:
        watch_time_col = cand
        break

if watch_time_col:
    c3.metric("평균 시청량", f"{w[watch_time_col].mean():.2f}")
else:
    c3.metric("평균 시청량", "시간 컬럼 없음")

st.divider()

st.subheader("상태 분류: 누가 위험한가 (v1)")
seg_col = None
for cand in ["segment", "sports_segment", "user_segment"]:
    if cand in churn.columns:
        seg_col = cand
        break

if seg_col and "is_risk" in churn.columns:
    seg = churn.groupby(seg_col)["is_risk"].agg(["count", "mean"]).reset_index()
    seg.columns = [seg_col, "user_count", "risk_ratio"]
    st.dataframe(seg, use_container_width=True)
else:
    st.info("세그먼트 컬럼이 없거나 위험 라벨이 없어 v1에서는 표시하지 않음")

st.divider()

st.subheader("타이밍 분석 / 이탈 구간 / 액션 가이드")
st.write("v1에서는 docs/persona_sports_dashboard.md에 정의한 구조를 기준으로, 데이터 컬럼 추가 시 지표를 확장하는 형태로 구성")