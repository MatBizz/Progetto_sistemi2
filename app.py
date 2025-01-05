import streamlit as st
import polars as pl
import altair as alt
import plotly.express as px
import pycountry
import pandas as pd
from data import life
from data import work

# dataset totale
df_tot = life(url = "estat_demo_mlexpec.tsv.gz")
# dataset con sola fascia <=1 anno
df = df_tot.filter(pl.col("age") == 1)
# dataset filtrato con iso-2 validi
df_eu = df.filter(~pl.col("country").is_in(["DE_TOT", "EA19", "EA20", "EEA30_2007", "EEA31", # ~ negazione da T a F e vicev. 
                                      "EFTA", "EU27_2007", "EU27_2020", "EU28", "FX", "SM"]))

countries = df.select("country").unique().sort("country") # paesi
years = df.select("year").unique().sort("year") # anni
sex = df.select("sex").unique().sort("sex") # sesso

st.write("## Analisi dell'Aspettativa di Vita nei Paesi Europei: Focus sulla fascia d'età infantile")
st.markdown(f"""**OBIETTIVO**: Analizzare l'aspettativa di vita per studiare un indice della
            salute generale per i diversi paesi europei e fare un confronto tra sesso, anno e paese.
            Alla fine si studia se esiste una correlazione tra l'aspettativa di vita e il tasso
            di povertà dei lavoratori.
""")

#### GRAFICO A BARRE
st.markdown(f"""
            #### Aspettativa di Vita medio per Paese ed Anno
""")
year_select0 = st.select_slider("Scegli un anno", years, key = "slider_0", value = 2003)# scelta anno da utente

bar_chart_data = (
    df_eu
    .filter(pl.col("year") == year_select0)# filtro per anno selezionato
    .group_by("country")
    .agg(
        pl.col("life_exp").mean().round(1).alias("average")# media asp. di vita per paese
    )
    .with_columns(
    pl.col("country")
    )
)

