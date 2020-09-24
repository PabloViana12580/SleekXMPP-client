"""
Universidad del Valle de Guatemala
Redes 
Proyecto numero dos: Uso de protocolo existente
Pablo Viana - 16091

este codigo se basa en varios ejemplos extraidos de: 
 - XMPP - The definitive guide
 - https://sleekxmpp.readthedocs.io/en/latest/getting_started/echobot.html
 - https://gist.github.com/eliangcs/e61c491f701055d488d8
"""

#Import libraries
import sys
import logging
import getpass
import sleekxmpp
import time
import ssl

from optparse import OptionParser
from sleekuser import SleekUser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Principal
def user_options(): 
    print(f"{bcolors.OKGREEN}*-----------------------* BIENVENIDO *-----------------------*{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}1. Mostrar todos los contactos {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}2. Agregar usuario {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}3. Mostrar información detallada de usuarios agregados {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}4. Chat uno a uno {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}5. Personalizar mensaje de presencia {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}6. Chat grupal {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}7. Enviar archivo {bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}8. Entrar a un grupo {bcolors.ENDC}")
    print(f"{bcolors.WARNING}9. Cerrar sesion {bcolors.ENDC}")
    print(f"{bcolors.WARNING}10. Borrar cuenta {bcolors.ENDC}")
    response = input("Escoja alguna de las 10 opciones anteriores (1-10): ")
    return response


if __name__ == '__main__':

    optp = OptionParser()

    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)

    opts, args = optp.parse_args()

    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    print("-------- BIENVENIDO -------- ")
    print("Este es un cliente de XMPP que deseas hacer: ")
    print("(1) Ingresar (2) registrarte")
    option = int(input("Escoge una opcion: "))

    username = input("Nombre de usuario: ")  
    opts.jid = username+"@redes2020.xyz"
    opts.password = getpass.getpass("Contraseña: ")
    opts.nick = input("Apodo: ")
    opts.room = "testroom@conference.redes2020.xyz"

    xmpp = SleekUser(opts.jid, opts.password, opts.nick, opts.room)
    if (option == 1):
        xmpp.del_event_handler("register", xmpp.register)
    
    #Registrando los plugins
    xmpp.register_plugin('xep_0004') # Data
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # MCU
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0066') # Out-of-band Data
    xmpp.register_plugin('xep_0077') # In-band Registration
    xmpp.register_plugin('xep_0199') # Ping
    xmpp.register_plugin('xep_0047') # transfer file
    xmpp['xep_0077'].force_registration = True

    #authentication over an unencrypted connection
    xmpp['feature_mechanisms'].unencrypted_plain = True
    xmpp.ssl_version = ssl.PROTOCOL_TLS

    if xmpp.connect(('redes2020.xyz', 5222)):
        xmpp.process(block=False)
        while(1): 
            choice = int(user_options())
            #Show all users
            if(choice == 1):
                print("Contacts: \n")
                respuesta = xmpp.get_users()
                print(respuesta)
            #Add user 
            elif(choice == 2):
                new_contact = input("username: \n")
                friend = new_contact + "@redes2020.xyz"
                xmpp.send_presence(pto = friend, ptype ='subscribe')

            #Show details from an specific user
            elif(choice == 3): 
                print("\n ", xmpp.client_roster, "\n") 

            #Direct message
            elif(choice == 4): 
                print("\nPRIVATE CHAT\n")
                username = input("\n To: ")
                user_to = username + "@redes2020.xyz"
                content = input("\n Content: ")
                xmpp.send_message(mto=user_to, mbody = content, mtype = 'chat')
                print("\n SENT \n")

            #Send presence message and change status
            elif(choice == 5):
                status = input("Status: ")
                flag = 0
                while(flag == 0):
                    print(f"{bcolors.BOLD}¿que icono deseas utilizar para tu estado?{bcolors.ENDC}")
                    print("1. Listo para chatear")
                    print("2. No estoy")
                    print("3. Me fui bastante tiempo")
                    print("4. No molestar")
                    icon_resp = int(input("Escoja un numero del 1 al 4: "))
                    flag = 1
                    if(icon_resp == 1):
                        show = "chat"
                    elif(icon_resp == 2):
                        show = "away"
                    elif(icon_resp == 3):
                        show = "xa"
                    elif(icon_resp == 4):
                        show = "dnd"
                    else: 
                        print("Please, try again")
                        flag = 0

                """
                self.send_presence(pstatus="i'm not around right now", pshow='xa')
                Where pstatus controls the type of icon your IM client will show, and you
                have the options of: chat, away, xa, and dnd. The value 'xa' means
                extended away and 'dnd' means do not disturb.
                """
                xmpp.makePresence(pfrom=xmpp.jid, pstatus=status, pshow=show)
                
            #Public chat
            elif(choice == 6): 
                xmpp.plugin['xep_0045'].joinMUC(xmpp.room, xmpp.nick)
                print("\nPUBLIC CHAT\n")
                msg_all = input("Message: ")
                xmpp.send_message(mto='all', mbody=msg_all, mtype='groupchat')
                print("\n SENT \n")

            #Send file
            elif(choice == 7): 
                username = input("\n To: ")
                send_to = username + "@redes2020.xyz"
                file = input("File: ")
                xmpp.send_files(send_to, file)
            
            # add to group
            elif (choice == 8):
                room = input("\n nombre del grupo: ")
                xmpp.add_to_group(room)
                xmpp.room = room

            #Exit
            elif(choice == 9): 
                print("Nos vemos")
                xmpp.disconnect()
                break

            #Delete account
            elif(choice == 10): 
                xmpp.delete_user()
                xmpp.disconnect()
                break

            #If the option is not between (1-10)
            else: 
                print("Invalid option")
       
    #Fail connection
    else:
        print("Unable to connect :(")