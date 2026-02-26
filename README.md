TVING 스포츠 페르소나 대시보드 (v1)

구성
- 설계 문서: docs/persona_sports_dashboard.md
- 대시보드 코드: app/streamlit_app.py

실행 방법
1) data/raw 폴더에 CSV 4개 넣기
- churn_final_data.csv
- watch_data.csv
- search_data.csv
- recommend_data.csv

2) 설치 및 실행
pip install -r requirements.txt
streamlit run app\streamlit_app.py

메모
- 오리지널 flag 기준은 현직자 답변 수신 전이므로 v1에서는 임시 기준으로 진행, 추후 v2에서 업데이트