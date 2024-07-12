# personalization_data.py
import time
import sys
from flask import Flask, request, jsonify
from threading import Thread


class PersonalizationServer(object):
    def __init__(self, logger, scheduled_interventions=None):
        super(PersonalizationServer, self).__init__()    
        if scheduled_interventions is None:
            scheduled_interventions = []
        self.scheduled_interventions = scheduled_interventions
        self.app = Flask(__name__)
        self._setup_routes()
        self.logger = logger

    def _setup_routes(self):
        @self.app.route('/CAIR_personalization_server', methods=['POST'])
        def receive_personalization_data():
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400
            try:
                self.logger.info("Personalization server: received data!")
                self.scheduled_interventions = data.get("scheduled_interventions", [])
                self.logger.info(str(time.time()))
                #self.logger.info(str(self.scheduled_interventions[0]["timestamp"]))
                return jsonify({"message": "Data received successfully"}), 200
            except Exception as e:
                self.logger.info("Personalization server: error processing data " + str(e))
                return jsonify({"error": str(e)}), 500
                
        @self.app.route('/CAIR_personalization_server/stop', methods=['POST'])
        def stop_server(): 
            self.logger.info("Personalization server: STOPPING")  
            sys.exit(1)

    def run_flask_server(self):
        try:
            self.app.run("0.0.0.0", port=5000)
            self.logger.info("Personalization server: starting...")
        except socket.error:
            self.logger.info("Personalization server error: address already in use!")
            

    def start_server_in_thread(self):
        thread = Thread(target=self.run_flask_server)
        thread.daemon = True
        thread.start()

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
        self.logger.info("Personalization server: " + str(current_time))
        
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