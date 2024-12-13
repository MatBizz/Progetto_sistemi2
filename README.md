# RUN
uv run streamlit run .\Codice\app.py

# OBIETTIVO
Analizzare l'aspettativa di vita per studiare un indice della salute generale per i diversi paesi europei e fare un confronto tra sesso, anno e paese, con l'aggiunta di un dataset sulla tasso di povertà dei lavoratori dove si studia se esiste una correlazione con l'aspettativa di vita.

Le analisi sono state effettuate con la sola fascia d'età <1 anno, tranne se specificato diversamente in singole analisi, per diversi
motivi, i principali sono una maggiore chiarezza dei risultati e perché rappresenta un indicatore della salute generale della popolazione, strettamente legato alla mortalità infantile e al contesto socioeconomico.

# Osservazioni

Le prove sono state eseguite con il tema chiaro

La visualizzazione grafica della cartina d'Europa l'ho fatta utilizzando Plotly prima della lezione del 11/12/24 che spiegava come implementarla con altair/geopandas. Ho deciso di tenerla in questo formato dato che il risultato finale mi sembra buono e sopratutto funzionante, considerando anche il tempo che ci avevo già dedicato.
Inoltre ho scelto una cartina limitata alla sola Europa dato che il dataset contiene esclusivamente osservazioni relative ai paesi europei.