import unittest
import json
from message import Message

# message.py tests
class TestMessage(unittest.TestCase):
    def test_message(self):
        # Create a message
        message = Message(1, 2)
        
        # Serialize and deserialize the message
        json_str = message.to_json()
        new_message = Message.from_json(json_str)
        
        # Check if the deserialized message is the same as the original
        self.assertEqual(new_message.sender_id, 1)
        self.assertEqual(new_message.logical_clock, 2)
        self.assertEqual(new_message.timestamp, message.timestamp)

    # ensure not able to make faulty message (missing fields)
    def test_faulty_message(self):
        # Create a message
        message = Message(1, 2)
        
        # Serialize the message
        json_str = message.to_json()
        
        # Remove a field from the serialized message
        data = json.loads(json_str)
        del data['sender_id']
        faulty_json_str = json.dumps(data)
        
        # Attempt to deserialize the faulty message
        with self.assertRaises(KeyError):
            _ = Message.from_json(faulty_json_str)


if __name__ == "__main__":
    unittest.main()