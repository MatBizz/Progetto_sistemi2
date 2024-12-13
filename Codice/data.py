import polars as pl

def life(url):
    raw = pl.read_csv(url,
                        separator="\t",
                        null_values=["", ":", ": "])

    df = (
        raw
        #
        .select(
            pl.col("freq,unit,sex,age,geo\\TIME_PERIOD")
                .str.split(",")
                .list.to_struct(fields=["freq", "unit", "sex", "age", "country"])
                .alias("combined"), # quello che si vuolle tanto viene eliminata
            pl.col("*").exclude("freq,unit,sex,age,geo\\TIME_PERIOD")
        )
        .unnest("combined")
        #
        .unpivot(
            index=["freq", "unit", "sex", "age", "country"],
            variable_name="year",
            value_name="life_exp"
        )
        #
        .with_columns(
            
            pl.col("year").str.replace(" ", "").cast(pl.Int64), # importante ordine di " " e ""
            # qualsiasi cosa che non sia un numero o un punto decimale -> ""
            pl.col("life_exp").str.replace_all(r"[^0-9\.]", "").cast(pl.Float64),#[^   ] negazione, fuori da [] indica
            # una parola che unizia con x - ^x --- \ carattere di escape --- senza r" " \\ 
            pl.col("country").str.replace(r"[\[\]]", "").alias("country"),

            pl.col("age").str.replace_all(r"[^0-9]", "").cast(pl.Int64)
        )
        .drop_nulls("life_exp")
    )
    df = df.select(
    pl.col("*").exclude("freq", "unit"))
    
    return df




def work(url): #In-Work Poverty Rate
    raw = pl.read_csv(url,
                        separator="\t",
                        null_values=["", ":", ": "])
    df = (raw
        .select(
            pl.col("freq,wstatus,sex,age,unit,geo\\TIME_PERIOD")
                .str.split(",")
                .list.to_struct(fields=["freq", "wstatus", "sex", "age", "unit", "geo"])
                .alias("combined"), # quello che si vuolle tanto viene eliminata
            pl.col("*").exclude("freq,unit,sex,age,geo\\TIME_PERIOD")
        )
        .unnest("combined")
        .unpivot(
            index=["freq", "wstatus", "sex", "age", "unit", "geo"],
            variable_name="year",
            value_name="poverty_rate"
        )
        .with_columns(
            pl.col("year").str.extract(r"(\d{4})").cast(pl.Int64), # estrae solo valori con 4 numeri
            pl.col("poverty_rate").str.extract(r"(\d+(\.\d+)?)").cast(pl.Float64), # estrae numeri interi o con il punto
            pl.col("geo").str.replace(r"[\[\]]", "").alias("country")
        )
        .drop_nulls("year")
        .drop_nulls("poverty_rate")
    )
    return df