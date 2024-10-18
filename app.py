import streamlit as st
import time
import requests
import pandas as pd
import pydeck as pdk

# Functie voor omgekeerde geocodering
def reverse_geocoding_app():
    st.title("Omgekeerde Geocodering")
    
    coords_input = st.text_area("Voer GPS-coördinaten in als een lijst van tuples (lat, lon):", 
                                "(52.377956, 4.897070), (52.378456, 4.897570)")
    
    if st.button("Bereken middelpunt en vind adres"):
        try:
            # Omzetten van de ingevoerde tekst naar een lijst van tuples
            coordinates = eval(coords_input)
            center = calculate_center(coordinates)
            st.write(f"Middelpunt: {center}")
            
            address_details, display_name = reverse_geocode_nominatim(center[0], center[1])
            if address_details:
                formatted_address = format_address(address_details)
                st.write(f"Het gevonden adres is: {formatted_address}")
            else:
                st.write(display_name)

            # Toon het middelpunt op de kaart met een semi-transparante stip
            map_data = pd.DataFrame({
                'lat': [center[0]],
                'lon': [center[1]],
            })
            
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                    latitude=center[0],
                    longitude=center[1],
                    zoom=16,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=map_data,
                        get_position='[lon, lat]',
                        get_radius=100,
                        get_color=[255, 0, 0, 128],  # Semi-transparante rode stip (RGBA)
                        pickable=True
                    ),
                ],
            ))

        except Exception as e:
            st.error(f"Er is een fout opgetreden: {e}")

# Functie om huidige tijd te tonen
def time_app():
    st.title("Huidige Tijd")
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    st.write(f"De huidige tijd is: {current_time}")
    st.write("De tijd wordt elke seconde bijgewerkt.")
    
    # Dynamisch updaten van de tijd elke seconde
    while True:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        st.write(f"Huidige tijd: {current_time}")
        time.sleep(1)

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
    params = {'lat': lat, 'lon': lng, 'format': 'json', 'addressdetails': 1}
    headers = {'User-Agent': 'Streamlit app'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'error' not in data:
            return data['address'], data['display_name']
        else:
            return None, "Geen adres gevonden"
    else:
        return None, f"Foutcode: {response.status_code}"

# Functie om het adres te formatteren
def format_address(address_details):
    straat = address_details.get('road', 'Onbekende straat')
    huisnummer = address_details.get('house_number', '')
    postcode = address_details.get('postcode', 'Onbekende postcode')
    woonplaats = address_details.get('city', address_details.get('town', address_details.get('village', 'Onbekende plaats')))
    formatted_address = f"{straat} {huisnummer}, {postcode}, {woonplaats}"
    return formatted_address

# Streamlit app startpunt met zijbalk voor applicatiekeuze
st.sidebar.title("Navigatie")
app_choice = st.sidebar.selectbox("Kies een applicatie", ["Omgekeerde Geocodering", "Huidige Tijd"])

# Keuze van applicatie
if app_choice == "Omgekeerde Geocodering":
    reverse_geocoding_app()
elif app_choice == "Huidige Tijd":
    time_app()
