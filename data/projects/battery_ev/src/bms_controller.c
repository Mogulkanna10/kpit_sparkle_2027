#include "Std_Types.h"

/**
 * @brief BMS_Func_001: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_001(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_002(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_002: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_002(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_003(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_003: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_003(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_004(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_004: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_004(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_005(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_005: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_005(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_006(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_006: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_006(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_007(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_007: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_007(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_008(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_008: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_008(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_009(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_009: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_009(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_010(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_010: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_010(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_011(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_011: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_011(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_012(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_012: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_012(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_013(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_013: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_013(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_014(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_014: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_014(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_015(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_015: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_015(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_016(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_016: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_016(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_017(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_017: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_017(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_018(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_018: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_018(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_019(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_019: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_019(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_020(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_020: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_020(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_021(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_021: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_021(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_022(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_022: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_022(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_023(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_023: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_023(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_024(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_024: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_024(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_025(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_025: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_025(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_026(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_026: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_026(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_027(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_027: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_027(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_028(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_028: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_028(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_029(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_029: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_029(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_030(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_030: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_030(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_031(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_031: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_031(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_032(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_032: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_032(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_033(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_033: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_033(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_034(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_034: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_034(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_035(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_035: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_035(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_036(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_036: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_036(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_037(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_037: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_037(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_038(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_038: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_038(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_039(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_039: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_039(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_040(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_040: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_040(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_041(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_041: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_041(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_042(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_042: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_042(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_043(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_043: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_043(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_044(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_044: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_044(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_045(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_045: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_045(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_046(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_046: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_046(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_047(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_047: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_047(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_048(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_048: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_048(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_049(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_049: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_049(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_050(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_050: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_050(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_051(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_051: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_051(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_052(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_052: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_052(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_053(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_053: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_053(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_054(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_054: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_054(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_055(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_055: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_055(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_056(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_056: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_056(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_057(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_057: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_057(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_058(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_058: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_058(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_059(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_059: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_059(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_060(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_060: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_060(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_061(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_061: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_061(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_062(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_062: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_062(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_063(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_063: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_063(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_064(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_064: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_064(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_065(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_065: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_065(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_066(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_066: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_066(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_067(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_067: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_067(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_068(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_068: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_068(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_069(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_069: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_069(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_070(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_070: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_070(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_071(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_071: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_071(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_072(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_072: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_072(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_073(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_073: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_073(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_074(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_074: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_074(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_075(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_075: Battery state of charge (SoC) estimation and cell balancing algorithm.
 */
Std_ReturnType BMS_Func_075(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_076(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_076: Accumulator pack sub-zero ambient temperature heating loop management.
 */
Std_ReturnType BMS_Func_076(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_077(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_077: Battery over-voltage and thermal runaway detection alarm protocol.
 */
Std_ReturnType BMS_Func_077(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_078(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_078: Insulation resistance monitoring and chassis ground fault detection.
 */
Std_ReturnType BMS_Func_078(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_079(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_079: Battery cell charging rate regulation and pack thermal protection derate mode.
 */
Std_ReturnType BMS_Func_079(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_080(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}

/**
 * @brief BMS_Func_080: High-voltage DC contactor isolation interlock and emergency disconnect.
 */
Std_ReturnType BMS_Func_080(uint32 input_val) {
    Rte_Read_Sensor(input_val);
    if (input_val > 100) { BMS_Func_001(input_val - 1); }
    Rte_Write_Actuator(input_val);
    return 0;
}
