import socket
import threading
import json
import time


class PersonalizationServer(object):
    def __init__(self, logger, host="0.0.0.0", port=5000):
        super(PersonalizationServer, self).__init__()
        self.logger = logger
        self.host = host
        self.port = port
        self.scheduled_interventions = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_thread = None
        self.running = False
        self.lock = threading.Lock()

    def start_server_in_thread(self):
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def run_server(self):
        self.logger.info("Server running on " + str(self.host) + ":" + str(self.port))
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                with client_socket:
                    data = client_socket.recv(1024)
                    if not data:
                        return
                    try:
                        request = json.loads(data.decode('utf-8'))
                        if "scheduled_interventions" in request:
                            with self.lock:
                                self.logger.info("Received data: " + json.dumps(request))
                                self.scheduled_interventions = request["scheduled_interventions"]
                                # Process the received data
                                response = {"message": "Data received successfully"}
                                client_socket.sendall(json.dumps(response).encode('utf-8'))
                        else:
                            response = {"error": "Invalid data format"}
                            self.scheduled_interventions = []
                            client_socket.sendall(json.dumps(response).encode('utf-8'))
                    except ValueError:
                        response = {"error": "Invalid JSON"}
                        self.scheduled_interventions = []
                        client_socket.sendall(json.dumps(response).encode('utf-8'))
            except socket.error as e:
                if self.running:
                    self.logger.info("Socket error: " + str(e))
                else:
                    self.logger.info("Socket closed!")
                break
        self.logger.info("Server running on " + str(self.host) + ":" + str(self.port))

    def stop_server(self):
        self.running = False
        self.server_socket.close()
        if self.server_thread:
            self.server_thread.join()

    # This method checks for interventions that are due based on their timestamp.
    # Interventions can be either fixed or periodic:
    # - Fixed interventions have the highest priority.
    # - Periodic interventions are considered if no fixed interventions are due.
    # If multiple interventions with the same priority are due, the function returns the one with the earliest timestamp.
    # Each intervention can contain either topics or actions, but not both.
    # The method keeps track of which topic/action has been chosen the last time using a counter.
    # If an intervention's counter reaches the length of its topics or actions, it resets to allow cyclic execution.
    def get_due_intervention(self):
        current_time = time.time()        
        self.logger.info("Personalization server current time: " + str(current_time))
        
        # Separate fixed and periodic interventions that are due based on their timestamp
        fixed_interventions = [i for i in self.scheduled_interventions
                               if i['type'] == 'fixed' and i['timestamp'] <= current_time]
        periodic_interventions = [i for i in self.scheduled_interventions
                                  if i['type'] == 'periodic' and i['timestamp'] <= current_time]

        # Sort interventions by timestamp (earliest first)
        fixed_interventions.sort(key=lambda x: x['timestamp'])
        periodic_interventions.sort(key=lambda x: x['timestamp'])

        # Determine which intervention to return: fixed interventions have higher priority
        if fixed_interventions:
            due_intervention = fixed_interventions[0]
        elif periodic_interventions:
            due_intervention = periodic_interventions[0]
        else:
            self.logger.info("Server: no due interventions")
            return None  # No due interventions

        # Increment the counter to keep track of execution times or initialize it if not present
        if "counter" not in due_intervention:
            counter = 0
        else:
            counter = due_intervention["counter"]

        # Ensure counter cycles within the list length to prevent IndexError and return result
        if "topics" in due_intervention and due_intervention["topics"]:
            result = {'type': 'topic', 'sentence': "Parliamo di " + due_intervention["topics"][counter]["name"],
                      'exclusive': due_intervention["topics"][counter]["exclusive"]}
            counter += 1
            counter %= len(due_intervention["topics"])
        elif "actions" in due_intervention and due_intervention["actions"]:
            result = {'type': 'action', "sentence": due_intervention["actions"][counter], 'exclusive': False}
            counter += 1
            counter %= len(due_intervention["actions"])
        else:
            return None  # No valid topics or actions found

        # Update the counter in the original scheduled_interventions list
        for intervention in self.scheduled_interventions:
            if intervention == due_intervention:
                intervention["counter"] = counter
                intervention["timestamp"] = intervention["timestamp"] + intervention["period"]
                break
        return result
