from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, current_user
import requests, os, random
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'IrisVue@2026#Cinema$Secure!HarisH')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///irisvue.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, User
from auth import auth, bcrypt
db.init_app(app)
bcrypt.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)
with app.app_context():
    db.create_all()

TMDB_KEY  = os.environ.get("TMDB_API_KEY", "e8ca821b35da67033f670add624c8eca")
OMDB_KEY  = os.environ.get("OMDB_API_KEY", "d8bbc9d")
TMDB_BASE = "https://api.themoviedb.org/3"
OMDB_BASE = "https://www.omdbapi.com"
TMDB_IMG  = "https://image.tmdb.org/t/p/"

OWNER = {"name": "S.R. HarisH Prabhu", "email": "harishrohinth008@gmail.com", "place": "Coimbatore, Tamil Nadu, India"}

def tmdb(endpoint, **params):
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=10, verify=False)
    r.raise_for_status()
    return r.json()

def omdb(imdb_id):
    try:
        r = requests.get(OMDB_BASE, params={"i": imdb_id, "apikey": OMDB_KEY}, timeout=6, verify=False)
        return r.json()
    except:
        return {}

def poster(path, size="w500"):
    return f"{TMDB_IMG}{size}{path}" if path else ""

def backdrop(path, size="w1280"):
    return f"{TMDB_IMG}{size}{path}" if path else ""

