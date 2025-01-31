from socket import gethostname
from flask import Flask, request, jsonify
# Flask: Framework web leggero per creare applicazioni web in Python.
# request: Modulo per gestire le richieste HTTP.
# jsonify: Funzione per convertire i dati in formato JSON.

from flask_sqlalchemy import SQLAlchemy
# Flask-SQLAlchemy: Estensione per Flask che semplifica l'integrazione con i database SQL.

from collections import defaultdict

from sqlalchemy import and_
# SQLAlchemy: Libreria SQL per Python che fornisce un toolkit ORM (Object-Relational Mapping).
# and_: Funzione per combinare più condizioni nelle query SQL.

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# Flask-JWT-Extended: Estensione per Flask che aggiunge il supporto per JSON Web Tokens (JWT).
# JWTManager: Gestore per configurare e gestire i JWT.
# create_access_token: Funzione per creare un token di accesso JWT.
# jwt_required: Decoratore per proteggere le route con autenticazione JWT.
# get_jwt_identity: Funzione per ottenere l'identità dell'utente dal token JWT.

# Un sistema di autenticazione solido è fondamentale per garantire la sicurezza di un'applicazione web.
# L'autenticazione è il processo di verifica dell'identità di un utente, assicurando che solo gli utenti autorizzati possano accedere a determinate risorse o eseguire determinate azioni.

# Flask-JWT-Extended utilizza JSON Web Tokens (JWT) per gestire l'autenticazione.
# I JWT sono token compatti, sicuri e auto-contenuti che possono essere utilizzati per autenticare le richieste tra un client e un server.
# I vantaggi di utilizzare JWT includono:
# - Sicurezza: I JWT possono essere firmati e crittografati per garantire che i dati non siano alterati e che solo le parti autorizzate possano leggerli.
# - Scalabilità: I JWT sono auto-contenuti, il che significa che tutte le informazioni necessarie per autenticare un utente sono incluse nel token stesso. Questo riduce la necessità di memorizzare sessioni sul server, migliorando la scalabilità.
# - Flessibilità: I JWT possono essere utilizzati in diversi contesti, come autenticazione web, API e microservizi.

# JWTManager: Questo gestore è responsabile della configurazione e gestione dei JWT nell'applicazione Flask.
# create_access_token: Questa funzione crea un token di accesso JWT che può essere utilizzato per autenticare le richieste future.
# jwt_required: Questo decoratore protegge le route, richiedendo che l'utente sia autenticato tramite un token JWT valido per accedere alla risorsa.
# get_jwt_identity: Questa funzione estrae l'identità dell'utente dal token JWT, permettendo di identificare l'utente autenticato.

# L'implementazione di un sistema di autenticazione solido con Flask-JWT-Extended aiuta a proteggere l'applicazione da accessi non autorizzati, garantendo che solo gli utenti legittimi possano accedere alle risorse sensibili.
# Questo è particolarmente importante per applicazioni che gestiscono dati personali, finanziari o altre informazioni sensibili, contribuendo a mantenere la fiducia degli utenti e a rispettare le normative di sicurezza.

from flask_cors import CORS
# Flask-CORS: Estensione per Flask che permette di abilitare le richieste CORS (Cross-Origin Resource Sharing).

from werkzeug.security import generate_password_hash, check_password_hash
# Werkzeug: Libreria WSGI per Python che fornisce utilità per la sicurezza.
# generate_password_hash: Funzione per generare hash delle password.
# check_password_hash: Funzione per verificare le password hashate.

# Utilizziamo `generate_password_hash` per creare hash sicuri delle password degli utenti.
# Questo è un requisito fondamentale per proteggere le password memorizzate nel database.
# L'hashing delle password è una pratica di sicurezza standard che aiuta a proteggere le informazioni sensibili degli utenti.
# In caso di violazione del database, gli hash delle password sono molto più difficili da decifrare rispetto alle password in chiaro.

# Utilizziamo `check_password_hash` per verificare le password fornite dagli utenti durante il login.
# Questo assicura che le password memorizzate non siano mai decifrate o esposte in chiaro.

