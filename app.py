import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

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
            return data['address'], data['display_name']
        else:
            return None, "Geen adres gevonden"
    else:
        return None, f"Foutcode: {response.status_code}"

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
        address_details, display_name = reverse_geocode_nominatim(center[0], center[1])
        
        if address_details:
            # Toon het volledige adres, inclusief huisnummer
            st.write(f"Het gevonden adres is: {display_name}")
            if 'house_number' in address_details:
                st.write(f"Huisnummer: {address_details['house_number']}")
            else:
                st.write("Huisnummer niet beschikbaar.")
        else:
            st.write(display_name)
        
        # Toon het middelpunt op de kaart met inzoommogelijkheid via pydeck
        map_df = pd.DataFrame({
            'lat': [center[0]],
            'lon': [center[1]]
        })
        
        # Stel de zoom in
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=center[0],
                longitude=center[1],
                zoom=16,  # Stel zoomniveau in
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=map_df,
                    get_position='[lon, lat]',
                    get_radius=100,
                    get_color=[255, 0, 0],
                    pickable=True
                ),
            ],
        ))
        
    except Exception as e:
        st.error(f"Er is een fout opgetreden: {e}")
