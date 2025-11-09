#####################################################################
# IMPORTATION DES MODULES
#####################################################################

from flask import Flask, make_response, render_template, request, jsonify
import sqlite3
import os
import folium
import pandas as pd
from io import BytesIO
import base64

import requests
from model import *

#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration d'application Flask
app = Flask(__name__)

# Assure la compatibilité de Matplotlib avec Flask



#####################################################################
# ROUTES VERS LES VUES
#####################################################################


# Route pour la page d'accueil
@app.route('/')
def accueil():
    # Affichage du template
    return render_template('index.html')

@app.route('/carte', methods=['GET', 'POST'])
def carte():
    departements = get_departements()
    station_count = None
    selected_departement = None
    
    if request.method == 'POST':
        selected_departement = request.form['select_departement']
        code_departement = get_code_departement(selected_departement)
        station_count = get_station_count(code_departement)
    
    return render_template('carte_index.html', departements=departements, station_count=station_count, selected_departement=selected_departement)

# Route pour la page d'accueil
@app.route('/carte_svg')
def carte_svg():
    # Affichage du template
    return render_template('carte_svg.html')

# Route pour la page d'accueil
@app.route('/apropos')
def apropos():
    return render_template('A_propos.html')

# Route pour la page d'accueil
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route pour la page d'accueil
@app.route('/filtres')
def filtres():
    return render_template('filtres_index.html')