# L'uso di hashing delle password aiuta a essere conformi a diverse normative di sicurezza, come:
# - GDPR (Regolamento Generale sulla Protezione dei Dati) nell'Unione Europea, che richiede la protezione dei dati personali degli utenti.
# - CCPA (California Consumer Privacy Act) negli Stati Uniti, che impone requisiti simili per la protezione dei dati personali.
# - PCI-DSS (Payment Card Industry Data Security Standard), che richiede la protezione delle informazioni sensibili, comprese le credenziali di accesso.

# L'adozione di queste pratiche di sicurezza aiuta a proteggere gli utenti e a mantenere la fiducia nel sistema, riducendo il rischio di violazioni dei dati e le relative conseguenze legali e reputazionali.

from datetime import datetime, timedelta
# datetime: Modulo per lavorare con date e orari.
# timedelta: Classe per rappresentare la differenza tra due date o orari.

from dotenv import load_dotenv
# python-dotenv: Libreria per caricare le variabili d'ambiente da un file .env.

import os
# os: Modulo per interagire con il sistema operativo, ad esempio per accedere alle variabili d'ambiente.

import secrets
# secrets: Modulo per generare numeri casuali sicuri per la crittografia.
# Ho utilizzato secrets per generare una chiave segreta casuale per il token JWT di backup alla mancanna di una chiave segreta nel file .env.

import uuid
# uuid: Modulo per generare identificatori univoci universali (UUID).
# Ho dovuto implementare uuid perché in precedenza assegnavo un ID utente intero autoincrementale alla creazione dell'utente.
# Questo creava problemi con il token JWT, poiché campo "subject" (user ID) all'interno del token decodificato doveva essere una stringa e non un intero.
# Dopo aver perso qualche ora sul debug di questo errore, ho deciso di utilizzare UUID per generare un ID utente come stringa.
# Questo ha risolto il problema, poiché UUID genera identificatori univoci in formato stringa, compatibili con i requisiti del token JWT.

app = Flask(__name__)

# Abilito CORS
CORS(app)

# Carico le variabili d'ambiente dall' .env file
load_dotenv()

secure_key = secrets.token_hex(16)
# Configuro il database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', secure_key)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Verifico che tutte le variabili d'ambiente richieste siano presenti
required_env_vars = [
    'ROOM_STANDARD_PRICE', 'ROOM_SUPERIOR_PRICE', 'ROOM_SUITE_PRICE',
    'ROOM_STANDARD_CAPACITY', 'ROOM_SUPERIOR_CAPACITY', 'ROOM_SUITE_CAPACITY',
    'ROOM_STANDARD_QUANTITY', 'ROOM_SUPERIOR_QUANTITY', 'ROOM_SUITE_QUANTITY'
]

for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Manca variabile d'ambiente: {var}")

####################################################
# Definizione dei modelli
####################################################
# Modello Utente
class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'user' o 'admin'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Questo modello rappresenta gli utenti del sistema.
    # Ogni utente ha un ID univoco, un nome utente, un'email, una password, un nome, un cognome e un ruolo.
    # Il ruolo può essere 'user' o 'admin'.
    # Le date di creazione e aggiornamento vengono gestite automaticamente.

# Modello Stanza
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    bookings = db.relationship('BookingRooms', backref='room', lazy=True)

    # Questo modello rappresenta le stanze disponibili nell'hotel.
    # Ogni stanza ha un ID univoco, un numero, un prezzo per notte, una capacità e un tipo.
    # La relazione 'bookings' collega le stanze alle prenotazioni.

# Modello Prenotazione
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')  # 'confirmed' o 'canceled'
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    rooms = db.relationship('BookingRooms', backref='booking', lazy=True)

    # Questo modello rappresenta le prenotazioni effettuate dagli utenti.
    # Ogni prenotazione ha un ID univoco, un ID utente, date di check-in e check-out, numero di ospiti e stato.
    # Lo stato può essere 'confirmed' o 'canceled'.
    # Le date di creazione e aggiornamento vengono gestite automaticamente.
    # La relazione 'rooms' collega le prenotazioni alle stanze.

