import sqlite3
from geopy.distance import geodesic

DATABASENAME = 'SAE_BASE.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASENAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_regions():
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_region, nom_region FROM region")
    regions = cursor.fetchall()
    conn.close()
    # Filtrer les départements qui ont des noms et des codes valides
    regions = [(code, nom) for code, nom in regions if code is not None and nom is not None]
    return regions

def get_departements():
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_departement, nom_departement FROM departement")
    departements = cursor.fetchall()
    conn.close()
    # Filtrer les départements qui ont des noms et des codes valides
    departements = [(code, nom) for code, nom in departements if code is not None and nom is not None]
    return departements

def get_communes():
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_commune, nom_commune FROM commune")
    communes = cursor.fetchall()
    conn.close()
    # Filtrer les départements qui ont des noms et des codes valides
    communes = [(code, nom) for code, nom in communes if code is not None and nom is not None]
    return communes

def get_nom_departement(code_departement):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nom_departement FROM departement WHERE code_departement=?", (code_departement,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def get_code_departement(nom_departement):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_departement FROM departement WHERE nom_departement=?", (nom_departement,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def get_code_region(nom_region):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_region FROM region WHERE nom_region=?", (nom_region,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def get_code_commune(nom_commune):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT code_commune FROM commune WHERE nom_commune=?", (nom_commune,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def get_id_region(nom_region):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id_region FROM region WHERE nom_region=?", (nom_region,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_id_departement(nom_departement):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id_departement FROM departement WHERE nom_departement=?", (nom_departement,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_departement_center(code_departement):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude FROM coordonnees c JOIN station s ON c.id_coordonnees = s.id_coordonnees WHERE s.id_departement=?", (code_departement,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return (result[0], result[1])
    else:
        return None

def get_station_count(code_departement):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM station
        WHERE id_departement = (
            SELECT id_departement
            FROM departement
            WHERE code_departement = ?
        )
    """, (code_departement,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0

def get_commune_center(nom_commune):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(c.latitude), AVG(c.longitude) FROM coordonnees c JOIN station s ON c.id_coordonnees = s.id_coordonnees JOIN commune cm ON s.id_commune = cm.id_commune WHERE cm.nom_commune = ?", (nom_commune,))
    result = cursor.fetchone()
    conn.close()
    return (result[0], result[1]) if result else None

def get_coordinates_within_radius(center, radius_km):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude, nom_station FROM coordonnees JOIN station ON station.id_coordonnees = coordonnees.id_coordonnees")
    coordinates = cursor.fetchall()
    conn.close()

    within_radius = []
    for lat, lon, loc in coordinates:
        if geodesic(center, (lat, lon)).kilometers <= radius_km:
            within_radius.append((lat, lon, loc))
    return within_radius

def get_station_details(nom_station):
    conn = sqlite3.connect(DATABASENAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.code_station, s.lien_station, s.date_creation, s.date_maj, s.date_arret, s.nom_bassin, s.lien_bassin,
               ce.nom_cours_eau, ce.lien_cours_eau
        FROM station s
        JOIN cours_eau ce ON s.id_cours_eau = ce.id_cours_eau
        WHERE s.nom_station = ?
    """, (nom_station,))
    row = cursor.fetchone()
    conn.close()

    if row:
        details = {
            'code_station': row[0] if row[0] else 'Inconnu',
            'lien_station': row[1] if row[1] else 'Inconnu',
            'date_creation': row[2] if row[2] else 'Inconnu',
            'date_maj': row[3] if row[3] else 'Inconnu',
            'date_arret': row[4] if row[4] else 'Inconnu',
            'nom_bassin': row[5] if row[5] else 'Inconnu',
            'lien_bassin': row[6] if row[6] else 'Inconnu',
            'nom_cours_eau': row[7] if row[7] else 'Inconnu',
            'lien_cours_eau': row[8] if row[8] else 'Inconnu'
        }
        return details
    return None
