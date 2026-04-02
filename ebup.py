import socket
import json
import threading
import time

class EBUProtocol :
    defaultPort = 1302
    starterBit = "EBUP-S-v1"
    enderBit = "EBUP-E-v1"

    ackQuery = {"type":"ack_query", "data":"ack_check"}
    ackAffirmative = {"type":"ack_query", "data":"ack_affirmative"}
    msgRecieved = {"type":"msgInfo", "data":"msg_recieved"}
    msgTypeError = {"type":"msgInfo", "data":"msg_returned_type_error"}
    discoverySearch = {"type":"discovery", "data":"discovery"}
    discoveryAns = {"type":"discovery", "data":"discovery_here"}
    message = {"type":"msg", "data":"", "priority":False}

    addressBook = []

    def __init__(self, systemID = None, systemPort = defaultPort):
        if systemID is None:
            systemID = self.getLocalIP()
            self.systemID = systemID
        else:
            self.systemID = systemID
            
        self.systemPort = systemPort

        print(f"EBUP interface initialized. Your system ID is {self.systemID} and your port is {self.systemPort}")
        
        self.buffer = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsocketopt(socket.SOL_SOCKET, socket.SOL_BROADCAST, 1)

        try:
            self.socket.bind(('0.0.0.0', self.systemPort))
            print(f"System {systemID} established. Port {self.systemPort}")
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
            ip = ipGetter.getsockname()[0]
        
        except Exception:
            ip = "127.0.0.1"
        
        finally:
            ipGetter.close()
        
        return ip

    def sendPocket(self, destination,  data, priority = False):
        if priority == True:
            data["priority"] = True

        if not isinstance(data,dict):
            data = {"type":"msg", "data":data, "priority":priority}

        packet = [  self.starterBit,
                    self.systemID,
                    destination,
                    data,
                    self.enderBit]

        jsonPacket = json.dumps(packet).encode("utf-8")
        
        try:
            self.socket.sendto(jsonPacket, (destination, self.systemPort))

        except Exception as e:
            print(f"Error : {e}")

    def listenForever(self):
        while self.running:
            try:
                raw_data, addr = self.socket.recvfrom(4096)
                packet = json.loads(raw_data.decode("utf-8"))

                self.parsePacket(packet)

            except Exception as e:
                pass

    def parsePacket(self, packet):
        if packet[0] == self.starterBit:
            senderID = packet[1]
            destinationID = packet[2]
            payload = packet[3]

            if packet[-1] == self.enderBit:
                if destinationID == self.systemID:

                    if payload == self.ackQuery:
                        self.sendPocket(senderID, self.ackAffirmative)
                        print(f"{senderID} system checked if you are available, response given as available")

                    elif payload == self.ackAffirmative:
                        self.buffer.append(f"ACK_RESPONSE_POSITIVE_{senderID}")

                    elif payload == self.msgRecieved:
                        print(f"Your priority message to {senderID} is sended") 

                    elif payload == self.discoverySearch:
                        self.sendPocket(senderID, self.discoveryAns)
                        print(f"Discovery search from {senderID} , answered.")

                    elif payload == self.discoveryAns:
                        self.buffer.append(f"DISCOVERY_ANS_FROM_{senderID}")
                        print(f"Discovery answer from {senderID}")

                    elif payload.get("type") == "msg":
                        print(f"\n [!] Mesaj alındı. Kaynak : {senderID}")
                        print(f"İçerik : {payload.get("data")} \n")

                    else:
                        print(f"Unknown type of message recieved.")
                        self.sendPocket(senderID, self.msgTypeError)
                
                    if payload.get("priority") == True:
                        self.sendPocket(senderID, self.msgRecieved)

                else:
                    print(f"There is a message to somebody else on the network")

    def isAvailable(self, destination, timeout = 3):
        self.sendPocket(destination, self.ackQuery)
        ackTimer = time.time()
        echoTimer = time.perf_counter()

        expectedACK = f"ACK_RESPONSE_POSITIVE_{destination}"
        while time.time() - ackTimer < timeout :
            if expectedACK in self.buffer:
                latency = (time.perf_counter() - echoTimer)*1000
                print(f"{destination} system is available. Latency -> {latency:.2f} ms")
                self.buffer.remove(expectedACK)
                return True
            time.sleep(0.1)
        print(f"Request to system {destination} timed out")
        return False

    def discovery(self, timeout):
        self.sendPocket("255.255.255.255", self.discoverySearch)
        discoveryTimer = time.time()
        expectedDiscovery = "DISCOVERY_ANS_FROM_"
        print(f"Discovery call for {timeout} seconds.")

        answers = []
        
        while time.time() - discoveryTimer < timeout:
            for item in list(self.buffer):
                if isinstance(item, str) and item.startswith(expectedDiscovery):
                    foundIP = item.replace(expectedDiscovery, "")

                    if foundIP not in answers and foundIP != self.systemID:
                        answers.append(foundIP)
                        print(f"System {foundIP} answered")

                    self.buffer.remove(item)
            time.sleep(0.1)

        if not answers:
            print(f"There is no answer to discovery call")
        else:
            print(f"There is {len(answers)} answers and from {answers}")
        
        if self.setAddressBook == True:
            self.updateAddressBook(answers)
        else:
            self.adressBook = []

        return answers
    
    def updateAddressBook(self, answers):
        for i in range(len(answers)):
            if answers[i] not in self.adressBook and answers[i] != self.systemID:
                self.adressBook.append({"ipAdress":answers[i], "createdTime":time.time()})

        return self.adressBook
    
    
        
