import polars as pl

def life(url): # Life expectancy by age and sex
    raw = pl.read_csv(url,
                        separator="\t",
                        null_values=["", ":", ": "])
    
    df = (
        raw
        # seleziona la colonna aggregata
        .select(
            pl.col("freq,unit,sex,age,geo\\TIME_PERIOD")
                .str.split(",") # separazione sul testo della colonna selezionata su ","
                .list.to_struct(fields=["freq", "unit", "sex", "age", "country"]) 
                .alias("combined"), # quello che si vuole tanto viene eliminata
            pl.col("*").exclude("freq,unit,sex,age,geo\\TIME_PERIOD") # eliminata la colonna con tutte le var. aggregate
        )
        .unnest("combined")# una nuova colonna per ogni variabile
        #
        .unpivot( # trasformiamo gli anni che sono variabili, in modalità delle osservazioni
                  # i valori che assomevano diventano modalità della nuova variable "life_exp"
            index=["freq", "unit", "sex", "age", "country"],# variabili(colonne) che non vengono toccate
            variable_name="year",# nuova colonna che contiene i nomi delle variabili non in index
            value_name="life_exp"# nuova colonna che contiene i valori delle colonne non in index
        )
        #
        .with_columns(
            
            pl.col("year").str.replace(" ", "").cast(pl.Int64), # sostituisce spazi con ""
            # qualsiasi cosa che non sia un numero o un punto decimale -> ""

            # sostituisce tutto tranne numeri e "." con ""
            pl.col("life_exp").str.replace_all(r"[^0-9\.]", "").cast(pl.Float64),#[^   ] negazione, fuori da [] indica
            # una parola che unizia con x - ^x --- \ carattere di escape --- senza r" " \\ 
            pl.col("country").str.replace(r"[\[\]]", "").alias("country"), #sostituisce [] con "", togliendole
            # togliamo da "age" tutto ciò che non sono numeri
            pl.col("age").str.replace_all(r"[^0-9]", "").cast(pl.Int64)
        )
        .drop_nulls("life_exp") # togliamo per sicurezza eventuali valori nulli di "life_exp"
    )
    df = df.select(
    pl.col("*").exclude("freq", "unit")) # togliamo le colonne "freq" e "unit" che non ci servono per le analisi
    
    return df

def work(url): #In-Work Poverty Rate
    raw = pl.read_csv(url,
                        separator="\t",
                        null_values=["", ":", ": "])

    df = (raw
        .select(
            pl.col("freq,wstatus,sex,age,unit,geo\\TIME_PERIOD")
                .str.split(",")# separazione della colonna su ","
                .list.to_struct(fields=["freq", "wstatus", "sex", "age", "unit", "geo"])
                .alias("combined"),
            pl.col("*").exclude("freq,unit,sex,age,geo\\TIME_PERIOD")# togliamo la colonna iniziale aggregata
        )
        .unnest("combined")# una nuova colonna per ogni variabile
        .unpivot(
            index=["freq", "wstatus", "sex", "age", "unit", "geo"],# variabili(colonne) che non vengono toccate
            variable_name="year",# nuova colonna che contiene i nomi delle variabili non in index
            value_name="poverty_rate"# nuova colonna che contiene i valori delle colonne non in index
        )
        .with_columns(
            pl.col("year").str.extract(r"(\d{4})").cast(pl.Int64), # estrae solo valori con 4 cifre consecutive
            pl.col("poverty_rate").str.extract(r"(\d+(\.\d+)?)").cast(pl.Float64), # estrae numeri interi o con il punto
            # estrae più cifre prima del . e poi più cifre dopo se ci sono(?)
            pl.col("geo").str.replace(r"[\[\]]", "").alias("country") #sostituisce [] con ""
        )
        .drop_nulls("year")# togliamo per sicurezza eventuali valori nulli di "year"
        .drop_nulls("poverty_rate")# togliamo per sicurezza eventuali valori nulli di "poverty_rate"
    )
    return df