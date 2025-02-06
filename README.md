# 🏨 Reactive Hotel Backend - Configurazione Ambiente

Questo progetto utilizza variabili d'ambiente per configurare il database, l'autenticazione JWT e la gestione delle stanze.

📌 Come Configurare il File .env

Crea un file .env nella directory principale del progetto e inserisci le seguenti variabili con i valori appropriati.

## 🔑 Autenticazione e Sicurezza

Chiave segreta per la generazione dei token JWT
```
JWT_SECRET_KEY=your_secret_key_here
```

📌 Questa chiave è utilizzata per firmare i token JWT. Se non impostata, verrà generata automaticamente una chiave casuale.

## 🗄️ Configurazione del Database

Connessione al database SQLite (modifica se si usa un database diverso)
```
SQLALCHEMY_DATABASE_URI=sqlite:///hotel.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

📌 Se si utilizza un database differente da SQLite, sostituire l'URI con la stringa di connessione appropriata (es. PostgreSQL, MySQL, ecc.).

## 🏠 Configurazione delle Stanze

### Prezzi per notte delle stanze (in valuta locale)
```
ROOM_STANDARD_PRICE=100.0
ROOM_SUPERIOR_PRICE=150.0
ROOM_SUITE_PRICE=250.0
```

### Capacità massima di ogni tipologia di stanza
```
ROOM_STANDARD_CAPACITY=2
ROOM_SUPERIOR_CAPACITY=3
ROOM_SUITE_CAPACITY=4
```

### Numero totale di stanze disponibili per ogni tipologia
```
ROOM_STANDARD_QUANTITY=10
ROOM_SUPERIOR_QUANTITY=15
ROOM_SUITE_QUANTITY=5
```

📌 Questi valori definiscono le caratteristiche delle stanze e possono essere modificati in base alle esigenze dell'hotel.

## 🚀 Esegui il Progetto

Dopo aver creato il file .env, installa le dipendenze ed esegui l'applicazione:

```
pip install -r requirements.txt
python app.py
```

Ora il backend è pronto per gestire l'hotel! 🏨🚀
