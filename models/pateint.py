import uuid
class Patient:
    def __init__(self):
        self.__patient_id = uuid.uuid4()

    def get_patient_id(self):
        return  self.__patient_id