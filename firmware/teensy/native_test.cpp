#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>

#include "include/c4m_protocol.hpp"

int main() {
    // Python encoder golden vector:
    // DRIVE seq=7, linear=450 mm/s, angular=250 mrad/s, issued=1000 ms, manual.
    constexpr std::array<std::uint8_t, 23> frame_bytes = {
        0x43,0x34,0x4d,0x31,0x01,0x02,0x00,0x09,0x00,0x00,0x00,0x07,
        0x01,0xc2,0x00,0xfa,0x00,0x00,0x03,0xe8,0x01,0x6d,0x8d
    };

    c4m::FrameView frame{};
    assert(c4m::decode_frame(frame_bytes.data(), frame_bytes.size(), frame));
    assert(frame.type == c4m::MessageType::Drive);
    assert(frame.sequence == 7);

    c4m::DrivePayload drive{};
    assert(c4m::decode_drive_payload(frame, drive));
    assert(drive.linear_mm_s == 450);
    assert(drive.angular_mrad_s == 250);
    assert(drive.issued_ms == 1000);
    assert(drive.source == c4m::DriveSource::Manual);

    auto corrupt = frame_bytes;
    corrupt[12] ^= 0x01;
    c4m::FrameView rejected{};
    assert(!c4m::decode_frame(corrupt.data(), corrupt.size(), rejected));

    std::cout << "C4M Teensy protocol golden vector: PASS\n";
    return 0;
}
