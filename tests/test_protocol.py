import unittest

from cars4mars.protocol import (
    DrivePayload,
    DriveSource,
    MessageType,
    ProtocolError,
    crc16_ccitt,
    decode_drive_payload,
    decode_frame,
    encode_drive_payload,
    encode_frame,
)


class ProtocolTests(unittest.TestCase):
    def test_crc_known_vector(self):
        self.assertEqual(crc16_ccitt(b"123456789"), 0x29B1)

    def test_frame_round_trip(self):
        raw = encode_frame(MessageType.HEARTBEAT, 42)
        frame = decode_frame(raw)
        self.assertEqual(frame.message_type, MessageType.HEARTBEAT)
        self.assertEqual(frame.sequence, 42)
        self.assertEqual(frame.payload, b"")

    def test_tamper_is_rejected(self):
        raw = bytearray(encode_frame(MessageType.HEARTBEAT, 1, b"abc"))
        raw[-3] ^= 0x01
        with self.assertRaisesRegex(ProtocolError, "CRC mismatch"):
            decode_frame(bytes(raw))

    def test_truncated_frame_is_rejected(self):
        with self.assertRaises(ProtocolError):
            decode_frame(b"C4M1")

    def test_drive_payload_round_trip(self):
        original = DrivePayload(
            linear_mm_s=650,
            angular_mrad_s=-320,
            issued_ms=123456,
            source=DriveSource.AUTONOMY,
        )
        decoded = decode_drive_payload(encode_drive_payload(original))
        self.assertEqual(decoded, original)
        self.assertAlmostEqual(decoded.linear_mps, 0.65)
        self.assertAlmostEqual(decoded.angular_rad_s, -0.32)

    def test_bad_drive_payload_length_is_rejected(self):
        with self.assertRaises(ProtocolError):
            decode_drive_payload(b"bad")


if __name__ == "__main__":
    unittest.main()
