from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, current_user
import requests, os, random
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)

# ── SECURITY CONFIG ───────────────────────────────────────────
app.config['SECRET_KEY']          = os.environ.get('SECRET_KEY', 'irisvue-secret-2026-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///irisvue.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── INIT EXTENSIONS ───────────────────────────────────────────
from models import db, User
from auth import auth, bcrypt

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please sign in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth)

# Create tables
with app.app_context():
    db.create_all()

TMDB_KEY  = os.environ.get("TMDB_API_KEY", "e8ca821b35da67033f670add624c8eca")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG  = "https://image.tmdb.org/t/p/"

# ── OWNER INFO ────────────────────────────────────────────────
OWNER = {
    "name":  "S.R. HarisH Prabhu",
    "email": "harishrohinth008@gmail.com",
    "place": "Coimbatore, Tamil Nadu, India",
}

def tmdb(endpoint, **params):
    params["api_key"] = TMDB_KEY
    r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=10, verify=False)
    r.raise_for_status()
    return r.json()

def poster(path, size="w500"):
    return f"{TMDB_IMG}{size}{path}" if path else ""

def backdrop(path, size="w1280"):
    return f"{TMDB_IMG}{size}{path}" if path else ""

# ── COMPREHENSIVE CAMERA DATABASE — 200+ FILMS ────────────────
CAMERA_SPECS = {
    # ── CHRISTOPHER NOLAN ──
    "interstellar":              {"camera": "IMAX 65mm / 35mm Film",          "lens": "Panavision Sphero 65",              "format": "IMAX / 35mm"},
    "the dark knight":           {"camera": "IMAX 65mm / 35mm Film",          "lens": "Panavision Primo",                  "format": "IMAX / 35mm"},
    "the dark knight rises":     {"camera": "IMAX 65mm / 35mm Film",          "lens": "Panavision Primo",                  "format": "IMAX / 35mm"},
    "inception":                 {"camera": "35mm Film / IMAX",               "lens": "Panavision Primo",                  "format": "35mm / IMAX"},
    "oppenheimer":               {"camera": "IMAX 65mm / Kodak 65mm",         "lens": "Panavision 65mm",                   "format": "IMAX 70mm"},
    "dunkirk":                   {"camera": "IMAX 65mm / 65mm Film",          "lens": "Panavision 65mm",                   "format": "IMAX / 65mm"},
    "memento":                   {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm"},
    "batman begins":             {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm Anamorphic"},
    "tenet":                     {"camera": "IMAX 65mm / Arri Alexa IMAX",    "lens": "Panavision 65mm",                   "format": "IMAX / Digital"},
    "the prestige":              {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm"},
    # ── DENIS VILLENEUVE ──
    "dune":                      {"camera": "Arri Alexa LF / Mini LF",        "lens": "Panavision Sphero 65 + Custom",     "format": "Digital 4K"},
    "dune part two":             {"camera": "Arri Alexa 35 / IMAX",           "lens": "Panavision Sphero 65",              "format": "IMAX / Digital"},
    "arrival":                   {"camera": "Arri Alexa XT Plus",             "lens": "Panavision Primo",                  "format": "Digital 3.4K"},
    "blade runner 2049":         {"camera": "Arri Alexa 65",                  "lens": "Prime DNA Lenses",                  "format": "Digital 6.5K"},
    "annihilation":              {"camera": "Arri Alexa Mini",                "lens": "Panavision Primo",                  "format": "Digital 4K"},
    "sicario":                   {"camera": "Arri Alexa XT",                  "lens": "Panavision Primo",                  "format": "Digital 3.4K"},
    "prisoners":                 {"camera": "Arri Alexa XT",                  "lens": "Zeiss Master Prime",                "format": "Digital 3.4K"},
    "enemy":                     {"camera": "Arri Alexa",                     "lens": "Zeiss Master Prime",                "format": "Digital"},
    # ── STANLEY KUBRICK ──
    "2001 a space odyssey":      {"camera": "Super Panavision 70",            "lens": "Panavision Super Sphero 65",        "format": "Super Panavision 70mm"},
    "barry lyndon":              {"camera": "35mm Film / Mitchell BNC",       "lens": "Zeiss f/0.7 NASA Lens",             "format": "35mm"},
    "the shining":               {"camera": "35mm Film",                      "lens": "Zeiss Standard Primes",             "format": "35mm"},
    "full metal jacket":         {"camera": "35mm Film",                      "lens": "Zeiss Standard Primes",             "format": "35mm"},
    "a clockwork orange":        {"camera": "35mm Film",                      "lens": "Zeiss Standard Primes",             "format": "35mm"},
    "eyes wide shut":            {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    # ── DAVID FINCHER ──
    "the social network":        {"camera": "Red Epic",                       "lens": "Zeiss Master Prime",                "format": "Digital 5K"},
    "gone girl":                 {"camera": "Red Epic Dragon",                "lens": "Zeiss Master Prime",                "format": "Digital 6K"},
    "zodiac":                    {"camera": "Viper FilmStream",               "lens": "Zeiss Master Prime",                "format": "Digital"},
    "fight club":                {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "se7en":                     {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "mank":                      {"camera": "Red Weapon Dragon 8K",           "lens": "Leica Summilux-C",                  "format": "Digital 8K B&W"},
    "the girl with the dragon tattoo": {"camera": "Red Epic",                "lens": "Zeiss Master Prime",                "format": "Digital 5K"},
    "house of cards":            {"camera": "Red Epic",                       "lens": "Zeiss Master Prime",                "format": "Digital 5K"},
    # ── QUENTIN TARANTINO ──
    "pulp fiction":              {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "inglourious basterds":      {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "the hateful eight":         {"camera": "Ultra Panavision 70",            "lens": "Panavision 70mm Anamorphic",        "format": "Ultra Panavision 70mm"},
    "once upon a time in hollywood": {"camera": "35mm Film",                 "lens": "Panavision C-Series + Primo",       "format": "35mm Anamorphic"},
    "django unchained":          {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "kill bill":                 {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "reservoir dogs":            {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    # ── ALFONSO CUARÓN ──
    "gravity":                   {"camera": "Arri Alexa Plus / M",            "lens": "Leica Summilux-C",                  "format": "Digital 2.8K"},
    "roma":                      {"camera": "Arri Alexa 65",                  "lens": "Zeiss Master Anamorphic",           "format": "Digital 6.5K B&W"},
    "children of men":           {"camera": "Arriflex 435 / Moviecam",        "lens": "Cooke S4",                          "format": "35mm"},
    "harry potter and the prisoner of azkaban": {"camera": "35mm Film",      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    # ── BONG JOON-HO ──
    "parasite":                  {"camera": "Arri Alexa Mini",                "lens": "Cooke S4/i",                        "format": "Digital 4K"},
    "snowpiercer":               {"camera": "Arri Alexa",                     "lens": "Zeiss Master Prime",                "format": "Digital"},
    "okja":                      {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "the host":                  {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    # ── WES ANDERSON ──
    "the grand budapest hotel":  {"camera": "35mm Film",                      "lens": "Various Ratios",                    "format": "35mm Multi-format"},
    "moonrise kingdom":          {"camera": "16mm Film",                      "lens": "Various Anamorphic",                "format": "16mm"},
    "the french dispatch":       {"camera": "35mm Film",                      "lens": "Various Anamorphic",                "format": "35mm Multi-format"},
    "asteroid city":             {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "isle of dogs":              {"camera": "Nikon / Canon DSLR",             "lens": "Various Macro Lenses",              "format": "Digital Stop Motion"},
    "rushmore":                  {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    # ── TERRENCE MALICK ──
    "the tree of life":          {"camera": "35mm Film / IMAX",               "lens": "Various Vintage Lenses",            "format": "35mm / IMAX"},
    "the thin red line":         {"camera": "35mm Film",                      "lens": "Various Lenses",                    "format": "35mm Anamorphic"},
    "badlands":                  {"camera": "35mm Film",                      "lens": "Various Lenses",                    "format": "35mm"},
    # ── MARTIN SCORSESE ──
    "taxi driver":               {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "goodfellas":                {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "the wolf of wall street":   {"camera": "Arri Alexa",                     "lens": "Panavision Primo",                  "format": "Digital 3.4K"},
    "the irishman":              {"camera": "Arri Alexa 65",                  "lens": "Panavision Sphero 65",              "format": "Digital 6.5K"},
    "casino":                    {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "raging bull":               {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm B&W"},
    "killers of the flower moon":{"camera": "Arri Alexa 35",                  "lens": "Panavision Sphero 65",              "format": "Digital 4K"},
    # ── FRANCIS FORD COPPOLA ──
    "the godfather":             {"camera": "35mm Film",                      "lens": "Prime Lenses",                      "format": "35mm"},
    "the godfather part ii":     {"camera": "35mm Film",                      "lens": "Prime Lenses",                      "format": "35mm"},
    "apocalypse now":            {"camera": "Panavision PSR / Panaflex",      "lens": "Panavision C-Series",               "format": "35mm"},
    # ── RIDLEY SCOTT ──
    "blade runner":              {"camera": "35mm Film / Panavision",         "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "alien":                     {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "gladiator":                 {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "the martian":               {"camera": "Arri Alexa XT / IMAX",          "lens": "Panavision Primo",                  "format": "Digital / IMAX"},
    # ── STEVEN SPIELBERG ──
    "schindler's list":          {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm B&W"},
    "jurassic park":             {"camera": "35mm Film",                      "lens": "Panavision Spherical",              "format": "35mm"},
    "saving private ryan":       {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "e.t.":                      {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "raiders of the lost ark":   {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    # ── GEORGE MILLER ──
    "mad max fury road":         {"camera": "Arri Alexa M / XT",              "lens": "Cooke S4 + Angenieux",              "format": "Digital 3.4K"},
    "mad max":                   {"camera": "35mm Film",                      "lens": "Panavision Lenses",                 "format": "35mm"},
    "three thousand years of longing": {"camera": "Arri Alexa LF",           "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    # ── JAMES CAMERON ──
    "avatar":                    {"camera": "Sony CineAlta F23 / F35",        "lens": "Panavision Primo",                  "format": "Digital 3D"},
    "avatar the way of water":   {"camera": "Arri Alexa LF / 65",            "lens": "Panavision Primo 70",               "format": "Digital 3D / HFR"},
    "titanic":                   {"camera": "Panavision Panaflex Platinum",   "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "terminator 2":              {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    # ── PAUL THOMAS ANDERSON ──
    "there will be blood":       {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "the master":                {"camera": "65mm Film",                      "lens": "Panavision 65mm",                   "format": "65mm"},
    "phantom thread":            {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "boogie nights":             {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "magnolia":                  {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "licorice pizza":            {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    # ── COEN BROTHERS ──
    "no country for old men":    {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm Spherical"},
    "fargo":                     {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "the big lebowski":          {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "true grit":                 {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "a serious man":             {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm"},
    # ── DARREN ARONOFSKY ──
    "requiem for a dream":       {"camera": "35mm Film",                      "lens": "Various + Custom",                  "format": "35mm"},
    "black swan":                {"camera": "16mm / 35mm Film",               "lens": "Zeiss Ultra Prime",                 "format": "16mm / 35mm"},
    "the wrestler":              {"camera": "16mm Film",                      "lens": "Zeiss Ultra Prime",                 "format": "16mm"},
    "mother!":                   {"camera": "16mm Film",                      "lens": "Zeiss Ultra Prime",                 "format": "16mm"},
    "pi":                        {"camera": "16mm Film",                      "lens": "Various",                           "format": "16mm B&W"},
    # ── ALEJANDRO IÑÁRRITU ──
    "the revenant":              {"camera": "Arri Alexa 65 / IMAX",          "lens": "Leica Summilux-C",                  "format": "IMAX / Digital"},
    "birdman":                   {"camera": "Arri Alexa XT",                  "lens": "Leica Summilux-C",                  "format": "Digital 3.4K"},
    "babel":                     {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "amores perros":             {"camera": "16mm / 35mm Film",               "lens": "Various",                           "format": "16mm / 35mm"},
    # ── YORGOS LANTHIMOS ──
    "poor things":               {"camera": "Kodak 35mm Film",                "lens": "Custom Fisheye + Anamorphic",       "format": "35mm B&W / Colour"},
    "the favourite":             {"camera": "35mm Film",                      "lens": "Fisheye Lens",                      "format": "35mm"},
    "the lobster":               {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "kinds of kindness":         {"camera": "Arri Alexa 35",                  "lens": "Zeiss Supreme Prime",               "format": "Digital 4K"},
    # ── JORDAN PEELE ──
    "get out":                   {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "us":                        {"camera": "Arri Alexa Mini",                "lens": "Leica Summilux-C",                  "format": "Digital 4K"},
    "nope":                      {"camera": "IMAX 65mm / Arri Alexa",        "lens": "Panavision 65mm",                   "format": "IMAX / Digital"},
    # ── ARI ASTER ──
    "hereditary":                {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "midsommar":                 {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Master Prime",                "format": "Digital 4.5K"},
    "beau is afraid":            {"camera": "Arri Alexa 35",                  "lens": "Panavision Sphero 65",              "format": "Digital 4K"},
    # ── ROBERT EGGERS ──
    "the lighthouse":            {"camera": "Arriflex 35 BL4s",               "lens": "Leica Summicron-C",                 "format": "35mm B&W 1.19:1"},
    "the witch":                 {"camera": "Arri Alexa XT",                  "lens": "Leica Summilux-C",                  "format": "Digital 3.4K"},
    "the northman":              {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "nosferatu":                 {"camera": "Arri Alexa 35",                  "lens": "Zeiss Supreme Prime",               "format": "Digital 4K"},
    # ── RECENT AWARDS FILMS ──
    "la la land":                {"camera": "35mm Anamorphic",                "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "whiplash":                  {"camera": "Canon EOS C300 / 5D",            "lens": "Zeiss CP.2 Compact Primes",         "format": "Digital"},
    "1917":                      {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "everything everywhere all at once": {"camera": "Sony Venice",           "lens": "Zeiss Supreme Prime",               "format": "Digital 6K"},
    "past lives":                {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "saltburn":                  {"camera": "16mm Film",                      "lens": "Zeiss Ultra Prime",                 "format": "16mm 1:1 Ratio"},
    "all of us strangers":       {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "the zone of interest":      {"camera": "Arri Alexa 35",                  "lens": "Zeiss Supreme Prime",               "format": "Digital 4K"},
    "tár":                       {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "aftersun":                  {"camera": "16mm Film / DV Video",           "lens": "Various",                           "format": "16mm / Digital"},
    "the banshees of inisherin": {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "the fabelmans":             {"camera": "Arri Alexa LF",                  "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "women talking":             {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "the holdovers":             {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "american fiction":          {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "anatomy of a fall":         {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Master Prime",                "format": "Digital 4.5K"},
    "poor things":               {"camera": "Kodak 35mm Film",                "lens": "Custom Fisheye + Anamorphic",       "format": "35mm B&W / Colour"},
    "oppenheimer":               {"camera": "IMAX 65mm / Kodak 65mm",         "lens": "Panavision 65mm",                   "format": "IMAX 70mm"},
    # ── HORROR CLASSICS ──
    "the exorcist":              {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "psycho":                    {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm B&W"},
    "halloween":                 {"camera": "35mm Film / Panavision",         "lens": "Panavision C-Series",               "format": "35mm Anamorphic"},
    "the silence of the lambs":  {"camera": "35mm Film",                      "lens": "Panavision Primo",                  "format": "35mm"},
    "get out":                   {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    # ── WONG KAR-WAI ──
    "in the mood for love":      {"camera": "35mm Film",                      "lens": "Various Telephoto",                 "format": "35mm"},
    "chungking express":         {"camera": "16mm Film",                      "lens": "Various",                           "format": "16mm"},
    "fallen angels":             {"camera": "16mm Film",                      "lens": "Various Wide Angle",                "format": "16mm"},
    "2046":                      {"camera": "35mm Film",                      "lens": "Various Telephoto",                 "format": "35mm"},
    # ── KOREAN CINEMA ──
    "oldboy":                    {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "the handmaiden":            {"camera": "Arri Alexa XT",                  "lens": "Panavision Anamorphic",             "format": "Digital 3.4K Anamorphic"},
    "burning":                   {"camera": "Arri Alexa Mini",                "lens": "Leica Summilux-C",                  "format": "Digital 4K"},
    "train to busan":            {"camera": "Arri Alexa",                     "lens": "Zeiss Master Prime",                "format": "Digital"},
    # ── JAPANESE CINEMA ──
    "spirited away":             {"camera": "Rendered Animation",             "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    "princess mononoke":         {"camera": "35mm Film + Digital Compositing","lens": "Various",                           "format": "35mm / Digital Hybrid"},
    "my neighbor totoro":        {"camera": "35mm Film Animation",            "lens": "Animation Cameras",                 "format": "35mm Animation"},
    "akira":                     {"camera": "35mm Film Animation",            "lens": "Animation Cameras",                 "format": "35mm Animation"},
    "seven samurai":             {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "rashomon":                  {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "ran":                       {"camera": "35mm Film",                      "lens": "Various Telephoto",                 "format": "35mm"},
    # ── FRENCH CINEMA ──
    "amelie":                    {"camera": "35mm Film",                      "lens": "Various Lenses",                    "format": "35mm"},
    "blue is the warmest colour":{"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "portrait of a lady on fire":{"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "caché":                     {"camera": "35mm Film / Video",              "lens": "Various",                           "format": "35mm / DV"},
    # ── CLASSICS ──
    "citizen kane":              {"camera": "35mm Film",                      "lens": "Various Deep Focus Lenses",         "format": "35mm"},
    "vertigo":                   {"camera": "35mm Film (VistaVision)",         "lens": "Various",                           "format": "VistaVision"},
    "lawrence of arabia":        {"camera": "Super Panavision 70",            "lens": "Panavision 65mm",                   "format": "Super Panavision 70mm"},
    "8½":                        {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "la dolce vita":             {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "the 400 blows":             {"camera": "35mm Film",                      "lens": "Various",                           "format": "35mm"},
    "breathless":                {"camera": "35mm Film (Handheld)",           "lens": "Various",                           "format": "35mm"},
    # ── SCI-FI & ACTION ──
    "the matrix":                {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "the matrix reloaded":       {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "guardians of the galaxy":   {"camera": "Arri Alexa XT",                  "lens": "Panavision Primo",                  "format": "Digital 3.4K"},
    "avengers endgame":          {"camera": "Arri Alexa IMAX / 65",          "lens": "Panavision Primo",                  "format": "IMAX / Digital"},
    "avengers infinity war":     {"camera": "Arri Alexa IMAX / 65",          "lens": "Panavision Primo",                  "format": "IMAX / Digital"},
    "top gun maverick":          {"camera": "Arri Alexa LF / IMAX",          "lens": "Panavision Primo",                  "format": "IMAX / Digital"},
    "mission impossible":        {"camera": "Arri Alexa / 35mm Film",         "lens": "Panavision Primo",                  "format": "35mm / Digital"},
    "john wick":                 {"camera": "Arri Alexa XT",                  "lens": "Zeiss Master Prime",                "format": "Digital 3.4K"},
    # ── ROMANCE & DRAMA ──
    "her":                       {"camera": "Arri Alexa Plus",                "lens": "Panavision Primo",                  "format": "Digital 3.4K"},
    "eternal sunshine of the spotless mind": {"camera": "35mm Film",         "lens": "Various Lenses",                    "format": "35mm"},
    "call me by your name":      {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "moonlight":                 {"camera": "Arri Alexa Mini",                "lens": "Leica Summilux-C",                  "format": "Digital 4K"},
    "normal people":             {"camera": "Arri Alexa Mini",                "lens": "Cooke S4",                          "format": "Digital 4K"},
    # ── ANIMATION ──
    "coco":                      {"camera": "Rendered CGI",                   "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    "wall-e":                    {"camera": "Rendered CGI",                   "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    "up":                        {"camera": "Rendered CGI",                   "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    "inside out":                {"camera": "Rendered CGI",                   "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    "your name":                 {"camera": "Digital Animation",              "lens": "Virtual Cameras",                   "format": "Digital Animation"},
    # ── TAMIL / INDIAN CINEMA ──
    "vikram":                    {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "master":                    {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "beast":                     {"camera": "Arri Alexa Mini LF",             "lens": "Cooke S7/i",                        "format": "Digital 4.5K"},
    "jailer":                    {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "leo":                       {"camera": "Arri Alexa 35",                  "lens": "Zeiss Supreme Prime",               "format": "Digital 4K"},
    "vettaiyan":                 {"camera": "Arri Alexa 35",                  "lens": "Panavision Primo",                  "format": "Digital 4K"},
    "kanguva":                   {"camera": "Arri Alexa 35 / IMAX",          "lens": "Panavision Sphero 65",              "format": "IMAX / Digital"},
    "2.0":                       {"camera": "Arri Alexa / Red Epic",          "lens": "Various",                           "format": "Digital / 3D"},
    "baahubali":                 {"camera": "Red Epic Dragon",                "lens": "Zeiss Master Prime",                "format": "Digital 6K"},
    "baahubali 2":               {"camera": "Red Epic Dragon / Weapon",       "lens": "Zeiss Master Prime",                "format": "Digital 6K / 8K"},
    "rrr":                       {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "pushpa":                    {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "kalki 2898 ad":             {"camera": "Arri Alexa 35 / IMAX",          "lens": "Panavision Sphero 65",              "format": "IMAX / Digital"},
    "vinnaithaandi varuvaayaa":  {"camera": "Red One MX",                     "lens": "Zeiss CP.2 Primes",                 "format": "Digital 4K"},
    "ko":                        {"camera": "Arri Alexa",                     "lens": "Zeiss Master Prime",                "format": "Digital"},
    "96":                        {"camera": "Arri Alexa Mini",                "lens": "Leica Summilux-C",                  "format": "Digital 4K"},
    "soorarai pottru":           {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "kaithi":                    {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "karnan":                    {"camera": "Arri Alexa Mini LF",             "lens": "Leica Summilux-C",                  "format": "Digital 4.5K"},
    "ratsasan":                  {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "super deluxe":              {"camera": "Arri Alexa Mini",                "lens": "Cooke S4",                          "format": "Digital 4K"},
    "mersal":                    {"camera": "Arri Alexa XT",                  "lens": "Zeiss Master Prime",                "format": "Digital 3.4K"},
    "bigil":                     {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "varisu":                    {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "thunivu":                   {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "ponniyin selvan":           {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "ponniyin selvan 2":         {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "mani ratnam":               {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    # ── BOLLYWOOD ──
    "lagaan":                    {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "dilwale dulhania le jayenge":{"camera": "35mm Film",                     "lens": "Various Prime Lenses",              "format": "35mm"},
    "3 idiots":                  {"camera": "35mm Film / Digital",            "lens": "Various",                           "format": "35mm / Digital"},
    "dangal":                    {"camera": "Arri Alexa",                     "lens": "Zeiss Master Prime",                "format": "Digital"},
    "pathaan":                   {"camera": "Arri Alexa LF",                  "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "brahmastra":                {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    # ── MISCELLANEOUS ──
    "the florida project":       {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm"},
    "first reformed":            {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm 1.33:1"},
    "uncut gems":                {"camera": "35mm Film",                      "lens": "Panavision C-Series",               "format": "35mm"},
    "good time":                 {"camera": "16mm Film",                      "lens": "Various",                           "format": "16mm"},
    "the lighthouse":            {"camera": "Arriflex 35 BL4s",               "lens": "Leica Summicron-C",                 "format": "35mm B&W 1.19:1"},
    "mid90s":                    {"camera": "16mm Film",                      "lens": "Various",                           "format": "16mm 1.33:1"},
    "waves":                     {"camera": "Arri Alexa Mini LF",             "lens": "Leica Summilux-C",                  "format": "Digital 4.5K"},
    "the power of the dog":      {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "spencer":                   {"camera": "16mm Film",                      "lens": "Zeiss Ultra Prime",                 "format": "16mm"},
    "nightmare alley":           {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "the french dispatch":       {"camera": "35mm Film",                      "lens": "Various Anamorphic",                "format": "35mm Multi-format"},
    "licorice pizza":            {"camera": "35mm Film",                      "lens": "Panavision Anamorphic",             "format": "35mm Anamorphic"},
    "c'mon c'mon":               {"camera": "35mm Film",                      "lens": "Various Prime Lenses",              "format": "35mm B&W"},
    "flee":                      {"camera": "Digital Animation / Archival",   "lens": "Various",                           "format": "Animation / Documentary"},
    "drive my car":              {"camera": "Arri Alexa Mini LF",             "lens": "Zeiss Supreme Prime",               "format": "Digital 4.5K"},
    "memoria":                   {"camera": "Arri Alexa Mini LF",             "lens": "Leica Summilux-C",                  "format": "Digital 4.5K"},
    "titane":                    {"camera": "Arri Alexa Mini",                "lens": "Zeiss Master Prime",                "format": "Digital 4K"},
    "the lost daughter":         {"camera": "Arri Alexa Mini LF",             "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "tick tick boom":            {"camera": "Arri Alexa LF",                  "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
    "being the ricardos":        {"camera": "Arri Alexa LF",                  "lens": "Panavision Primo",                  "format": "Digital 4.5K"},
}

def get_camera(title):
    key = title.lower()
    for k, v in CAMERA_SPECS.items():
        if k in key:
            return v
    return {"camera": "N/A", "lens": "N/A", "format": "N/A"}

# ── QUOTES DATABASE ───────────────────────────────────────────
QUOTES = {
    "interstellar": [
        "We used to look up at the sky and wonder at our place in the stars. Now we just look down and worry about our place in the dirt.",
        "Do not go gentle into that good night. Rage, rage against the dying of the light.",
        "Love is the one thing we're capable of perceiving that transcends dimensions of time and space.",
    ],
    "the dark knight": [
        "Why so serious?",
        "You either die a hero, or you live long enough to see yourself become the villain.",
        "Madness is like gravity. All it takes is a little push.",
    ],
    "fight club": [
        "The things you own end up owning you.",
        "It's only after we've lost everything that we're free to do anything.",
        "You are not your job, you're not how much money you have in the bank.",
    ],
    "pulp fiction": [
        "English, do you speak it?",
        "The path of the righteous man is beset on all sides by the inequities of the selfish.",
        "Personality goes a long way.",
    ],
    "inception": [
        "You mustn't be afraid to dream a little bigger, darling.",
        "An idea is like a virus. Resilient. Highly contagious.",
        "What is the most resilient parasite? An idea.",
    ],
    "parasite": [
        "You know what kind of plan never fails? No plan. No plan at all.",
        "It's so metaphorical.",
    ],
    "the godfather": [
        "I'm gonna make him an offer he can't refuse.",
        "Leave the gun. Take the cannoli.",
        "A man who doesn't spend time with his family can never be a real man.",
    ],
    "schindler's list": [
        "Whoever saves one life, saves the world entire.",
        "Power is when we have every justification to kill, and we don't.",
    ],
    "la la land": [
        "Here's to the ones who dream, foolish as they may seem.",
        "This is the dream. It's conflict and it's compromise.",
    ],
    "blade runner 2049": [
        "All the best memories are hers.",
        "Dying for the right cause is the most human thing we can do.",
    ],
    "arrival": [
        "Language is the foundation of civilization. It is the glue that holds a people together.",
        "If you could see your whole life from start to finish, would you change things?",
    ],
    "her": [
        "The past is just a story we tell ourselves.",
        "I can feel the fear that you carry around and I wish I could make it better.",
    ],
    "no country for old men": [
        "What's the most you ever lost in a coin toss?",
        "You can't stop what's coming. It ain't all waiting on you.",
    ],
    "there will be blood": [
        "I drink your milkshake! I drink it up!",
        "I have a competition in me. I want no one else to succeed.",
    ],
    "2001 a space odyssey": [
        "I'm sorry, Dave. I'm afraid I can't do that.",
        "My God — it's full of stars!",
    ],
    "whiplash": [
        "There are no two words in the English language more harmful than 'good job.'",
        "Were you rushing or were you dragging?",
    ],
    "the revenant": [
        "I ain't afraid to die anymore. I done it already.",
        "As long as you can still grab a breath, you fight.",
    ],
    "mad max fury road": [
        "What a lovely day!",
        "We are not things.",
        "Who killed the world?",
    ],
    "dune": [
        "A great man doesn't seek to lead. He's called to it.",
        "I must not fear. Fear is the mind-killer.",
        "The mystery of life isn't a problem to solve, but a reality to experience.",
    ],
    "oppenheimer": [
        "Now I am become Death, the destroyer of worlds.",
        "Theory will only take you so far.",
    ],
    "everything everywhere all at once": [
        "Of all the places I could be, I just want to be here with you.",
        "The only thing I know is that we have to be kind.",
    ],
    "goodfellas": [
        "As far back as I can remember, I always wanted to be a gangster.",
        "Funny how? Funny like I'm a clown?",
    ],
    "taxi driver": [
        "You talkin' to me?",
        "Someday a real rain will come and wash all the scum off the streets.",
    ],
    "se7en": [
        "What's in the box?",
        "Ernest Hemingway once wrote: 'The world is a fine place and worth fighting for.' I agree with the second part.",
    ],
    "the shining": [
        "Here's Johnny!",
        "All work and no play makes Jack a dull boy.",
    ],
    "oldboy": [
        "Laugh and the world laughs with you. Weep and you weep alone.",
    ],
    "in the mood for love": [
        "He remembers those vanished years, as though looking through a dusty window pane.",
    ],
}

def get_quotes(title):
    key = title.lower()
    for k, v in QUOTES.items():
        if k in key:
            return v
    return []

# ── MOODS ─────────────────────────────────────────────────────
MOODS = [
    {"id": 878,   "name": "Science Fiction", "sub": "Worlds beyond imagination"},
    {"id": 18,    "name": "Drama",            "sub": "Stories that stay with you"},
    {"id": 53,    "name": "Thriller",         "sub": "Edge of your seat"},
    {"id": 10749, "name": "Romance",          "sub": "Love in every form"},
    {"id": 35,    "name": "Comedy",           "sub": "Pure, unfiltered laughter"},
    {"id": 27,    "name": "Horror",           "sub": "Fear as an art form"},
    {"id": 28,    "name": "Action",           "sub": "Relentless momentum"},
    {"id": 99,    "name": "Documentary",      "sub": "Truth, unscripted"},
    {"id": 14,    "name": "Fantasy",          "sub": "The impossible made real"},
    {"id": 80,    "name": "Crime",            "sub": "Morality at its darkest"},
    {"id": 10752, "name": "War",              "sub": "The cost of conflict"},
    {"id": 37,    "name": "Western",          "sub": "Lawless frontiers"},
    {"id": 36,    "name": "History",          "sub": "The world that was"},
    {"id": 10402, "name": "Music",            "sub": "Rhythm and soul"},
    {"id": 9648,  "name": "Mystery",          "sub": "Nothing is as it seems"},
    {"id": 16,    "name": "Animation",        "sub": "Art in motion"},
    {"id": 12,    "name": "Adventure",        "sub": "Beyond the horizon"},
    {"id": 10751, "name": "Family",           "sub": "For every generation"},
]

FILM_CLUBS = [
    {"id": 1,  "name": "The Long Take Society",    "desc": "Devoted to unbroken cinematography and single-shot mastery.",       "members": 4820,  "films_count": 48},
    {"id": 2,  "name": "Criterion Collective",     "desc": "Deep dives into the Criterion Collection and art cinema.",          "members": 9340,  "films_count": 120},
    {"id": 3,  "name": "Midnight Horror Club",     "desc": "Weekly horror screenings and post-film discussions.",               "members": 6210,  "films_count": 89},
    {"id": 4,  "name": "Sci-Fi Symposium",         "desc": "Exploring ideas, futures, and the science behind the fiction.",     "members": 7650,  "films_count": 76},
    {"id": 5,  "name": "Auteur Studies",           "desc": "Director-focused deep dives, one filmmaker per month.",             "members": 3290,  "films_count": 62},
    {"id": 6,  "name": "World Cinema Circle",      "desc": "Films from every country, every language, every culture.",         "members": 5540,  "films_count": 203},
    {"id": 7,  "name": "New Waves",                "desc": "French New Wave, Iranian cinema, Korean New Wave and beyond.",      "members": 2870,  "films_count": 94},
    {"id": 8,  "name": "Cinematography Lab",       "desc": "Frame by frame analysis of the world's most beautiful films.",     "members": 3110,  "films_count": 55},
    {"id": 9,  "name": "The Reel Noir",            "desc": "Classic and neo-noir — shadows, femmes fatales, moral ambiguity.",  "members": 4450,  "films_count": 71},
    {"id": 10, "name": "Animation Appreciation",  "desc": "Pixar, Ghibli, indie animation and the art of the moving drawing.", "members": 8920,  "films_count": 88},
    {"id": 11, "name": "Tamil Cinema Club",        "desc": "Celebrating the rich legacy and modern brilliance of Tamil films.", "members": 12400, "films_count": 156},
    {"id": 12, "name": "Indian Parallel Cinema",  "desc": "The art house tradition from Ray to Kashyap and beyond.",          "members": 3780,  "films_count": 98},
]

DNA_TYPES = {
    "visionary": {
        "title": "The Visionary",
        "desc": "You gravitate toward films that challenge perception and expand the boundaries of what cinema can be. You appreciate technical craft as much as emotional depth.",
        "directors": ["Christopher Nolan", "Denis Villeneuve", "Alfonso Cuarón"],
        "films": ["Interstellar", "Blade Runner 2049", "Arrival"],
    },
    "empath": {
        "title": "The Empath",
        "desc": "Character and emotion drive your viewing. You find yourself drawn to intimate stories, complex relationships, and performances that leave a mark.",
        "directors": ["Wong Kar-wai", "Céline Sciamma", "Barry Jenkins"],
        "films": ["In the Mood for Love", "Past Lives", "Moonlight"],
    },
    "thrill_seeker": {
        "title": "The Thrill Seeker",
        "desc": "Tension is your currency. You live for the films that keep you on the edge of your seat — the heist, the chase, the revelation.",
        "directors": ["David Fincher", "Park Chan-wook", "Bong Joon-ho"],
        "films": ["Parasite", "Oldboy", "Gone Girl"],
    },
    "archivist": {
        "title": "The Archivist",
        "desc": "You understand that cinema is a century-old art form with a rich history. You seek the classics, the overlooked, and the historically significant.",
        "directors": ["Stanley Kubrick", "Akira Kurosawa", "Orson Welles"],
        "films": ["2001: A Space Odyssey", "Seven Samurai", "Citizen Kane"],
    },
    "poet": {
        "title": "The Poet",
        "desc": "Atmosphere over plot. Mood over structure. You're drawn to films that feel more like paintings — slow, deliberate, visually transcendent.",
        "directors": ["Terrence Malick", "Andrei Tarkovsky", "Apichatpong Weerasethakul"],
        "films": ["The Tree of Life", "Stalker", "Uncle Boonmee"],
    },
    "rebel": {
        "title": "The Rebel",
        "desc": "You prefer films that break rules — genre-bending, politically charged, formally experimental, and unapologetically provocative.",
        "directors": ["Jean-Luc Godard", "Lars von Trier", "Gaspar Noé"],
        "films": ["Breathless", "Melancholia", "Enter the Void"],
    },
}

# ── ROUTES ────────────────────────────────────────────────────
@app.route("/")
def index():
    trending = tmdb("/trending/movie/week")["results"][:12]
    featured = trending[0] if trending else None
    popular  = tmdb("/movie/popular")["results"][:8]
    upcoming = tmdb("/movie/upcoming")["results"][:5]
    return render_template("index.html",
        trending=trending, featured=featured,
        popular=popular, upcoming=upcoming,
        moods=MOODS[:10], poster=poster, backdrop=backdrop,
        owner=OWNER)

@app.route("/movie/<int:movie_id>")
def movie_page(movie_id):
    data     = tmdb(f"/movie/{movie_id}", append_to_response="credits,images,videos,keywords,recommendations")
    credits  = data.get("credits", {})
    videos   = data.get("videos", {})
    images   = data.get("images", {})
    recs     = data.get("recommendations", {}).get("results", [])[:8]
    backdrops  = [b for b in images.get("backdrops", []) if b.get("file_path")][:10]
    trailers   = [v for v in videos.get("results", []) if v.get("type") == "Trailer" and v.get("site") == "YouTube"]
    trailer    = trailers[0]["key"] if trailers else None
    cast       = credits.get("cast", [])[:20]
    crew       = credits.get("crew", [])
    director   = next((c["name"] for c in crew if c["job"] == "Director"), "N/A")
    dop        = next((c["name"] for c in crew if c["job"] == "Director of Photography"), "N/A")
    composer   = next((c["name"] for c in crew if c["job"] == "Original Music Composer"), "N/A")
    editor     = next((c["name"] for c in crew if c["job"] == "Editor"), "N/A")
    writer     = next((c["name"] for c in crew if c["job"] in ["Screenplay", "Writer"]), "N/A")
    producer   = next((c["name"] for c in crew if c["job"] == "Producer"), "N/A")
    cam        = get_camera(data.get("title", ""))
    quotes     = get_quotes(data.get("title", ""))
    mins       = data.get("runtime", 0)
    runtime    = f"{mins // 60}h {mins % 60}m" if mins else "N/A"
    imdb_id    = data.get("imdb_id")
    keywords   = data.get("keywords", {}).get("keywords", [])[:12]
    return render_template("movie.html",
        movie=data, backdrops=backdrops, trailer=trailer,
        cast=cast, director=director, dop=dop,
        composer=composer, editor=editor, writer=writer,
        producer=producer, cam=cam, quotes=quotes,
        runtime=runtime, imdb_id=imdb_id,
        keywords=keywords, recommendations=recs,
        poster=poster, backdrop=backdrop, owner=OWNER)

@app.route("/search")
def search():
    q       = request.args.get("q", "")
    results = tmdb("/search/movie", query=q)["results"] if q else []
    return render_template("search.html", results=results, query=q, poster=poster, owner=OWNER)

@app.route("/genre/<int:genre_id>")
def genre(genre_id):
    mood    = next((m for m in MOODS if m["id"] == genre_id), None)
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
    return jsonify({
        "a": {"id": a["id"], "title": a["title"], "poster": poster(a.get("poster_path"), "w342"), "year": (a.get("release_date") or "")[:4], "rating": round(a.get("vote_average", 0), 1)},
        "b": {"id": b["id"], "title": b["title"], "poster": poster(b.get("poster_path"), "w342"), "year": (b.get("release_date") or "")[:4], "rating": round(b.get("vote_average", 0), 1)},
    })

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
    mapping = {
        "visionary":     ["sci-fi", "epic", "technical", "nolan", "villeneuve"],
        "empath":        ["drama", "romance", "character", "emotion", "intimate"],
        "thrill_seeker": ["thriller", "crime", "twist", "tension", "fincher"],
        "archivist":     ["classic", "old", "criterion", "kubrick", "history"],
        "poet":          ["slow", "visual", "atmospheric", "malick", "art"],
        "rebel":         ["experimental", "provocative", "avant", "godard", "rule"],
    }
    for ans in answers:
        for dtype, keywords in mapping.items():
            if any(k in ans.lower() for k in keywords):
                scores[dtype] += 1
    result_type = max(scores, key=scores.get)
    return jsonify(DNA_TYPES[result_type])

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

@app.route("/api/watchlist/info/<int:movie_id>")
def watchlist_info(movie_id):
    data = tmdb(f"/movie/{movie_id}")
    return jsonify({"id": data["id"], "title": data["title"], "year": (data.get("release_date") or "")[:4], "rating": round(data.get("vote_average", 0), 1), "poster": poster(data.get("poster_path"), "w342"), "overview": data.get("overview", "")})

@app.route("/api/search")
def api_search():
    q    = request.args.get("q", "")
    data = tmdb("/search/movie", query=q) if q else {"results": []}
    out  = [{"id": m["id"], "title": m["title"], "year": (m.get("release_date") or "")[:4], "rating": round(m.get("vote_average", 0), 1), "poster": poster(m.get("poster_path"), "w92")} for m in data.get("results", [])[:8]]
    return jsonify(out)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
