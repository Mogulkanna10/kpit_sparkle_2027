#include "Rte_Body.h"
#include "Std_Types.h"

/* Body Control Module Implementation */
static uint8 g_cabin_target_temp = 22;
static uint8 g_ambient_lux = 100;

/**
 * @brief Body controller sub-function BODY_Func_001
 */
Std_ReturnType BODY_Func_001(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_002(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_002
 */
Std_ReturnType BODY_Func_002(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_003(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_003
 */
Std_ReturnType BODY_Func_003(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_004(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_004
 */
Std_ReturnType BODY_Func_004(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_005(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_005
 */
Std_ReturnType BODY_Func_005(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_006(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_006
 */
Std_ReturnType BODY_Func_006(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_007(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_007
 */
Std_ReturnType BODY_Func_007(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_008(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_008
 */
Std_ReturnType BODY_Func_008(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_009(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_009
 */
Std_ReturnType BODY_Func_009(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_010(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_010
 */
Std_ReturnType BODY_Func_010(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_011(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_011
 */
Std_ReturnType BODY_Func_011(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_012(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_012
 */
Std_ReturnType BODY_Func_012(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_013(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_013
 */
Std_ReturnType BODY_Func_013(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_014(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_014
 */
Std_ReturnType BODY_Func_014(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_015(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_015
 */
Std_ReturnType BODY_Func_015(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_016(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_016
 */
Std_ReturnType BODY_Func_016(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_017(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_017
 */
Std_ReturnType BODY_Func_017(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_018(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_018
 */
Std_ReturnType BODY_Func_018(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_019(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_019
 */
Std_ReturnType BODY_Func_019(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_020(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_020
 */
Std_ReturnType BODY_Func_020(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_021(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_021
 */
Std_ReturnType BODY_Func_021(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_022(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_022
 */
Std_ReturnType BODY_Func_022(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_023(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_023
 */
Std_ReturnType BODY_Func_023(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_024(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_024
 */
Std_ReturnType BODY_Func_024(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_025(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_025
 */
Std_ReturnType BODY_Func_025(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_026(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_026
 */
Std_ReturnType BODY_Func_026(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_027(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_027
 */
Std_ReturnType BODY_Func_027(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_028(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_028
 */
Std_ReturnType BODY_Func_028(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_029(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_029
 */
Std_ReturnType BODY_Func_029(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_030(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_030
 */
Std_ReturnType BODY_Func_030(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_031(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_031
 */
Std_ReturnType BODY_Func_031(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_032(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_032
 */
Std_ReturnType BODY_Func_032(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_033(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_033
 */
Std_ReturnType BODY_Func_033(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_034(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_034
 */
Std_ReturnType BODY_Func_034(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_035(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_035
 */
Std_ReturnType BODY_Func_035(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_036(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_036
 */
Std_ReturnType BODY_Func_036(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_037(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_037
 */
Std_ReturnType BODY_Func_037(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_038(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_038
 */
Std_ReturnType BODY_Func_038(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_039(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_039
 */
Std_ReturnType BODY_Func_039(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_040(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_040
 */
Std_ReturnType BODY_Func_040(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_041(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_041
 */
Std_ReturnType BODY_Func_041(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_042(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_042
 */
Std_ReturnType BODY_Func_042(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_043(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_043
 */
Std_ReturnType BODY_Func_043(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_044(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_044
 */
Std_ReturnType BODY_Func_044(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_045(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_045
 */
Std_ReturnType BODY_Func_045(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_046(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_046
 */
Std_ReturnType BODY_Func_046(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_047(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_047
 */
Std_ReturnType BODY_Func_047(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_048(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}

/**
 * @brief Body controller sub-function BODY_Func_048
 */
Std_ReturnType BODY_Func_048(uint32 input_data) {
    Rte_Read_Sensor(input_data);
    if (input_data > 100) {
        BODY_Func_001(input_data - 1);
    }
    Rte_Write_Actuator(input_data);
    return E_OK;
}