# Route pour la page d'analyse
@app.route('/analyses', methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        nom_commune = request.form.get('nom_commune', '')
        nom_region = request.form.get('nom_region', '')
        nom_departement = request.form.get('nom_departement', '')
        date_prelevement = request.form.get('date_prelevement', '')

        # Créez une réponse
        response = make_response(render_template('analyse.html', analyses=data['data'], current_page=page, total_pages=total_pages, regions=get_regions(), departements=get_departements(), communes=get_communes()))

        # Enregistrez les données du formulaire dans les cookies
        response.set_cookie('nom_commune', nom_commune)
        response.set_cookie('nom_region', nom_region)
        response.set_cookie('nom_departement', nom_departement)
        response.set_cookie('date_prelevement', date_prelevement)
        response.set_cookie('page', str(page))
        return response
    else:
        page = request.args.get('page', 1, type=int)
        nom_commune = request.args.get('nom_commune', '')
        nom_region = request.args.get('nom_region', '')
        nom_departement = request.args.get('nom_departement', '')
        date_prelevement = request.args.get('date_prelevement', '')

        code_commune = get_code_commune(nom_commune)
        code_region = get_code_region(nom_region)
        code_departement = get_code_departement(nom_departement)

        params = ''
        if page:
            params += f'page={page}&'
        if code_commune:
            params += f'code_commune={code_commune}&'
        if code_region:
            params += f'code_region={code_region}&'
        if code_departement:
            params += f'code_departement={code_departement}&'
        if date_prelevement:
            params += f'date_debut_prelevement={date_prelevement}&'

        url = f'https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/analyse_pc?{params}'
        response = requests.get(url)
        data = response.json()

        regions = get_regions()
        departements = get_departements()
        communes = get_communes()

        # Extrait le nombre total de pages à partir de l'URL de la dernière page
        last_page_url = data.get('last', '')
        if last_page_url:
            total_pages = int(last_page_url.split('page=')[1].split('&')[0])
        else:
            total_pages = 1

        return render_template('analyse.html', analyses=data['data'], current_page=page, total_pages=total_pages, regions=regions, departements=departements, communes=communes)


# Route pour la page d'analyse
@app.route('/station', methods=['GET', 'POST'])
def station():
    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        nom_commune = request.form.get('nom_commune', '')
        nom_region = request.form.get('nom_region', '')
        nom_departement = request.form.get('nom_departement', '')
        date_prelevement = request.form.get('date_prelevement', '')

        # Créez une réponse
        response = make_response(render_template('station.html', analyses=data['data'], current_page=page, total_pages=total_pages, regions=get_regions(), departements=get_departements(), communes=get_communes()))

        # Enregistrez les données du formulaire dans les cookies
        response.set_cookie('nom_commune', nom_commune)
        response.set_cookie('nom_region', nom_region)
        response.set_cookie('nom_departement', nom_departement)
        response.set_cookie('date_prelevement', date_prelevement)
        response.set_cookie('page', str(page))
        return response
    else:
        page = request.args.get('page', 1, type=int)
        nom_commune = request.args.get('nom_commune', '')
        nom_region = request.args.get('nom_region', '')
        nom_departement = request.args.get('nom_departement', '')
        date_prelevement = request.args.get('date_prelevement', '')

        code_commune = get_code_commune(nom_commune)
        code_region = get_code_region(nom_region)
        code_departement = get_code_departement(nom_departement)

        params = ''
        if page:
            params += f'page={page}&'
        if code_commune:
            params += f'code_commune={code_commune}&'
        if code_region:
            params += f'code_region={code_region}&'
        if code_departement:
            params += f'code_departement={code_departement}&'
        if date_prelevement:
            params += f'date_debut_prelevement={date_prelevement}&'

        url = f'https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/station_pc?{params}'
        response = requests.get(url)
        data = response.json()

        regions = get_regions()
        departements = get_departements()
        communes = get_communes()

        # Extrait le nombre total de pages à partir de l'URL de la dernière page
        last_page_url = data.get('last', '')
        if last_page_url:
            total_pages = int(last_page_url.split('page=')[1].split('&')[0])
        else:
            total_pages = 1

        return render_template('station.html', stations=data['data'], current_page=page, total_pages=total_pages, regions=regions, departements=departements, communes=communes)

# Route pour la page d'opérations
@app.route('/operations', methods=['GET', 'POST'])
def operations():
    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        nom_commune = request.form.get('nom_commune', '')
        nom_region = request.form.get('nom_region', '')
        nom_departement = request.form.get('nom_departement', '')
        date_prelevement = request.form.get('date_prelevement', '')

        # Créez une réponse
        response = make_response(render_template('operations.html', analyses=data['data'], current_page=page, total_pages=total_pages, regions=get_regions(), departements=get_departements(), communes=get_communes()))

        # Enregistrez les données du formulaire dans les cookies
        response.set_cookie('nom_commune', nom_commune)
        response.set_cookie('nom_region', nom_region)
        response.set_cookie('nom_departement', nom_departement)
        response.set_cookie('date_prelevement', date_prelevement)
        response.set_cookie('page', str(page))
        return response
    else:
        page = request.args.get('page', 1, type=int)
        nom_commune = request.args.get('nom_commune', '')
        nom_region = request.args.get('nom_region', '')
        nom_departement = request.args.get('nom_departement', '')
        date_prelevement = request.args.get('date_prelevement', '')

        code_commune = get_code_commune(nom_commune)
        code_region = get_code_region(nom_region)
        code_departement = get_code_departement(nom_departement)

        params = ''
        if page:
            params += f'page={page}&'
        if code_commune:
            params += f'code_commune={code_commune}&'
        if code_region:
            params += f'code_region={code_region}&'
        if code_departement:
            params += f'code_departement={code_departement}&'
        if date_prelevement:
            params += f'date_debut_prelevement={date_prelevement}&'

        url = f'https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/operation_pc?{params}'
        response = requests.get(url)
        data = response.json()

        regions = get_regions()
        departements = get_departements()
        communes = get_communes()

        # Extrait le nombre total de pages à partir de l'URL de la dernière page
        last_page_url = data.get('last', '')
        if last_page_url:
            total_pages = int(last_page_url.split('page=')[1].split('&')[0])
        else:
            total_pages = 1

        return render_template('operations.html', operations=data['data'], current_page=page, total_pages=total_pages, regions=regions, departements=departements, communes=communes)

# Route pour la page d'analyse
@app.route('/conditions', methods=['GET', 'POST'])
def conditions():
    if request.method == 'POST':
        page = request.form.get('page', 1, type=int)
        nom_commune = request.form.get('nom_commune', '')
        nom_region = request.form.get('nom_region', '')
        nom_departement = request.form.get('nom_departement', '')
        date_prelevement = request.form.get('date_prelevement', '')

        # Créez une réponse
        response = make_response(render_template('conditions.html', analyses=data['data'], current_page=page, total_pages=total_pages, regions=get_regions(), departements=get_departements(), communes=get_communes()))

        # Enregistrez les données du formulaire dans les cookies
        response.set_cookie('nom_commune', nom_commune)
        response.set_cookie('nom_region', nom_region)
        response.set_cookie('nom_departement', nom_departement)
        response.set_cookie('date_prelevement', date_prelevement)
        response.set_cookie('page', str(page))
        return response
    else:
        page = request.args.get('page', 1, type=int)
        nom_commune = request.args.get('nom_commune', '')
        nom_region = request.args.get('nom_region', '')
        nom_departement = request.args.get('nom_departement', '')
        date_prelevement = request.args.get('date_prelevement', '')

        code_commune = get_code_commune(nom_commune)
        code_region = get_code_region(nom_region)
        code_departement = get_code_departement(nom_departement)

        params = ''
        if page:
            params += f'page={page}&'
        if code_commune:
            params += f'code_commune={code_commune}&'
        if code_region:
            params += f'code_region={code_region}&'
        if code_departement:
            params += f'code_departement={code_departement}&'
        if date_prelevement:
            params += f'date_debut_prelevement={date_prelevement}&'

        url = f'https://hubeau.eaufrance.fr/api/v2/qualite_rivieres/condition_environnementale_pc?{params}'
        response = requests.get(url)
        data = response.json()

        regions = get_regions()
        departements = get_departements()
        communes = get_communes()

        # Extrait le nombre total de pages à partir de l'URL de la dernière page
        last_page_url = data.get('last', '')
        if last_page_url:
            total_pages = int(last_page_url.split('page=')[1].split('&')[0])
        else:
            total_pages = 1

        return render_template('conditions.html', conditions=data['data'], current_page=page, total_pages=total_pages, regions=regions, departements=departements, communes=communes)


@app.route('/get_departements')
def get_departements_by_region():
    region_nom = request.args.get('region')
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    if region_nom:
        id_region = get_id_region(region_nom)
        cursor.execute("""
            SELECT DISTINCT d.nom_departement
            FROM departement d
            JOIN station s ON s.id_departement = d.id_departement
            WHERE s.id_region = ?
        """, (id_region,))
    else:
        cursor.execute("SELECT DISTINCT nom_departement FROM departement")
    departements = cursor.fetchall()
    conn.close()
    departements = [{"nom": nom_departement[0]} for nom_departement in departements]
    return jsonify(departements)

@app.route('/get_communes')
def get_communes_by_departement():
    departement_nom = request.args.get('departement')
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    if departement_nom:
        id_departement = get_id_departement(departement_nom)
        cursor.execute("""
            SELECT DISTINCT c.nom_commune
            FROM commune c
            JOIN station s ON s.id_commune = c.id_commune
            WHERE s.id_departement = ?
        """, (id_departement,))
    else:
        cursor.execute("SELECT DISTINCT nom_commune FROM commune")
    communes = cursor.fetchall()
    conn.close()
    communes = [{"nom": nom_commune[0]} for nom_commune in communes]
    return jsonify(communes)

@app.route('/map')
def map():
    communes = get_communes()
    initial_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}', 
                     attr='Google', 
                     name='Google Maps', 
                     overlay=False, 
                     control=True).add_to(initial_map)
    folium.LayerControl().add_to(initial_map)
    initial_map_html = initial_map._repr_html_()
    return render_template('map_index.html', communes=communes, initial_map_html=initial_map_html, show_square=False, stations=[])

