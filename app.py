import streamlit as st
import requests
import pandas as pd

# Functie om het middelpunt van GPS-coördinaten te berekenen
def calculate_center(coordinates):
    latitudes = [coord[0] for coord in coordinates]
    longitudes = [coord[1] for coord in coordinates]
    
    center_lat = sum(latitudes) / len(latitudes)
    center_lng = sum(longitudes) / len(longitudes)
    
    return (center_lat, center_lng)

# Functie voor omgekeerde geocodering met Nominatim
def reverse_geocode_nominatim(lat, lng):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lng,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {'User-Agent': 'Streamlit app'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'error' not in data:
            return data['display_name']
        else:
            return "Geen adres gevonden"
    else:
        return f"Foutcode: {response.status_code}"

# Streamlit app
st.title("Omgekeerde Geocodering met GPS-coördinaten")

# Invoerveld voor GPS-coördinaten
coords_input = st.text_area("Voer GPS-coördinaten in als een lijst van tuples (lat, lon):", 
                            "(52.377956, 4.897070), (52.378456, 4.897570), (52.378956, 4.898070), (52.379456, 4.898570)")

# Knop om actie te triggeren
if st.button("Bereken middelpunt en vind adres"):
    try:
        # Omzetten van de ingevoerde tekst naar een lijst van tuples
        coordinates = eval(coords_input)
        
        # Bereken het middelpunt van de ingevoerde coördinaten
        center = calculate_center(coordinates)
        st.write(f"Middelpunt: {center}")
        
        # Roep de Nominatim API aan voor het adres
        address = reverse_geocode_nominatim(center[0], center[1])
        st.write(f"Het gevonden adres is: {address}")
        
        # Toon het middelpunt op de kaart
        df = pd.DataFrame({
            'lat': [center[0]],
            'lon': [center[1]]
        })
        st.map(df)
        
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
