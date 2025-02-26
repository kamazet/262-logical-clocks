import json
import time

class Message:
    def __init__(self, sender_id, logical_clock):
        self.sender_id = sender_id
        self.logical_clock = logical_clock
        self.timestamp = time.time()
    
    def to_json(self):
        return json.dumps({
            'sender_id': self.sender_id,
            'logical_clock': self.logical_clock,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        msg = cls(data['sender_id'], data['logical_clock'])
        msg.timestamp = data['timestamp']
        return msg 