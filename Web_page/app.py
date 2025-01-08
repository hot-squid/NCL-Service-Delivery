import streamlit as st
import streamlit.components.v1 as components
import requests

st.title("NCL Services")

# Tabs for displaying maps
tab1, tab2 = st.tabs(["Service Locations", "Choropleth"])

# Function to fetch HTML content from a URL
def fetch_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"<p>Error: Unable to fetch HTML content (status code {response.status_code})</p>"
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"

# Display the service locations map
with tab1:
    st.subheader("Service Locations")
    service_map_url = "https://raw.githubusercontent.com/hot-squid/NCL-Service-Delivery/main/Web_page/Basic.html"
    service_map_html = fetch_html_content(service_map_url)
    components.html(service_map_html, height=500)

# Display the cyclist casualties choropleth map
with tab2:
    st.subheader("ADD: Choropleth of cycling incidents 2018-2022")
    choropleth_map_url = "https://raw.githubusercontent.com/hot-squid/NCL-Service-Delivery/main/Web_page/cloro.html"
    choropleth_map_html = fetch_html_content(choropleth_map_url)
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
