"""
Universidad del Valle de Guatemala
Redes 
Proyecto numero dos: Uso de protocolo existente
Pablo Viana - 16091

este codigo se basa en varios ejemplos extraidos de: 
 - XMPP - The definitive guide
 - https://sleekxmpp.readthedocs.io/en/latest/
 - https://gist.github.com/eliangcs/e61c491f701055d488d8
"""
import sleekxmpp
import logging
import sys
import xml.etree.ElementTree as ET
from sleekxmpp.exceptions import IqError, IqTimeout

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Clase para definir un usuario utilizando sleek
class SleekUser(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, nick, room):

        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick

        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("message", self.message)
        self.add_event_handler("register", self.register, threaded=True)
        self.add_event_handler("groupchat_message", self.response_when_nick, threaded=True)
        self.add_event_handler("muc::%s::got_online" % self.room, self.hellow_everyone, threaded=True)

    """Esta funcion significa que se empieza una sesion"""
    def start(self, event):
        print("\nSesion iniciada")
        print("<------------------->")
        self.send_presence()
        self.get_roster()

    """Quitar el usuario del servidor"""
    def delete_user(self):
        request = self.Iq()
        request['type'] = 'set'
        request['from'] = self.boundjid.user
        request['register'] = ' '
        request['register']['remove'] = ' '
        try:
            request.send(now=True)
            print("Cuenta eliminada %s!" % self.boundjid)
        except IqError as e:
            logging.error("no se pudo eliminar la cuenta: %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("no contesto el server")
            self.disconnect()
    
    """ Ver todos los usuarios conectados en el servidor """
    def get_users(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.redes2020.xyz'
        xml = ET.fromstring("<query xmlns='jabber:iq:search'>\
                                <x xmlns='jabber:x:data' type='submit'>\
                                    <field type='hidden' var='FORM_TYPE'>\
                                        <value>jabber:iq:search</value>\
                                    </field>\
                                    <field var='Username'>\
                                        <value>1</value>\
                                    </field>\
                                    <field var='search'>\
                                        <value>*</value>\
                                    </field>\
                                </x>\
                              </query>")
        iq.append(xml)
        try:
            response = iq.send()
            data = []
            temp = []
            cont = 0
            for i in response.findall('.//{jabber:x:data}value'):
                cont += 1
                txt = ''
                if i.text != None:
                    txt = i.text

                temp.append(txt)
                if cont == 4:
                    cont = 0
                    data.append(temp)
                    temp = []

            return data
        except IqError as e:
            print(f"No se pudo s\n {e.iq['error']['text']}")
            self.disconnect()
        except IqTimeout:
            print("El server no responde")
            self.disconnect()

    """Funcion para registrar un usuario en el servidor"""
    def register(self, iq):
        request = self.Iq()
        request['type'] = 'set'
        request['register']['username'] = self.boundjid.user
        request['register']['password'] = self.password
        try:
            request.send(now=True)
            logging.info("Te has registrado: %s!" % self.boundjid)
        except IqError as e:
            logging.error("No se pudo registrar, tal vez el usuario ya existe %s" %
                    e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            logging.error("no contesto el servidor")
            self.disconnect()
    
    """ Funcion para entrar a un room """
    def add_to_group(self, room):
        self.plugin['xep_0045'].joinMUC(room,
                                    self.nick,
                                    wait=True)

    """Funcion para recibir un mensaje"""
    def message(self, msg):
        print("\n", msg['from'], ": ")
        print(f"{bcolors.OKGREEN}TE HA LLEGADO UN MENSAJE {bcolors.ENDC}")
        print("este es -> ", msg['body'],"\n")

    """ Funcion para un chat de grupo """
    def hellow_everyone(self, presence):
            if presence['muc']['nick'] != self.nick:
                self.send_message(mto=presence['from'].bare,
                mbody="Que onda mucha!, %s %s" % (presence['muc']['role'],
                presence['muc']['nick']),
                mtype='groupchat')
    
    """ Funcion para un mensaje grupal """
    def response_when_nick(self, msg):
            if msg['mucnick'] != self.nick and self.nick in msg['body']:
                self.send_message(mto=msg['from'].bare,
                          mbody="¿Quien dijo mi nombre?, %s." % msg['mucnick'],
                          mtype='groupchat')
                print ("%(body)s" % msg)

    """ Funcion para mandar un archivo a otro usuario """
    def send_files(self,receiver, filename):
        stream = self['xep_0047'].open_stream(receiver)
        with open(filename) as f:
            data = f.read()
            stream.sendall(data)
        
    