base = (alt.Chart(bar_chart_data)
        .encode(
                alt.X("country:N", title = "Paesi", sort = "-y"),
                alt.Y("average:Q", title = "Aspettativa di vita media"),
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
            Il grafico a barre cevidenzia l'**aspettativa di vita media** nei vari paesi europei nell'anno scelto tramite lo slider.
            Sull'asse X si trovano i nomi dei paesi, rappresentati da una barra, mentre sull'asse Y è riportata
            l'aspettativa di vita media. Questo tipo di visualizzazione permette di osservare differenze
            significative tra i paesi.
''')

### CONFRONTO SESSI
st.markdown(f"""
            #### Confronto dell'Aspettativa di Vita per Sesso ed Anno
""")
year_select1 = st.select_slider("Scegli un anno", years, key = "slider_1", value = 2003)# scelta anno da utente

sex_data = (
    df_eu
    .filter(pl.col("year") == year_select1)# filtro per anno scelto
    .filter(pl.col("sex").is_in(["M", "F"]))# teniamo solo sesso maschio e femmina
    .group_by("country", "sex")
    .agg(
        pl.col("life_exp").mean().alias("average_life_exp")# media asp. di vita per sesso e paese
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
            Il grafico a barre confronta l'**aspettativa di vita media** tra femmine e maschi
            nei diversi paesi, per l'anno selezionato.
            L'asse X mostra l'aspettativa di vita media mentre l'asse Y riporta i paesi e ogni barra è suddivisa
            e colorata in base al sesso. Questo tipo di visualizzazione consente di osservare
            rapidamente le **disparità**, se esistenti, tra i due sessi in termini di aspettativa di vita
            e di confrontarle tra i vari stati europei.

''')

### CARTINA GEOGRAFICA
# necessario passare a pandas per applicare il metodo .map()
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
year_select2 = st.select_slider("Scegli un anno", years, key = "slider_2", value = 2003)# scelta anno da utente

df_fig = (
    df_iso3
    .filter(pl.col("year") == year_select2) # filtro per anno selezionato
        .group_by("country_iso3")
        .agg(
            pl.col("life_exp").mean().round(2).alias("asp. di vita media")# media asp. di vita per paese
                                                                          #(codice isp3 invece di iso2 in questo caso)
        )
)

fig = px.choropleth(
    df_fig,
    locationmode = "ISO-3",
    locations = "country_iso3",
    color = "asp. di vita media",
    hover_name = "country_iso3",
    color_continuous_scale = px.colors.sequential.Viridis_r,
    scope = "europe",
    width = 800,
    height = 600
)
st.plotly_chart(fig)

st.markdown(f'''
            La mappa visualizza l'**aspettativa di vita media** nei paesi europei per l'anno selezionato.
            Ogni paese europeo è colorato in base alla scala cromatica Viridis_r, mostrata accanto alla mappa:
            i colori scuri indicano valori più alti, quelli chiari valori più bassi.

            La mappa ci permette di avere una visualizzazione facilmente interpretabile e
            di cogliere facilmete **differenze** o **somiglianze** tra i vari paesi o individuare
            eventuali pattern geografici, per esempio risulta che i paesi europei occidentali tendano ad avere
            aspettative di vita medie più alte rispetto alla parte orientale.
''')

### CARTINA GEOGRAFICA GAP SESSI
st.markdown(f"""
            #### Gap dell'Aspettativa di Vita media per Paese ed anno
""")
year_select3 = st.select_slider("Scegli un anno", years, key = "slider_3", value = 2003)# scelta anno da utente

df1 = (
    df_iso3
    .filter(pl.col("sex").is_in(["M", "F"]))# teniamo solo sesso maschio e femmina (no T - totale)
    .filter(pl.col("year") == year_select3)# filtro per anno selezionato
    .group_by(["country_iso3", "sex"])
    .agg(
        pl.col("life_exp").mean().alias("average_life_exp")# media asp. di vita per paese e sesso
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
        (pl.col("female_avg") - pl.col("male_avg")).alias("Deviazione")
    )
)

fig1 = px.choropleth(
    df_fig1,
    locationmode = "ISO-3",
    locations = "country_iso3",       
    color = "Deviazione",
    hover_name = "country_iso3",
    color_continuous_scale = px.colors.sequential.Viridis_r,
    scope = "europe",
    width = 800,
    height = 600
)
st.plotly_chart(fig1)

st.markdown(f'''
            La mappa mostra la **differenza** tra l'aspettativa di vita delle femmine con quella dei maschi
            per l'anno selezionato, con colori che indicano l'ampiezza della deviazione. In particolare i paesi
            in cui il colore è più scuro indicano una maggiore disparità tra i sessi, mentre colori più chiari
            rappresentano valori più vicini.

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
    .filter(pl.col("sex") == "T")  # consideriamo tutti i sessi
    .group_by("year")
    .agg(
        pl.col("life_exp").mean().round(2).alias("global_average")# media asp. di vita per anno
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
            L'asse X rappresenta gli anni e l'asse Y l'aspettativa di vita media globale. La linea mostra l'andamento
            nel tempo e i punti sono le osservazioni.

            Il grafico offre una visione chiara e immediata di come l'aspettativa di vita sia cambiata nel tempo,
            in particolare in questo caso si osserva un **trend crescente**.
            E' utile per avere un'idea generale di come fattori globali, quali **miglioramenti della medicina**,
            **guerre** o **pandemie** abbiamo influenzato sulla vita media della popolazione nel corso del tempo.
            Per esempio si riesce a vedere l'effetto del covid nel 2020.
''')

### TREND PER PAESE ED ANNO

st.markdown(f"""
            #### Tred dell'Aspettativa di Vita per Paese e Sesso
""")
# multi select per paesi 
selected_countries = st.multiselect("Scegli uno o più paesi", countries, default = ["IT", "BE", "CH"]) #ita, germ, svizz
filtered_df = (
    df
    .filter(pl.col("country").is_in(selected_countries))# filtro oss per paesi scelti
    .filter(pl.col("sex") != "T") # non consideriamo il totale dato che vogliamo distinguere maschi da femmine
    .group_by("year", "country", "sex")
    .agg(
        pl.col("life_exp").mean()# media asp. di vita per anno, paese e sesso
    )
)           

col1, col2 = st.columns([1, 1])  # divido la pagina in due colonne, per avere i 2 grafici affiancati bene

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
            Questo grafico mostra l'**evoluzione dell'aspettativa di vita media nel tempo*, distinguendo maschi
            e femmine, per i paesi selezionati.
            L'asse X mostra gli anni, mentre l'asse Y riporta l'aspettativa di vita media.
            Il grafico a destra mostra le osservazioni delle femmine, mentre quello a sinistra dei maschi,
            inoltre la linea che mostra l'andamento nel tempo è colorata in base ai paesi, seguendo la leggenda a lato.
            
            Dai dati risulta ci sia generalmente un miglioramento nel tempo, e le donne tendono ad avere un valore
            più alto rispetto agli uomini.
            ''')

# DEVIAZIONE DALLA MEDIA GLOBALE
st.markdown(f"""
            #### Anomalie principali rispetto alla media globale per Anno
""")
year_select4 = st.select_slider("Scegli un anno", years, key = "slider_4", value = 2003)# scelta anno da utenmte

data = (
    df_eu
    .filter(pl.col("year") == year_select4)# filtro per anno selezionato
    .group_by("country")
    .agg(
        (pl.col("life_exp").mean()).alias("average_life_exp")  # media asp. di vita di ogni paese rispetto all'anno scelto
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
            Questo grafico ci permette di visualizzare i 10 paesi che presentano le maggiori **deviazioni**
            dall'aspettativa di vita media globale per l'anno selezionato. In particolare mostra i 5 paesi 
            con la più alta deviazione positiva, cioè con una aspettativa di vita superiore alla media globale,
            e i 5 paesi con la maggiore deviazione negativa, quindi con un'aspettativa di vita inferiore alla media globale.
             L'asse X mostra la deviazione dalla media, mentre l'asse Y riporta i paesi.

            Permette di avere un'idea generale di quali paesi sono i migliori e quali i peggiori rispetto alla
            media globale, rispetto all'anno selezionato.
""")

### ANALISI CON TUTTE LE ETA'

countries_list = countries["country"].to_list()  # colonna "country" in lista, per usarla come indice
st.markdown(f"""
            #### Cambiamento dell'Aspettativa di Vita per Paese
""")
# scelta utente del paese
countrie_select = st.selectbox("Scegli un paese", countries_list, index = countries_list.index("IT"), key = "selectbox_0")

data = (
    df_tot
    .filter(pl.col("country") == (countrie_select))# filtro per paese scelto
    .filter(pl.col("sex") != "T")# consideriamo solo maschi e femmine
    .filter(pl.col("year") != 2023)# pochi datinel 2023, errori di visualizzazione, quindi tolti
    .with_columns(
        pl.col("life_exp")
        .qcut(100) # percentili, per una visualizzazione migliore
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
            Questo grafico analizza come l'aspettativa di vita media varia tra diverse fasce di età e come cambia nel tempo,
            per il paese selezionato dall'utente, suddiviso per genere.
            Il grafico in alto mostra le osservazioni per le femmine, mentre quello in basso per i maschi, inoltre
            l'asse X rappresenta gli anni, l'asse Y mostra le età e il colore indica il **percentile** dell'aspettativa
            di vita, in particolare colorazioni più scure indicano percentili più bassi, mentre quelle più chiare
            percentili più alti.
            Ci permette quindi di identificare **cambiamenti storici** nell'aspettativa di vita di una popolazione
            e di notare differenze per diverse età e sesso.

            :red[NOTA:] in questa analisi sono state usate tutte le età disponibili nel dataset
            """)

### INNER JOIN
# carico dataset tasso dei lavoratori a rischio di povertà
df_work = work(url = "estat_ilc_iw01.tsv.gz")
# aggrego la media dell'aspettativa di vita per paese e anno, con dataset con solo eta <= 1
df_mean = (df
           .group_by("country", "year")
           .agg(
               pl.col("life_exp").mean().round(2).alias("life_exp_mean")
               )
           )
# stessa cosa per altro dataset
work_mean = (df_work
           .group_by("country", "year")
           .agg(
               pl.col("poverty_rate").mean().round(2).alias("poverty_rate_mean")
               )
           )

# join in paese ed anno per avere un'unico dataframe
df_join = df_mean.join(
    work_mean, 
    on = ["country", "year"],
    how = "inner"
)

# dataframe join con unpivot colonne
df_long = (
    df_join.melt(
        id_vars=["country", "year"], # rimangono invariate
        value_vars=["life_exp_mean", "poverty_rate_mean"], # valori nuova colonna
        variable_name="metric",# nome nuova colonna
        value_name="value" # nome colonna con valori delle 2 var unite
    )
)

st.markdown(f"""
            #### Correlazione tra Aspettativa di Vita Media e Tasso Lavoratori a Rischio Povertà Medio per Paese
""")
# paesi da scegliere
countries_join = df_join.select("country").unique().sort("country")
# scelta utente
country_select = st.selectbox("Scegli un Paese", countries_join)
# data filtrati
df_filtered = df_long.filter(pl.col("country") == country_select)
# daatframe join filtrato per il paese scelto per il grafico
df_filtered_join = df_join.filter(pl.col("country") == country_select)

# grafico aspettativa di vita media
life_exp_chart = (
    alt.Chart(df_filtered.filter(pl.col("metric") == "life_exp_mean"))
    .mark_line(color="blue", point=True)
    .encode(
        x=alt.X("year:O", title="Anno"),
        y=alt.Y("value:Q", title="Aspettativa di Vita Media", scale=alt.Scale(zero=False)),
        tooltip=["year", "value"]
    )
)

# grafico tasso di lavoratori a rischio di povertà medio
poverty_chart_p = (
    alt.Chart(df_filtered.filter(pl.col("metric") == "poverty_rate_mean"))
    .mark_line(color="orange")
    .encode(
        x=alt.X("year:O", title="Anno"),
        y=alt.Y("value:Q", title="Tasso di Povertà Medio", 
                scale=alt.Scale(zero=False), 
                axis=alt.Axis(titleColor="orange")),
        tooltip=["year", "value"]
    )
    .transform_calculate(  # serve per avere un asse separato
        Value="datum.Value * 1"
    )
)
# punti per tasso di lavoratori a rischio di povertà medio
points_poverty = (
    alt.Chart(df_filtered_join)
    .mark_point(color="orange", shape="diamond", fill="orange")
    .encode(
        x=alt.X("year:O"),
        y=alt.Y("poverty_rate_mean:Q"),
        tooltip=["year", "poverty_rate_mean"]
    )
)
# combina i due grafici
poverty_chart = poverty_chart_p + points_poverty
chart = (
    alt.layer(
        life_exp_chart,
        poverty_chart
    )
    .resolve_scale(
        y="independent"  # assi y indipendenti
    )
    .properties(
        width=800,
        height=400,
    )
)
st.altair_chart(chart, use_container_width=True)

# correlazione
correlation = df_filtered_join.select([
    pl.corr("life_exp_mean", "poverty_rate_mean", method="pearson").round(2)
])
correlation_value = correlation.to_series().item(0)

st.markdown(f"""
            Paese selezionato: {country_select}

            Correlazione: {correlation_value}

            Il grafico presenta due scale verticali:

            L'asse sinistro (in blu) rappresenta l'aspettativa di vita media in anni.
            L'asse destro (in arancione) mostra il tasso di lavoratori a rischio di povertà medio (%).
            Le linee tracciate, per il paese selezionato, seguono i valori osservati per entrambe le metriche nel corso degli anni.

            La visualizzazione consente di individuare eventuali correlazioni o divergenze tra i due trend,
            mostrando come l'andamento socioeconomico potrebbe influenzare la salute pubblica.

            Il grafico evidenzia che, per molti paesi europei, emerge una relazione positiva più o meno stretta tra
            aspettativa di vita media e tasso di lavoratori a rischio povertà medio. E' però importante ricordare che 
            **correlazione non implica causalità** e che ci potrebbero essere altri fattori non osservati, come accesso
            ai servizi sanitari, educazione e politiche pubbliche, che possono influenzare il risultato.

            Una mia possibile interpretazione dei risulati è che col tempo l'igiene personale e i servizi sanitari
            sono migliorati e diventati più accessibili, quindi anche chi è **considerato** a rischio di povertà
            può permettersi acqua potabile, cibo e medicine. Portando quindi a influire di più sulla **qualità**
            della vita rispetto alla sua **durata**.
""")

### CONCLUSIONI
if st.button("Leggi le conclusioni del progetto"):
    st.markdown(f"""
                Le principali conclusioni, che sono messe in evidenza dall'analisi dei dati
                sull'aspettativa di vita e il tasso di lavoratori a rischio povertà nei paesi europei, sono:

                - L'aspettativa di vita sembra sia cresciuta costantemente dal 1960,
                grazie a migliori condizioni sanitarie e socioeconomiche. Si riscontrano però anche periodi
                di cali temporanei, che si possono attribuire a fattori quali guerre o pandemie (es. covid 2020/2021).
                - Le donne mostrano una maggiore aspettativa di vita rispetto uomini in tutti i paesi analizzati,
                ma il divario tra i sessi varia significativamente da paese a paese.
                - E' emersa una correlazione positiva più o meno evidente tra il tasso di povertà dei lavoratori e l'aspettativa di vita,
                per alcuni paesi europei, mentre per altri incorrelazione o una lieve correlazione negativa,
                questo può indicare che ci sono altri fattori non osservati che giocano un ruolo importante.
                E siccome correlazione non implica causalità, potrebbe essere un caso di correlazione spuria tra le
                due variabili osservate.

                Questi risultati offrono una panoramica utile per comprendere l'evoluzione della salute pubblica in Europa,
                fornendo spunti per ulteriori analisi.
""")

st.markdown(f"""
    Dataset: 'Life expectancy by age and sex'  
    Fonte: [Eurostat :chart:](https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en&category=demo.demo_mor)
            
    Dataset: 'In-work at-risk-of-poverty rate by age and sex'  
    Fonte: [Eurostat :chart:](https://ec.europa.eu/eurostat/databrowser/view/ilc_iw01/default/table?lang=en&category=livcon.ilc.ilc_ip.ilc_iw)
""")