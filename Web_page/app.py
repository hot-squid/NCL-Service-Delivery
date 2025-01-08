import streamlit as st
import streamlit.components.v1 as components

st.title("NCL Services")

# Tabs for displaying maps
tab1, tab2 = st.tabs(["Service Locations", "Choropleth"])

# Display the service locations map
with tab1:
    st.subheader("Service Locations")
    with open(https://raw.githubusercontent.com/hot-squid/NCL-Service-Delivery/main/Web_page/Basic.html", "r") as f:
        service_map_html = f.read()
    components.html(service_map_html, height=500)

# Display the cyclist casualties choropleth map
with tab2:
    st.subheader("ADD: Choropleth of cycling incidents 2018-2022")
    with open("https://raw.githubusercontent.com/hot-squid/NCL-Service-Delivery/main/Web_page/cloro.html", "r") as f:
        choropleth_map_html = f.read()
    components.html(choropleth_map_html, height=500)

st.info('''Demo of basic Geopandas and Streamlit functions for mental health services across
North Central London. 

Add-ons/research avenues:
- Relevant demographics/choropleths (e.g. SEND population/MH crisis call figures)
- Travel time forecasting (how long do some families travel?)
- Service allocation analysis (Are services accesible?)
- New service planning (where would be best to place new service?)
- Public transport networks (are there decent public transport routes?)
- More service detail (e.g. contact details, image, information, type of service)

Note - postcodes/addresses for some services pulled from LLMs and require verification
before concrete research.''')
