#pragma once

#include <cstddef>
#include <cstdint>

namespace c4m {

constexpr std::uint8_t VERSION = 1;
constexpr std::size_t HEADER_SIZE = 12;
constexpr std::size_t CRC_SIZE = 2;
constexpr std::size_t DRIVE_PAYLOAD_SIZE = 9;

enum class MessageType : std::uint8_t {
    Heartbeat = 1,
    Drive = 2,
    Estop = 3,
    ResetEstop = 4,
    Telemetry = 5,
};

enum class DriveSource : std::uint8_t {
    Manual = 1,
    Autonomy = 2,
};

struct FrameView {
    MessageType type;
    std::uint32_t sequence;
    const std::uint8_t* payload;
    std::uint16_t payload_length;
};

struct DrivePayload {
    std::int16_t linear_mm_s;
    std::int16_t angular_mrad_s;
    std::uint32_t issued_ms;
    DriveSource source;
};

inline std::uint16_t read_u16_be(const std::uint8_t* p) {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(p[0]) << 8) | p[1]);
}

inline std::uint32_t read_u32_be(const std::uint8_t* p) {
    return (static_cast<std::uint32_t>(p[0]) << 24) |
           (static_cast<std::uint32_t>(p[1]) << 16) |
           (static_cast<std::uint32_t>(p[2]) << 8) |
           static_cast<std::uint32_t>(p[3]);
}

inline std::int16_t read_i16_be(const std::uint8_t* p) {
    return static_cast<std::int16_t>(read_u16_be(p));
}

inline std::uint16_t crc16_ccitt(const std::uint8_t* data, std::size_t length) {
    std::uint16_t crc = 0xFFFF;
    for (std::size_t i = 0; i < length; ++i) {
        crc ^= static_cast<std::uint16_t>(data[i]) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

inline bool decode_frame(const std::uint8_t* data, std::size_t length, FrameView& out) {
    if (length < HEADER_SIZE + CRC_SIZE) return false;
    if (data[0] != 'C' || data[1] != '4' || data[2] != 'M' || data[3] != '1') return false;
    if (data[4] != VERSION) return false;

    const auto raw_type = data[5];
    if (raw_type < static_cast<std::uint8_t>(MessageType::Heartbeat) ||
        raw_type > static_cast<std::uint8_t>(MessageType::Telemetry)) return false;

    const auto payload_length = read_u16_be(data + 6);
    const auto expected_length = HEADER_SIZE + static_cast<std::size_t>(payload_length) + CRC_SIZE;
    if (length != expected_length) return false;

    const auto expected_crc = read_u16_be(data + length - CRC_SIZE);
    if (crc16_ccitt(data, length - CRC_SIZE) != expected_crc) return false;

    out.type = static_cast<MessageType>(raw_type);
    out.sequence = read_u32_be(data + 8);
    out.payload = data + HEADER_SIZE;
    out.payload_length = payload_length;
    return true;
}

inline bool decode_drive_payload(const FrameView& frame, DrivePayload& out) {
    if (frame.type != MessageType::Drive || frame.payload_length != DRIVE_PAYLOAD_SIZE) return false;
    const auto* p = frame.payload;
    const auto raw_source = p[8];
    if (raw_source != static_cast<std::uint8_t>(DriveSource::Manual) &&
        raw_source != static_cast<std::uint8_t>(DriveSource::Autonomy)) return false;

    out.linear_mm_s = read_i16_be(p);
    out.angular_mrad_s = read_i16_be(p + 2);
    out.issued_ms = read_u32_be(p + 4);
    out.source = static_cast<DriveSource>(raw_source);
    return true;
}

}  // namespace c4m
