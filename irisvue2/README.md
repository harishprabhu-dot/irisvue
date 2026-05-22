# IRISVUE — Complete Platform
### Your Cinematic View of the World

---

## ALL PAGES

| Page        | URL           | What it does                                  |
|-------------|---------------|-----------------------------------------------|
| Homepage    | /             | Trending, popular, upcoming, mood discovery   |
| Film Page   | /movie/<id>   | Full details, dynamic theme, shots, quotes    |
| Search      | /search       | Search any film by title                      |
| Genre       | /genre/<id>   | Browse films by genre/mood                    |
| Battles     | /battles      | Vote between two films                        |
| Clubs       | /clubs        | Join and browse film clubs                    |
| Cinema DNA  | /dna          | 8-question quiz — discover your film identity |
| Community   | /community    | Live activity feed + trending sidebar         |
| Watchlist   | /watchlist    | Saved films (persists in browser)             |

---

## SETUP — 4 STEPS

### 1. Get free TMDB API key
- Go to www.themoviedb.org/signup
- Settings → API → Create → Personal use
- Copy your API key

### 2. Add your key to app.py
Open app.py, find this line:
```
TMDB_KEY = os.environ.get("TMDB_API_KEY", "YOUR_TMDB_API_KEY_HERE")
```
Replace YOUR_TMDB_API_KEY_HERE with your actual key.

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run
```
python app.py
```
Open http://localhost:5000

---

## DEPLOY TO RENDER (Go Live)

1. Create account at github.com
2. Create new repository called "irisvue"
3. Upload all these files into the repo
4. Go to render.com — sign up with GitHub
5. New → Web Service → Select irisvue repo
6. Set:
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
7. Environment tab → Add variable:
   - TMDB_API_KEY = your key
8. Click Deploy
9. Your site is live at yourname.onrender.com

---

## FILE STRUCTURE

```
irisvue/
├── app.py                    Main backend — all routes + data
├── requirements.txt          Python packages
├── Procfile                  Render start command
├── templates/
│   ├── index.html            Homepage
│   ├── movie.html            Movie detail page
│   ├── search.html           Search results
│   ├── battles.html          Film battles
│   ├── clubs.html            Film clubs
│   ├── dna.html              Cinema DNA quiz
│   ├── community.html        Activity feed
│   └── watchlist.html        Personal watchlist
└── static/
    ├── css/
    │   ├── style.css         Main design system
    │   └── movie.css         Movie page styles
    └── js/
        └── main.js           Search + animations
```

---

## FEATURES INCLUDED

Movie Page:
- Dynamic color theme extracted from poster
- Film color palette (8 colors)
- TMDB + IMDb + Irisvue ratings
- Camera, lens, film format (80+ films in database)
- Director, DOP, Composer, Editor, Writer, Producer
- Filming countries + production companies
- Budget + box office
- Full cast with photos
- 10 best cinematic shots + lightbox
- Memorable quotes (30+ films in database)
- Story with download
- First Watch vs Rewatch mode
- Star rating system
- Add to Watchlist button
- Film recommendations

Platform:
- Mood-based discovery (20 genres)
- Live search dropdown
- Film Battles (vote + auto-load next)
- 10 Film Clubs with join/leave
- Cinema DNA quiz (8 questions, 6 personality types)
- Community activity feed
- Watchlist (saved in browser, no login needed)
- Upcoming releases

---

2026 Irisvue. Uses the TMDB API. Not endorsed or certified by TMDB.
