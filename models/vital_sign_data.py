class VitalSignData:
    def __init__(self, heart_rate=None, respiration_rate=None, activity=None):
        self.set_heart_rate(heart_rate)
        self.set_respiration_rate(respiration_rate)
        self.set_activity(activity)

    def set_heart_rate(self, value):
        if not (0 <= value <= 300):  #Assumption
            raise ValueError("HEART RATE VALUE SHOULD BE IN  RANGE 0 - 300")
        self.__heart_rate = value

    def set_respiration_rate(self, value):
        if not (0 <= value <= 100):  #Assumption
            raise ValueError("RESPIRATION RATE VALUE SHOULD BE IN  RANGE 0 - 100")
        self.__respiration_rate = value

    def set_activity(self, value):
        if not (0 <= value <= 20): #Assumption
            raise ValueError("ACTIVITY VALUE SHOULD BE IN  RANGE 0 - 20")
        self.__activity = value

    def get_heart_rate(self):
        return self.__heart_rate

    def get_respiration_rate(self):
        return self.__respiration_rate

    def get_activity(self):
        return self.__activity

    def to_json(self):
        return {
            "heart_rate": self.get_heart_rate(),
            "respiration_rate": self.get_respiration_rate(),
            "activity": self.get_activity()
        }
