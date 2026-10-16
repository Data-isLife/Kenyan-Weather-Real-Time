import requests
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/open-admin-data/kenya-administrative-divisions/master/data/all-subcounty.json"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
EXPECTED_SUBCOUNTIES = 290
EXPECTED_COUNTIES = 47


def _name(value):
    """Return a readable English/local name from the source's name field."""
    if isinstance(value, dict):
        return value.get("en") or value.get("local")
    if isinstance(value, str):
        return value
    return None


@st.cache_data(ttl=60 * 60, show_spinner=False)
def load_locations():
    """Load and validate the published Kenya sub-county location dataset."""
    response = requests.get(DATA_URL, timeout=20)
    response.raise_for_status()
    records = response.json()

    # Support either the published flat list or common API response wrappers.
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
            lat = float(geo["lat"])
            lon = float(geo["lon"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        locations.append({"county": county, "subcounty": name, "lat": lat, "lon": lon})

    if len(locations) != EXPECTED_SUBCOUNTIES:
        raise ValueError(
            f"Location data validation failed: expected {EXPECTED_SUBCOUNTIES} records, "
            f"but found {len(locations)} valid records."
        )
    if len({location["county"] for location in locations}) != EXPECTED_COUNTIES:
        raise ValueError(f"Location data validation failed: expected {EXPECTED_COUNTIES} counties.")
    return locations


def main():
    st.set_page_config(page_title="Kenya Weather", page_icon="🌦️", layout="centered")
    st.title("🌦️ Kenya Weather")
    st.caption("Current weather by county and sub-county")
    st.write("Choose an area in Kenya and enter your own OpenWeatherMap API key to get current weather.")

    try:
        locations = load_locations()
    except (requests.RequestException, ValueError, TypeError) as error:
        st.error("Could not load Kenya's location list. Check your internet connection, then refresh the app.")
        st.caption(f"Details: {error}")
        return

    county_names = sorted({row["county"] for row in locations})
    county = st.selectbox("County", county_names)
    subcounty_names = sorted(
        row["subcounty"] for row in locations if row["county"] == county
    )
    subcounty = st.selectbox("Sub-county", subcounty_names)
    api_key = st.text_input(
        "Your OpenWeatherMap API key",
        type="password",
        help="The key is used for the weather request and is not saved by this app.",
    )
    st.caption("After you enter your key and click **Get weather**, please wait a few seconds while the latest weather is retrieved.")
    units = st.selectbox("Temperature units", ["Celsius", "Fahrenheit"])

    if st.button("Get weather", type="primary", use_container_width=True):
        if not api_key.strip():
            st.warning("Enter your API key first.")
        else:
            location = next(
                row for row in locations
                if row["county"] == county and row["subcounty"] == subcounty
            )
            with st.spinner("Please wait — getting the latest weather for this sub-county…"):
                try:
                    response = requests.get(
                        WEATHER_URL,
                        params={
                            "lat": location["lat"],
                            "lon": location["lon"],
                            "appid": api_key.strip(),
                            "units": "metric" if units == "Celsius" else "imperial",
                        },
                        timeout=15,
                    )
                    if response.status_code == 401:
                        st.error("OpenWeatherMap rejected this key. Check that it is correct and active.")
                        return
                    if response.status_code == 429:
                        st.error("The weather service limit was reached. Try again later.")
                        return
                    response.raise_for_status()
                    weather = response.json()
                    conditions = weather["weather"][0]
                    temp_unit = "°C" if units == "Celsius" else "°F"
                    wind_unit = "m/s" if units == "Celsius" else "mph"
                    st.subheader(f"{subcounty}, {county}")
                    col1, col2 = st.columns(2)
                    col1.metric("Temperature", f"{weather['main']['temp']:.1f}{temp_unit}")
                    col2.metric("Feels like", f"{weather['main']['feels_like']:.1f}{temp_unit}")
                    humidity = weather["main"]["humidity"]
                    wind_speed = weather.get("wind", {}).get("speed", "—")
                    st.write(
                        f"**{conditions['description'].capitalize()}** · "
                        f"Humidity {humidity}% · Wind {wind_speed} {wind_unit}"
                    )
                    st.caption(
                        "Weather data provided by OpenWeatherMap. Coordinates: "
                        f"{location['lat']:.4f}, {location['lon']:.4f} "
                        "(representative sub-county point)."
                    )
                except requests.Timeout:
                    st.error("The request timed out. Check your connection and try again.")
                except requests.ConnectionError:
                    st.error("Could not connect to the weather service. Check your internet connection.")
                except requests.HTTPError as error:
                    st.error(f"The weather service returned an error: {error}")
                except (requests.RequestException, KeyError, IndexError, ValueError, TypeError):
                    st.error("The weather service returned an unexpected response. Please try again later.")

    with st.expander("About the location data"):
        st.write(
            "The selector uses the Open Admin Data Kenya administrative divisions dataset. "
            "Its 290 sub-county-level records and WGS84 coordinates are weather lookup points. "
            "A representative point cannot describe weather at every place in a large sub-county."
        )
        st.markdown(
            "Data: [Kenya Administrative Divisions](https://github.com/open-admin-data/kenya-administrative-divisions) · CC BY 4.0. "
            "Weather: [OpenWeatherMap](https://openweathermap.org/)."
        )


if __name__ == "__main__":
    main()

