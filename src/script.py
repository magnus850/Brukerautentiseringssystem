import mariadb
import bcrypt
import pwinput
import cutie
from dotenv import load_dotenv
import os

load_dotenv(
)

max_passord_lengde = 24
min_passord_lengde = 6
max_brukernavn_lengde = 15    
min_brukernavn_lengde = 6

conn = mariadb.connect(
    user = os.getenv('DB_BRUKER'),
    password= os.getenv('DB_PASSORD'),
    host = os.getenv('DB_HOST'),
    database = os.getenv('DB'),
    unix_socket = '/opt/homebrew/var/mysql/mysql.sock'
    )

cur = conn.cursor()

ja_nei = ['ja',
          'nei']

def lag_bruker():
    while True:
        nytt_brukernavn = input('Brukernavn(6-18): ')
        if min_brukernavn_lengde <= len(nytt_brukernavn) <= max_brukernavn_lengde:
            break
        print('Hold brukernavnlengde innen 6-18 tegn')
    
    #sjekker om brukernavn allerede fins
    cur.execute('select bruker from brukere where bruker = %s',
                (nytt_brukernavn,))
    if cur.fetchone() != None:
        print('Brukernavn er tatt, velg et annet')
        lag_bruker()
        return
    else:
        while True:
            tall = 0
            nytt_passord = pwinput.pwinput(prompt='Passord(6-24): ', mask = '*')
            for tegn in list(nytt_passord):
                if tegn.isdigit():
                    tall += 1
            if min_passord_lengde >= len(nytt_passord):
                print('Hold passorlengde innen 6-24 tegn')
            if max_passord_lengde <= len(nytt_passord):
                print('Hold passorlengde innen 6-24 tegn')
            if tall < 3:
                print('Passord må inneholde minst 3 tall')
            if min_passord_lengde <= len(nytt_passord) <= max_passord_lengde and tall >= 3:
                break
            
        passord_hashing(nytt_passord, nytt_brukernavn, None, None, None)
    
    
def logg_inn():
    while True:
        brukernavn = input('Brukernavn: ')
        if min_brukernavn_lengde <= len(brukernavn) <= max_brukernavn_lengde:
            break
        print('Hold brukernavnlengde innen 6-18 tegn')
    
    cur.execute(
        'SELECT id, passord FROM brukere WHERE bruker = %s',
        (brukernavn,))
    resultat = cur.fetchone()
    if resultat:
        print('Finnes ikke bruker med det brukernavnet')
        print('Prøv et annet brukernavn?')
        ja = ja_nei[cutie.select(ja_nei)]
        if ja == 'ja':
            logg_inn()
        if ja == 'nei':
            lag_bruker_logg_inn()
        return
    if resultat:
        logg_inn_passord(resultat)
        
def logg_inn_passord(resultat):
    while True:
        passord = pwinput.pwinput(prompt='Passord: ', mask = '*')
        if min_passord_lengde <= len(passord) <= max_passord_lengde:
            break

            
    liste = list(resultat)
    passord_hashing(passord, None, liste[0], liste[1], resultat)
        
        
def registrer_bruker(passord, brukernavn):
    cur.execute('insert into brukere (bruker, passord) values (%s, %s)',
        (brukernavn, passord))
    conn.commit()
    if cur.fetchone:
        print(f'Du er nå logget inn som {brukernavn}')
        cur.execute('select id from brukere where bruker = %s', (brukernavn,))
        id = list(cur.fetchone(
        ))
        endre_passord_eller_logg_ut(id)


def passord_hashing(input_passord, input_brukernavn, id, db_passord, resultat):
    byte_passord = input_passord.encode('utf-8')
    salt = bcrypt.gensalt()
    hasha_passord = bcrypt.hashpw(byte_passord, salt)
    hasha_passord_string = hasha_passord.decode('utf-8')
    
    #nytt passord
    if input_brukernavn == None and db_passord == None:
        registrer_nytt_passord(hasha_passord_string, id)
        return

    #sjekke passord
    if input_brukernavn == None:
        input_byte = input_passord.encode('utf-8')
        passord_byte = db_passord.encode('utf-8')
        if bcrypt.checkpw(input_byte, passord_byte):
            print(f'Du er logget inn')
            endre_passord_eller_logg_ut(id)
            return
        else: 
            print('Feil passord, prøv på nytt?')
            ja = ja_nei[cutie.select(ja_nei)]
            if ja == 'ja':
                logg_inn_passord(resultat)
            if ja == 'nei':
                lag_bruker_logg_inn()

    registrer_bruker(hasha_passord_string, input_brukernavn)
    
muligheter =[
    'Endre passord',
    'Logg ut'
]

def endre_passord_eller_logg_ut(id):
    mul = muligheter[cutie.select(muligheter)]
    if mul == 'Logg ut':
        print('Du er logget ut')
        lag_bruker_logg_inn()
        return
    if mul == 'Endre passord':
        while True:
            tall = 0
            nytt_passord = pwinput.pwinput(prompt='Passord(6-24): ', mask = '*')
            for tegn in list(nytt_passord):
                if tegn.isdigit():
                    tall += 1
            if min_passord_lengde >= len(nytt_passord):
                print('Hold passorlengde innen 6-24 tegn')
            if max_passord_lengde <= len(nytt_passord):
                print('Hold passorlengde innen 6-24 tegn')
            if tall < 3:
                print('Passord må inneholde minst 3 tall')
            if min_passord_lengde <= len(nytt_passord) <= max_passord_lengde and tall >= 3:
                break
        passord_hashing(nytt_passord, None, id, None, None)
        return
        
        
def registrer_nytt_passord(passord, id):
    cur.execute(
    'UPDATE brukere SET passord = %s WHERE id = %s',
    (passord, id))
    conn.commit()
    if cur.fetchone:
        print('Du har endret passord')
        endre_passord_eller_logg_ut(id)
    
print('Velkommen til Kurdistans offisielle brukerautentiseringssystem!')
valg = [
    'Lag bruker',
    'Logg inn',
    'Avslutt'
]

def lag_bruker_logg_inn():
    valgt_valg = valg[cutie.select(valg)]
    if valgt_valg == 'Lag bruker':
        lag_bruker() 
    if valgt_valg == 'Logg inn':
        print('Logg inn')
        logg_inn()
    if valgt_valg == 'Avslutt':
        conn.close()

lag_bruker_logg_inn()

    