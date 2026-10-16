# Kenya Weather

A browser-based weather app for 47 Kenyan counties and 290 sub-county-level divisions. It uses representative WGS84 coordinates from the Open Admin Data Kenya administrative divisions dataset and fetches current conditions from OpenWeatherMap.

## Publish and share without a code editor

1. Create a **Public** repository on GitHub.
2. Choose **Add file → Upload files** and upload `app.py`, `requirements.txt`, and `README.md` from this folder. Do not upload or commit an API key.
3. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and choose **Create app**.
4. Select your repository, the `main` branch, and `app.py`, then deploy.
5. Share the Streamlit URL. Each visitor enters their own OpenWeatherMap API key.

## Run on Windows (optional)

Open PowerShell and run these two commands. They install the required packages and start the app in Streamlit:

```powershell
py -m pip install -r "C:\path\to\kenya-weather-app\requirements.txt"
py -m streamlit run "C:\path\to\kenya-weather-app\app.py"
```

Replace `C:\path\to\kenya-weather-app` with the folder where you saved these files. Do not run the app with `py app.py`; Streamlit needs to launch it with `py -m streamlit run`.

## API key and data

The app asks for the API key each session and does not save it to a file or Streamlit secrets. The key is sent from the Streamlit server to OpenWeatherMap to request weather. Use a key you control and follow OpenWeatherMap's terms and usage limits.

Administrative location data is loaded from the [Open Admin Data Kenya dataset](https://github.com/open-admin-data/kenya-administrative-divisions), licensed CC BY 4.0. The app checks that it receives 290 valid sub-county records across 47 counties before showing the selectors. An internet connection is needed to load the list and weather data.

The 290 number is also used for Kenya's constituencies. Some datasets label the corresponding level “sub-county”; legal/administrative and electoral terminology can differ, and some administrative sources report different counts. This app labels these divisions as sub-counties because that is how its cited source classifies them. Coordinates are representative weather lookup points, not exact locations for every home or place in a sub-county.

Weather data: [OpenWeatherMap Current Weather API](https://openweathermap.org/api/current).
