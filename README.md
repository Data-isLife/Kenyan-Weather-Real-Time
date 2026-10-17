# Kenya Weather 🌦️

Check the current weather for your location or a county and sub-county in Kenya. The app also gives simple suggestions to help you prepare for the conditions.

## Use the app

1. Open the app in your browser.
2. Choose **Use my current location** and press **Get location**. Allow your browser to share your location when asked.
3. If you prefer not to share your location, choose **Choose a county and sub-county** instead.
4. Press **Get weather** and wait a few seconds for the result.

You do not need to create an OpenWeatherMap account or enter an API key to use the deployed app. Location access is optional. If you deny permission, you can still choose a county and sub-county manually.

## What the app shows

- Current temperature and feels-like temperature
- Weather conditions, humidity, and wind
- General preparation suggestions based on the reported weather, such as taking rain protection when rain is expected

Weather can change and may differ across a large sub-county. The suggestions are general guidance, not official alerts. Follow local authority advice during severe weather.

## About the location data

The county and sub-county list comes from the [Kenya Administrative Divisions dataset](https://github.com/open-admin-data/kenya-administrative-divisions), which provides 47 counties and 290 sub-county-level records. The dataset is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Its coordinates are representative points for weather lookups; they are not exact coordinates for every home or place in an area.

Current weather is provided by the [OpenWeatherMap Current Weather API](https://openweathermap.org/api/current).

## For the app owner

The deployed app uses the owner's OpenWeatherMap API key so visitors can use the app without their own keys. Add the key in Streamlit Community Cloud under **App settings → Secrets**. Use this setting name:

```toml
OPENWEATHER_API_KEY = "your-new-key"
```

Keep the real key private. Do not add it to this repository, `app.py`, or a public message. A public app's visitors share the owner's API usage quota.

To publish or update the app, upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore` to the root of a GitHub repository, then deploy that repository through [Streamlit Community Cloud](https://share.streamlit.io/). Streamlit installs the packages listed in `requirements.txt` when it builds the app.
