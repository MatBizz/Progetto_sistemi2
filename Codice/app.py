import streamlit as st
import polars as pl
import altair as alt
import plotly.express as px
import pycountry
import pandas as pd
from data import life
from data import work

# dataset totale
df_tot = life(url = "Data\estat_demo_mlexpec.tsv.gz")
# dataset con sola fascia <=1 anno
df = df_tot.filter(pl.col("age") == 1)
# dataset filtrato con iso-2 validi
df_eu = df.filter(~pl.col("country").is_in(["DE_TOT", "EA19", "EA20", "EEA30_2007", "EEA31", # ~ negazione da T a F e vicev. 
                                      "EFTA", "EU27_2007", "EU27_2020", "EU28", "FX", "SM"]))

countries = df.select("country").unique().sort("country") # paesi
years = df.select("year").unique().sort("year") # anni
sex = df.select("sex").unique().sort("sex") # sesso

st.write("## PROGETTO - ASPETTATIVA DI VITA")
st.markdown(f"""**OBIETTIVO**: Analizzare l'aspettativa di vita per studiare un indice della
            salute generale per i diversi paesi europei e fare un confronto tra sesso, anno e paese.
            Alla fine si studia se esiste una correlazione tra l'aspettativa di vita e il tasso
            di povertà dei lavoratori.
""")

#### GRAFICO A BARRE
st.markdown(f"""
            #### Aspettativa di Vita medio per Paese ed Anno
""")
year_select0 = st.select_slider("Scegli un anno", years, key = "slider_0", value = 2003)

bar_chart_data = (
    df_eu
    .filter(pl.col("year") == year_select0)
    .group_by("country")
    .agg(
        pl.col("life_exp").mean().round(1).alias("average")
    )
    .with_columns(
    pl.col("country")
    )
)

base = (alt.Chart(bar_chart_data)
        .encode(
                alt.X("country:N", title = "paesi", sort = "-y"),
                alt.Y("average:Q", title = "life exp media"),
                text = "average",
        )
        .properties(
            width = alt.Step(22),
            height = 400
        )
)
st.altair_chart(
    base.mark_bar(color="skyblue") + base.mark_text(align = "center", dx = 0), use_container_width = False)

st.markdown(f'''
            Questo grafico a barre mostra l'**aspettativa di vita media** per ogni paese per l'anno selezionato.
            Aiuta a individuare rapidamente quali paesi hanno valori più alti o più bassi rispetto agli altri.
''')

### CONFRONTO SESSI
st.markdown(f"""
            #### Confronto dell'Aspettativa di Vita per Sesso ed Anno
""")
year_select1 = st.select_slider("Scegli un anno", years, key = "slider_1", value = 2003)

sex_data = (
    df_eu
    .filter(pl.col("year") == year_select1)
    .filter(pl.col("sex").is_in(["M", "F"]))
    .group_by("country", "sex")
    .agg(
        pl.col("life_exp").mean().alias("average_life_exp")
    )
)

sex_chart = (
    alt.Chart(sex_data)
    .mark_bar()
    .encode(
        alt.X("average_life_exp:Q", title = "Aspettativa di vita media"),
        alt.Y("country:N", sort = "-x", title = "Paesi"),
        alt.Color("sex:N", title = "Sesso"),
        tooltip = ["country", "sex", "average_life_exp"]
    )
    .properties(
        width = 600,
        height = alt.Step(20)
    )
)
st.altair_chart(sex_chart, use_container_width = True)

st.markdown('''
            Questo grafico a barre confronta l'**aspettativa di vita media** tra uomini e donne 
            per i diversi paesi nell'anno indicato. 

            Ci permette di confrontare facilmente le differenze di aspettativa di vita tra i sessi,
            evidenziando le **disparità** esistenti tra le diverse nazioni.
''')

### CARTINA GEOGRAFICA
 
# conversione in pandas
df_pandas = df_eu.to_pandas()
# dizionario di conversione ISO-2 a ISO-3
iso2_to_iso3 = {country.alpha_2: country.alpha_3 for country in pycountry.countries}
# da iso2 a iso3
df_pandas["country_iso3"] = df_pandas["country"].map(iso2_to_iso3)
# ritorna in polars
df_iso3 = pl.from_pandas(df_pandas)

st.markdown(f"""
            #### Aspettativa di Vita media per Paese ed Anno
""")
year_select2 = st.select_slider("Scegli un anno", years, key = "slider_2", value = 2003)

df_fig = (
    df_iso3
    .filter(pl.col("year") == year_select2)
        .group_by("country_iso3")
        .agg(
            pl.col("life_exp").mean().round(2).alias("media")
        )
)

