import streamlit as st
import math
import datetime
import requests

# ------------------ 🌐 CSS Styling ------------------ #
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

    .stApp {
        background-image: url('https://wallpaperaccess.com/full/310085.jpg');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }

    .block-container {
        padding: 2rem;
        max-width: 600px;
        margin: auto;
        background: rgba(255, 255, 255, 0.07);  /* More glassy */
        backdrop-filter: blur(12px);
        border-radius: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
    }

    html, [class*="css"] {
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    h1, h2, h3 {
        text-align: center;
        color: #FAFAFA;
        font-family: 'Orbitron', sans-serif;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.1);
        color: #fff;
        border: 1px solid #ffffff33;
        border-radius: 10px;
        padding: 0.4rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #1CB5E0 0%, #000851 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #000851 0%, #1CB5E0 100%);
        transform: scale(1.03);
    }

    .stCheckbox > div {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 0.6rem;
        border-radius: 10px;
        color: #fff;
    }

    .stMetric {
        background-color: rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        text-align: center;
        box-shadow: 0 0 10px rgba(255,255,255,0.2);
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ 🌞 PHYSICAL BACKGROUND ------------------ #

def calcDays(date):
    mapp = {'1': 31, '2': 28, '3': 31, '4': 30, '5': 31, '6': 30,
            '7': 31, '8': 31, '9': 30, '10': 31, '11': 30, '12': 31}
    noofDays = 0
    d, m, y = map(int, date.split('/'))
    if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
        mapp['2'] = 29
    for i in range(1, m):
        noofDays += mapp[str(i)]
    noofDays += d
    return noofDays

def calcIo(date):
    Isc = 1.367
    ang = 2 * math.pi * calcDays(date) / 365
    x = math.cos(ang)
    Io = Isc * (1 + 0.034 * x)
    return Io

def day_of_year(date_str):
    day, month, year = map(int, date_str.split('/'))
    date = datetime.date(year, month, day)
    return date.timetuple().tm_yday

def solar_declination(n):
    return 23.45 * math.pi / 180 * math.sin(2 * math.pi * (284 + n) / 365)

def sunset_hour_angle(phi_rad, delta):
    cos_ws = -math.tan(phi_rad) * math.tan(delta)
    cos_ws = max(min(cos_ws, 1), -1)
    return math.acos(cos_ws)

def get_coordinates(district, state, country):
    query = f"{district}, {state}, {country}"
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code == 200:
        data = response.json()
        if data:
            lat, lon = float(data[0]['lat']), float(data[0]['lon'])
            return lat, lon
        else:
            st.warning(f"No results found for: {query}")
            return None, None
    else:
        st.error(f"Geocoding API Error {response.status_code}: {response.text}")
        return None, None

def calc_Ho(date_str, latitude_deg):
    Gsc = 1367
    n = day_of_year(date_str)
    phi_rad = math.radians(latitude_deg)
    delta = solar_declination(n)
    omega_s = sunset_hour_angle(phi_rad, delta)
    Ho = (24 * 3600 / math.pi) * Gsc * (1 + 0.034 * math.cos(2 * math.pi * n / 365)) * (
        math.cos(phi_rad) * math.cos(delta) * math.sin(omega_s) +
        omega_s * math.sin(phi_rad) * math.sin(delta)
    )
    return Ho / 1e6

# ------------------ 🧪 Streamlit UI ------------------ #

st.title(":sun_with_face: Solar Irradiance & Radiation Calculator")

col1, col2 = st.columns(2)

with col1:
    selected_date = st.date_input("🗓️ Select a date")
    st.subheader("📍 Location Input")

    latitude = None
    use_location_search = st.checkbox("Use district/state/country instead of manual latitude", value=False)

    if use_location_search:
        district = st.text_input("District")
        state = st.text_input("State")
        country = st.text_input("Country", value="India")

        if district and state and country:
            lat, lon = get_coordinates(district, state, country)
            if lat is not None:
                latitude = lat
                st.info(f"📌 Located: Latitude = {lat:.4f}, Longitude = {lon:.4f}")
    else:
        latitude = st.number_input("Enter latitude (in degrees)", min_value=-90.0, max_value=90.0, value=28.61)

with col2:
    if selected_date and latitude is not None:
        formatted_date = selected_date.strftime("%d/%m/%Y")
        manual_day = calcDays(formatted_date)
        datetime_day = day_of_year(formatted_date)
        io_value = calcIo(formatted_date)
        ho_value = calc_Ho(formatted_date, latitude)

        with st.container():
            st.markdown("""
            <div style="
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(10px);
                margin-top: 20px;
            ">
            <h2 style="text-align:center; color:#f0f0f0; font-family: 'Orbitron', sans-serif;">📊 Results</h2>
            </div>
            """, unsafe_allow_html=True)

            st.metric(label="📆 Day of Year", value=f"{datetime_day}")
            st.metric(label="☀️ Extraterrestrial Irradiance (Io)", value=f"{io_value:.4f} kW/m²")
            st.metric(label="📈 Daily Solar Radiation (Ho)", value=f"{ho_value:.4f} MJ/m²/day")
        # ------------------ 👣 Custom Footer ------------------ #
st.markdown("""
    <hr style="border: 0.5px solid rgba(255, 255, 255, 0.1); margin-top: 3rem;" />
    <div style="text-align: center; padding: 1.5rem 0; color: #ccc; font-size: 0.9rem;
                background-color: rgba(255, 255, 255, 0.05); border-radius: 15px; 
                backdrop-filter: blur(6px); box-shadow: 0 0 10px rgba(255,255,255,0.15);">
        Made with ❤️ @<a href="https://www.github.com/karlex1">Sanchit(Karlex) </a>
            </div>
""", unsafe_allow_html=True)
