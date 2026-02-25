from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_URL = "https://api.jikan.moe/v4"

@app.route('/', methods=['GET', 'HEAD'])
def home():
    # Fix for Render health check: returns 200 OK for HEAD requests
    if request.method == 'HEAD':
        return '', 200
    
    query = request.args.get('search')
    genre_id = request.args.get('genre')
    params = {"limit": 24}
    
    try:
        if query:
            params["q"] = query
            res = requests.get(f"{API_URL}/anime", params=params)
        elif genre_id:
            params["genres"] = genre_id
            res = requests.get(f"{API_URL}/anime", params=params)
        else:
            res = requests.get(f"{API_URL}/top/anime?filter=airing", params=params)
        
        data = res.json().get('data', [])
        # Filter content to maintain site quality
        anime_list = [a for a in data if not any(g['name'] == 'Harem' for g in a.get('genres', []))]
    except Exception:
        anime_list = []

    return render_template('index.html', animes=anime_list)

@app.route('/anime/<int:anime_id>')
def detail(anime_id):
    try:
        # Fetching core details, episodes, and related seasons
        info = requests.get(f"{API_URL}/anime/{anime_id}").json().get('data', {})
        eps = requests.get(f"{API_URL}/anime/{anime_id}/episodes").json().get('data', [])
        rels = requests.get(f"{API_URL}/anime/{anime_id}/relations").json().get('data', [])
        return render_template('detail.html', info=info, episodes=eps, relations=rels)
    except Exception:
        return "Anime details not found", 404

if __name__ == '__main__':
    app.run(debug=True)