# Modello Prenotazione/Stanza
class BookingRooms(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    # Questo modello rappresenta l'associazione tra prenotazioni e stanze.
    # Ogni associazione ha un ID univoco, un ID prenotazione e un ID stanza.

# Relazioni
    # Un utente può avere molte prenotazioni (user_id in Booking).
    # Questo significa che un singolo utente può effettuare diverse prenotazioni nel tempo.
    # Ad esempio, un utente potrebbe prenotare una stanza per una vacanza estiva e poi fare un'altra prenotazione per un viaggio di lavoro.

    # Una stanza può essere associata a molte prenotazioni (room_id in BookingRooms).
    # Questo è utile perché una stanza può essere prenotata da diversi utenti in periodi di tempo diversi.
    # Ad esempio, la stanza numero 101 potrebbe essere prenotata da un utente per una settimana e poi da un altro utente per la settimana successiva.

    # Una prenotazione può includere molte stanze (booking_id in BookingRooms).
    # Questo permette di gestire prenotazioni che includono più stanze, come nel caso di una famiglia numerosa o di un gruppo di amici che viaggiano insieme.
    # Ad esempio, una prenotazione potrebbe includere sia una stanza standard che una suite per soddisfare le esigenze di tutti i membri del gruppo.

# Motivo delle Relazioni
    # Scalabilità: La struttura relazionale permette di gestire facilmente molte prenotazioni e stanze.
    # Questo è importante perché un hotel può avere molte stanze e molti utenti che effettuano prenotazioni.
    # Tale struttura relazionale assicura che il sistema possa gestire un numero crescente di prenotazioni senza problemi.

    # Integrità dei Dati: Le relazioni esterne garantiscono che le prenotazioni e le stanze siano sempre collegate a utenti e prenotazioni validi.
    # Questo significa che non ci saranno prenotazioni orfane senza un utente associato o stanze prenotate senza una prenotazione valida.

    # Flessibilità: La relazione molti-a-molti tra Booking e Room tramite BookingRooms permette di gestire prenotazioni che includono più stanze, migliorando la flessibilità del sistema.
    # Questo è utile per gestire diverse esigenze degli utenti, come prenotazioni di gruppo o prenotazioni che richiedono stanze di diversi tipi.
    # Ad esempio, un utente potrebbe prenotare una stanza standard per sé e una stanza superior per un collega nello stesso periodo.


####################################################
# Funzioni di utilità
####################################################
def create_rooms():
    # Verifica se ci sono già stanze nel database
    if Room.query.count() == 0:
        rooms = []

        try:
            # Recupera i valori delle variabili d'ambiente e li converte nei tipi appropriati
            standard_price = float(os.getenv('ROOM_STANDARD_PRICE'))
            superior_price = float(os.getenv('ROOM_SUPERIOR_PRICE'))
            suite_price = float(os.getenv('ROOM_SUITE_PRICE'))
            standard_capacity = int(os.getenv('ROOM_STANDARD_CAPACITY'))
            superior_capacity = int(os.getenv('ROOM_SUPERIOR_CAPACITY'))
            suite_capacity = int(os.getenv('ROOM_SUITE_CAPACITY'))
            standard_quantity = int(os.getenv('ROOM_STANDARD_QUANTITY'))
            superior_quantity = int(os.getenv('ROOM_SUPERIOR_QUANTITY'))
            suite_quantity = int(os.getenv('ROOM_SUITE_QUANTITY'))

        # Gestisce gli errori di tipo e di valore delle variabili d'ambiente
        except TypeError as e:
            print(f"Errore: Variabile d'ambiente mancante o non valida: {e}")
            return
        except ValueError as e:
            print(f"Errore: Variabile d'ambiente non valida: {e}")
            return

        # Crea stanze di tipo standard
        for i in range(1, standard_quantity + 1):
            rooms.append(Room(
                number=f"{100+i}",
                price=standard_price,
                capacity=standard_capacity,
                room_type="standard",
            ))

        # Crea stanze di tipo superior
        for i in range(standard_quantity + 1, standard_quantity + superior_quantity + 1):
            rooms.append(Room(
                number=f"{200+i}",
                price=superior_price,
                capacity=superior_capacity,
                room_type="superior",
            ))

        # Crea stanze di tipo suite
        for i in range(standard_quantity + superior_quantity + 1, standard_quantity + superior_quantity + suite_quantity + 1):
            rooms.append(Room(
                number=f"{300+i}",
                price=suite_price,
                capacity=suite_capacity,
                room_type="suite",
            ))

        try:
            # Salva tutte le stanze create nel database
            db.session.bulk_save_objects(rooms)
            db.session.commit()
            print(f"{len(rooms)} stanze create.")
        except Exception as e:
            # Gestisce gli errori durante il salvataggio delle stanze e annulla la transazione
            db.session.rollback()
            print(f"Errore durante la creazione delle stanze: {e}")
    else:
        # Messaggio se le stanze sono già presenti nel database
        print("Le stanze sono già presenti nel database.")

def get_available_rooms(check_in_date, check_out_date):
    try:
        # Converte le date in formato stringa in oggetti datetime
        check_in = datetime.strptime(check_in_date, '%Y%m%d')
        check_out = datetime.strptime(check_out_date, '%Y%m%d')

        # Recupera tutte le stanze dal database
        all_rooms = Room.query.all()

        # Recupera le prenotazioni che si sovrappongono con l'intervallo di date specificato e che non sono cancellate
        overlapping_bookings = Booking.query.filter(
            and_(
                Booking.check_in < check_out,
                Booking.check_out > check_in,
                Booking.status != 'canceled'
            )
        ).all()

        # Ottiene gli ID delle stanze che sono prenotate
        booked_room_ids = {booking_room.room_id for booking in overlapping_bookings for booking_room in booking.rooms}

        # Filtra le stanze prenotate
        available_rooms = [room for room in all_rooms if room.id not in booked_room_ids]

        # Restituisce le stanze disponibili
        return available_rooms
    except Exception as e:
        # Gestisce eventuali errori durante il recupero delle stanze disponibili
        raise Exception(f"Errore durante il recupero delle stanze disponibili: {e}")

def get_user_bookings(user_id):
    try:
        # Recupera tutte le prenotazioni per un dato utente
        bookings = Booking.query.filter_by(user_id=user_id).all()
        
        # Crea una lista di dizionari con i dettagli delle prenotazioni
        bookings_list = [{
            "id": booking.id,
            "check_in": booking.check_in.strftime('%Y%m%d'),
            "check_out": booking.check_out.strftime('%Y%m%d'),
            "guests": booking.guests,
            "status": booking.status,
            "rooms": [{"id": room.room.id, "number": room.room.number, "type": room.room.room_type} for room in booking.rooms]
        } for booking in bookings]
        
        # Restituisce la lista delle prenotazioni
        return bookings_list
    except Exception as e:
        # Gestisce eventuali errori durante il recupero delle prenotazioni
        raise Exception(f"Errore durante il recupero delle prenotazioni: {e}")

def create_booking(user_id, check_in, check_out, guests, room_types):
    try:
        # Verifica la disponibilità delle stanze
        available_rooms = get_available_rooms(check_in, check_out)

        # Raggruppa le stanze disponibili per tipo
        available_rooms_by_type = {}
        for room in available_rooms:
            available_rooms_by_type.setdefault(room.room_type, []).append(room)

        # Seleziona le stanze in base ai tipi richiesti
        selected_rooms = []
        for room_type in room_types:
            if room_type in available_rooms_by_type and available_rooms_by_type[room_type]:
                selected_rooms.append(available_rooms_by_type[room_type].pop(0))
            else:
                raise ValueError(f"Stanze di tipo {room_type} non disponibili per il periodo richiesto")

        # Crea la prenotazione
        check_in_date = datetime.strptime(check_in, '%Y%m%d').date()
        check_out_date = datetime.strptime(check_out, '%Y%m%d').date()
        new_booking = Booking(user_id=user_id, check_in=check_in_date, check_out=check_out_date, guests=guests)
        db.session.add(new_booking)
        db.session.commit()

        # Associa le stanze alla prenotazione
        for room in selected_rooms:
            booking_room = BookingRooms(booking_id=new_booking.id, room_id=room.id)
            db.session.add(booking_room)

        db.session.commit()

        # Calcola il prezzo totale
        staying_days = (check_out_date - check_in_date).days
        total_price = sum(room.price * staying_days for room in selected_rooms)

        # Prepara i dati di risposta
        booked_rooms_info = [{
            "room_id": room.id,
            "room_number": room.number,
            "room_type": room.room_type,
            "price": room.price
        } for room in selected_rooms]

        return {
            "message": "Prenotazione effettuata con successo",
            "booking_id": new_booking.id,
            "check_in": check_in_date.strftime('%Y-%m-%d'),
            "check_out": check_out_date.strftime('%Y-%m-%d'),
            "guests": guests,
            "rooms": booked_rooms_info,
            "total_price": total_price
        }
    except Exception as e:
        # Gestisce eventuali errori durante la creazione della prenotazione
        db.session.rollback()
        raise Exception(f"Errore durante la creazione della prenotazione: {e}")

def cancel_booking_by_id(booking_id, user_id):
    try:
        # Recupera l'utente dal database
        user = User.query.get(user_id)
        if not user:
            raise ValueError("Utente non trovato")

        # Se l'utente è un admin, può cancellare qualsiasi prenotazione
        if user.role == 'admin':
            booking = Booking.query.filter_by(id=booking_id).first()
        else:
            # Altrimenti, può cancellare solo le proprie prenotazioni
            booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

        if not booking:
            raise ValueError("Prenotazione non trovata")

        if booking.status == 'canceled':
            raise ValueError("La prenotazione è già stata cancellata")

        # Imposta lo stato della prenotazione a 'canceled'
        booking.status = 'canceled'
        db.session.commit()

        # Prepara i dettagli delle stanze prenotate
        booked_rooms_info = [{
            "room_id": room.room.id,
            "room_number": room.room.number,
            "room_type": room.room.room_type,
            "price": room.room.price
        } for room in booking.rooms]

        # Restituisce i dettagli della prenotazione cancellata
        return {
            "booking_id": booking.id,
            "check_in": booking.check_in.strftime('%Y-%m-%d'),
            "check_out": booking.check_out.strftime('%Y-%m-%d'),
            "guests": booking.guests,
            "rooms": booked_rooms_info,
            "status": booking.status
        }
    except Exception as e:
        raise Exception(f"Errore durante la cancellazione della prenotazione: {e}")

def modify_booking(booking_id, user_id, new_check_in, new_check_out, new_guests, new_room_types):
    try:
        # Cancella la prenotazione esistente
        cancel_booking_by_id(booking_id, user_id)

        # Crea una nuova prenotazione
        new_booking_details = create_booking(user_id, new_check_in, new_check_out, new_guests, new_room_types)

        # Restituisce i dettagli della nuova prenotazione
        return new_booking_details
    except Exception as e:
        raise Exception(f"Errore durante la modifica della prenotazione: {e}")

def get_room_suggestions(check_in, check_out, guests, rooms_requested):
    try:
        # Verifica la disponibilità delle stanze
        available_rooms = get_available_rooms(check_in, check_out)

        # Verifica se la capacità totale delle stanze disponibili può ospitare gli ospiti
        total_capacity = sum(room.capacity for room in available_rooms)
        if total_capacity < guests:
            raise ValueError("Non ci sono abbastanza camere disponibili per ospitare il numero di ospiti richiesto.")

        # Verifica se ci sono abbastanza stanze per soddisfare la richiesta
        if rooms_requested > len(available_rooms):
            raise ValueError("Non ci sono abbastanza camere disponibili per soddisfare la richiesta.")

        # Raggruppa le stanze disponibili per tipo e conta il numero di stanze per tipo
        rooms_by_type = defaultdict(list)
        room_type_counts = defaultdict(int)
        for room in available_rooms:
            rooms_by_type[room.room_type].append(room)
            room_type_counts[room.room_type] += 1

        # Trova una combinazione valida di stanze che possa ospitare il numero di ospiti e il numero di stanze richiesto
        valid_combinations = []
        for room_type, rooms in rooms_by_type.items():
            rooms.sort(key=lambda room: room.price)  # Ordina le stanze per prezzo in ordine crescente
            combination = []
            total_capacity = 0
            for room in rooms:
                if len(combination) < rooms_requested and total_capacity < guests:
                    combination.append(room)
                    total_capacity += room.capacity
                if len(combination) == rooms_requested and total_capacity >= guests:
                    break
            if len(combination) == rooms_requested and total_capacity >= guests:
                valid_combinations.append(combination)

        # Seleziona la prima combinazione valida o le prime stanze disponibili se non viene trovata una combinazione valida
        selected_combination = valid_combinations[0] if valid_combinations else available_rooms[:rooms_requested]

        # Assicura che la combinazione selezionata abbia il numero corretto di stanze e possa ospitare gli ospiti
        total_selected_capacity = sum(room.capacity for room in selected_combination)
        if total_selected_capacity < guests:
            additional_rooms_needed = guests - total_selected_capacity
            additional_rooms = [room for room in available_rooms if room not in selected_combination]
            for room in additional_rooms:
                if additional_rooms_needed <= 0:
                    break
                selected_combination.append(room)
                additional_rooms_needed -= room.capacity

        # Calcola il numero di giorni tra check_in e check_out
        check_in_date = datetime.strptime(check_in, '%Y%m%d')
        check_out_date = datetime.strptime(check_out, '%Y%m%d')
        num_days = (check_out_date - check_in_date).days

        # Calcola il costo totale
        total_cost_selected_combination = sum(room.price * num_days for room in selected_combination)

        # Semplifica l'oggetto di output per la combinazione selezionata
        simplified_combination = [{
            "id": room.id,
            "number": room.number,
            "price": room.price,
            "capacity": room.capacity,
            "room_type": room.room_type
        } for room in selected_combination]

        # Semplifica l'oggetto di output per le stanze disponibili
        simplified_available_rooms = [{
            "id": room.id,
            "number": room.number,
            "price": room.price,
            "capacity": room.capacity,
            "room_type": room.room_type
        } for room in available_rooms]

        # Crea un array di oggetti per i conteggi dei tipi di stanza con capacità totale
        room_type_counts_array = [
            {
                "room_type": room_type,
                "count": count,
                "capacity": rooms_by_type[room_type][0].capacity,
                "price": sum(room.price for room in rooms_by_type[room_type]) / count
            }
            for room_type, count in room_type_counts.items()
        ]

        # Restituisce le combinazioni selezionate, le stanze disponibili, i conteggi dei tipi di stanza e il costo totale
        return {
            "selected_combination": simplified_combination,
            "available_rooms": simplified_available_rooms,
            "room_type_counts": room_type_counts_array,
            "total_cost_selected_combination": total_cost_selected_combination
        }
    except Exception as e:
        raise Exception(f"Errore durante il recupero delle stanze disponibili: {e}")


####################################################
# Endpoints
####################################################
# Endpoint per la registrazione di un nuovo utente
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    firstname = data.get('firstName')
    surname = data.get('surname')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Verifica che tutti i dati richiesti siano presenti
    if not all([firstname, surname, username, email, password]):
        return jsonify({"error": "Dati mancanti"}), 400

    # Verifica che l'username non sia già in uso
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username già in uso"}), 400

    # Verifica che l'email non sia già in uso
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email già in uso"}), 400

    # Crea una password hashata
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password, email=email, first_name=firstname, surname=surname)
    try:
        # Aggiunge il nuovo utente al database
        db.session.add(new_user)
        db.session.commit()
        # Crea un token di accesso per l'utente registrato
        access_token = create_access_token(identity=new_user.id)
        return jsonify({"message": "Utente registrato con successo.", "access_token": access_token, "firstName": new_user.first_name, "surname": new_user.surname}), 201
    except Exception as e:
        # Gestisce eventuali errori durante la registrazione
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

