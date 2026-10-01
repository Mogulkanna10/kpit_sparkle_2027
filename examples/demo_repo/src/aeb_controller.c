#include <stdio.h>
#include <stdbool.h>

/* AUTOSAR AEB C Implementation */

void C_Function_CalculateTTC(float distance, float relative_speed) {
    if (relative_speed > 0.0f) {
        float ttc = distance / relative_speed;
        if (ttc < 1.5f) {
            C_Function_TriggerBrake(ttc);
        }
    }
}

void C_Function_TriggerBrake(float ttc_value) {
    /* Emergency Deceleration Actuation Clamp */
    printf("EMERGENCY BRAKE TRIGGERED: TTC=%f\n", ttc_value);
    Rte_Write_PpBrakeCommand_DecelRequest(8.5f);
}

void C_Function_CabinClimateControl(float target_temp) {
    /* Body Electronics Decoy Function */
    printf("Setting cabin temperature to %f\n", target_temp);
}

void C_Function_UnspecifiedAlert(int alert_code) {
    /* Ambiguous alert function */
    printf("Driver alert code: %d\n", alert_code);
}