CAMERA_SPECS = {
    "interstellar":{"camera":"IMAX 65mm / 35mm Film","lens":"Panavision Sphero 65","format":"IMAX / 35mm"},
    "the dark knight":{"camera":"IMAX 65mm / 35mm Film","lens":"Panavision Primo","format":"IMAX / 35mm"},
    "the dark knight rises":{"camera":"IMAX 65mm / 35mm Film","lens":"Panavision Primo","format":"IMAX / 35mm"},
    "inception":{"camera":"35mm Film / IMAX","lens":"Panavision Primo","format":"35mm / IMAX"},
    "oppenheimer":{"camera":"IMAX 65mm / Kodak 65mm","lens":"Panavision 65mm","format":"IMAX 70mm"},
    "dunkirk":{"camera":"IMAX 65mm / 65mm Film","lens":"Panavision 65mm","format":"IMAX / 65mm"},
    "memento":{"camera":"35mm Film","lens":"Panavision Primo","format":"35mm"},
    "tenet":{"camera":"IMAX 65mm / Arri Alexa IMAX","lens":"Panavision 65mm","format":"IMAX / Digital"},
    "dune":{"camera":"Arri Alexa LF / Mini LF","lens":"Panavision Sphero 65 + Custom","format":"Digital 4K"},
    "dune part two":{"camera":"Arri Alexa 35 / IMAX","lens":"Panavision Sphero 65","format":"IMAX / Digital"},
    "arrival":{"camera":"Arri Alexa XT Plus","lens":"Panavision Primo","format":"Digital 3.4K"},
    "blade runner 2049":{"camera":"Arri Alexa 65","lens":"Prime DNA Lenses","format":"Digital 6.5K"},
    "annihilation":{"camera":"Arri Alexa Mini","lens":"Panavision Primo","format":"Digital 4K"},
    "sicario":{"camera":"Arri Alexa XT","lens":"Panavision Primo","format":"Digital 3.4K"},
    "prisoners":{"camera":"Arri Alexa XT","lens":"Zeiss Master Prime","format":"Digital 3.4K"},
    "2001 a space odyssey":{"camera":"Super Panavision 70","lens":"Panavision Super Sphero 65","format":"Super Panavision 70mm"},
    "barry lyndon":{"camera":"35mm Film / Mitchell BNC","lens":"Zeiss f/0.7 NASA Lens","format":"35mm"},
    "the shining":{"camera":"35mm Film","lens":"Zeiss Standard Primes","format":"35mm"},
    "full metal jacket":{"camera":"35mm Film","lens":"Zeiss Standard Primes","format":"35mm"},
    "the social network":{"camera":"Red Epic","lens":"Zeiss Master Prime","format":"Digital 5K"},
    "gone girl":{"camera":"Red Epic Dragon","lens":"Zeiss Master Prime","format":"Digital 6K"},
    "zodiac":{"camera":"Viper FilmStream","lens":"Zeiss Master Prime","format":"Digital"},
    "fight club":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "se7en":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "mank":{"camera":"Red Weapon Dragon 8K","lens":"Leica Summilux-C","format":"Digital 8K B&W"},
    "pulp fiction":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "inglourious basterds":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm Anamorphic"},
    "the hateful eight":{"camera":"Ultra Panavision 70","lens":"Panavision 70mm Anamorphic","format":"Ultra Panavision 70mm"},
    "once upon a time in hollywood":{"camera":"35mm Film","lens":"Panavision C-Series + Primo","format":"35mm Anamorphic"},
    "django unchained":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm Anamorphic"},
    "kill bill":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "gravity":{"camera":"Arri Alexa Plus / M","lens":"Leica Summilux-C","format":"Digital 2.8K"},
    "roma":{"camera":"Arri Alexa 65","lens":"Zeiss Master Anamorphic","format":"Digital 6.5K B&W"},
    "children of men":{"camera":"Arriflex 435 / Moviecam","lens":"Cooke S4","format":"35mm"},
    "parasite":{"camera":"Arri Alexa Mini","lens":"Cooke S4/i","format":"Digital 4K"},
    "the grand budapest hotel":{"camera":"35mm Film","lens":"Various Ratios","format":"35mm Multi-format"},
    "the tree of life":{"camera":"35mm Film / IMAX","lens":"Various Vintage Lenses","format":"35mm / IMAX"},
    "taxi driver":{"camera":"35mm Film","lens":"Various Prime Lenses","format":"35mm"},
    "goodfellas":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "the wolf of wall street":{"camera":"Arri Alexa","lens":"Panavision Primo","format":"Digital 3.4K"},
    "the irishman":{"camera":"Arri Alexa 65","lens":"Panavision Sphero 65","format":"Digital 6.5K"},
    "killers of the flower moon":{"camera":"Arri Alexa 35","lens":"Panavision Sphero 65","format":"Digital 4K"},
    "the godfather":{"camera":"35mm Film","lens":"Prime Lenses","format":"35mm"},
    "apocalypse now":{"camera":"Panavision PSR / Panaflex","lens":"Panavision C-Series","format":"35mm"},
    "blade runner":{"camera":"35mm Film / Panavision","lens":"Panavision C-Series","format":"35mm Anamorphic"},
    "alien":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm Anamorphic"},
    "gladiator":{"camera":"35mm Film","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "schindler's list":{"camera":"35mm Film","lens":"Panavision Primo","format":"35mm B&W"},
    "jurassic park":{"camera":"35mm Film","lens":"Panavision Spherical","format":"35mm"},
    "saving private ryan":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "mad max fury road":{"camera":"Arri Alexa M / XT","lens":"Cooke S4 + Angenieux","format":"Digital 3.4K"},
    "avatar":{"camera":"Sony CineAlta F23 / F35","lens":"Panavision Primo","format":"Digital 3D"},
    "avatar the way of water":{"camera":"Arri Alexa LF / 65","lens":"Panavision Primo 70","format":"Digital 3D / HFR"},
    "titanic":{"camera":"Panavision Panaflex Platinum","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "there will be blood":{"camera":"35mm Film","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "the master":{"camera":"65mm Film","lens":"Panavision 65mm","format":"65mm"},
    "phantom thread":{"camera":"35mm Film","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "no country for old men":{"camera":"35mm Film","lens":"Panavision Primo","format":"35mm Spherical"},
    "requiem for a dream":{"camera":"35mm Film","lens":"Various + Custom","format":"35mm"},
    "black swan":{"camera":"16mm / 35mm Film","lens":"Zeiss Ultra Prime","format":"16mm / 35mm"},
    "the revenant":{"camera":"Arri Alexa 65 / IMAX","lens":"Leica Summilux-C","format":"IMAX / Digital"},
    "birdman":{"camera":"Arri Alexa XT","lens":"Leica Summilux-C","format":"Digital 3.4K"},
    "poor things":{"camera":"Kodak 35mm Film","lens":"Custom Fisheye + Anamorphic","format":"35mm B&W / Colour"},
    "the favourite":{"camera":"35mm Film","lens":"Fisheye Lens","format":"35mm"},
    "get out":{"camera":"Arri Alexa Mini","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "us":{"camera":"Arri Alexa Mini","lens":"Leica Summilux-C","format":"Digital 4K"},
    "nope":{"camera":"IMAX 65mm / Arri Alexa","lens":"Panavision 65mm","format":"IMAX / Digital"},
    "hereditary":{"camera":"Arri Alexa Mini","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "midsommar":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Master Prime","format":"Digital 4.5K"},
    "the lighthouse":{"camera":"Arriflex 35 BL4s","lens":"Leica Summicron-C","format":"35mm B&W 1.19:1"},
    "the witch":{"camera":"Arri Alexa XT","lens":"Leica Summilux-C","format":"Digital 3.4K"},
    "la la land":{"camera":"35mm Anamorphic","lens":"Panavision C-Series","format":"35mm Anamorphic"},
    "whiplash":{"camera":"Canon EOS C300 / 5D","lens":"Zeiss CP.2 Compact Primes","format":"Digital"},
    "1917":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "everything everywhere all at once":{"camera":"Sony Venice","lens":"Zeiss Supreme Prime","format":"Digital 6K"},
    "past lives":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Supreme Prime","format":"Digital 4.5K"},
    "saltburn":{"camera":"16mm Film","lens":"Zeiss Ultra Prime","format":"16mm 1:1 Ratio"},
    "the zone of interest":{"camera":"Arri Alexa 35","lens":"Zeiss Supreme Prime","format":"Digital 4K"},
    "the banshees of inisherin":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Supreme Prime","format":"Digital 4.5K"},
    "in the mood for love":{"camera":"35mm Film","lens":"Various Telephoto","format":"35mm"},
    "chungking express":{"camera":"16mm Film","lens":"Various","format":"16mm"},
    "oldboy":{"camera":"35mm Film","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "spirited away":{"camera":"Rendered Animation","lens":"Virtual Cameras","format":"Digital Animation"},
    "seven samurai":{"camera":"35mm Film","lens":"Various","format":"35mm"},
    "citizen kane":{"camera":"35mm Film","lens":"Various Deep Focus Lenses","format":"35mm"},
    "the matrix":{"camera":"35mm Film","lens":"Panavision C-Series","format":"35mm"},
    "avengers endgame":{"camera":"Arri Alexa IMAX / 65","lens":"Panavision Primo","format":"IMAX / Digital"},
    "top gun maverick":{"camera":"Arri Alexa LF / IMAX","lens":"Panavision Primo","format":"IMAX / Digital"},
    "her":{"camera":"Arri Alexa Plus","lens":"Panavision Primo","format":"Digital 3.4K"},
    "moonlight":{"camera":"Arri Alexa Mini","lens":"Leica Summilux-C","format":"Digital 4K"},
    "coco":{"camera":"Rendered CGI","lens":"Virtual Cameras","format":"Digital Animation"},
    "vikram":{"camera":"Arri Alexa Mini LF","lens":"Panavision Primo","format":"Digital 4.5K"},
    "master":{"camera":"Arri Alexa Mini","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "beast":{"camera":"Arri Alexa Mini LF","lens":"Cooke S7/i","format":"Digital 4.5K"},
    "jailer":{"camera":"Arri Alexa Mini LF","lens":"Panavision Primo","format":"Digital 4.5K"},
    "leo":{"camera":"Arri Alexa 35","lens":"Zeiss Supreme Prime","format":"Digital 4K"},
    "vettaiyan":{"camera":"Arri Alexa 35","lens":"Panavision Primo","format":"Digital 4K"},
    "kanguva":{"camera":"Arri Alexa 35 / IMAX","lens":"Panavision Sphero 65","format":"IMAX / Digital"},
    "baahubali":{"camera":"Red Epic Dragon","lens":"Zeiss Master Prime","format":"Digital 6K"},
    "baahubali 2":{"camera":"Red Epic Dragon / Weapon","lens":"Zeiss Master Prime","format":"Digital 6K / 8K"},
    "rrr":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Supreme Prime","format":"Digital 4.5K"},
    "pushpa":{"camera":"Arri Alexa Mini","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "kalki 2898 ad":{"camera":"Arri Alexa 35 / IMAX","lens":"Panavision Sphero 65","format":"IMAX / Digital"},
    "96":{"camera":"Arri Alexa Mini","lens":"Leica Summilux-C","format":"Digital 4K"},
    "soorarai pottru":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Supreme Prime","format":"Digital 4.5K"},
    "kaithi":{"camera":"Arri Alexa Mini","lens":"Zeiss Master Prime","format":"Digital 4K"},
    "karnan":{"camera":"Arri Alexa Mini LF","lens":"Leica Summilux-C","format":"Digital 4.5K"},
    "super deluxe":{"camera":"Arri Alexa Mini","lens":"Cooke S4","format":"Digital 4K"},
    "mersal":{"camera":"Arri Alexa XT","lens":"Zeiss Master Prime","format":"Digital 3.4K"},
    "ponniyin selvan":{"camera":"Arri Alexa Mini LF","lens":"Panavision Primo","format":"Digital 4.5K"},
    "dangal":{"camera":"Arri Alexa","lens":"Zeiss Master Prime","format":"Digital"},
    "brahmastra":{"camera":"Arri Alexa Mini LF","lens":"Panavision Primo","format":"Digital 4.5K"},
    "the power of the dog":{"camera":"Arri Alexa Mini LF","lens":"Panavision Primo","format":"Digital 4.5K"},
    "the holdovers":{"camera":"35mm Film","lens":"Panavision Anamorphic","format":"35mm Anamorphic"},
    "anatomy of a fall":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Master Prime","format":"Digital 4.5K"},
    "drive my car":{"camera":"Arri Alexa Mini LF","lens":"Zeiss Supreme Prime","format":"Digital 4.5K"},
}

def get_camera(title):
    key = title.lower()
    for k, v in CAMERA_SPECS.items():
        if k in key:
            return v
    return {"camera": "N/A", "lens": "N/A", "format": "N/A"}

QUOTES = {
    "interstellar":["We used to look up at the sky and wonder at our place in the stars.","Do not go gentle into that good night.","Love is the one thing we're capable of perceiving that transcends dimensions of time and space."],
    "the dark knight":["Why so serious?","You either die a hero, or you live long enough to see yourself become the villain.","Madness is like gravity. All it takes is a little push."],
    "fight club":["The things you own end up owning you.","It's only after we've lost everything that we're free to do anything."],
    "pulp fiction":["English, do you speak it?","The path of the righteous man is beset on all sides by the inequities of the selfish."],
    "inception":["You mustn't be afraid to dream a little bigger, darling.","An idea is like a virus. Resilient. Highly contagious."],
    "parasite":["You know what kind of plan never fails? No plan. No plan at all.","It's so metaphorical."],
    "the godfather":["I'm gonna make him an offer he can't refuse.","Leave the gun. Take the cannoli."],
    "la la land":["Here's to the ones who dream, foolish as they may seem."],
    "blade runner 2049":["All the best memories are hers.","Dying for the right cause is the most human thing we can do."],
    "arrival":["Language is the foundation of civilization.","If you could see your whole life from start to finish, would you change things?"],
    "her":["The past is just a story we tell ourselves."],
    "no country for old men":["What's the most you ever lost in a coin toss?","You can't stop what's coming."],
    "there will be blood":["I drink your milkshake! I drink it up!"],
    "2001 a space odyssey":["I'm sorry, Dave. I'm afraid I can't do that."],
    "whiplash":["There are no two words in the English language more harmful than good job."],
    "the revenant":["I ain't afraid to die anymore. I done it already."],
    "mad max fury road":["What a lovely day!","We are not things.","Who killed the world?"],
    "dune":["A great man doesn't seek to lead. He's called to it.","I must not fear. Fear is the mind-killer."],
    "oppenheimer":["Now I am become Death, the destroyer of worlds.","Theory will only take you so far."],
    "everything everywhere all at once":["Of all the places I could be, I just want to be here with you.","The only thing I know is that we have to be kind."],
    "goodfellas":["As far back as I can remember, I always wanted to be a gangster."],
    "taxi driver":["You talkin to me?"],
    "se7en":["What's in the box?"],
    "the shining":["Here's Johnny!"],
    "oldboy":["Laugh and the world laughs with you. Weep and you weep alone."],
}

def get_quotes(title):
    key = title.lower()
    for k, v in QUOTES.items():
        if k in key:
            return v
    return []

FILMING_LOCATIONS = {
    "interstellar":     [{"country":"USA","cities":"Alberta, Canada · Iceland · Utah"},{"country":"Canada","cities":"Fort Macleod, Alberta"}],
    "dune":             [{"country":"UAE","cities":"Abu Dhabi desert"},{"country":"Jordan","cities":"Wadi Rum"},{"country":"Hungary","cities":"Budapest studios"}],
    "parasite":         [{"country":"South Korea","cities":"Seoul · Mapo-gu"}],
    "oppenheimer":      [{"country":"USA","cities":"Los Alamos, New Mexico · Princeton, New Jersey"}],
    "la la land":       [{"country":"USA","cities":"Los Angeles · Griffith Observatory · Hermosa Beach"}],
    "the godfather":    [{"country":"USA","cities":"New York City · Long Island"},{"country":"Italy","cities":"Sicily · Savoca · Forza d'Agro"}],
    "1917":             [{"country":"UK","cities":"Wiltshire · Govan · Chatham"}],
    "the revenant":     [{"country":"Canada","cities":"Calgary · Kananaskis Country"},{"country":"Argentina","cities":"Tierra del Fuego"}],
    "mad max fury road":[{"country":"Namibia","cities":"Namib Desert · Dorob National Park"},{"country":"Australia","cities":"Broken Hill, NSW"}],
    "gravity":          [{"country":"UK","cities":"Shepperton Studios · Pinewood Studios"}],
    "inception":        [{"country":"UK","cities":"London"},{"country":"France","cities":"Paris"},{"country":"Japan","cities":"Tokyo"},{"country":"Canada","cities":"Alberta"}],
    "blade runner 2049":[{"country":"Hungary","cities":"Budapest"},{"country":"Spain","cities":"Almeria desert"},{"country":"Iceland","cities":"Vik"}],
    "avatar":           [{"country":"New Zealand","cities":"Fiordland National Park"}],
    "titanic":          [{"country":"Mexico","cities":"Rosarito Beach"},{"country":"USA","cities":"Halifax, Nova Scotia"}],
    "schindler's list": [{"country":"Poland","cities":"Krakow · Auschwitz"},{"country":"USA","cities":"Universal Studios"}],
    "the dark knight":  [{"country":"USA","cities":"Chicago · New York"},{"country":"UK","cities":"London"},{"country":"Hong Kong","cities":"Hong Kong"}],
    "no country for old men":[{"country":"USA","cities":"Texas · New Mexico · Las Vegas, NM"}],
    "there will be blood":[{"country":"USA","cities":"Marfa, Texas · California"}],
    "roma":             [{"country":"Mexico","cities":"Colonia Roma, Mexico City"}],
    "the lighthouse":   [{"country":"Canada","cities":"Cape Forchu, Nova Scotia"}],
    "midsommar":        [{"country":"Sweden","cities":"Halsingland"},{"country":"Hungary","cities":"Budapest studios"}],
    "vikram":           [{"country":"India","cities":"Chennai · Hyderabad · Dubai"}],
    "master":           [{"country":"India","cities":"Chennai · Neyveli · Yercaud"}],
    "ponniyin selvan":  [{"country":"India","cities":"Tamil Nadu · Pondicherry"},{"country":"Thailand","cities":"Bangkok"},{"country":"UAE","cities":"Dubai"}],
    "kanguva":          [{"country":"India","cities":"Chennai · Hyderabad"},{"country":"Spain","cities":"Almeria"},{"country":"Turkey","cities":"Cappadocia"}],
    "rrr":              [{"country":"India","cities":"Hyderabad · Araku Valley"},{"country":"Ukraine","cities":"Kyiv"},{"country":"Bulgaria","cities":"Sofia"}],
    "baahubali 2":      [{"country":"India","cities":"Hyderabad · Lepakshi · Hampi"},{"country":"Bulgaria","cities":"Sofia"}],
    "goodfellas":       [{"country":"USA","cities":"New York City · Queens · The Copacabana"}],
    "the godfather part ii":[{"country":"USA","cities":"New York · Nevada"},{"country":"Italy","cities":"Sicily"}],
    "apocalypse now":   [{"country":"Philippines","cities":"Baler · Iba · Pagsanjan"}],
    "seven samurai":    [{"country":"Japan","cities":"Nogawa Park · Toho Studios, Tokyo"}],
}

def get_locations(title):
    key = title.lower()
    for k, v in FILMING_LOCATIONS.items():
        if k in key:
            return v
    return []

MOODS = [
    {"id":878,"name":"Science Fiction","sub":"Worlds beyond imagination"},
    {"id":18,"name":"Drama","sub":"Stories that stay with you"},
    {"id":53,"name":"Thriller","sub":"Edge of your seat"},
    {"id":10749,"name":"Romance","sub":"Love in every form"},
    {"id":35,"name":"Comedy","sub":"Pure, unfiltered laughter"},
    {"id":27,"name":"Horror","sub":"Fear as an art form"},
    {"id":28,"name":"Action","sub":"Relentless momentum"},
    {"id":99,"name":"Documentary","sub":"Truth, unscripted"},
    {"id":14,"name":"Fantasy","sub":"The impossible made real"},
    {"id":80,"name":"Crime","sub":"Morality at its darkest"},
    {"id":10752,"name":"War","sub":"The cost of conflict"},
    {"id":37,"name":"Western","sub":"Lawless frontiers"},
    {"id":36,"name":"History","sub":"The world that was"},
    {"id":10402,"name":"Music","sub":"Rhythm and soul"},
    {"id":9648,"name":"Mystery","sub":"Nothing is as it seems"},
    {"id":16,"name":"Animation","sub":"Art in motion"},
    {"id":12,"name":"Adventure","sub":"Beyond the horizon"},
    {"id":10751,"name":"Family","sub":"For every generation"},
]

FILM_CLUBS = [
    {"id":1,"name":"The Long Take Society","desc":"Devoted to unbroken cinematography and single-shot mastery.","members":4820,"films_count":48},
    {"id":2,"name":"Criterion Collective","desc":"Deep dives into the Criterion Collection and art cinema.","members":9340,"films_count":120},
    {"id":3,"name":"Midnight Horror Club","desc":"Weekly horror screenings and post-film discussions.","members":6210,"films_count":89},
    {"id":4,"name":"Sci-Fi Symposium","desc":"Exploring ideas, futures, and the science behind the fiction.","members":7650,"films_count":76},
    {"id":5,"name":"Auteur Studies","desc":"Director-focused deep dives, one filmmaker per month.","members":3290,"films_count":62},
    {"id":6,"name":"World Cinema Circle","desc":"Films from every country, every language, every culture.","members":5540,"films_count":203},
    {"id":7,"name":"New Waves","desc":"French New Wave, Iranian cinema, Korean New Wave and beyond.","members":2870,"films_count":94},
    {"id":8,"name":"Cinematography Lab","desc":"Frame by frame analysis of the world's most beautiful films.","members":3110,"films_count":55},
    {"id":9,"name":"The Reel Noir","desc":"Classic and neo-noir, shadows, femmes fatales, moral ambiguity.","members":4450,"films_count":71},
    {"id":10,"name":"Animation Appreciation","desc":"Pixar, Ghibli, indie animation and the art of the moving drawing.","members":8920,"films_count":88},
    {"id":11,"name":"Tamil Cinema Club","desc":"Celebrating the rich legacy and modern brilliance of Tamil films.","members":12400,"films_count":156},
    {"id":12,"name":"Indian Parallel Cinema","desc":"The art house tradition from Ray to Kashyap and beyond.","members":3780,"films_count":98},
]

DNA_TYPES = {
    "visionary":{"title":"The Visionary","desc":"You gravitate toward films that challenge perception and expand the boundaries of what cinema can be.","directors":["Christopher Nolan","Denis Villeneuve","Alfonso Cuaron"],"films":["Interstellar","Blade Runner 2049","Arrival"]},
    "empath":{"title":"The Empath","desc":"Character and emotion drive your viewing. You find yourself drawn to intimate stories and complex relationships.","directors":["Wong Kar-wai","Celine Sciamma","Barry Jenkins"],"films":["In the Mood for Love","Past Lives","Moonlight"]},
    "thrill_seeker":{"title":"The Thrill Seeker","desc":"Tension is your currency. You live for the films that keep you on the edge of your seat.","directors":["David Fincher","Park Chan-wook","Bong Joon-ho"],"films":["Parasite","Oldboy","Gone Girl"]},
    "archivist":{"title":"The Archivist","desc":"You seek the classics, the overlooked, and the historically significant.","directors":["Stanley Kubrick","Akira Kurosawa","Orson Welles"],"films":["2001: A Space Odyssey","Seven Samurai","Citizen Kane"]},
    "poet":{"title":"The Poet","desc":"Atmosphere over plot. You are drawn to films that feel more like paintings.","directors":["Terrence Malick","Andrei Tarkovsky","Apichatpong Weerasethakul"],"films":["The Tree of Life","Stalker","Uncle Boonmee"]},
    "rebel":{"title":"The Rebel","desc":"You prefer films that break rules, genre-bending, politically charged, formally experimental.","directors":["Jean-Luc Godard","Lars von Trier","Gaspar Noe"],"films":["Breathless","Melancholia","Enter the Void"]},
}

DIRECTORS = [
    {"name":"Christopher Nolan","tmdb_id":525,"nationality":"British-American","known_for":["Interstellar","The Dark Knight","Inception","Oppenheimer"],"style":"Epic, cerebral, technically obsessive filmmaker known for non-linear narratives and IMAX photography."},
    {"name":"Denis Villeneuve","tmdb_id":137427,"nationality":"Canadian","known_for":["Dune","Arrival","Blade Runner 2049","Sicario"],"style":"Visually immersive director known for deliberate pacing and stunning wide-format cinematography."},
    {"name":"Bong Joon-ho","tmdb_id":21684,"nationality":"South Korean","known_for":["Parasite","Snowpiercer","The Host","Okja"],"style":"Genre-defying filmmaker blending social commentary with sharp thriller instincts."},
    {"name":"Martin Scorsese","tmdb_id":1032,"nationality":"American","known_for":["Goodfellas","Taxi Driver","The Irishman","Killers of the Flower Moon"],"style":"Master of crime cinema with kinetic editing and deep character studies."},
    {"name":"David Fincher","tmdb_id":7467,"nationality":"American","known_for":["Fight Club","Gone Girl","Se7en","The Social Network"],"style":"Meticulously precise director known for dark thrillers and obsessive visual control."},
    {"name":"Alfonso Cuaron","tmdb_id":11630,"nationality":"Mexican","known_for":["Gravity","Roma","Children of Men","Y Tu Mama Tambien"],"style":"Master of the long take with immersive cinematography and emotional depth."},
    {"name":"Quentin Tarantino","tmdb_id":138,"nationality":"American","known_for":["Pulp Fiction","Inglourious Basterds","The Hateful Eight"],"style":"Pop culture-obsessed auteur known for sharp dialogue and revisionist history."},
    {"name":"Stanley Kubrick","tmdb_id":240,"nationality":"American-British","known_for":["2001: A Space Odyssey","The Shining","Barry Lyndon","Full Metal Jacket"],"style":"Perfectionist visionary known for technical mastery and psychological depth."},
    {"name":"Wong Kar-wai","tmdb_id":13316,"nationality":"Hong Kong","known_for":["In the Mood for Love","Chungking Express","2046"],"style":"Romantic, melancholic filmmaker known for saturated cinematography and emotional longing."},
    {"name":"Mani Ratnam","tmdb_id":5765,"nationality":"Indian","known_for":["Ponniyin Selvan","Roja","Dil Se","Bombay"],"style":"Master of Tamil and Hindi cinema blending romance, politics, and stunning visuals."},
    {"name":"Shankar","tmdb_id":56812,"nationality":"Indian","known_for":["2.0","Enthiran","Indian","Vikram Vedha"],"style":"Visionary Tamil filmmaker known for spectacular VFX-driven blockbusters."},
    {"name":"Alejandro Inarritu","tmdb_id":1032,"nationality":"Mexican","known_for":["The Revenant","Birdman","Babel","Amores Perros"],"style":"Intense, immersive director known for single-take cinematography and raw human drama."},
    {"name":"Wes Anderson","tmdb_id":5820,"nationality":"American","known_for":["The Grand Budapest Hotel","Moonrise Kingdom","The French Dispatch"],"style":"Symmetrical, whimsical auteur with a distinctly precise visual style and deadpan humor."},
    {"name":"Paul Thomas Anderson","tmdb_id":4762,"nationality":"American","known_for":["There Will Be Blood","The Master","Phantom Thread","Boogie Nights"],"style":"Character-obsessed filmmaker known for operatic performances and 70mm cinematography."},
    {"name":"Terrence Malick","tmdb_id":1770,"nationality":"American","known_for":["The Tree of Life","The Thin Red Line","Badlands"],"style":"Philosophical, poetic filmmaker known for impressionistic photography and voiceover narration."},
]

DOPS = [
    {"id":1,"name":"Roger Deakins","style":"Master of natural light","bio":"14-time Oscar nominee, won for Blade Runner 2049 and 1917. Known for his painterly approach to natural light.","films":["Blade Runner 2049","1917","Sicario","Prisoners","No Country for Old Men"]},
    {"id":2,"name":"Emmanuel Lubezki","style":"Long take virtuoso","bio":"Three consecutive Oscar wins for Gravity, Birdman, and The Revenant. Pioneer of the continuous take.","films":["Gravity","Birdman","The Revenant","Children of Men","The Tree of Life"]},
    {"id":3,"name":"Hoyte van Hoytema","style":"IMAX master","bio":"Christopher Nolan's cinematographer of choice. Known for pushing IMAX and 65mm film formats to their limits.","films":["Interstellar","Dunkirk","Tenet","Oppenheimer","Spectre"]},
    {"id":4,"name":"Greig Fraser","style":"Digital innovator","bio":"Oscar winner for Dune. Also shot Rogue One and The Batman. Known for his bold use of digital formats.","films":["Dune","Dune: Part Two","The Batman","Zero Dark Thirty","Lion"]},
    {"id":5,"name":"Robert Richardson","style":"Kinetic energy","bio":"Three Oscar wins. Known for his intense, high-energy photography with Tarantino and Scorsese.","films":["The Hateful Eight","Hugo","Inglourious Basterds","JFK","Casino"]},
    {"id":6,"name":"Rodrigo Prieto","style":"Emotional realism","bio":"Known for his versatile, emotionally charged photography across genres and cultures.","films":["Barbie","Silence","The Wolf of Wall Street","Brokeback Mountain"]},
    {"id":7,"name":"Linus Sandgren","style":"Vibrant classicism","bio":"Oscar winner for La La Land. Known for vibrant, classical compositions with modern energy.","films":["La La Land","Babylon","No Time to Die","First Man"]},
    {"id":8,"name":"Santosh Sivan","style":"Indian master","bio":"One of India's greatest DPs. Known for poetic visuals in Tamil and Hindi cinema.","films":["Ponniyin Selvan","Roja","Dil Se","The Terrorist","Asoka"]},
    {"id":9,"name":"P.C. Sreeram","style":"Legendary visuals","bio":"Legendary Indian cinematographer known for stunning work in Tamil and Telugu cinema.","films":["Nayakan","Thevar Magan","Bombay","Kaakha Kaakha"]},
    {"id":10,"name":"Nirav Shah","style":"Action precision","bio":"Known for high-octane Tamil blockbusters with precise action photography.","films":["Kaithi","Vikram","Thunivu","Doctor"]},
]

TAMIL_IDS = {
    "modern": [1009248, 663712, 830785, 934433, 920, 1092539, 766507, 1087822, 948550, 700391, 786892, 614934],
    "classic": [9320, 14160, 11688, 11654, 73835, 49051, 49844, 85350],
}

# ── ROUTES ────────────────────────────────────────────────────

@app.route("/")
def index():
    trending = tmdb("/trending/movie/week")["results"][:12]
    featured = trending[0] if trending else None
    popular  = tmdb("/movie/popular")["results"][:8]
    upcoming = tmdb("/movie/upcoming")["results"][:5]
    return render_template("index.html", trending=trending, featured=featured, popular=popular, upcoming=upcoming, moods=MOODS[:10], poster=poster, backdrop=backdrop, owner=OWNER)

@app.route("/movie/<int:movie_id>")
def movie_page(movie_id):
    data      = tmdb(f"/movie/{movie_id}", append_to_response="credits,images,videos,keywords,recommendations")
    credits   = data.get("credits", {})
    videos    = data.get("videos", {})
    images    = data.get("images", {})
    recs      = data.get("recommendations", {}).get("results", [])[:8]
    backdrops = [b for b in images.get("backdrops", []) if b.get("file_path")][:10]
    trailers  = [v for v in videos.get("results", []) if v.get("type") == "Trailer" and v.get("site") == "YouTube"]
    trailer   = trailers[0]["key"] if trailers else None
    cast      = credits.get("cast", [])[:20]
    crew      = credits.get("crew", [])
    director  = next((c["name"] for c in crew if c["job"] == "Director"), "N/A")
    dop       = next((c["name"] for c in crew if c["job"] == "Director of Photography"), "N/A")
    composer  = next((c["name"] for c in crew if c["job"] == "Original Music Composer"), "N/A")
    editor    = next((c["name"] for c in crew if c["job"] == "Editor"), "N/A")
    writer    = next((c["name"] for c in crew if c["job"] in ["Screenplay","Writer"]), "N/A")
    producer  = next((c["name"] for c in crew if c["job"] == "Producer"), "N/A")
    cam       = get_camera(data.get("title",""))
    quotes    = get_quotes(data.get("title",""))
    locations = get_locations(data.get("title",""))
    mins      = data.get("runtime", 0)
    runtime   = f"{mins//60}h {mins%60}m" if mins else "N/A"
    imdb_id   = data.get("imdb_id")
    keywords  = data.get("keywords", {}).get("keywords", [])[:12]
    awards    = omdb(imdb_id) if imdb_id else {}
    # Add production countries as locations if no custom locations
    if not locations and data.get("production_countries"):
        locations = [{"country": c["name"], "cities": "Various locations"} for c in data["production_countries"]]
    return render_template("movie.html", movie=data, backdrops=backdrops, trailer=trailer, cast=cast, director=director, dop=dop, composer=composer, editor=editor, writer=writer, producer=producer, cam=cam, quotes=quotes, locations=locations, awards=awards, runtime=runtime, imdb_id=imdb_id, keywords=keywords, recommendations=recs, poster=poster, backdrop=backdrop, owner=OWNER)

@app.route("/search")
def search():
    q = request.args.get("q","")
    results = tmdb("/search/movie", query=q)["results"] if q else []
    return render_template("search.html", results=results, query=q, poster=poster, owner=OWNER)

@app.route("/genre/<int:genre_id>")
def genre(genre_id):
    mood = next((m for m in MOODS if m["id"] == genre_id), None)
    results = tmdb("/discover/movie", with_genres=genre_id, sort_by="vote_average.desc", vote_count_gte=500)["results"]
    return render_template("search.html", results=results, query=mood["name"] if mood else "Genre", poster=poster, owner=OWNER)

@app.route("/battles")
def battles():
    popular = tmdb("/movie/popular")["results"]
    a = random.choice(popular[:20])
    b = random.choice([m for m in popular[:20] if m["id"] != a["id"]])
    return render_template("battles.html", film_a=a, film_b=b, poster=poster, owner=OWNER)

@app.route("/api/battles/new")
def battles_new():
    popular = tmdb("/movie/popular")["results"]
    a = random.choice(popular[:20])
    b = random.choice([m for m in popular[:20] if m["id"] != a["id"]])
    return jsonify({"a":{"id":a["id"],"title":a["title"],"poster":poster(a.get("poster_path"),"w342"),"year":(a.get("release_date") or "")[:4],"rating":round(a.get("vote_average",0),1)},"b":{"id":b["id"],"title":b["title"],"poster":poster(b.get("poster_path"),"w342"),"year":(b.get("release_date") or "")[:4],"rating":round(b.get("vote_average",0),1)}})

@app.route("/clubs")
def clubs():
    return render_template("clubs.html", clubs=FILM_CLUBS, owner=OWNER)

@app.route("/dna")
def dna():
    return render_template("dna.html", dna_types=DNA_TYPES, owner=OWNER)

@app.route("/api/dna/result", methods=["POST"])
def dna_result():
    answers = request.json.get("answers", [])
    scores  = {k: 0 for k in DNA_TYPES}
    mapping = {"visionary":["sci-fi","epic","technical","nolan","villeneuve"],"empath":["drama","romance","character","emotion","intimate"],"thrill_seeker":["thriller","crime","twist","tension","fincher"],"archivist":["classic","old","criterion","kubrick","history"],"poet":["slow","visual","atmospheric","malick","art"],"rebel":["experimental","provocative","avant","godard","rule"]}
    for ans in answers:
        for dtype, keywords in mapping.items():
            if any(k in ans.lower() for k in keywords):
                scores[dtype] += 1
    return jsonify(DNA_TYPES[max(scores, key=scores.get)])

@app.route("/community")
def community():
    trending = tmdb("/trending/movie/week")["results"][:10]
    popular  = tmdb("/movie/popular")["results"][:10]
    return render_template("community.html", trending=trending, popular=popular, poster=poster, backdrop=backdrop, owner=OWNER)

@app.route("/watchlist")
def watchlist():
    return render_template("watchlist.html", owner=OWNER)

@app.route("/about")
def about():
    return render_template("about.html", owner=OWNER)

@app.route("/directors")
def directors():
    return render_template("directors.html", directors=DIRECTORS, owner=OWNER)

@app.route("/director/<int:person_id>")
def director_page(person_id):
    person = tmdb(f"/person/{person_id}")
    credits = tmdb(f"/person/{person_id}/movie_credits")
    films = sorted([f for f in credits.get("crew",[]) if f.get("job")=="Director" and f.get("vote_count",0)>100], key=lambda x: x.get("release_date",""), reverse=True)
    return render_template("director.html", director=person, films=films, poster=poster, owner=OWNER)

@app.route("/cinematographers")
def cinematographers():
    return render_template("cinematographers.html", dops=DOPS, owner=OWNER)

@app.route("/cinematographer/<int:dop_id>")
def cinematographer_page(dop_id):
    dop = next((d for d in DOPS if d["id"] == dop_id), None)
    if not dop:
        return redirect("/cinematographers")
    results = tmdb("/search/person", query=dop["name"])["results"]
    films = []
    if results:
        pid = results[0]["id"]
        credits = tmdb(f"/person/{pid}/movie_credits")
        films = sorted([f for f in credits.get("crew",[]) if "Cinematograph" in f.get("job","") or "Director of Photography" in f.get("job","")], key=lambda x: x.get("release_date",""), reverse=True)[:20]
    return render_template("cinematographers.html", dops=DOPS, selected=dop, films=films, poster=poster, owner=OWNER)

@app.route("/decades")
def decades():
    return render_template("decades.html", decade=None, films=[], owner=OWNER)

@app.route("/decades/<int:decade>")
def decade_films(decade):
    start = decade
    end   = decade + 9
    results = tmdb("/discover/movie", primary_release_date_gte=f"{start}-01-01", primary_release_date_lte=f"{end}-12-31", sort_by="vote_average.desc", vote_count_gte=500)["results"][:24]
    return render_template("decades.html", decade=decade, films=results, poster=poster, owner=OWNER)

@app.route("/tamil")
def tamil():
    era = request.args.get("era","")
    sections = []
    if not era or era == "modern":
        modern = tmdb("/discover/movie", with_original_language="ta", sort_by="vote_average.desc", vote_count_gte=100, primary_release_date_gte="2015-01-01")["results"][:12]
        sections.append({"title":"Modern Tamil Cinema","desc":"2015 to present — the new golden era","films":modern})
    if not era or era == "classic":
        classic = tmdb("/discover/movie", with_original_language="ta", sort_by="vote_average.desc", vote_count_gte=50, primary_release_date_lte="2000-12-31")["results"][:12]
        sections.append({"title":"Classic Tamil Cinema","desc":"The films that built Kollywood","films":classic})
    if not sections or era:
        all_tamil = tmdb("/discover/movie", with_original_language="ta", sort_by="vote_average.desc", vote_count_gte=50)["results"][:20]
        if not sections:
            sections.append({"title":"Tamil Cinema","desc":"The best of Kollywood","films":all_tamil})
    return render_template("tamil.html", sections=sections, era=era, poster=poster, owner=OWNER)

@app.route("/boxoffice")
def boxoffice():
    now_playing = tmdb("/movie/now_playing")["results"][:15]
    upcoming    = tmdb("/movie/upcoming")["results"][:10]
    popular     = tmdb("/movie/top_rated")["results"][:10]
    return render_template("boxoffice.html", now_playing=now_playing, upcoming=upcoming, popular=popular, poster=poster, owner=OWNER)

@app.route("/api/watchlist/info/<int:movie_id>")
def watchlist_info(movie_id):
    data = tmdb(f"/movie/{movie_id}")
    return jsonify({"id":data["id"],"title":data["title"],"year":(data.get("release_date") or "")[:4],"rating":round(data.get("vote_average",0),1),"poster":poster(data.get("poster_path"),"w342"),"overview":data.get("overview","")})

@app.route("/api/search")
def api_search():
    q = request.args.get("q","")
    data = tmdb("/search/movie", query=q) if q else {"results":[]}
    return jsonify([{"id":m["id"],"title":m["title"],"year":(m.get("release_date") or "")[:4],"rating":round(m.get("vote_average",0),1),"poster":poster(m.get("poster_path"),"w92")} for m in data.get("results",[])[:8]])

@app.route("/google5cf9d1583ad86428.html")
def google_verify():
    return "google-site-verification: google5cf9d1583ad86428.html"

@app.route("/sitemap.xml")
def sitemap():
    pages = ["","/search","/battles","/clubs","/dna","/community","/watchlist","/about","/directors","/cinematographers","/decades","/tamil","/boxoffice"]
    urls  = "\n".join([f"  <url><loc>https://irisvue.onrender.com{p}</loc></url>" for p in pages])
    xml   = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>'
    return app.response_class(xml, mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
