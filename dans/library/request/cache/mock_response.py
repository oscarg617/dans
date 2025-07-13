
class MockResponse:
    
    def __init__(self, status_code=None, text=None, json_data=None):
        self.status_code = status_code
        self.text = text
        self.json_data = json_data
    
    def json(self):
        return self.json_data

class MockAPIResponse:
    
    def __init__(self, data_frames=None):
        self.data_frames = data_frames
    
    def get_data_frames(self):
        return self.data_frames
