import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json
import time
from datetime import datetime, timedelta
import pytz
import numpy as np
from typing import Dict, List, Optional
import os
import base64
try:
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    print("Warning: geopy and timezonefinder not available. Some features will be disabled.")

# 페이지 설정
st.set_page_config(
    page_title="✈️ FlightAware Advanced Tracker",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FlightAware Advanced CSS - Clean White/Gray Theme (Compact)
st.markdown("""
<style>
    /* 전체 배경 - 깔끔한 화이트/그레이 */
    .stApp {
        background: #fafafa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 메인 헤더 - 밝은 회색 */
    .main-header {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        color: #495057;
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        animation: slideInFromTop 0.6s ease-out;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(73, 80, 87, 0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    .main-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 0.6rem;
        opacity: 0.8;
        margin: 0.1rem 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* 컴팩트 카드 디자인 */
    .advanced-card {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.4rem;
        margin: 0.3rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
        font-size: 0.7rem;
    }
    
    .advanced-card h4 {
        font-size: 0.65rem;
        margin: 0 0 0.2rem 0;
        color: #6c757d;
    }
    
    .advanced-card p {
        font-size: 0.65rem;
        margin: 0.1rem 0;
        color: #2c3e50;
    }
    
    .advanced-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(108, 117, 125, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .advanced-card:hover::before {
        left: 100%;
    }
    
    .advanced-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        border-color: #6c757d;
    }
    
    /* 섹션 제목 - 컴팩트 */
    .section-title {
        color: #2c3e50;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.8rem 0 0.4rem 0;
        padding-left: 0.5rem;
        border-left: 3px solid #6c757d;
    }
    
    /* 메트릭 컨테이너 - 컴팩트 */
    .metric-container {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        padding: 0.5rem;
        text-align: center;
        margin: 0.3rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .metric-container h4 {
        font-size: 0.7rem;
        margin: 0 0 0.3rem 0;
        color: #6c757d;
    }
    
    .metric-container h3 {
        font-size: 0.9rem;
        margin: 0;
        color: #2c3e50;
    }
    
    .metric-container:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-color: #6c757d;
    }
    
    /* 버튼 스타일 - 컴팩트 */
    .stButton > button {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.4rem 1.2rem;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 6px rgba(108, 117, 125, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(108, 117, 125, 0.4);
        background: linear-gradient(135deg, #495057 0%, #343a40 100%);
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg {
        background: #f8f9fa;
        border-right: 1px solid #e1e5e9;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        color: #2c3e50;
        font-size: 0.75rem;
        padding: 0.3rem 0.5rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6c757d;
        box-shadow: 0 0 0 2px rgba(108, 117, 125, 0.2);
    }
    
    .stSelectbox > div > div > select {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        color: #2c3e50;
        font-size: 0.75rem;
        padding: 0.3rem 0.5rem;
    }
    
    /* 테이블 스타일 */
    .dataframe {
        background: white;
        border-radius: 6px;
        overflow: hidden;
        border: 1px solid #e1e5e9;
        font-size: 0.7rem;
    }
    
    /* 메인 검색 영역 */
    .main-search-container {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .search-title {
        color: #2c3e50;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .search-subtitle {
        color: #6c757d;
        font-size: 0.7rem;
        margin-bottom: 1.2rem;
        line-height: 1.4;
    }
    
    .search-section {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .search-divider {
        color: #6c757d;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .search-input-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .search-input {
        padding: 0.5rem 0.8rem;
        border: 1px solid #e1e5e9;
        border-radius: 6px;
        font-size: 0.75rem;
        min-width: 200px;
    }
    
    .search-button {
        background: #6c757d;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .search-button:hover {
        background: #495057;
    }
    
    /* 애니메이션 */
    @keyframes slideInFromTop {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .fade-in {
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* 로딩 스피너 - 컴팩트 */
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(108, 117, 125, 0.3);
        border-radius: 50%;
        border-top-color: #6c757d;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* 상태 표시기 - 컴팩트 */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-on-time { background-color: #28a745; }
    .status-delayed { background-color: #ffc107; }
    .status-cancelled { background-color: #dc3545; }
    .status-boarding { background-color: #17a2b8; }
</style>
""", unsafe_allow_html=True)

# 고급 FlightAware API 클래스
class AdvancedFlightAwareAPI:
    def __init__(self):
        self.api_key = os.getenv("FLIGHTAWARE_API_KEY")
        self.base_url = "https://flightxml.flightaware.com/json/FlightXML2"
        if GEOPY_AVAILABLE:
            self.geolocator = Nominatim(user_agent="flightaware_app")
            self.tf = TimezoneFinder()
        else:
            self.geolocator = None
            self.tf = None
        
    def get_flight_info_advanced(self, flight_number: str) -> Dict:
        """고급 항공편 정보 조회"""
        # 실제 API 호출 시뮬레이션
        time.sleep(1)
        
        # 항공편 상태 시뮬레이션
        statuses = ["On Time", "Delayed", "Boarding", "Departed", "In Flight", "Landed"]
        current_status = np.random.choice(statuses)
        
        # 지연 시간 계산
        delay_minutes = np.random.randint(0, 120) if current_status == "Delayed" else 0
        
        return {
            "flight_number": flight_number,
            "airline": self._get_airline_from_code(flight_number[:2]),
            "aircraft": np.random.choice(["Boeing 737-800", "Airbus A320", "Boeing 777-300ER", "Airbus A330-300"]),
            "departure": {
                "airport": "ICN",
                "airport_name": "인천국제공항",
                "city": "서울",
                "country": "대한민국",
                "scheduled_time": "14:30",
                "actual_time": f"{(14 + delay_minutes // 60):02d}:{(30 + delay_minutes % 60):02d}",
                "gate": "A12",
                "terminal": "T1",
                "latitude": 37.4602,
                "longitude": 126.4407
            },
            "arrival": {
                "airport": "NRT",
                "airport_name": "나리타국제공항",
                "city": "도쿄",
                "country": "일본",
                "scheduled_time": "17:45",
                "actual_time": f"{(17 + delay_minutes // 60):02d}:{(45 + delay_minutes % 60):02d}",
                "gate": "B8",
                "terminal": "T1",
                "latitude": 35.7720,
                "longitude": 140.3928
            },
            "status": current_status,
            "delay_minutes": delay_minutes,
            "duration": "2시간 10분",
            "distance": "1,300 km",
            "altitude": f"{np.random.randint(30000, 40000):,} ft",
            "speed": f"{np.random.randint(800, 950)} km/h",
            "progress": np.random.randint(0, 100)
        }
    
    def get_weather_info(self, airport_code: str) -> Dict:
        """공항 날씨 정보 조회"""
        # 세션 상태에 데이터 캐싱
        cache_key = f"weather_{airport_code}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(hash(airport_code + "weather") % 2**32)
        
        # 날씨 시뮬레이션
        conditions = ["맑음", "흐림", "비", "눈", "안개"]
        result = {
            "temperature": np.random.randint(-5, 35),
            "condition": np.random.choice(conditions),
            "humidity": np.random.randint(30, 90),
            "wind_speed": np.random.randint(5, 25),
            "visibility": np.random.randint(5, 15)
        }
        
        st.session_state[cache_key] = result
        return result
    
    def get_airport_delays(self, airport_code: str) -> Dict:
        """공항 지연 정보"""
        # 세션 상태에 데이터 캐싱
        cache_key = f"delays_{airport_code}"
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(hash(airport_code + "delays") % 2**32)
        
        result = {
            "average_delay": np.random.randint(10, 45),
            "delayed_flights": np.random.randint(5, 25),
            "cancelled_flights": np.random.randint(0, 5),
            "total_flights": np.random.randint(100, 300)
        }
        
        st.session_state[cache_key] = result
        return result
    
    def get_flight_route(self, flight_number: str) -> List[Dict]:
        """항공편 경로 정보"""
        # 실제 경로 시뮬레이션
        route_points = [
            {"lat": 37.4602, "lon": 126.4407, "alt": 0, "time": "14:30", "status": "Departure"},
            {"lat": 37.0, "lon": 130.0, "alt": 35000, "time": "15:00", "status": "Climbing"},
            {"lat": 36.5, "lon": 135.0, "alt": 38000, "time": "15:30", "status": "Cruising"},
            {"lat": 36.0, "lon": 137.5, "alt": 38000, "time": "16:00", "status": "Cruising"},
            {"lat": 35.8, "lon": 139.5, "alt": 25000, "time": "16:30", "status": "Descending"},
            {"lat": 35.7720, "lon": 140.3928, "alt": 0, "time": "17:45", "status": "Arrival"}
        ]
        return route_points
    
    def _get_airline_from_code(self, code: str) -> str:
        """항공사 코드를 이름으로 변환"""
        airlines = {
            "KE": "대한항공",
            "OZ": "아시아나항공",
            "JL": "일본항공",
            "NH": "전일본공수",
            "CA": "중국국제항공",
            "MU": "중국동방항공",
            "SQ": "싱가포르항공",
            "TG": "타이항공",
            "AA": "아메리칸항공",
            "DL": "델타항공",
            "UA": "유나이티드항공"
        }
        return airlines.get(code, code)

# API 인스턴스
flight_api = AdvancedFlightAwareAPI()

# 메인 애플리케이션
def main():
    # 메인 헤더
    st.markdown("""
    <div class="main-header fade-in">
        <h1 class="main-title">Flight Tracker Advanced</h1>
        <p class="main-subtitle">Advanced Flight Tracking & Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 기본 대시보드만 표시
    display_advanced_dashboard()

def display_detailed_flight_info(flight_number: str):
    """상세 항공편 정보 표시"""
    st.markdown('<h2 class="section-title">📋 항공편 상세 정보</h2>', unsafe_allow_html=True)
    
    with st.spinner("상세 정보를 조회하는 중..."):
        flight_info = flight_api.get_flight_info_advanced(flight_number)
    
    # 항공편 기본 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3>✈️ 항공편</h3>
            <h2>{flight_info["flight_number"]}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🏢 항공사</h3>
            <h2>{flight_info["airline"]}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h3>🛩️ 항공기</h3>
            <h2>{flight_info["aircraft"]}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status_color = "🟢" if flight_info["status"] == "On Time" else "🟡" if "Delayed" in flight_info["status"] else "🔴"
        st.markdown(f"""
        <div class="metric-container">
            <h3>📊 상태</h3>
            <h2>{status_color} {flight_info['status']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # 지연 정보
    if flight_info["delay_minutes"] > 0:
        st.warning(f"⚠️ {flight_info['delay_minutes']}분 지연")
    
    # 출발/도착 정보
    st.markdown('<h3 class="section-title">🛫 출발 정보</h3>', unsafe_allow_html=True)
    dep_col1, dep_col2, dep_col3, dep_col4 = st.columns(4)
    
    with dep_col1:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🏢 공항</h4>
            <p><strong>{flight_info['departure']['airport']}</strong></p>
            <p>{flight_info['departure']['airport_name']}</p>
            <p>{flight_info['departure']['city']}, {flight_info['departure']['country']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dep_col2:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>⏰ 시간</h4>
            <p><strong>예정:</strong> {flight_info['departure']['scheduled_time']}</p>
            <p><strong>실제:</strong> {flight_info['departure']['actual_time']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dep_col3:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🚪 게이트</h4>
            <p><strong>게이트:</strong> {flight_info['departure']['gate']}</p>
            <p><strong>터미널:</strong> {flight_info['departure']['terminal']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with dep_col4:
        weather = flight_api.get_weather_info(flight_info['departure']['airport'])
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🌤️ 날씨</h4>
            <p><strong>온도:</strong> {weather['temperature']}°C</p>
            <p><strong>상태:</strong> {weather['condition']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 도착 정보
    st.markdown('<h3 class="section-title">🛬 도착 정보</h3>', unsafe_allow_html=True)
    arr_col1, arr_col2, arr_col3, arr_col4 = st.columns(4)
    
    with arr_col1:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🏢 공항</h4>
            <p><strong>{flight_info['arrival']['airport']}</strong></p>
            <p>{flight_info['arrival']['airport_name']}</p>
            <p>{flight_info['arrival']['city']}, {flight_info['arrival']['country']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with arr_col2:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>⏰ 시간</h4>
            <p><strong>예정:</strong> {flight_info['arrival']['scheduled_time']}</p>
            <p><strong>실제:</strong> {flight_info['arrival']['actual_time']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with arr_col3:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🚪 게이트</h4>
            <p><strong>게이트:</strong> {flight_info['arrival']['gate']}</p>
            <p><strong>터미널:</strong> {flight_info['arrival']['terminal']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with arr_col4:
        weather = flight_api.get_weather_info(flight_info['arrival']['airport'])
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🌤️ 날씨</h4>
            <p><strong>온도:</strong> {weather['temperature']}°C</p>
            <p><strong>상태:</strong> {weather['condition']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 비행 상세 정보
    st.markdown('<h3 class="section-title">📊 비행 상세</h3>', unsafe_allow_html=True)
    detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
    
    with detail_col1:
        st.metric("비행 시간", flight_info["duration"])
    with detail_col2:
        st.metric("거리", flight_info["distance"])
    with detail_col3:
        st.metric("현재 고도", flight_info["altitude"])
    with detail_col4:
        st.metric("현재 속도", flight_info["speed"])
    
    # 진행률 표시
    st.markdown('<h3 class="section-title">📈 비행 진행률</h3>', unsafe_allow_html=True)
    progress = flight_info["progress"]
    st.progress(progress / 100)
    st.write(f"비행 진행률: {progress}%")

def display_realtime_tracking(flight_number: str):
    """실시간 추적 표시"""
    st.markdown(f'<h2 class="section-title">📍 {flight_number} 실시간 추적</h2>', unsafe_allow_html=True)
    
    # 항공편 정보
    flight_info = flight_api.get_flight_info_advanced(flight_number)
    route_points = flight_api.get_flight_route(flight_number)
    
    # 실시간 추적 맵
    st.markdown('<h3 class="section-title">🗺️ 실시간 추적 맵</h3>', unsafe_allow_html=True)
    
    # 지도 생성
    m = folium.Map(
        location=[36.0, 135.0],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # 경로 그리기
    route_coords = [[point["lat"], point["lon"]] for point in route_points]
    folium.PolyLine(
        route_coords,
        color='blue',
        weight=4,
        opacity=0.8,
        popup=f'{flight_number} 경로'
    ).add_to(m)
    
    # 경로 포인트 마커
    for i, point in enumerate(route_points):
        color = 'green' if i == 0 else 'red' if i == len(route_points) - 1 else 'blue'
        folium.Marker(
            [point["lat"], point["lon"]],
            popup=f'{point["time"]} - {point["status"]}',
            icon=folium.Icon(color=color, icon='plane')
        ).add_to(m)
    
    # 현재 위치 (시뮬레이션)
    current_point = route_points[2]  # 중간 지점
    folium.Marker(
        [current_point["lat"], current_point["lon"]],
        popup=f'{flight_number} 현재 위치',
        icon=folium.Icon(color='orange', icon='plane', prefix='fa')
    ).add_to(m)
    
    st_folium(m, width=700, height=500)
    
    # 실시간 정보
    st.markdown('<h3 class="section-title">📡 실시간 정보</h3>', unsafe_allow_html=True)
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.metric("현재 고도", flight_info["altitude"])
    with info_col2:
        st.metric("현재 속도", flight_info["speed"])
    with info_col3:
        st.metric("남은 거리", f"{np.random.randint(500, 1000)} km")
    with info_col4:
        st.metric("예상 도착", flight_info["arrival"]["actual_time"])
    
    # 경로 상세 정보
    st.markdown('<h3 class="section-title">🛤️ 경로 상세</h3>', unsafe_allow_html=True)
    
    route_df = pd.DataFrame(route_points)
    st.dataframe(route_df, use_container_width=True)

def display_airport_status(airport_code: str):
    """공항 현황 표시"""
    st.markdown(f'<h2 class="section-title">🏢 {airport_code} 공항 현황</h2>', unsafe_allow_html=True)
    
    # 공항 지연 정보
    delay_info = flight_api.get_airport_delays(airport_code)
    
    # 지연 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균 지연", f"{delay_info['average_delay']}분")
    with col2:
        st.metric("지연 항공편", f"{delay_info['delayed_flights']}편")
    with col3:
        st.metric("취소 항공편", f"{delay_info['cancelled_flights']}편")
    with col4:
        st.metric("총 항공편", f"{delay_info['total_flights']}편")
    
    # 지연 차트
    st.markdown('<h3 class="section-title">📊 시간대별 지연 현황</h3>', unsafe_allow_html=True)
    
    # 세션 상태에 데이터 캐싱
    if "delay_chart_data" not in st.session_state:
        hours = list(range(24))
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(131415)
        delays = [np.random.randint(0, 60) for _ in hours]
        st.session_state["delay_chart_data"] = {"hours": hours, "delays": delays}
    
    delay_data = st.session_state["delay_chart_data"]
    hours = delay_data["hours"]
    delays = delay_data["delays"]
    
    fig = px.bar(
        x=hours,
        y=delays,
        title="시간대별 평균 지연 시간",
        color=delays,
        color_continuous_scale="reds"
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis_title="시간",
        yaxis_title="지연 시간 (분)"
    )
    st.plotly_chart(fig, use_container_width=True)

def display_weather_info(airport_code: str):
    """날씨 정보 표시"""
    st.markdown(f'<h2 class="section-title">🌤️ {airport_code} 날씨 정보</h2>', unsafe_allow_html=True)
    
    weather = flight_api.get_weather_info(airport_code)
    
    # 날씨 정보 카드
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>🌡️ 온도</h4>
            <h2>{weather['temperature']}°C</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>☁️ 상태</h4>
            <h2>{weather['condition']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>💧 습도</h4>
            <h2>{weather['humidity']}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>💨 풍속</h4>
            <h2>{weather['wind_speed']} km/h</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="advanced-card">
            <h4>👁️ 가시거리</h4>
            <h2>{weather['visibility']} km</h2>
        </div>
        """, unsafe_allow_html=True)

def display_delay_analysis(airport_code: str):
    """지연 분석 표시"""
    st.markdown(f'<h2 class="section-title">⏰ {airport_code} 지연 분석</h2>', unsafe_allow_html=True)
    
    # 지연 원인 분석 (시뮬레이션)
    delay_causes = {
        "기상 조건": 35,
        "항공 교통": 25,
        "기술적 문제": 20,
        "승객 지연": 15,
        "기타": 5
    }
    
    # 지연 원인 차트
    fig = px.pie(
        values=list(delay_causes.values()),
        names=list(delay_causes.keys()),
        title="지연 원인 분석",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#2c3e50',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 지연 트렌드
    st.markdown('<h3 class="section-title">📈 지연 트렌드</h3>', unsafe_allow_html=True)
    
    # 세션 상태에 데이터 캐싱
    if "delay_trend_data" not in st.session_state:
        days = list(range(1, 31))
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(161718)
        daily_delays = [np.random.randint(10, 50) for _ in days]
        st.session_state["delay_trend_data"] = {"days": days, "daily_delays": daily_delays}
    
    trend_data = st.session_state["delay_trend_data"]
    days = trend_data["days"]
    daily_delays = trend_data["daily_delays"]
    
    fig = px.line(
        x=days,
        y=daily_delays,
        title="일별 평균 지연 시간",
        markers=True
    )
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#2c3e50',
        xaxis_title="일",
        yaxis_title="지연 시간 (분)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def display_flight_comparison(flight1: str, flight2: str):
    """항공편 비교 표시"""
    st.markdown(f'<h2 class="section-title">⚖️ 항공편 비교: {flight1} vs {flight2}</h2>', unsafe_allow_html=True)
    
    # 두 항공편 정보 조회
    info1 = flight_api.get_flight_info_advanced(flight1)
    info2 = flight_api.get_flight_info_advanced(flight2)
    
    # 비교 테이블
    comparison_data = {
        "항목": ["항공편 번호", "항공사", "항공기", "상태", "지연 시간", "비행 시간", "거리"],
        flight1: [
            info1["flight_number"],
            info1["airline"],
            info1["aircraft"],
            info1["status"],
            f"{info1['delay_minutes']}분",
            info1["duration"],
            info1["distance"]
        ],
        flight2: [
            info2["flight_number"],
            info2["airline"],
            info2["aircraft"],
            info2["status"],
            f"{info2['delay_minutes']}분",
            info2["duration"],
            info2["distance"]
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)
    
    # 비교 차트
    st.markdown('<h3 class="section-title">📊 비교 차트</h3>', unsafe_allow_html=True)
    
    metrics = ["지연 시간", "비행 시간", "거리"]
    values1 = [info1["delay_minutes"], 130, 1300]  # 시뮬레이션
    values2 = [info2["delay_minutes"], 125, 1300]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name=flight1, x=metrics, y=values1))
    fig.add_trace(go.Bar(name=flight2, x=metrics, y=values2))
    
    fig.update_layout(
        title="항공편 비교",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#2c3e50',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def display_advanced_dashboard():
    """고급 대시보드 표시"""
    st.markdown('<h2 class="section-title">📊 고급 항공 현황 대시보드</h2>', unsafe_allow_html=True)
    
    # 주요 공항 현황
    st.markdown('<h3 class="section-title">🏢 주요 공항 현황</h3>', unsafe_allow_html=True)
    
    # 세션 상태에 데이터 캐싱
    if "advanced_airport_data" not in st.session_state:
        airports = ["ICN", "NRT", "HND", "PEK", "PVG", "SIN", "BKK"]
        airport_data = []
        
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(789)
        
        for airport in airports:
            delay_info = flight_api.get_airport_delays(airport)
            weather = flight_api.get_weather_info(airport)
            
            airport_data.append({
                "공항": airport,
                "총 항공편": delay_info["total_flights"],
                "지연 항공편": delay_info["delayed_flights"],
                "평균 지연": f"{delay_info['average_delay']}분",
                "온도": f"{weather['temperature']}°C",
                "날씨": weather["condition"]
            })
        
        st.session_state["advanced_airport_data"] = airport_data
    
    df = pd.DataFrame(st.session_state["advanced_airport_data"])
    st.dataframe(df, use_container_width=True)
    
    
    # 실시간 항공 교통 현황 (제목과 새로고침 버튼을 같은 줄에)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<h3 class="section-title">🛩️ Real-time Flight Status</h3>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄", key="refresh_flights", help="Refresh flight data", use_container_width=True):
            # 세션 상태 초기화하여 새 데이터 생성
            if "flight_map_data" in st.session_state:
                del st.session_state["flight_map_data"]
            if "flight_details" in st.session_state:
                del st.session_state["flight_details"]
            st.rerun()
    
    # 세션 상태에 맵 데이터 캐싱
    if "flight_map_data" not in st.session_state:
        # 현재 시간을 시드로 사용하여 매번 다른 데이터 생성
        import time
        current_time = int(time.time())
        np.random.seed(current_time % 2**32)
        
        flight_positions = []
        flight_details = []
        
        # 전 세계 주요 항공사 및 노선 데이터
        global_airlines = [
            "KE", "OZ", "NH", "JL", "CA", "MU", "CZ", "3U",  # 아시아
            "AA", "UA", "DL", "WN", "B6", "AS", "F9",        # 미국
            "LH", "AF", "BA", "KL", "LX", "OS", "SK",        # 유럽
            "QF", "VA", "NZ", "JQ",                          # 오세아니아
            "EK", "QR", "EY", "SV", "MS", "TK",              # 중동/아프리카
            "AC", "WS", "TS", "PD",                          # 캐나다
            "AV", "CM", "AR", "LA", "JJ"                     # 남미
        ]
        
        global_routes = [
            # 아시아 내
            "ICN → NRT", "ICN → LAX", "ICN → FRA", "ICN → SIN", "ICN → BKK", "ICN → HKG", "ICN → TPE",
            "NRT → LAX", "NRT → JFK", "NRT → LHR", "NRT → CDG", "NRT → FRA",
            "PEK → LAX", "PEK → JFK", "PEK → LHR", "PEK → CDG", "PEK → FRA",
            "SIN → LHR", "SIN → CDG", "SIN → FRA", "SIN → JFK", "SIN → LAX",
            # 대서양 횡단
            "JFK → LHR", "JFK → CDG", "JFK → FRA", "JFK → AMS", "JFK → ZUR",
            "LAX → LHR", "LAX → CDG", "LAX → FRA", "LAX → AMS",
            "LHR → JFK", "LHR → LAX", "LHR → ORD", "LHR → MIA",
            "CDG → JFK", "CDG → LAX", "CDG → ORD", "CDG → MIA",
            # 태평양 횡단
            "LAX → NRT", "LAX → ICN", "LAX → PEK", "LAX → PVG",
            "JFK → NRT", "JFK → ICN", "JFK → PEK", "JFK → PVG",
            # 유럽 내
            "LHR → CDG", "LHR → FRA", "LHR → AMS", "LHR → ZUR", "LHR → VIE",
            "CDG → FRA", "CDG → AMS", "CDG → ZUR", "CDG → VIE",
            # 중동/아프리카
            "DXB → LHR", "DXB → CDG", "DXB → JFK", "DXB → LAX",
            "DOH → LHR", "DOH → CDG", "DOH → JFK", "DOH → LAX",
            # 오세아니아
            "SYD → LAX", "SYD → LHR", "SYD → CDG", "SYD → JFK",
            "MEL → LAX", "MEL → LHR", "MEL → CDG", "MEL → JFK"
        ]
        
        statuses = ["On Time", "Delayed", "Boarding", "In Flight", "Approaching", "Departed", "Landed"]
        
        # 전 세계 주요 항공로에 따른 비행기 위치 생성
        for i in range(50):  # 항공편 수 대폭 증가
            # 전 세계 좌표 범위
            region = np.random.choice(["asia_pacific", "trans_pacific", "trans_atlantic", "europe", "americas", "middle_east_africa"])
            
            if region == "asia_pacific":
                lat = np.random.uniform(10, 50)   # 아시아-태평양
                lon = np.random.uniform(100, 180)
            elif region == "trans_pacific":
                lat = np.random.uniform(20, 60)   # 태평양 횡단
                lon = np.random.uniform(120, 240)
            elif region == "trans_atlantic":
                lat = np.random.uniform(30, 70)   # 대서양 횡단
                lon = np.random.uniform(-80, 20)
            elif region == "europe":
                lat = np.random.uniform(35, 70)   # 유럽
                lon = np.random.uniform(-10, 40)
            elif region == "americas":
                lat = np.random.uniform(10, 70)   # 아메리카
                lon = np.random.uniform(-180, -50)
            else:  # middle_east_africa
                lat = np.random.uniform(-35, 50)  # 중동-아프리카
                lon = np.random.uniform(-20, 60)
            
            flight_positions.append({"lat": lat, "lon": lon})
            
            # 항공편 상세 정보 생성
            airline = np.random.choice(global_airlines)
            flight_num = f"{airline}{np.random.randint(100, 9999)}"
            route = np.random.choice(global_routes)
            status = np.random.choice(statuses)
            altitude = np.random.randint(5000, 45000)
            speed = np.random.randint(300, 900)
            
            flight_details.append({
                "flight_number": flight_num,
                "altitude": f"{altitude:,} ft",
                "speed": f"{speed} km/h",
                "route": route,
                "status": status
            })
        
        st.session_state["flight_map_data"] = flight_positions
        st.session_state["flight_details"] = flight_details
    
    # 전 세계 항공 교통 맵
    m = folium.Map(
        location=[20.0, 0.0],  # 전 세계 중심
        zoom_start=2,          # 전 세계 보기
        tiles='OpenStreetMap'
    )
    
    # 전 세계 주요 허브 공항 마커
    major_airports = [
        # 아시아-태평양
        {"name": "ICN", "lat": 37.4602, "lon": 126.4407, "city": "Seoul"},
        {"name": "NRT", "lat": 35.7720, "lon": 140.3928, "city": "Tokyo"},
        {"name": "HND", "lat": 35.5494, "lon": 139.7798, "city": "Tokyo"},
        {"name": "PEK", "lat": 40.0799, "lon": 116.6031, "city": "Beijing"},
        {"name": "PVG", "lat": 31.1434, "lon": 121.8052, "city": "Shanghai"},
        {"name": "HKG", "lat": 22.3080, "lon": 113.9185, "city": "Hong Kong"},
        {"name": "SIN", "lat": 1.3644, "lon": 103.9915, "city": "Singapore"},
        {"name": "BKK", "lat": 13.6900, "lon": 100.7501, "city": "Bangkok"},
        {"name": "KUL", "lat": 2.7456, "lon": 101.7099, "city": "Kuala Lumpur"},
        {"name": "MNL", "lat": 14.5086, "lon": 121.0196, "city": "Manila"},
        {"name": "CGK", "lat": -6.1256, "lon": 106.6558, "city": "Jakarta"},
        {"name": "SYD", "lat": -33.9399, "lon": 151.1753, "city": "Sydney"},
        {"name": "MEL", "lat": -37.6733, "lon": 144.8433, "city": "Melbourne"},
        
        # 유럽
        {"name": "LHR", "lat": 51.4700, "lon": -0.4543, "city": "London"},
        {"name": "CDG", "lat": 49.0097, "lon": 2.5479, "city": "Paris"},
        {"name": "FRA", "lat": 50.0379, "lon": 8.5622, "city": "Frankfurt"},
        {"name": "AMS", "lat": 52.3105, "lon": 4.7683, "city": "Amsterdam"},
        {"name": "MAD", "lat": 40.4983, "lon": -3.5676, "city": "Madrid"},
        {"name": "FCO", "lat": 41.8003, "lon": 12.2389, "city": "Rome"},
        {"name": "ZUR", "lat": 47.4647, "lon": 8.5492, "city": "Zurich"},
        {"name": "VIE", "lat": 48.1103, "lon": 16.5697, "city": "Vienna"},
        {"name": "IST", "lat": 41.2753, "lon": 28.7519, "city": "Istanbul"},
        
        # 북미
        {"name": "JFK", "lat": 40.6413, "lon": -73.7781, "city": "New York"},
        {"name": "LAX", "lat": 33.9416, "lon": -118.4085, "city": "Los Angeles"},
        {"name": "ORD", "lat": 41.9786, "lon": -87.9048, "city": "Chicago"},
        {"name": "ATL", "lat": 33.6407, "lon": -84.4277, "city": "Atlanta"},
        {"name": "DFW", "lat": 32.8968, "lon": -97.0380, "city": "Dallas"},
        {"name": "DEN", "lat": 39.8561, "lon": -104.6737, "city": "Denver"},
        {"name": "SFO", "lat": 37.6213, "lon": -122.3790, "city": "San Francisco"},
        {"name": "SEA", "lat": 47.4502, "lon": -122.3088, "city": "Seattle"},
        {"name": "MIA", "lat": 25.7959, "lon": -80.2870, "city": "Miami"},
        {"name": "YYZ", "lat": 43.6777, "lon": -79.6248, "city": "Toronto"},
        {"name": "YVR", "lat": 49.1967, "lon": -123.1815, "city": "Vancouver"},
        
        # 중동/아프리카
        {"name": "DXB", "lat": 25.2532, "lon": 55.3657, "city": "Dubai"},
        {"name": "DOH", "lat": 25.2611, "lon": 51.5651, "city": "Doha"},
        {"name": "AUH", "lat": 24.4331, "lon": 54.6511, "city": "Abu Dhabi"},
        {"name": "JNB", "lat": -26.1367, "lon": 28.2411, "city": "Johannesburg"},
        {"name": "CAI", "lat": 30.1127, "lon": 31.4000, "city": "Cairo"},
        {"name": "NBO", "lat": -1.3192, "lon": 36.9278, "city": "Nairobi"},
        
        # 남미
        {"name": "GRU", "lat": -23.4356, "lon": -46.4731, "city": "São Paulo"},
        {"name": "EZE", "lat": -34.8222, "lon": -58.5358, "city": "Buenos Aires"},
        {"name": "LIM", "lat": -12.0219, "lon": -77.1143, "city": "Lima"},
        {"name": "BOG", "lat": 4.7016, "lon": -74.1469, "city": "Bogotá"}
    ]
    
    for airport in major_airports:
        # 공항 정보 팝업
        airport_info = f"""
        <div style="font-family: Arial; font-size: 12px; line-height: 1.4; width: 150px;">
            <div style="background: #e3f2fd; padding: 8px; border-radius: 5px; border-left: 3px solid #2196f3;">
                <b style="color: #1976d2; font-size: 14px;">✈️ {airport["name"]}</b><br>
                <span style="color: #424242;">{airport["city"]}</span><br>
                <small style="color: #666;">Major Hub Airport</small>
            </div>
        </div>
        """
        
        folium.Marker(
            [airport["lat"], airport["lon"]],
            popup=folium.Popup(airport_info, max_width=200),
            tooltip=f"{airport['name']} - {airport['city']}",
            icon=folium.Icon(color='blue', icon='plane', prefix='fa')
        ).add_to(m)
    
    # 캐싱된 항공편 위치 및 정보 사용
    flight_positions = st.session_state.get("flight_map_data", [])
    flight_details = st.session_state.get("flight_details", [])
    
    for i, (pos, details) in enumerate(zip(flight_positions, flight_details)):
        # 항공편 정보 생성 (더 상세한 정보)
        flight_info = f"""
        <div style="font-family: Arial; font-size: 11px; line-height: 1.3; width: 180px;">
            <div style="background: #f8f9fa; padding: 8px; border-radius: 5px; border-left: 3px solid #007bff;">
                <b style="color: #007bff; font-size: 13px;">✈️ {details['flight_number']}</b><br>
                <span style="color: #28a745; font-weight: bold;">{details['status']}</span><br><br>
                <b>Route:</b> {details['route']}<br>
                <b>Altitude:</b> {details['altitude']}<br>
                <b>Speed:</b> {details['speed']}<br>
                <small style="color: #6c757d;">Click for details</small>
            </div>
        </div>
        """
        
        # 상태에 따른 색상 결정
        status_colors = {
            "On Time": "green",
            "Delayed": "orange", 
            "Boarding": "blue",
            "In Flight": "red",
            "Approaching": "purple",
            "Departed": "gray"
        }
        color = status_colors.get(details['status'], 'red')
        
        folium.Marker(
            [pos["lat"], pos["lon"]],
            popup=folium.Popup(flight_info, max_width=200),
            tooltip=f"{details['flight_number']} - {details['status']}",
            icon=folium.Icon(color=color, icon='plane', prefix='fa')
        ).add_to(m)
    
    # 지도 크기를 1496*471에 맞게 조정
    st_folium(m, width=1496, height=471)

if __name__ == "__main__":
    main()
