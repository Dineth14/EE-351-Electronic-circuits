"""Converter registry for dynamic model creation."""

from power_electronics.converters.ac_dc import (
    FullBridgeRectifier,
    FullWaveCenterTapRectifier,
    HalfWaveRectifier,
    SCRFullBridgeRectifier,
    SCRHalfWaveRectifier,
    ThreePhaseBridgeRectifier,
    ThreePhaseHalfRectifier,
    ViennaRectifier,
)
from power_electronics.converters.dc_ac import (
    CascadedHBridgeInverter,
    NPCInverter,
    PushPullInverter,
    SinglePhaseHBridgeVSI,
    ThreePhaseVSI,
)
from power_electronics.converters.dc_dc import (
    BoostConverter,
    BuckBoostConverter,
    BuckConverter,
    CukConverter,
    DualActiveBridgeConverter,
    FlybackConverter,
    ForwardConverter,
    SepicConverter,
)

CONVERTER_REGISTRY = {
    "half_wave": HalfWaveRectifier,
    "full_wave_centertap": FullWaveCenterTapRectifier,
    "full_bridge": FullBridgeRectifier,
    "three_phase_half": ThreePhaseHalfRectifier,
    "three_phase_bridge": ThreePhaseBridgeRectifier,
    "scr_half_wave": SCRHalfWaveRectifier,
    "scr_full_bridge": SCRFullBridgeRectifier,
    "vienna_rectifier": ViennaRectifier,
    "single_phase_hbridge": SinglePhaseHBridgeVSI,
    "three_phase_vsi": ThreePhaseVSI,
    "push_pull": PushPullInverter,
    "cascaded_hbridge": CascadedHBridgeInverter,
    "npc_inverter": NPCInverter,
    "buck": BuckConverter,
    "boost": BoostConverter,
    "buck_boost": BuckBoostConverter,
    "cuk": CukConverter,
    "sepic": SepicConverter,
    "flyback": FlybackConverter,
    "forward": ForwardConverter,
    "dual_active_bridge": DualActiveBridgeConverter,
}

__all__ = ["CONVERTER_REGISTRY"]
