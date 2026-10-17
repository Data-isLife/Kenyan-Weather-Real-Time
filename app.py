import requests
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

DATA_URL = "https://raw.githubusercontent.com/open-admin-data/kenya-administrative-divisions/master/data/all-subcounty.json"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
EXPECTED_SUBCOUNTIES = 290
EXPECTED_COUNTIES = 47


def _name(value):
    if isinstance(value, dict):
        return value.get("en") or value.get("local")
    return value if isinstance(value, str) else None


@st.cache_data(ttl=60 * 60, show_spinner=False)
def load_locations():
    response = requests.get(DATA_URL, timeout=20)
    response.raise_for_status()
    records = response.json()
    if isinstance(records, dict):
        records = records.get("data", records.get("results"))
    if not isinstance(records, list):
        raise ValueError("The location data response was not a list.")

    locations = []
    for record in records:
        if not isinstance(record, dict):
            continue
        name = _name(record.get("name"))
        parent = record.get("parent") or {}
        county = _name(parent.get("name")) if isinstance(parent, dict) else None
        geo = record.get("geo") or {}
        if not name or not county or not isinstance(geo, dict):
            continue
        try:
            lat, lon = float(geo["lat"]), float(geo["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            locations.append({"county": county, "subcounty": name, "lat": lat, "lon": lon})

    if len(locations) != EXPECTED_SUBCOUNTIES:
        raise ValueError(f"Expected {EXPECTED_SUBCOUNTIES} valid areas, received {len(locations)}.")
    if len({place["county"] for place in locations}) != EXPECTED_COUNTIES:
        raise ValueError(f"Expected {EXPECTED_COUNTIES} counties in the location data.")
    return locations


def get_weather_key():
    try:
        return str(st.secrets.get("OPENWEATHER_API_KEY", "")).strip()
    except (FileNotFoundError, KeyError):
        return ""


def preparation_advice(weather, units):
    condition = weather.get("weather", [{}])[0]
    weather_id = condition.get("id", 0)
    group = condition.get("main", "").lower()
    temperature = weather.get("main", {}).get("temp")
    is_celsius = units == "Celsius"
    hot_limit, cold_limit = (35, 12) if is_celsius else (95, 54)
    advice = []

    if 200 <= weather_id < 300:
        advice.append("Thunderstorms are reported. Stay indoors where possible, and avoid open areas, tall isolated trees, and floodwater.")
    elif 300 <= weather_id < 600 or group == "rain":
        advice.append("Rain is reported. Carry an umbrella or raincoat, allow extra travel time, and avoid walking or driving through floodwater.")
    elif 600 <= weather_id < 700 or group == "snow":
        advice.append("Wintry conditions are reported. Dress warmly and take care on slippery roads and paths.")
    elif 700 <= weather_id < 800 or group in {"mist", "smoke", "haze", "dust", "fog", "sand", "ash", "squall", "tornado"}:
        advice.append("Reduced visibility or unusual atmospheric conditions are reported. Take extra care when travelling and follow local advisories.")
    elif weather_id == 800 or group == "clear":
        advice.append("Clear conditions are reported. Sunglasses, a hat, and water may be useful when spending time outdoors.")
    else:
        advice.append("Check the conditions again before travelling, as weather can change across the area.")

    if isinstance(temperature, (int, float)):
        if temperature >= hot_limit:
            advice.append("It is very warm. Drink water, seek shade, and limit strenuous activity in the hottest part of the day.")
        elif temperature <= cold_limit:
            advice.append("It is cool. Consider an extra layer, especially in the early morning or evening.")
    return advice


def main():
    st.set_page_config(page_title="Kenya Weather", page_icon="🌦️", layout="centered")
    st.title("🌦️ Kenya Weather")
    st.caption("Current weather for your location or any Kenyan county and sub-county")

    api_key = get_weather_key()
    if not api_key:
        st.error("The app owner needs to add the OpenWeatherMap key in the app's Streamlit Secrets settings before weather lookups can work.")
        st.info('In Streamlit Community Cloud, open the app menu → Settings → Secrets, then add: OPENWEATHER_API_KEY = "your-new-key"')
        st.stop()

    try:
        locations = load_locations()
    except (requests.RequestException, ValueError, TypeError):
        st.error("Could not load the Kenya location list. Check the internet connection and refresh the app.")
        st.stop()

    selection = st.radio(
        "Where should we check the weather?",
        ["Use my current location", "Choose a county and sub-county"],
        index=0,
    )
    selected_name = ""
    coords = None

    if selection == "Use my current location":
        st.write("Choose **Get location** below and allow your browser to share your location. Your browser may ask you to confirm permission.")
        try:
            browser_location = streamlit_geolocation()
        except Exception:
            browser_location = None
        if isinstance(browser_location, dict):
            try:
                lat = float(browser_location["latitude"])
                lon = float(browser_location["longitude"])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    coords = {"lat": lat, "lon": lon}
                    selected_name = "Your current location"
                    st.success("Location received. Click **Get weather** when you’re ready.")
            except (KeyError, TypeError, ValueError):
                pass
        if coords is None:
            st.info("Allow location access to use your current location, or choose a county and sub-county above.")
    else:
        county_names = sorted({place["county"] for place in locations})
        county = st.selectbox("County", county_names)
        subcounty_names = sorted(place["subcounty"] for place in locations if place["county"] == county)
        subcounty = st.selectbox("Sub-county", subcounty_names)
        place = next(place for place in locations if place["county"] == county and place["subcounty"] == subcounty)
        coords = {"lat": place["lat"], "lon": place["lon"]}
        selected_name = f"{subcounty}, {county}"

    units = st.selectbox("Temperature units", ["Celsius", "Fahrenheit"])
    if st.button("Get weather", type="primary", use_container_width=True, disabled=coords is None):
        with st.spinner("Please wait — getting the latest weather…"):
            try:
                response = requests.get(
                    WEATHER_URL,
                    params={
                        "lat": coords["lat"],
                        "lon": coords["lon"],
                        "appid": api_key,
                        "units": "metric" if units == "Celsius" else "imperial",
                    },
                    timeout=15,
                )
                if response.status_code == 401:
                    st.error("The app’s weather key was rejected. The app owner should check or replace it in Streamlit Secrets.")
                elif response.status_code == 429:
                    st.error("The weather service limit was reached. Please try again later.")
                else:
                    response.raise_for_status()
                    weather = response.json()
                    condition = weather["weather"][0]
                    st.subheader(selected_name)
                    temp_unit = "°C" if units == "Celsius" else "°F"
                    wind_unit = "m/s" if units == "Celsius" else "mph"
                    col1, col2 = st.columns(2)
                    col1.metric("Temperature", f"{weather['main']['temp']:.1f}{temp_unit}")
                    col2.metric("Feels like", f"{weather['main']['feels_like']:.1f}{temp_unit}")
                    st.write(
                        f"**{condition['description'].capitalize()}** · "
                        f"Humidity {weather['main']['humidity']}% · "
                        f"Wind {weather.get('wind', {}).get('speed', '—')} {wind_unit}"
                    )
                    st.markdown("#### What to prepare for")
                    for tip in preparation_advice(weather, units):
                        st.write(f"- {tip}")
                    st.caption("Weather can vary within a sub-county. Advice is general; follow official local alerts for urgent conditions.")
            except requests.Timeout:
                st.error("The weather request took too long. Check your connection and try again.")
            except requests.ConnectionError:
                st.error("Could not connect to the weather service. Check your connection and try again.")
            except requests.HTTPError:
                st.error("The weather service returned an error. Please try again later.")
            except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
                st.error("The weather service returned an unexpected response. Please try again later.")

    with st.expander("About location and weather advice"):
        st.write("Your current location is requested only after you choose the location button and allow browser access. If you prefer not to share it, select a county and sub-county instead. The location data uses representative points for the areas, so weather may vary within them.")
        st.write("The preparation tips are general guidance based on the reported conditions and temperature. They are not official weather warnings.")
        st.markdown("Location data: [Kenya Administrative Divisions](https://github.com/open-admin-data/kenya-administrative-divisions), CC BY 4.0. Weather: [OpenWeatherMap](https://openweathermap.org/).")


if __name__ == "__main__":
    main()
