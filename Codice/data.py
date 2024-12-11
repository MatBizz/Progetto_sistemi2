import polars as pl
import gzip

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
            pl.col("country").str.replace(r"[\[\]]", "").alias("country")
        )
        .filter(pl.col("age") == "Y_LT1") # .filter(pl.col("age").is_in(["Y_LT1"]))
        .drop_nulls("life_exp")
    )
    df = df.select(
    pl.col("*").exclude("age", "freq", "unit"))
    
    return df

"""
    df = df.with_columns(
        pl.when(pl.col("age") == 1)
            .then(pl.lit("<=1 anno"))
        .when((pl.col("age")>=2) & (pl.col("age")<=12))
            .then(pl.lit("2-12 anni"))
        .when((pl.col("age")>=13) & (pl.col("age")<=20))
            .then(pl.lit("13-20 anni"))
        .when((pl.col("age")>=21) & (pl.col("age")<=30))
            .then(pl.lit("21-30 anni"))
        .when((pl.col("age")>=31) & (pl.col("age")<=50))
            .then(pl.lit("31-50 anni"))
            .when(pl.col("age") > 50)
        .then(pl.lit(">=50 anni"))
        .alias("Fascia età")
        )
"""


df = life("Data\estat_demo_mlexpec.tsv.gz")
#print(df)


def work(url):
    pass