fig = px.choropleth(
    df_fig,
    locationmode = "ISO-3",
    locations = "country_iso3",
    color = "media",
    hover_name = "country_iso3",
    color_continuous_scale = px.colors.sequential.Viridis_r,
    scope = "europe",
    width = 800,
    height = 600
)
st.plotly_chart(fig)

st.markdown(f'''
            Questo grafico rappresenta una mappa dell'Europa, ogni paese è colorato in base
            alla sua **aspettativa di vita media** per l'anno selezionato.

            La mappa ci permette di avere una visualizzazione facilmente interpretabile e
            di cogliere facilmete **differenze** o **somiglianze** tra i vari paesi o individuare
            eventuali pattern geografici.
''')

### CARTINA GEOGRAFICA GAP SESSI
st.markdown(f"""
            #### Gap dell'Aspettativa di Vita media per Paese ed anno
""")
year_select3 = st.select_slider("Scegli un anno", years, key = "slider_3", value = 2003)

df1 = (
    df_iso3
    .filter(pl.col("sex").is_in(["M", "F"]))
    .filter(pl.col("year") == year_select3)
    .group_by(["country_iso3", "sex"])
    .agg(
        pl.col("life_exp").mean().alias("average_life_exp")
    )
)

# pivot per avere una colonna per ogni sesso
pivoted_means = (
    df1
    .pivot(
        values = "average_life_exp",
        index = ["country_iso3"],  
        columns = "sex" 
    )
    .rename({"M": "male_avg", "F": "female_avg"})
)

df_fig1 = ( # differenza tra femmine e maschi
    pivoted_means
    .with_columns(
        (pl.col("female_avg") - pl.col("male_avg")).alias("gender_life_exp_gap")
    )
)

fig1 = px.choropleth(
    df_fig1,
    locationmode = "ISO-3",
    locations = "country_iso3",       
    color = "gender_life_exp_gap",
    hover_name = "country_iso3",
    color_continuous_scale = px.colors.sequential.Viridis_r,
    scope = "europe",
    width = 800,
    height = 600
)
st.plotly_chart(fig1)

st.markdown(f'''
            Questo grafico mostra il **gap dell'aspettativa di vita media** 
            tra uomini e donne in Europa per l'anno selezionato.

            Un valore positivo indica che le donne vivono mediamente più a lungo degli uomini, 
            mentre un valore negativo indica il contrario.

            La mappa permette di osservare visivamente le **disparità di genere** in termini di 
            aspettativa di vita, evidenziando paesi con una differenza maggiore o minore tra 
            i due sessi.
''')

### TREND DI CRESCITA GLOBALE
st.markdown(f"""
            #### Trend Globale dell'Aspettativa di Vita
""")
global_trend_data = (
    df
    .filter(pl.col("sex") == "T")  
    .group_by("year")
    .agg(
        pl.col("life_exp").mean().round(2).alias("global_average")
    )
)

global_trend_chart = (
    alt.Chart(global_trend_data)
    .mark_line(point = True)
    .encode(
        alt.X("year:O", title = "Anno"),
        alt.Y("global_average:Q", title = "Aspettativa di vita media globale", scale = alt.Scale(domain = [68, 82])),
        tooltip=["year", "global_average"]
    )
    .properties(
        width = 800,
        height = 400
    )
)

st.altair_chart(global_trend_chart, use_container_width = True)

st.markdown('''
            Questo grafico mostra l'andamento dell'**aspettativa di vita media globale** nel corso degli anni. 
            E' stata considerata la media dell'aspettativa di vita a livello globale, considerando tutti i sessi, 
            con i punti che evidenziano i dati specifici di ogni anno. 

            Il grafico offre una visione chiara e immediata di come l'aspettativa di vita sia cambiata nel tempo.
            E' utile per avere un'idea generale di come fattori globali, quali **miglioramenti della medicina**,
            **guerre** o **pandemie** abbiamo influenzato sulla vita media della popolazione nel corso del tempo.
            Per esempio si riesce a vedere l'effetto nel 2020 del covid.
''')

### TREND PER PAESE ED ANNO

st.markdown(f"""
            #### Tred dell'Aspettativa di Vita per Paese e Sesso
""")
selected_countries = st.multiselect("Scegli uno o più paesi", countries, default = ["IT", "BE", "CH"]) #ita, germ, svizz
filtered_df = (
    df
    .filter(pl.col("country").is_in(selected_countries))
    .filter(pl.col("sex") != "T")
    .group_by("year", "country", "sex")
    .agg(
        pl.col("life_exp").mean()
    )
)           

