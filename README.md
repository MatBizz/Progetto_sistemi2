# RUN
uv run streamlit run app.py

Alcune volte su windows bisogna usare: uv run -n streamlit run app.py

# OBIETTIVO
Analizzare l'aspettativa di vita per studiare un indice della salute generale per i diversi paesi europei e fare un confronto tra sesso, anno e paese. Alla fine si studia se esiste una correlazione tra l'aspettativa di vita e il tasso di povertà dei lavoratori.

# OSSERVAZIONI
1) Le prove sono state eseguite con il tema chiaro

2) Le analisi sono state effettuate con la sola fascia d'età <=1 anno, tranne se specificato diversamente in singole analisi,
   per diversi motivi, i principali sono una maggiore chiarezza dei risultati e perché rappresenta un indicatore della salute
   generale della popolazione, strettamente legato alla mortalità infantile, all'igiene, alla sanità pubblica e al contesto socioeconomico.

3) La visualizzazione grafica della cartina d'Europa l'ho fatta utilizzando Plotly prima della lezione del 11/12/24 che spiegava come
   implementarla con altair/geopandas. Ho deciso di tenerla in questo formato dato che il risultato finale mi sembra buono e sopratutto funzionante, considerando anche il tempo che ci avevo già dedicato.
   Inoltre ho scelto una cartina limitata alla sola Europa dato che il dataset contiene esclusivamente osservazioni relative ai paesi europei.
   Come proiezione è stata utilizzata la "azimuthal equal area", per preservare le aree.

4) Per l'analisi della correlazione è stato fatto inizialmente uno scatterplot, con l'utente che poteva scegliere l'anno
   e ogni punto rappresentava un paese. Il grafico è stato scartato data la bassa o nulla correlazione che dava vita a
   soli grafici con nuvole di punti sparpagliati e quindi poco informativi.
   E' stato scelto l'altro grafico per avere inoltre a disposizione l'andamento nel tempo delle due variabili.

# PREPROCESSING
I due dataset utilizzati, entrambi provenienti da Eurostat, presentavano una struttura iniziale simile, non conforme al formato tidy.
Nello specifico:
- Le variabili erano aggregate in un'unica colonna, che è stata suddivisa in più colonne, ognuna corrispondente a una singola variabile.
- Gli anni erano rappresentati come colonne, ciascuna contenente le osservazioni relative all'aspettativa di vita.
  Tramite un'operazione di unpivot, sono state create la variabile year, contenente gli anni come modalità e la variabile life_exp, derivata dalle osservazioni presenti nelle colonne degli anni.

Lo stesso processo è stato applicato al secondo dataset, con la differenza che è stata creata la variabile poverty_rate per rappresentare le osservazioni originali.

# CONCLUSIONI
Le principali conclusioni, che sono messe in evidenza dall'analisi dei dati
sull'aspettativa di vita e il tasso di lavoratori a rischio povertà nei paesi europei, sono:

- L'aspettativa di vita sembra sia cresciuta costantemente dal 1960,
  grazie a migliori condizioni sanitarie e socioeconomiche. Si riscontrano però anche periodi
  di cali temporanei, che si possono attribuire a fattori quali guerre o pandemie (es. covid 2020/2021).
- Le donne mostrano una maggiore aspettativa di vita rispetto uomini in tutti i paesi analizzati,
  ma il divario tra i sessi varia significativamente da paese a paese.
- Per alcuni paesi europei è emersa una correlazione positiva più o meno evidente tra il tasso di povertà dei lavoratori e 
  l'aspettativa di vita, mentre per altri incorrelazione o una lieve correlazione negativa,
  questo può indicare che ci sono altri fattori non osservati che giocano un ruolo importante.
  E siccome correlazione non implica causalità, potrebbe essere un caso di correlazione spuria tra le due variabili osservate.

Questi risultati offrono una panoramica utile per comprendere l'evoluzione della salute pubblica in Europa,
fornendo spunti per ulteriori analisi.

# FONTI
**Dataset**: 'Life expectancy by age and sex'

**Descrizione**: Questo dataset proviene da eurostat.
             Misura l'aspettativa di vita, suddivisa per anno, paese (esclusivamente del continente europeo), sesso ed età.
             Il periodo coperto è dal 1960 al 2023.

**Fonte**: https://ec.europa.eu/eurostat/databrowser/view/demo_mlexpec/default/table?lang=en&category=demo.demo_mor
            
**Dataset**: 'In-work at-risk-of-poverty rate by age and sex'

**Descrizione**: Questo dataset proviene da eurostat.
             Misura il tasso dei lavoratori a rischio di povertà, suddivisa per anno, paese (esclusivamente del continente europeo), sesso ed età (fascie di età).
             Il periodo coperto è dal 2003 al 2023.

**Fonte**: https://ec.europa.eu/eurostat/databrowser/view/ilc_iw01/default/table?lang=en&category=livcon.ilc.ilc_ip.ilc_iw