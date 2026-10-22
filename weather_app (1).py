import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Weather App", page_icon="🌤️")
st.title("🌤️ Weather App")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


@st.cache_data(ttl=600)
def geocode(city: str):
    r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
    r.raise_for_status()
    results = r.json().get("results")
    return results[0] if results else None


@st.cache_data(ttl=600)
def get_weather(lat: float, lon: float):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


city = st.text_input("Enter a city", value="Nellore")

if city:
    try:
        place = geocode(city)
        if not place:
            st.warning("City not found. Try another name.")
        else:
            data = get_weather(place["latitude"], place["longitude"])
            cur = data["current"]

            st.subheader(f"{place['name']}, {place.get('country', '')}")
            st.write(WEATHER_CODES.get(cur["weather_code"], "Unknown"))

            c1, c2, c3 = st.columns(3)
            c1.metric("Temperature", f"{cur['temperature_2m']} °C")
            c2.metric("Humidity", f"{cur['relative_humidity_2m']} %")
            c3.metric("Wind", f"{cur['wind_speed_10m']} km/h")

            st.subheader("7-day forecast")
            daily = pd.DataFrame({
                "Date": data["daily"]["time"],
                "Max °C": data["daily"]["temperature_2m_max"],
                "Min °C": data["daily"]["temperature_2m_min"],
                "Rain (mm)": data["daily"]["precipitation_sum"],
            }).set_index("Date")

            st.line_chart(daily[["Max °C", "Min °C"]])
            st.dataframe(daily)
    except requests.RequestException as e:
        st.error(f"Could not fetch weather data: {e}")