# Endpoint per il login di un utente
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')  # Può essere l'username o l'email
    password = data.get('password')

    # Verifica che i dati richiesti siano presenti
    if not identifier or not password:
        return jsonify({"error": "Dati mancanti"}), 400

    # Cerca l'utente nel database usando username o email
    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
    if user and check_password_hash(user.password, password):
        # Crea un token di accesso per l'utente autenticato
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
        try:
            # Recupera le prenotazioni dell'utente
            bookings_list = get_user_bookings(user.id)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({
            "access_token": access_token,
            "firstName": user.first_name,
            "surname": user.surname,
            "bookings": bookings_list
        }), 200
    return jsonify({"error": "Credenziali errate."}), 401

# Endpoint per ottenere suggerimenti sulle stanze e le stanze disponibili
@app.route('/rooms_per_type_and_suggestion', methods=['POST'])
def rooms_per_type_and_suggestion():
    data = request.get_json()
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    guests = data.get('guests')
    rooms_requested = data.get('rooms')

    # Verifica che i dati richiesti siano presenti
    if not check_in or not check_out or not guests or not rooms_requested:
        return jsonify({"error": "Dati mancanti"}), 400

    try:
        # Ottiene i suggerimenti sulle stanze
        room_suggestions = get_room_suggestions(check_in, check_out, guests, rooms_requested)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(room_suggestions), 200

