import streamlit as st
import polars as pl
import altair as alt
import plotly.express as px
import pycountry
import pandas as pd
from data import life

# dataset
df = life(url = "Data\estat_demo_mlexpec.tsv.gz")


# Inizializzare le variabili di sessione
# problema reset
if "country" not in st.session_state:
    st.session_state["country"] = "IT"
if "sex" not in st.session_state:
    st.session_state["sex"] = "completo"

countries = df.select("country").unique().sort("country") # stati
years = df.select("year").unique().sort("year") #anni
sex = df.select("sex").unique().sort("sex") # sesso

st.write("# ANALISI ASPETTATIVA DI VITA")



### ANALISI ESPLORATIVA 

selected_countries = st.multiselect("Scegli uno o più paesi", countries, default= ["IT", "FR", "DE"])
filtered_df = (df
               .filter(pl.col("country").is_in(selected_countries))
               .filter(pl.col("sex") != "T") # 
               .group_by("year","country", "sex")
                .agg(
                    pl.col("life_exp").mean()
                )
                )             

chart = (
    alt.Chart(filtered_df)
    .mark_line()
    .encode(
        alt.X("year:O", title = "Year").scale(zero = False),
        alt.Y("life_exp:Q", title = "Average life expectancy"), # aggregate="mean" non va
        alt.Facet("sex:N"),
        color=alt.Color("country:N"),
        tooltip = ["country", "year", "life_exp"],

    )
    .properties(
        width = 600,
        height = 300,
        title="Aspettativa di vita per paese e sesso"
    )
)
st.altair_chart(chart, use_container_width=True)

st.markdown(''':red[**COMMENTARE**]''')

#### GRAFICO A BARRE
selected_year = st.select_slider("Scegli un anno", years, key="slider_0")

bar_chart_data = (
    df
    .filter(pl.col("year") == selected_year)
    .group_by("country")
    .agg(
        pl.col("life_exp").mean().round(2).alias("average")
    )
    .with_columns(
    pl.col("country").cast(pl.Categorical())
    )
)

base = (alt.Chart(bar_chart_data)
        .encode(
                alt.X('average:Q', title = "life exp media"),
                alt.Y("country:N", title = "paesi", sort = "-x"),
                text='average'
        )
        .properties(
            width = 600,
            height=alt.Step(20),  
            title="Aspettativa di vita medio per paese e anno"
        )
)
base.mark_bar() + base.mark_text(align='left', dx=2)

st.markdown(''':red[**COMMENTARE**]''')

### CARTINA GEOGRAFICA

year_select1 = st.select_slider("Scegli un anno", years, key="slider_1")

df_fig = (
    df
    .filter(pl.col("year") == year_select1)
        .group_by("country")
        .agg(
            pl.col("life_exp").mean().alias("media")
        )
    .filter(~pl.col("country").is_in(["DE_TOT", "EA19", "EA20", "EEA30_2007", "EEA31",
                                      "EFTA", "EU27_2007", "EU27_2020", "EU28", "FX", "SM"]))
)
# converte in pandas
df_pandas = df_fig.to_pandas()
# dizionario di conversione ISO-2 a ISO-3
iso2_to_iso3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}
# da iso2 a iso3
df_pandas["country_iso3"] = df_pandas["country"].map(iso2_to_iso3)
# ritorna in polars
df_fig = pl.from_pandas(df_pandas)


fig = px.choropleth(
    df_fig,
    locationmode="ISO-3",
    locations = "country_iso3",          # Colonna con i codici ISO dei paesi
    color = "media",                     # Colonna con la fascia di aspettativa di vita
    hover_name = "country_iso3",         # Nome visualizzato
    color_continuous_scale=px.colors.sequential.Viridis_r,
    scope="europe",
    title = f"Aspettativa di vita media per Paese - Anno {year_select1}",
    width=800,
    height=600
)
st.plotly_chart(fig)

st.markdown(''':red[**COMMENTARE**]''')

st.markdown(f"""
    Dataset: 'Life expectancy by age and sex'  
    Fonte: [Eurostat :chart:](https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en&category=demo.demo_mor)
""")




