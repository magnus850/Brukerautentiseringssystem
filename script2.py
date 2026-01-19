import mariadb
import bcrypt
import pwinput

max_passord_lengde = 24
min_passord_lengde = 6
max_brukernavn_lengde = 18    
min_brukernavn_lengde = 6

conn = mariadb.connect(
    user='magnus',
    password='Smogholst1',
    host = 'localhost',
    database = 'brukersystem',
    unix_socket = '/opt/homebrew/var/mysql/mysql.sock'
    )

cur = conn.cursor()

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
            nytt_passord = pwinput.pwinput(prompt='Passord(6-24): ', mask = '*')
            if min_passord_lengde <= len(nytt_passord) <= max_passord_lengde:
                break
            print('Hold passorlengde innen 6-24 tegn')
            
        passord_hashing(nytt_passord, nytt_brukernavn, None, None)
    
    
def logg_inn():
    print("Logg inn")
    while True:
        brukernavn = input('Brukernavn(6-18): ')
        if min_brukernavn_lengde <= len(brukernavn) <= max_brukernavn_lengde:
            break
        print('Hold brukernavnlengde innen 6-18 tegn')
    
    cur.execute(
        'SELECT id, passord FROM brukere WHERE bruker = %s',
        (brukernavn,))
    resultat = cur.fetchone()
    if resultat == None:
        print('Feil brukernavn')
        return
    if resultat:
        while True:
            passord = pwinput.pwinput(prompt='Passord(6-24): ', mask = '*')
            if min_passord_lengde <= len(passord) <= max_passord_lengde:
                break
            print('Hold passorlengde innen 6-24 tegn')
        liste = list(resultat)
        passord_hashing(passord, None, liste[0], liste[1])
        
        
def registrer_bruker(passord, brukernavn):
    cur.execute('insert into brukere (bruker, passord) values (%s, %s)',
        (brukernavn, passord))
    if cur.fetchone:
        print(f'Du har lagd en bruker ved navn {brukernavn}')


def passord_hashing(input_passord, input_brukernavn, id, db_passord):
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
            print('Du er logget inn')
            endre_passord(id)
            return
        else: 
            print('Feil passord') 
            return
    registrer_bruker(hasha_passord_string, input_brukernavn)
    
    
def endre_passord(id):
    endre_passord = input('Vil du endre passord? ja/nei: ')
    if endre_passord == 'ja':
        while True:
            nytt_passord = pwinput.pwinput(prompt='Passord(6-24): ', mask = '*')
            if min_passord_lengde <= len(nytt_passord) <= max_passord_lengde:
                break
            print('Hold passorlengde innen 6-24 tegn')
        passord_hashing(nytt_passord, None, id, None)
        return
    else: return
    
    
def registrer_nytt_passord(passord, id):
    cur.execute(
    'UPDATE brukere SET passord = %s WHERE id = %s',
    (passord, id))
    if cur.fetchone:
        print('Du har endret passord')
    
    
def innlogging_eller_nybruker():
    innlogging = input('Vil du logge inn? ja/nei: ')
    if innlogging == 'ja':
        logg_inn()
    if innlogging == 'nei':
        nybruker = input('Vil du lage en ny bruker? ja/nei: ')
        if nybruker == 'ja':
            print('Lag bruker')
            lag_bruker()
            
            
innlogging_eller_nybruker()

conn.commit()
conn.close()
