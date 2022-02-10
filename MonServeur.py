from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from json import JSONDecodeError
import json
import sqlite3

"""
Serveur HTTP de test - pas sécure pour production.
Inspiré de https://gist.github.com/bradmontgomery/2219997
"""
class MonServeur(BaseHTTPRequestHandler):
    error_message_format = '''
    <head>
        <title>Erreur</title>
    </head>
    <body>
        <h1>Une erreur est survenue</h1>
        <p>Code d'erreur: %(code)d.
        <p>Message: %(message)s.
        <p>Détails: %(code)s = %(explain)s.
    </body>
    '''

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            data = {}
            for idx, col in enumerate(cursor.description):
                data[col[0]] = row[idx]
            return data

        try:
            if self.client_address[0] not in allowed_hosts:
                self.send_error(403)
                print(f'Accès interdit à partir de {self.client_address}')
            else:
                if self.path.endswith("/"):
                    self._set_headers()
                    fichier = open('index.html','r').read()
                    fichier = fichier.format(titre='Bienvenue!', message='Ce site web est fait par Christopher Boisvert')
                    self.wfile.write(fichier.encode())

                elif self.path.endswith("/auteur"):
                    self._set_headers()
                    fichier = open('auteur.html','r').read()
                    fichier = fichier.format(titre='Christopher Boisvert')
                    self.wfile.write(fichier.encode())

                elif self.path.endswith("/amis"):
                    con = sqlite3.connect('boisvertchristopheramis.db')
                    con.row_factory = row_to_dict
                    cur = con.cursor()
                    self._set_headers()
                    liste_amis = cur.execute("SELECT id,prenom,nomfamille FROM amis").fetchall()
                    self.wfile.write(json.dumps(liste_amis).encode())
                    con.close();
                    
                elif self.path.endswith('.png'):
                    self.send_response(200, "OK")
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    # ouvre le fichier en lecture seule (r) et en mode binaire (b)
                    self.wfile.write(open(self.path.split("/")[-1],'rb').read())

                elif self.path.endswith('.jpg'):
                    self.send_response(200, "OK")
                    self.send_header("Content-Type", "image/png")
                    self.end_headers()
                    # ouvre le fichier en lecture seule (r) et en mode binaire (b)
                    self.wfile.write(open(self.path.split("/")[-1],'rb').read())

                elif self.path.endswith('/style.css'):
                    self.send_response(200, "OK")
                    self.send_header("Content-Type", "text/css")
                    self.end_headers()
                    self.wfile.write(open('style.css','rb').read())

                else:
                    self.send_error(404)
        except Exception as e:
            self.send_error(500)

    def do_POST(self):
        def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            data = {}
            for idx, col in enumerate(cursor.description):
                data[col[0]] = row[idx]
            return data

        try :
            if self.client_address[0] not in allowed_hosts:
                self.send_error(403)
                print(f'Accès interdit à partir de {self.client_address}')
            else: 
                if self.path.endswith("/amis"):
                    taille = int(self.headers['Content-Length'])
                    payload = self.rfile.read(taille).decode('utf-8')
                
                    if payload == "":
                        self.send_error(400)
                    else:
                        donnees_json = json.loads(payload)

                        if 'nomfamille' not in donnees_json:
                            self.send_error(400, "Veuillez fournir un nom !")

                        if 'prenom' not in donnees_json:
                            self.send_error(400)

                        prenom = donnees_json['prenom']
                        nomfamille = donnees_json['nomfamille']

                        con = sqlite3.connect('boisvertchristopheramis.db')
                        con.row_factory = row_to_dict
                        cur = con.cursor()
                        cur.execute("INSERT INTO amis(prenom,nomfamille) values (?, ?)", (prenom, nomfamille))
                        con.commit()
                        cur.close()
                        # envoie en-tête HTTP avec code HTTP
                        self._set_headers()
                        self.send_response(200, "OK")
                        self.send_header("Content-Type", "application/json")
                else:
                    self.send_error(404)
        except Exception as e:
            self.send_error(500)
                    
try:
    host = '0.0.0.0'
    port = 8080
    allowed_hosts = ('127.0.0.1',)
    print(f'Lancement du serveur {host}:{port} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('Appuyez sur Ctrl+C pour arrêter le serveur convenablement.')
    mon_serveur = HTTPServer((host, port), MonServeur)
    mon_serveur.serve_forever()
except KeyboardInterrupt:
    print('\nFin du programme, vous avez appuyé sur Ctrl+C.')
    print(f'Arrêt du serveur {host}:{port} - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
except Exception as e:
    print(f'Une exception est survenue {str(e)}')