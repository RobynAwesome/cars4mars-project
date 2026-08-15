#include <cassert>
#include <iostream>

#include "include/safety_core.hpp"

int main() {
    c4m::SafetyCore core;

    auto hb = core.heartbeat(0);
    assert(hb.accepted);
    assert(hb.state == c4m::SafetyState::Ready);

    auto drive = core.command(400, 200, 100, 100);
    assert(drive.accepted);
    assert(drive.motor_enable);
    assert(drive.state == c4m::SafetyState::Motion);

    // Heartbeat may keep the controller alive but cannot preserve stale motion.
    core.heartbeat(550);
    auto stale = core.tick(601);
    assert(stale.motor_enable);
    assert(stale.linear_mm_s == 0);
    assert(stale.angular_mrad_s == 0);
    assert(stale.state == c4m::SafetyState::Ready);

    // Liveness loss removes motor enable entirely.
    auto dead = core.tick(1051);
    assert(!dead.motor_enable);
    assert(dead.state == c4m::SafetyState::SafeDisabled);

    // Out-of-bounds command faults closed.
    auto bad = core.command(1200, 0, 1100, 1100);
    assert(!bad.accepted);
    assert(!bad.motor_enable);
    assert(bad.state == c4m::SafetyState::Fault);

    // E-stop dominates all subsequent motion until explicit reset.
    auto stop = core.emergency_stop();
    assert(!stop.motor_enable);
    assert(stop.state == c4m::SafetyState::EstopLatched);
    auto blocked = core.command(100, 0, 1200, 1200);
    assert(!blocked.accepted);
    assert(blocked.state == c4m::SafetyState::EstopLatched);

    auto reset = core.reset_estop();
    assert(reset.accepted);
    assert(!reset.motor_enable);
    assert(reset.state == c4m::SafetyState::SafeDisabled);

    std::cout << "C4M embedded safety core: PASS\n";
    return 0;
}
