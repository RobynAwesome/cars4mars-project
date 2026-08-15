#pragma once

#include <cstddef>
#include <cstdint>

#include "c4m_protocol.hpp"
#include "safety_core.hpp"

namespace c4m {

struct ProcessorResult {
    bool accepted;
    bool frame_valid;
    bool sequence_accepted;
    std::uint32_t sequence;
    SafetyDecision safety;
};

class CommandProcessor {
public:
    explicit CommandProcessor(SafetyCore core = SafetyCore{}) : core_(core) {}

    ProcessorResult handle(const std::uint8_t* data, std::size_t length, std::uint32_t now_ms) {
        FrameView frame{};
        if (!decode_frame(data, length, frame)) {
            return ProcessorResult{false, false, false, 0, snapshot(false)};
        }

        // A valid E-stop is safe even when duplicated or replayed. A stale reset
        // or motion command is not safe and must never consume control authority.
        if (frame.type == MessageType::Estop) {
            return ProcessorResult{true, true, true, frame.sequence, core_.emergency_stop()};
        }

        if (have_sequence_ && !is_newer(frame.sequence, last_sequence_)) {
            return ProcessorResult{false, true, false, frame.sequence, snapshot(false)};
        }

        SafetyDecision decision{};
        bool structurally_supported = true;
        switch (frame.type) {
            case MessageType::Heartbeat:
                decision = core_.heartbeat(now_ms);
                break;
            case MessageType::Drive: {
                DrivePayload drive{};
                if (!decode_drive_payload(frame, drive)) {
                    return ProcessorResult{false, true, false, frame.sequence, snapshot(false)};
                }
                decision = core_.command(
                    drive.linear_mm_s,
                    drive.angular_mrad_s,
                    drive.issued_ms,
                    now_ms);
                break;
            }
            case MessageType::ResetEstop:
                decision = core_.reset_estop();
                break;
            case MessageType::Telemetry:
            case MessageType::Estop:
            default:
                structurally_supported = false;
                decision = snapshot(false);
                break;
        }

        if (!structurally_supported) {
            return ProcessorResult{false, true, false, frame.sequence, decision};
        }

        // Consume a fresh sequence even if the safety core rejects the command.
        // This prevents repeated hazardous packets from being retried unchanged.
        last_sequence_ = frame.sequence;
        have_sequence_ = true;
        return ProcessorResult{decision.accepted, true, true, frame.sequence, decision};
    }

    SafetyDecision tick(std::uint32_t now_ms) { return core_.tick(now_ms); }
    const SafetyCore& core() const { return core_; }

private:
    static bool is_newer(std::uint32_t candidate, std::uint32_t previous) {
        const std::uint32_t delta = candidate - previous;
        return delta != 0 && delta < 0x80000000u;
    }

    SafetyDecision snapshot(bool accepted) const {
        return SafetyDecision{
            accepted,
            core_.motor_enable(),
            core_.linear_mm_s(),
            core_.angular_mrad_s(),
            core_.state(),
        };
    }

    SafetyCore core_;
    bool have_sequence_ = false;
    std::uint32_t last_sequence_ = 0;
};

}  // namespace c4m