col1, col2 = st.columns([1, 1])  # divido la pagina in due colonne

with col1:
    chart = (
        alt.Chart(filtered_df)
        .mark_line()
        .encode(
            alt.X("year:O", title = "Anno").scale(zero=False),
            alt.Y("life_exp:Q", title = "Aspettativa di vita media", scale = alt.Scale(domain = [55, 90])),
            alt.Facet("sex:N", columns = 2),  # mette i grafici uno di fianco all'altro invece che uno sotto l'altro
            color = alt.Color("country:N"),
            tooltip = ["country", "year", "life_exp"],
        )
        .properties(
            width = 300,
            height = 300
        )
    )

    st.altair_chart(chart, use_container_width = True)

st.markdown(f'''
            Questo grafico mostra l'**evoluzione dell'aspettativa di vita media nel tempo** per i paesi selezionati,
            distinguendo maschi e femmine, permettendo di confrontare le differenze di genere nel tempo. 
            ''')

# DEVIAZIONE DALLA MEDIA GLOBALE
st.markdown(f"""
            #### Anomalie principali rispetto alla media globale per Anno
""")
year_select4 = st.select_slider("Scegli un anno", years, key = "slider_4", value = 2003)

data = (
    df_eu
    .filter(pl.col("year") == year_select4)
    .group_by("country")
    .agg(
        (pl.col("life_exp").mean()).alias("average_life_exp")  # media di ogni paese rispetto all'anno scelto
    )
)

# media globale rispetto all'anno scelto
global_mean = (
    data
    .select(pl.col("average_life_exp").mean())
    .to_series()# to_series per accederedirettamente ai valori della colonna
    .item(0)  # ritorna il valore scalare
)

# deviazione dalla media globale
deviation = data.with_columns(
    (pl.col("average_life_exp") - global_mean).round(2).alias("deviation_from_mean")
)

top_5_positive = deviation.sort("deviation_from_mean", descending = True).head(5)
top_5_negative = deviation.sort("deviation_from_mean", descending = False).head(5)

top_countries = top_5_positive.vstack(top_5_negative)

deviation_chart = (
    alt.Chart(top_countries)
    .mark_bar()
    .encode(
        alt.X("deviation_from_mean:Q", title = "Deviazione dalla media"),
        alt.Y("country:N", sort = "-x", title = "Paesi"),
        tooltip = ["country", "deviation_from_mean"]
    )
    .properties(
        width = 600,
        height = alt.Step(20)
    )
)
st.altair_chart(deviation_chart, use_container_width = True)
st.markdown(f"""
            Questo grafico ci permette di visualizzare i paesi che presentano le maggiori **deviazioni**
            dall'aspettativa di vita media globale per l'anno selezionato.

            Vengono mostrati solo i 5 paesi con la più alta deviazione positiva, cioè con una aspettativa di vita
            superiore alla media globale, e i 5 paesi con la maggiore deviazione negativa, quindi con un'aspettativa
            di vita inferiore alla media globale, per avere una visualizzazione più contenuta ma informativa.
""")

### ANALISI CON TUTTE LE ETA'

countries_list = countries["country"].to_list()  # colonna "country" in lista, per usarla come indice
st.markdown(f"""
            #### Cambiamento dell'Aspettativa di Vita per Paese
""")
countrie_select = st.selectbox("Scegli un paese", countries_list, index = countries_list.index("IT"), key = "selectbox_0")

data = (
    df_tot
    .filter(pl.col("country") == (countrie_select))
    .filter(pl.col("sex") != "T")
    .filter(pl.col("year") != 2023)# pochi dati, errori di visualizzazione
    .with_columns(
        pl.col("life_exp")
        .qcut(100) # percentili
        .rank(method = "dense")
        .alias("Percentile")
    )
)

chart = (
    alt.Chart(data)
    .mark_rect(stroke = None, opacity = 1)
    .encode(
        alt.X("year:O", title = "Anno"),
        alt.Y("age:O", sort="descending", title = "Età"),
        alt.Color("Percentile:Q", scale=alt.Scale(scheme="inferno")),
        alt.Facet("sex:N")
    )
    .properties(
        height= 250
        )
)
st.altair_chart(chart, use_container_width=True)

st.markdown(f"""
            Questo grafico mostra l'**andamento** dell'aspettativa di vita per il paese selezionato,
            suddiviso per sesso.
            La colorazione indica il **percentile** dell'aspettativa di vita per quella fascia.
            Ci permette quindi di identificare **cambiamenti storici** nell'aspettativa di vita di una popolazione
            e di notare differenze per diverse età e sesso.

            :red[NOTA:] in questa analisi sono state usate tutte le età disponibili nel dataset
            """)

