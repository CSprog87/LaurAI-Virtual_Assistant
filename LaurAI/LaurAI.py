import speech_recognition as sr
import pyttsx3
import requests
import spotipy
import spotipy.util as util
from newsapi import NewsApiClient
import JarvisAI
import random

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Set the microphone as the audio source
microphone = sr.Microphone()

# Create an instance of JarvisAI
jarvis = JarvisAI()

# Spotify API credentials
SPOTIFY_USERNAME = 'your_username'
SPOTIFY_CLIENT_ID = 'your_client_id'
SPOTIFY_CLIENT_SECRET = 'your_client_secret'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback/'

# OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = 'your_api_key'

# NewsAPI key
NEWSAPI_API_KEY = 'your_api_key'

# Spotipy authentication scope
SCOPE = 'user-read-private user-read-playback-state user-modify-playback-state'


def set_language(lang):
    if lang == 'english':
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # English voice
    elif lang == 'spanish':
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)  # Spanish voice


def speak(text):
    engine.say(text)
    engine.runAndWait()


def process_query(query):
    response = jarvis.get_response(query)
    speak(response)


def search_wikipedia(query):
    response = jarvis.search_wikipedia(query)
    speak(response)


def play_music():
    # Get Spotify authorization token
    token = util.prompt_for_user_token(
        SPOTIFY_USERNAME,
        scope=SCOPE,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI
    )

    if token:
        # Create Spotify client
        sp = spotipy.Spotify(auth=token)

        # Example: Play a random playlist
        playlists = sp.current_user_playlists(limit=20)['items']
        random_playlist = random.choice(playlists)
        playlist_id = random_playlist['id']
        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
        speak("Enjoy the music!")
    else:
        speak("Sorry, I am unable to authenticate with Spotify at the moment.")


def tell_joke():
    response = jarvis.get_joke()
    speak(response)


def get_weather():
    city = 'Your_City_Name'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}'

    try:
        response = requests.get(url)
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        speak(f"The weather in {city} is {description} with a temperature of {temperature} Kelvin.")
    except requests.exceptions.RequestException:
        speak("Sorry, I am unable to fetch the weather information at the moment.")


def get_news():
    newsapi = NewsApiClient(api_key=NEWSAPI_API_KEY)
    top_headlines = newsapi.get_top_headlines(language='en')
    if 'articles' in top_headlines and len(top_headlines['articles']) > 0:
        articles = top_headlines['articles']
        speak("Here are some top news headlines:")
        for article in articles:
            title = article['title']
            speak(title)
    else:
        speak("Sorry, I am unable to fetch the news at the moment.")


while True:
    try:
        with microphone as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        print("Recognizing...")

        query = recognizer.recognize_google(audio)
        print(f"User: {query}")

        if "Laura" in query:
            query = query.replace("Laura", "").strip()

            if "language" in query:
                if "English" in query:
                    set_language('english')
                    speak("Language set to English.")
                elif "Spanish" in query:
                    set_language('spanish')
                    speak("Idioma establecido en español.")

            elif "wikipedia" in query:
                search_query = query.replace("wikipedia", "").strip()
                search_wikipedia(search_query)
            elif "play music" in query:
                play_music()
            elif "joke" in query:
                tell_joke()
            elif "weather" in query:
                get_weather()
            elif "news" in query:
                get_news()
            else:
                process_query(query)

    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
    except sr.RequestError:
        print("Sorry, I am unable to process your request at the moment.")
