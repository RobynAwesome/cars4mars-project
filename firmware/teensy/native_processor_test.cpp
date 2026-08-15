#include <array>
#include <cassert>
#include <cstdint>
#include <iostream>

#include "include/command_processor.hpp"

int main() {
    constexpr std::array<std::uint8_t, 14> heartbeat = {
        0x43,0x34,0x4d,0x31,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x06,0x88,0x52
    };
    constexpr std::array<std::uint8_t, 23> drive = {
        0x43,0x34,0x4d,0x31,0x01,0x02,0x00,0x09,0x00,0x00,0x00,0x07,
        0x01,0xc2,0x00,0xfa,0x00,0x00,0x03,0xe8,0x01,0x6d,0x8d
    };
    constexpr std::array<std::uint8_t, 14> old_estop = {
        0x43,0x34,0x4d,0x31,0x01,0x03,0x00,0x00,0x00,0x00,0x00,0x01,0x98,0x56
    };
    constexpr std::array<std::uint8_t, 14> reset = {
        0x43,0x34,0x4d,0x31,0x01,0x04,0x00,0x00,0x00,0x00,0x00,0x08,0x10,0x3b
    };

    c4m::CommandProcessor processor;

    auto hb = processor.handle(heartbeat.data(), heartbeat.size(), 900);
    assert(hb.accepted);
    assert(hb.safety.state == c4m::SafetyState::Ready);

    auto moving = processor.handle(drive.data(), drive.size(), 1000);
    assert(moving.accepted);
    assert(moving.safety.motor_enable);
    assert(moving.safety.linear_mm_s == 450);
    assert(moving.safety.angular_mrad_s == 250);

    // Exact replay cannot refresh or repeat motion authority.
    auto replay = processor.handle(drive.data(), drive.size(), 1010);
    assert(!replay.accepted);
    assert(replay.frame_valid);
    assert(!replay.sequence_accepted);

    // Old E-stop remains authoritative because stopping on replay is safe.
    auto stopped = processor.handle(old_estop.data(), old_estop.size(), 1020);
    assert(stopped.accepted);
    assert(!stopped.safety.motor_enable);
    assert(stopped.safety.state == c4m::SafetyState::EstopLatched);

    // A fresh reset may clear the software latch but does not re-enable motors.
    auto cleared = processor.handle(reset.data(), reset.size(), 1030);
    assert(cleared.accepted);
    assert(!cleared.safety.motor_enable);
    assert(cleared.safety.state == c4m::SafetyState::SafeDisabled);

    // Corrupt frame cannot alter state or establish authority.
    auto corrupt = heartbeat;
    corrupt[0] = 0x00;
    auto rejected = processor.handle(corrupt.data(), corrupt.size(), 1040);
    assert(!rejected.accepted);
    assert(!rejected.frame_valid);
    assert(!processor.core().motor_enable());

    std::cout << "C4M embedded command processor: PASS\n";
    return 0;
}
