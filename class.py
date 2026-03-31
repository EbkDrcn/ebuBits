import socket
import json
import threading
import time

starterBit = "STARTERBIT/WELCOMETOEBUBITSCOMM"
enderBit = "ENDERBIT/GOODBYEFROMEBUBITSCOMM"

class ebuBits :
    defaultPort = 1302

    def __init__(self, systemID = None, systemPort = defaultPort):
        if systemID is None:
            systemID = getLocalIP()
        else:
            self.systemID = systemID
            
        self.systemPort = systemPort
        print(f"Your ebuBits session is initializing. Your system ID is {self.systemID} and your port is {self.systemPort}")
        self.buffer = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.socket.bind(('127.0.0.1', self.systemPort))
            print(f"Sistem {systemID} established. Port {self.systemPort}")
        except OSError:
            print(f"Error establishing port {self.systemPort}, already in use")

        self.running = True
        self.listenerThread = threading.Thread(target=self.listenForever, daemon=True)
        self.listenerThread.start()

    @staticmethod
    def getLocalIP():
        ipGetter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ipGetter.connect(("8.8.8.8", 80))
            ip = ipGetter.getsockname()[]
        expect Exception:
            ip = "127.0.0.1"
        finally:
            ipGetter.close()
        return ip

    def sendPocket(self, destination,  data):
        packet = [starterBit + self.systemID + destination + data + enderBit]
        jsonPacket = json.dumps(packet).encode("utf-8")

        self.socket.sendto(jsonPacket, ('127.0.0.1', self.systemPort))

    def listenForever(self):
        while self.running:
            try:
                raw_data, addr = self.socket.recvfrom(4096)
                packet = json.loads(raw_data.decode("utf-8"))

                self.parsePacket(packet)

            except Exception as e:
                pass

    def parsePacket(self, packet):
        if packet[0] == starterBit:
            senderID = packet[1]
            destinationID = packet[2]
            payload = packet[3]

            if packet[-1] == enderBit:
                if destinationID == self.systemID:

                    if payload == "isAvailableCheck":
                        self.sendPocket(senderID, "ACK_POSITIVE")
                        print(f"{senderID} system checked if you are available, response given as available")

                    elif payload == "ACK_POSITIVE":
                        self.buffer.append(f"ACK_RESPONSE_POSITIVE_{senderID}") 

                    else:
                        print(f"\n [!] Mesaj alındı. Kaynak : {senderID}")
                        print(f"İçerik : {payload} \n")
                
                else:
                    print(f"Başkasına gönderilen bir mesaj bulundu")

    def isAvailable(self, destination, responseTime = 3):
        self.sendPocket(destination, "isAvailableCheck")
        self.ackTimer = time.time()
        self.requestedACK = f"ACK_RESPONSE_POSITIVE_{destination}"
        while time.time() - self.ackTimer < responseTime :
            if self.requestedACK in self.buffer:
                print(f"{destination} system is available")
                self.buffer.remove(self.requestedACK)
                return True
            time.sleep(0.1)
        print(f"Request to system {destination} timed out")
        return False



        





