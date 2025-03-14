from flask import Flask, request, render_template
import pandas as pd
import math

app = Flask(__name__)

# Dictionnaire complet des ligues et equipes
ligues = {
    "Premier League": [
        "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace",
        "Everton", "Fulham", "Ipswich Town", "Leicester City", "Liverpool", "Manchester City",
        "Manchester United", "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham Hotspur",
        "West Ham United", "Wolverhampton Wanderers"
    ],
    "LaLiga": [
        "Alavés", "Athletic Bilbao", "Atlético Madrid", "Barcelona", "Betis", "Celta Vigo", "Espanyol",
        "Getafe", "Girona", "Las Palmas", "Leganés", "Mallorca", "Osasuna", "Rayo Vallecano",
        "Real Madrid", "Real Sociedad", "Sevilla", "Valencia", "Valladolid", "Villarreal"
    ],
    "Serie A": [
        "Atalanta", "Bologna", "Cagliari", "Como", "Empoli", "Fiorentina", "Genoa", "Inter Milan",
        "Juventus", "Lazio", "Lecce", "AC Milan", "Monza", "Napoli", "Parma", "Roma", "Torino",
        "Udinese", "Venezia", "Verona"
    ],
    "Bundesliga": [
        "Augsburg", "Bayern Munich", "Bochum", "Borussia Dortmund", "Borussia Mönchengladbach", "Bremen",
        "Eintracht Frankfurt", "Freiburg", "Heidenheim", "Hoffenheim", "Holstein Kiel", "Mainz",
        "RB Leipzig", "St. Pauli", "Stuttgart", "Union Berlin", "Bayer Leverkusen", "Wolfsburg"
    ],
    "Ligue 1": [
        "Angers", "Auxerre", "Brest", "Le Havre", "Lens", "Lille", "Lyon", "Marseille", "Monaco",
        "Montpellier", "Nantes", "Nice", "PSG", "Reims", "Rennes", "Saint-Étienne", "Strasbourg", "Toulouse"
    ],
    "Ligue des Champions": [
        "AC Milan", "Arsenal", "AS Monaco", "Aston Villa", "Atalanta", "Atlético Madrid", "Barcelona",
        "Bayern Munich", "Bayer Leverkusen", "Benfica", "Bologna", "Borussia Dortmund", "Brest", "Celtic",
        "Club Brugge", "Crvena Zvezda", "Dinamo Zagreb", "Feyenoord", "Girona", "Inter Milan", "Juventus",
        "Lille", "Liverpool", "Manchester City", "PSG", "Porto", "RB Leipzig", "Real Madrid", "Salzburg",
        "Shakhtar Donetsk", "Slovan Bratislava", "Sparta Prague", "Sporting CP", "Sturm Graz", "VfB Stuttgart",
        "Young Boys"
    ],
    "Ligue Europa": [
        "Ajax", "Anderlecht", "Athletic Bilbao", "AZ Alkmaar", "Bodo/Glimt", "Braga", "Dynamo Kyiv",
        "Elfsborg", "FCSB", "Fenerbahçe", "Ferencvaros", "Galatasaray", "Hoffenheim", "Lazio",
        "Ludogorets Razgrad", "Lyon", "Maccabi Tel Aviv", "Malmo FF", "Manchester United", "Midtjylland",
        "Nice", "Olympiacos", "PAOK", "Porto", "Qarabag", "Rangers", "Real Sociedad", "RFS", "Roma",
        "Slavia Prague", "Tottenham Hotspur", "Twente", "Union Saint-Gilloise", "Viktoria Plzen",
        "Eintracht Frankfurt", "Besiktas"
    ]
}

# URLs FBref pour chaque ligue (stats 2024-2025)
urls = {
    "Premier League": "https://fbref.com/en/comps/9/Premier-League-Stats",
    "LaLiga": "https://fbref.com/en/comps/12/La-Liga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/Serie-A-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/Bundesliga-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/Ligue-1-Stats",
    "Ligue des Champions": "https://fbref.com/en/comps/8/Champions-League-Stats",
    "Ligue Europa": "https://fbref.com/en/comps/19/Europa-League-Stats"
}

# Scraping FBref
def obtenir_stats_equipe(nom_equipe, ligue):
    url = urls[ligue]
    try:
        dfs = pd.read_html(url)
        stats_table = dfs[0]  # Premiere table contient les stats d'equipe
        equipe_stats = stats_table[stats_table["Squad"] == nom_equipe]
        if not equipe_stats.empty:
            buts_marques = equipe_stats["GF"].values[0] / equipe_stats["MP"].values[0]  # Buts par match
            buts_encaisses = equipe_stats["GA"].values[0] / equipe_stats["MP"].values[0]
            return float(buts_marques), float(buts_encaisses)
    except:
        pass
    return 1.5, 1.5  # Valeur par defaut si echec

# Loi de Poisson
def poisson_proba(buts_moyens, k):
    return (math.exp(-buts_moyens) * (buts_moyens ** k)) / math.factorial(k)

def calculer_proba_over(buts_moy_a, buts_moy_b, seuil):
    buts_attendus = buts_moy_a + buts_moy_b
    proba_sous_seuil = sum(poisson_proba(buts_attendus, k) for k in range(int(seuil + 1)))
    return (1 - proba_sous_seuil) * 100

@app.route("/", methods=["GET", "POST"])
def home():
    allowed_hosts = ["lespronosdedavy.com", "pronostics-over.onrender.com"]  # Autorise Render pour les tests
    if request.host not in allowed_hosts:
        return "Veuillez accéder à cet outil via lespronosdedavy.com", 403
    # Le reste du code reste inchangé
    if request.method == "POST":
        ligue = request.form["ligue"]
        equipe_a = request.form["equipe_a"]
        equipe_b = request.form["equipe_b"]
        seuil = float(request.form["seuil"].replace("Over ", ""))
        
        if equipe_a == equipe_b:
            return render_template("index.html", ligues=ligues, equipes=ligues[ligue], selected_ligue=ligue, erreur="Choisissez deux equipes differentes !")
        
        buts_marques_a, buts_encaisses_a = obtenir_stats_equipe(equipe_a, ligue)
        buts_marques_b, buts_encaisses_b = obtenir_stats_equipe(equipe_b, ligue)
        buts_moy_a = (buts_marques_a + buts_encaisses_b) / 2
        buts_moy_b = (buts_marques_b + buts_encaisses_a) / 2
        
        proba = calculer_proba_over(buts_moy_a, buts_moy_b, seuil)
        couleur = "green" if proba > 60 else "orange"
        
        return render_template(
            "result.html",
            equipe_a=equipe_a,
            equipe_b=equipe_b,
            proba=proba,
            seuil=f"Over {seuil}",
            couleur=couleur,
            ligue=ligue
        )
    return render_template("index.html", ligues=ligues, equipes=ligues["Premier League"], selected_ligue="Premier League")

if __name__ == "__main__":
    app.run(debug=True)
