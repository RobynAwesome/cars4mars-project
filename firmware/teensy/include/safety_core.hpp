#pragma once

#include <cstdint>

namespace c4m {

enum class SafetyState : std::uint8_t {
    SafeDisabled = 0,
    Ready = 1,
    Motion = 2,
    EstopLatched = 3,
    Fault = 4,
};

struct SafetyDecision {
    bool accepted;
    bool motor_enable;
    std::int16_t linear_mm_s;
    std::int16_t angular_mrad_s;
    SafetyState state;
};

class SafetyCore {
public:
    SafetyCore(
        std::int16_t max_linear_mm_s = 1000,
        std::int16_t max_angular_mrad_s = 2000,
        std::uint32_t command_timeout_ms = 500,
        std::uint32_t liveness_timeout_ms = 500)
        : max_linear_mm_s_(max_linear_mm_s),
          max_angular_mrad_s_(max_angular_mrad_s),
          command_timeout_ms_(command_timeout_ms),
          liveness_timeout_ms_(liveness_timeout_ms) {}

    SafetyDecision heartbeat(std::uint32_t now_ms) {
        if (estop_latched_) return decision(false);
        last_liveness_ms_ = now_ms;
        have_liveness_ = true;
        if (state_ == SafetyState::SafeDisabled && !faulted_) state_ = SafetyState::Ready;
        return decision(true);
    }

    SafetyDecision command(
        std::int16_t linear_mm_s,
        std::int16_t angular_mrad_s,
        std::uint32_t issued_ms,
        std::uint32_t now_ms) {
        if (estop_latched_) return decision(false);
        if (issued_ms > now_ms) return fault();
        if ((now_ms - issued_ms) > command_timeout_ms_) return fault();
        if (abs16(linear_mm_s) > max_linear_mm_s_) return fault();
        if (abs16(angular_mrad_s) > max_angular_mrad_s_) return fault();

        faulted_ = false;
        linear_mm_s_ = linear_mm_s;
        angular_mrad_s_ = angular_mrad_s;
        motor_enable_ = true;
        state_ = (linear_mm_s != 0 || angular_mrad_s != 0) ? SafetyState::Motion : SafetyState::Ready;
        last_command_ms_ = now_ms;
        last_liveness_ms_ = now_ms;
        have_command_ = true;
        have_liveness_ = true;
        return decision(true);
    }

    SafetyDecision tick(std::uint32_t now_ms) {
        if (estop_latched_) return decision(false);

        if (have_command_ && (now_ms - last_command_ms_) > command_timeout_ms_) {
            zero_velocity();
            if (motor_enable_) state_ = SafetyState::Ready;
        }

        if (!have_liveness_ || (now_ms - last_liveness_ms_) > liveness_timeout_ms_) {
            return safe_disable();
        }
        return decision(true);
    }

    SafetyDecision emergency_stop() {
        estop_latched_ = true;
        faulted_ = true;
        zero_velocity();
        motor_enable_ = false;
        state_ = SafetyState::EstopLatched;
        return decision(false);
    }

    SafetyDecision reset_estop() {
        estop_latched_ = false;
        faulted_ = false;
        zero_velocity();
        motor_enable_ = false;
        have_command_ = false;
        have_liveness_ = false;
        state_ = SafetyState::SafeDisabled;
        return decision(true);
    }

    SafetyState state() const { return state_; }
    bool motor_enable() const { return motor_enable_; }
    std::int16_t linear_mm_s() const { return linear_mm_s_; }
    std::int16_t angular_mrad_s() const { return angular_mrad_s_; }

private:
    static std::int32_t abs16(std::int16_t value) {
        return value < 0 ? -static_cast<std::int32_t>(value) : static_cast<std::int32_t>(value);
    }

    void zero_velocity() {
        linear_mm_s_ = 0;
        angular_mrad_s_ = 0;
    }

    SafetyDecision safe_disable() {
        zero_velocity();
        motor_enable_ = false;
        state_ = SafetyState::SafeDisabled;
        return decision(false);
    }

    SafetyDecision fault() {
        faulted_ = true;
        zero_velocity();
        motor_enable_ = false;
        state_ = SafetyState::Fault;
        return decision(false);
    }

    SafetyDecision decision(bool accepted) const {
        return SafetyDecision{accepted, motor_enable_, linear_mm_s_, angular_mrad_s_, state_};
    }

    std::int16_t max_linear_mm_s_;
    std::int16_t max_angular_mrad_s_;
    std::uint32_t command_timeout_ms_;
    std::uint32_t liveness_timeout_ms_;

    SafetyState state_ = SafetyState::SafeDisabled;
    bool motor_enable_ = false;
    bool estop_latched_ = false;
    bool faulted_ = false;
    bool have_command_ = false;
    bool have_liveness_ = false;
    std::int16_t linear_mm_s_ = 0;
    std::int16_t angular_mrad_s_ = 0;
    std::uint32_t last_command_ms_ = 0;
    std::uint32_t last_liveness_ms_ = 0;
};

}  // namespace c4m
