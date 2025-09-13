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
    
    # 메인 검색 영역 (Streamlit 네이티브 컴포넌트로 변경)
    st.markdown("""
    <div class="main-search-container fade-in">
        <h2 class="search-title">Advanced Flight Search</h2>
        <p class="search-subtitle">FlightAware is at the heart of aviation as a leader in providing accurate and actionable advanced data and insights for all aviation decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Flight 번호 검색
    st.markdown("**Search by Flight #:**")
    col1, col2 = st.columns([4, 1])
    with col1:
        flight_search = st.text_input("", placeholder="Enter flight number", key="main_flight_search_adv", label_visibility="collapsed")
    with col2:
        flight_search_btn = st.button("Search", key="main_flight_btn_adv")
    
    # Route 검색
    st.markdown("**Search by Route:**")
    col1, col2, col3, col4 = st.columns([2, 0.5, 2, 1])
    with col1:
        departure_search = st.text_input("", placeholder="Departure", key="main_departure_adv", label_visibility="collapsed")
    with col2:
        st.markdown('<div style="text-align: center; color: #6c757d; font-size: 0.7rem; margin-top: 0.5rem;">⇄</div>', unsafe_allow_html=True)
    with col3:
        destination_search = st.text_input("", placeholder="Destination", key="main_destination_adv", label_visibility="collapsed")
    with col4:
        route_search_btn = st.button("Search", key="main_route_btn_adv")
    
    # 검색 결과 처리
    if flight_search_btn and flight_search:
        st.session_state["flight_search_adv"] = True
        st.session_state["flight_number_adv"] = flight_search
        # st.rerun() 제거 - 자동으로 리렌더링됨
    
    if route_search_btn and departure_search and destination_search:
        st.session_state["route_search_adv"] = True
        st.session_state["departure_adv"] = departure_search
        st.session_state["destination_adv"] = destination_search
        # st.rerun() 제거 - 자동으로 리렌더링됨
    
    # 사이드바 (간소화)
    with st.sidebar:
        st.markdown("### Advanced Search")
        
        search_type = st.selectbox(
            "Search Type",
            ["Detailed Flight Info", "Real-time Tracking", "Airport Status", "Weather Info", "Delay Analysis", "Flight Comparison"],
            key="advanced_search_type"
        )
        
        if search_type == "Detailed Flight Info":
            flight_number = st.text_input("Flight Number", "KE001", key="advanced_flight_num")
            search_button = st.button("🔍 Search", key="detailed_search")
            
        elif search_type == "Real-time Tracking":
            flight_number = st.text_input("Flight Number", "KE001", key="track_flight_num")
            search_button = st.button("📍 Track", key="realtime_track")
            
        elif search_type == "Airport Status":
            airport_code = st.text_input("Airport Code", "ICN", key="status_airport_code").upper()
            search_button = st.button("🏢 Status", key="airport_status")
            
        elif search_type == "Weather Info":
            airport_code = st.text_input("Airport Code", "ICN", key="weather_airport_code").upper()
            search_button = st.button("🌤️ Weather", key="weather_search")
            
        elif search_type == "Delay Analysis":
            airport_code = st.text_input("Airport Code", "ICN", key="delay_airport_code").upper()
            search_button = st.button("⏰ Analysis", key="delay_analysis")
            
        else:  # Flight Comparison
            flight1 = st.text_input("First Flight", "KE001", key="compare_flight1")
            flight2 = st.text_input("Second Flight", "OZ101", key="compare_flight2")
            search_button = st.button("⚖️ Compare", key="flight_compare")
    
    # 메인 컨텐츠
    if st.session_state.get("flight_search_adv", False):
        display_detailed_flight_info(st.session_state.get("flight_number_adv", ""))
        
    elif st.session_state.get("route_search_adv", False):
        st.info(f"Route Search: {st.session_state.get('departure_adv', '')} → {st.session_state.get('destination_adv', '')}")
        # Route 검색 결과 표시 (추후 구현)
        
    elif search_type == "Detailed Flight Info" and st.session_state.get("detailed_search", False):
        display_detailed_flight_info(flight_number)
        
    elif search_type == "Real-time Tracking" and st.session_state.get("realtime_track", False):
        display_realtime_tracking(flight_number)
        
    elif search_type == "Airport Status" and st.session_state.get("airport_status", False):
        display_airport_status(airport_code)
        
    elif search_type == "Weather Info" and st.session_state.get("weather_search", False):
        display_weather_info(airport_code)
        
    elif search_type == "Delay Analysis" and st.session_state.get("delay_analysis", False):
        display_delay_analysis(airport_code)
        
    elif search_type == "Flight Comparison" and st.session_state.get("flight_compare", False):
        display_flight_comparison(flight1, flight2)
    
    # 기본 대시보드
    if not any([st.session_state.get("flight_search_adv", False),
                st.session_state.get("route_search_adv", False),
                st.session_state.get("detailed_search", False), 
                st.session_state.get("realtime_track", False),
                st.session_state.get("airport_status", False),
                st.session_state.get("weather_search", False),
                st.session_state.get("delay_analysis", False),
                st.session_state.get("flight_compare", False)]):
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
    
    # 항공사별 성과
    st.markdown('<h3 class="section-title">✈️ 항공사별 성과</h3>', unsafe_allow_html=True)
    
    # 세션 상태에 데이터 캐싱
    if "advanced_airline_data" not in st.session_state:
        airlines = ["대한항공", "아시아나항공", "일본항공", "전일본공수", "중국국제항공"]
        # 고정된 시드로 일관된 데이터 생성
        np.random.seed(101112)
        on_time_rates = [np.random.randint(85, 98) for _ in airlines]
        customer_satisfaction = [np.random.randint(80, 95) for _ in airlines]
        st.session_state["advanced_airline_data"] = {
            "airlines": airlines, 
            "on_time_rates": on_time_rates, 
            "customer_satisfaction": customer_satisfaction
        }
    
    airline_data = st.session_state["advanced_airline_data"]
    airlines = airline_data["airlines"]
    on_time_rates = airline_data["on_time_rates"]
    customer_satisfaction = airline_data["customer_satisfaction"]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="정시율", x=airlines, y=on_time_rates))
    fig.add_trace(go.Bar(name="고객 만족도", x=airlines, y=customer_satisfaction))
    
    fig.update_layout(
        title="항공사별 성과 비교",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color='#2c3e50',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 실시간 항공 교통 현황
    st.markdown('<h3 class="section-title">🛩️ 실시간 항공 교통 현황</h3>', unsafe_allow_html=True)
    
    # 시뮬레이션된 항공 교통 맵
    m = folium.Map(
        location=[35.0, 135.0],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # 주요 공항 마커
    major_airports = [
        {"name": "ICN", "lat": 37.4602, "lon": 126.4407},
        {"name": "NRT", "lat": 35.7720, "lon": 140.3928},
        {"name": "HND", "lat": 35.5494, "lon": 139.7798},
        {"name": "PEK", "lat": 40.0799, "lon": 116.6031},
        {"name": "PVG", "lat": 31.1434, "lon": 121.8052}
    ]
    
    for airport in major_airports:
        folium.Marker(
            [airport["lat"], airport["lon"]],
            popup=airport["name"],
            icon=folium.Icon(color='blue', icon='plane')
        ).add_to(m)
    
    # 시뮬레이션된 항공편들
    for _ in range(20):
        lat = np.random.uniform(30, 45)
        lon = np.random.uniform(120, 150)
        folium.Marker(
            [lat, lon],
            icon=folium.Icon(color='red', icon='plane', prefix='fa')
        ).add_to(m)
    
    st_folium(m, width=700, height=350)

if __name__ == "__main__":
    main()
