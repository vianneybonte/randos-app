import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import  json, requests
pd.options.mode.chained_assignment = None  # default='warn'
st.set_page_config(
  page_title="Randos app",
 layout="wide",
)
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
df_randos.applymap(lambda x: x.strip() if isinstance(x, str) else x)


#st.dataframe(df_randos)


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



sorted_unique_massif = sorted(df_randos.massif.unique(), reverse= True)
sorted_unique_activite = sorted(df_randos.activite.unique(), reverse= True)

st.sidebar.title("Décrivez votre rando du jour")

selected_massif = st.sidebar.selectbox('Dans quel massif ?', sorted_unique_massif)
selected_activite = st.sidebar.selectbox('Quelle activité ?', sorted_unique_activite)
selected_famille = st.sidebar.selectbox('Quel type de rando ?', ["Normale", "Famille"])
    
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

st.text( str(length_df) +' ballade(s) trouvée(s) avec ces paramètres.')


choix_final = sorted(df_randos_filtered.libelle.unique())
choix = st.selectbox('Choisir une rando :', choix_final)

df_randos_choisie = df_randos[(df_randos.libelle == (choix)) ]

df_infos = df_randos_choisie[["libelle","resume"]]
df_itineraire = df_randos_choisie[["itineraire"]]
df_acces = df_randos_choisie[[ "depart", "acces"]]
df_technique = df_randos_choisie[["denivellee",
                        "duree","difficulte","materiel"]]
df_total = df_randos_choisie[["libelle","resume", "depart", "acces","denivellee",
                        "duree","difficulte","materiel"]]

liste_infos = [df_infos.libelle, df_infos.resume]
liste_itineraire = [df_itineraire.itineraire]
liste_acces = [df_acces.depart, df_acces.acces]
liste_technique = [df_technique.denivellee, df_technique.duree, df_technique.difficulte, df_technique.materiel]
liste_total = [df_total.libelle, df_total.resume, df_total.depart, df_total.acces, df_total.denivellee, df_total.duree, df_total.difficulte, df_total.materiel]


def affiche_tableau(tab, liste, label, width):
    tableau = go.Figure(data=[go.Table(
        
      columnwidth = width,
        header=dict(values=list(tab.columns),
                    fill_color='green',
                    align='center'),
        cells=dict(values= liste,
                   fill_color='white',
                   font_color = "black",
                   align='center'))
    ])
    
    tableau.update_layout(width=1600)

    st.write(label)
    st.write(tableau)
    
if length_df> 1 :
    affiche_tableau(df_infos, liste_infos, label="Informations :", width=[80,500,500])
    affiche_tableau(df_itineraire, liste_itineraire, label="Itineraire :", width=[1600])
    affiche_tableau(df_acces, liste_acces, label="Accès :", width=[180,500])
    affiche_tableau(df_technique, liste_technique, label="Informations techniques :", width=[500,500,500,500])
    affiche_tableau(df_total, liste_total, label="Résumé complet :", width=[80,500,150,500,80,80,80,80])


#ajouter une carte qui pointe vers la ballade sélectionnée
#st.map(df_randos)


#ajouter appel api de météo

#ajouter machine learning prévision température