@app.route('/map_post', methods=['POST'])
def map_post():
    nom_commune = request.form['commune']  # Récupérer la commune sélectionnée
    radius_km = float(request.form['radius'])
    center = get_commune_center(nom_commune)
    
    if not center:
        return "Commune non trouvée", 404

    coordinates = get_coordinates_within_radius(center, radius_km)

    mymap = folium.Map(location=center, zoom_start=10)
    folium.TileLayer('https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}', 
                     attr='Google', 
                     name='Google Maps', 
                     overlay=False, 
                     control=True).add_to(mymap)
    folium.LayerControl().add_to(mymap)

    stations = []
    for coord in coordinates:
        lat, lon, loc = coord
        stations.append(loc)
        icon = folium.Icon(color='green', icon='tint')
        folium.Marker([lat, lon], popup=loc, icon=icon).add_to(mymap)

    map_html = mymap._repr_html_()
    return render_template('map_index.html', communes=get_communes(), initial_map_html=map_html, show_square=True, stations=stations, selected_commune=nom_commune)

@app.route('/station_details', methods=['POST'])
def station_details():
    data = request.get_json()
    nom_station = data.get('station_name')
    details = get_station_details(nom_station)
    if details:
        return jsonify(details)
    else:
        return jsonify({'error': 'Station non trouvée'}), 404

@app.route('/update_departement_info', methods=['POST'])
def update_departement_info():
    departement_name = request.form.get('departement_name')
    print(departement_name)
    # Faites quelque chose avec le nom du département, par exemple enregistrez-le dans une variable de session, etc.
    return 'Informations du département mises à jour avec succès !'

#####################################################################
# POINT D'ENTREE DU PROGRAMME
#####################################################################

if __name__ == '__main__':
    app.run(debug=True)