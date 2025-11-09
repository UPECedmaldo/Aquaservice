import sqlite3
import pandas as pd
import folium
import json
import requests
from IPython.display import display

# Étape 1: Connexion à la base de données SQLite et extraction des données
conn = sqlite3.connect("SAE_BASE.db")
query = "SELECT * FROM departement"
departements = pd.read_sql_query(query, conn)

# Étape 2: Télécharger le fichier GeoJSON des départements français métropolitains et d'outre-mer
url_departements = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
response_departements = requests.get(url_departements)
geojson_departements = response_departements.json()

# Télécharger le fichier GeoJSON des régions françaises, y compris les régions d'outre-mer
url_regions = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
response_regions = requests.get(url_regions)
geojson_regions = response_regions.json()

# Étape 3: Créer une carte Folium
location = [47, 1]  # Position centrale sur la France
zoom = 6  # Niveau de zoom initial
tiles = 'cartodbpositron'  # Style de la carte

Carte = folium.Map(location=location, zoom_start=zoom, tiles=tiles)

# Étape 4: Ajouter les contours des départements avec des couleurs basées sur code_departement
folium.GeoJson(
    geojson_departements,
    name='Départements',
    style_function=lambda feature: {
        'fillColor': '#b0fc97',  
        'color': 'black',
        'weight': 2,    
        'dashArray': '5, 5',
        'fillOpacity': 0.5,
    },
    highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.8},
    tooltip=folium.GeoJsonTooltip(fields=['nom'], aliases=['Nom:'])
).add_to(Carte)

# Ajouter les contours des régions d'outre-mer
folium.GeoJson(
    geojson_regions,
    name='Régions Outre-Mer',
    style_function=lambda feature: {
        'fillColor': '#b0fc97' if feature['properties']['nom'] in ['Guadeloupe', 'Martinique', 'Guyane', 'La Réunion', 'Mayotte'] else 'none',  
        'color': 'black',
        'weight': 2,    
        'dashArray': '5, 5',
        'fillOpacity': 0.5,
    },
    highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.8},
    tooltip=folium.GeoJsonTooltip(fields=['nom'], aliases=['Nom:'])
).add_to(Carte)

# Affichage de la carte dans un notebook Jupyter
display(Carte)

# Sauvegarde de la carte en HTML
Carte.save('templates/carte_svg.html')
