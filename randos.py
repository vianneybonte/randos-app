import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import  json, requests
pd.options.mode.chained_assignment = None  # default='warn'

st.title('Randonnons !')

st.markdown("""
Pas d'idée de randos autour de Grenoble ? Pas de soucis !'
* **Data source:** https://www.data.gouv.fr/fr/datasets/balades-dans-les-massifs-autour-de-grenoble/.
* **Auteur** : Vianney BONTE
* **Python libraries:** pandas, streamlit, plotly

""")

@st.cache
def load_data():
    url = 'https://entrepot.metropolegrenoble.fr/opendata/38185-GRE/Environnement/json/balade.json'
    resp = requests.get(url, verify=False)
    dict_randos = json.loads(resp.text)
    df_randos = pd.json_normalize(dict_randos)
    return df_randos 

df_randos = load_data()  

# Filtering datas
liste_col = ['idtf', 'libelle', 'resume', 'depart', 'acces', 'itineraire',
             'cartographie', 'difficulte', 'passage_difficile', 'passage_vertigineux', 
             'probleme_orientation', 'duree', 'denivellee', 'altitude', 'temps_trajet',
             'transport', 'materiel', 'famille', 'lac', 'refuge', 'activite.libelle', 
             'massif.libelle', 'adresse.libelle', 'adresse.latitude', 'adresse.longitude']
df_randos = df_randos[liste_col]

df_randos['duree'] = df_randos['duree'].str.replace('h','.')
df_randos['famille'] = df_randos['famille'].replace(True,'Famille')
df_randos['famille'] = df_randos['famille'].replace(False, 'Normale')
df_randos["duree"] = pd.to_numeric(df_randos["duree"])
df_randos["denivellee"] = pd.to_numeric(df_randos["denivellee"])
df_randos = df_randos.rename(columns={'massif.libelle': 'massif',
                                      'activite.libelle': 'activite',
                                      'adresse.latitude': 'lat',
                                      'adresse.longitude': 'lon'})

sorted_unique_massif = sorted(df_randos.massif.unique())
sorted_unique_activite = sorted(df_randos.activite.unique())

st.sidebar.title("Décrivez votre rando du jour")

selected_massif = st.sidebar.selectbox('Dans quel massif ?', sorted_unique_massif)
selected_activite = st.sidebar.selectbox('Quelle activité ?', sorted_unique_activite)
selected_famille = st.sidebar.selectbox('Quel type de rando ?', ["Famille","Normale"])
    
selected_duration = st.sidebar.slider('Durée', 2, 10, (2, 10), 1)
selected_denivellee = st.sidebar.slider('Dénivellée', 90, 2390, (90, 2390), 25)

df_randos_filtered = df_randos[(df_randos.duree >= (selected_duration[0]))
                               & (df_randos.duree <= (selected_duration[1]))
                               & (df_randos.denivellee >= (selected_denivellee[0]))
                               & (df_randos.denivellee <= (selected_denivellee[1]))
                               & (df_randos.massif == selected_massif)
                               & (df_randos.famille == selected_famille)
                               & (df_randos.activite == selected_activite)
                               ]
                               
length_df = len(df_randos_filtered)

st.text( str(length_df) +' Ballade(s) trouvée(s) avec ces paramètres.')


choix_final = sorted(df_randos_filtered.libelle.unique())
choix = st.selectbox('Choisir une rando :', choix_final)

df_randos_choisie = df_randos[(df_randos.libelle == (choix)) ]

df = df_randos_choisie[["libelle","resume", "depart", "acces","denivellee",
                        "duree","difficulte","materiel"]]


fig = go.Figure(data=[go.Table(
    
  columnwidth = [80,500,150,200,80,80,80,80],
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='center'),
    cells=dict(values=[df.libelle, df.resume, df.depart, df.acces, df.denivellee, df.duree, df.difficulte, df.materiel],
               fill_color='lavender',
               align='center'))
])

st.write(fig)