# Endpoint per ottenere le prenotazioni di un utente
@app.route('/user_bookings', methods=['GET'])
@jwt_required()
def user_bookings():
    user_id = get_jwt_identity()
    try:
        bookings = get_user_bookings(user_id)
        return jsonify(bookings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint per creare una prenotazione
@app.route('/book', methods=['POST'])
@jwt_required()
def book():
    data = request.get_json()
    user_id = get_jwt_identity()
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    guests = data.get('guests')
    room_types = data.get('room_types')  # Array di tipi di stanza

    # Verifica che i dati richiesti siano presenti
    if not check_in or not check_out or not guests or not room_types:
        return jsonify({"error": "Dati mancanti"}), 400

    try:
        # Crea la prenotazione
        booking_details = create_booking(user_id, check_in, check_out, guests, room_types)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(booking_details), 201

# Endpoint per cancellare una prenotazione
@app.route('/cancel_booking', methods=['POST'])
@jwt_required()
def cancel_booking():
    data = request.get_json()
    booking_id = data.get('booking_id')
    user_id = get_jwt_identity()

    # Verifica che l'ID della prenotazione sia presente
    if not booking_id:
        return jsonify({"error": "Booking ID is required"}), 400

    try:
        # Cancella la prenotazione
        booking_details = cancel_booking_by_id(booking_id, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": "Booking canceled successfully",
        "booking": booking_details
    }), 200

