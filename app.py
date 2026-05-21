import streamlit as st
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

# 앱 제목 설정
st.title("시계열 데이터 몬테카를로")
st.markdown("업로드 데이터에 가우시안 노이즈 적용")

# 1. 파일 업로드 (CSV)
uploaded_file = st.file_uploader("원본 CSV 파일을 업로드하세요 ('Data' 컬럼 필수)", type=['csv'])

if uploaded_file is not None:
    # 데이터 읽기
    df = pd.read_csv(uploaded_file)
    
    if 'Data' not in df.columns:
        st.error("⚠️ 업로드한 파일에 'Data' 컬럼이 없습니다. 파일 형식을 확인해주세요.")
    else:
        st.success("파일이 성공적으로 업로드되었습니다.")
        base_data = df['Data'].values
        n_time_steps = len(base_data)

        st.markdown("---")
        st.subheader("파라미터 설정")
        
        # 2 & 3. 사용자 입력 폼 (컬럼으로 나누어 UI 구성)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            upper_error = st.number_input("상한 허용 오차 (절대값)", min_value=0.0, value=0.5, step=0.1, help="기준 데이터 + 입력값")
        with col2:
            lower_error = st.number_input("하한 허용 오차 (절대값)", min_value=0.0, value=0.5, step=0.1, help="기준 데이터 - 입력값")
        with col3:
            n_simulations = st.number_input("데이터 생성 수 (n)", min_value=1, max_value=10000, value=100, step=10)

        # 4. 생성하기 버튼
        if st.button("데이터 생성하기"):
            with st.spinner('가상 데이터를 생성중...'):
                # 3-sigma 규칙을 위한 표준편차 계산
                # 상/하한 중 더 넓은 범위를 기준으로 가우시안 분포를 형성하고, 이후 Clipping으로 잘라냄
                max_abs_error = max(upper_error, lower_error)
                sigma = max_abs_error / 3.0 if max_abs_error > 0 else 0
                
                virtual_data = np.zeros((n_simulations, n_time_steps))
                
                # 노이즈 생성 및 클리핑
                for i in range(n_simulations):
                    # 전체 시계열 길이에 맞는 노이즈를 한 번에 생성 (속도 최적화)
                    noise = np.random.normal(loc=0.0, scale=sigma, size=n_time_steps)
                    simulated_series = base_data + noise
                    
                    # 사용자가 지정한 상한/하한 절대값으로 상하한선 설정 및 클리핑
                    upper_bound = base_data + upper_error
                    lower_bound = base_data - lower_error
                    lower_bound = np.maximum(0, lower_bound)
                    simulated_series = np.clip(simulated_series, lower_bound, upper_bound)
                    
                    virtual_data[i] = simulated_series
                
                st.success(f"※ {n_simulations}개의 가상 시계열 데이터가 생성되었습니다!")
                
                # # 시각화 (사용자가 결과를 눈으로 확인할 수 있도록 제공)
                # st.subheader("📈 생성 결과 미리보기")
                # fig, ax = plt.subplots(figsize=(10, 4))
                
                # # 시각화 부하를 줄이기 위해 최대 100개만 플로팅
                # plot_count = min(n_simulations, 100)
                # for i in range(plot_count):
                #     ax.plot(virtual_data[i], color='gray', alpha=0.1)
                
                # ax.plot(base_data, color='red', linewidth=1.5, marker='.', label='Original')
                # ax.plot(base_data + upper_error, color='blue', linestyle='--', linewidth=1, label='Upper Bound')
                # ax.plot(base_data - lower_error, color='blue', linestyle='--', linewidth=1, label='Lower Bound')
                # ax.set_title(f'Monte Carlo Simulation (Showing {plot_count} samples)')
                # ax.legend(loc='upper right')
                # st.pyplot(fig)

                # 데이터프레임 변환
                columns = [f'Sim_{i+1}' for i in range(n_simulations)]
                result_df = pd.DataFrame(virtual_data.T, columns=columns)
                result_df.insert(0, 'Original_Data', base_data)
                
                # 4. CSV 다운로드 버튼
                st.markdown("---")
                csv = result_df.to_csv(index=False).encode('utf-8-sig') # 한글 깨짐 방지 인코딩
                st.download_button(
                    label="↓ 결과 CSV 다운로드",
                    data=csv,
                    file_name="New-samples_Noise.csv",
                    mime="text/csv"
                )