### INNER JOIN

df_work = work(url = "Data\estat_ilc_iw01.tsv.gz")

df_mean = (df
           .group_by("country", "year")
           .agg(
               pl.col("life_exp").mean().round(2).alias("life_exp_mean")
               )
           )
work_mean = (df_work
           .group_by("country", "year")
           .agg(
               pl.col("poverty_rate").mean().round(2).alias("poverty_rate_mean")
               )
           )

df_join = df_mean.join(
    work_mean, 
    on = ["country", "year"],
    how = "inner"
)

years_work = df_work.select("year").unique().sort("year")

st.markdown(f"""
            #### Correlazione tra Aspettativa di Vita e Tasso di Povertà per Anno
""")

year_select5 = st.select_slider("Scegli un anno", years_work, key = "slider_5", value = 2013)

df_join = df_join.filter(pl.col("year") == year_select5)

correlation = df_join.select([
    pl.corr("life_exp_mean", "poverty_rate_mean", method="pearson").round(2)
])
correlation = correlation.to_series().item(0)

scatter_plot = (
    alt.Chart(df_join)
    .mark_circle(size = 60)
    .encode(
        alt.X("life_exp_mean:Q", title = "Aspettativa di vita media",scale = alt.Scale(domain = [65, 85])),
        alt.Y("poverty_rate_mean:Q", title = "Tasso lavoratori a rischio di povertà medio"),
        tooltip = ["country", "life_exp_mean", "poverty_rate_mean"]
    )
    .properties(
        width = 600,
        height = 400
    )
)

st.altair_chart(scatter_plot, use_container_width = True)

st.markdown(f"""
            Questo scatterplot mostra la **relazione** tra l'aspettativa di vita media e il tasso lavoratori
            a rischio di povertà medio per ciascun paese.
            La distribuzione dei punti fornisce una panoramica della possibile **correlazione** tra queste due variabili,
            consentendo anche di identificare eventuali outlier, cioè paesi che si discostano significativamente
            dalla tendenza generale.

            Tuttavia, non sembra esserci una correlazione evidente o forte tra le due variabili (infatti la correlazione, 
            nell'anno {year_select5} risulta {correlation}). Per arrivare a conclusioni più dettagliate, sarebbero necessarie
            analisi aggiuntive, ma ciò non è l'obiettivo del progetto.
            
            Una mia, possibile, interpretazione di questo risultato è che l'aspettativa di vita media, come evidenziato 
            dalle analisi precedenti, è aumentata nel corso degli anni grazie a miglioramenti nelle condizioni igieniche 
            e sanitarie. Ciò ha consentito anche alle persone classificate come a **rischio di povertà** di potersi permettere 
            medicine e cure mediche, con un impatto più significativo sulla qualità della vita rispetto alla salute generale.
""")

if st.button("Leggi le conclusioni del progetto"):
    st.markdown(f"""
                Le principali conclusioni, che sono messe in evidenza dall'analisi dei dati
                sull'aspettativa di vita e il tasso di povertà dei lavoratori nei paesi europei, sono:

                - L'aspettativa di vita sembra sia cresciuta costantemente dal 1960, grazie a migliori condizioni
                  sanitarie e socioeconomiche. Si riscontrano però anche periodi con cali temporanei, che
                  si possono attribuire a fattori quali guerre o pandemie (es. covid 2020/2021).
                - Le donne vivono più a lungo degli uomini in tutti i paesi analizzati,
                  ma il divario può variare significativamente.
                - Non è emersa una correlazione evidente tra il tasso di povertà dei lavoratori e l'aspettativa di vita,
                  questo può indicare che ci sono altri fattori non osservati che giocano un ruolo importante,
                  come l'accesso ai servizi sanitari.

                Questi risultati offrono una panoramica utile per comprendere l'evoluzione della salute pubblica in Europa,
                fornendo spunti per ulteriori analisi.
""")

st.markdown(f"""
    Dataset: 'Life expectancy by age and sex'  
    Fonte: [Eurostat :chart:](https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en&category=demo.demo_mor)
            
    Dataset: 'In-work at-risk-of-poverty rate by age and sex'  
    Fonte: [Eurostat :chart:](https://ec.europa.eu/eurostat/databrowser/view/ilc_iw01/default/table?lang=en&category=livcon.ilc.ilc_ip.ilc_iw)
""")