# Endpoint per modificare una prenotazione
@app.route('/modify_booking', methods=['POST'])
@jwt_required()
def modify_booking_endpoint():
    data = request.get_json()
    booking_id = data.get('booking_id')
    new_check_in = data.get('new_check_in')
    new_check_out = data.get('new_check_out')
    new_guests = data.get('new_guests')
    new_room_types = data.get('new_room_types')
    user_id = get_jwt_identity()

    # Verifica che i dati richiesti siano presenti
    if not booking_id or not new_check_in or not new_check_out or not new_guests or not new_room_types:
        return jsonify({"error": "Dati mancanti"}), 400

    try:
        # Modifica la prenotazione
        new_booking_details = modify_booking(booking_id, user_id, new_check_in, new_check_out, new_guests, new_room_types)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(new_booking_details), 201


####################################################
# Inizializzazione dell'applicazione
####################################################
if __name__ == '__main__':
    # Crea un contesto dell'applicazione
    with app.app_context():
        # Definisce il percorso del database
        db_path = os.path.join(app.instance_path, 'hotel.db')
        
        # Verifica se il database esiste
        if not os.path.exists(db_path):
            # Se il database non esiste, lo crea e aggiunge le stanze
            db.create_all()
            create_rooms()
        else:
            # Se il database esiste già, stampa un messaggio e aggiunge le stanze
            print("Il database esiste già.")
            create_rooms()

# Necessario per deploy su pythonanywhere
    if 'liveconsole' not in gethostname():
        app.run()