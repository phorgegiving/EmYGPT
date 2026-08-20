#include "config.h"
#include "servo_ctrl.h"
#include <Arduino.h>

#define DEFAULT_SPEED 3.0f

static ServoTarget servos[SERVO_COUNT];

static uint32_t angle_to_duty(float angle, int minAngle, int maxAngle) {
    float clamped = constrain(angle, (float)minAngle, (float)maxAngle);
    float us = SERVO_MIN_US + (clamped / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
    return (uint32_t)((us / 20000.0f) * 65535.0f);
}

static void apply(ServoID id) {
    uint32_t duty = angle_to_duty(
        servos[id].current,
        servos[id].minAngle,
        servos[id].maxAngle
    );
    ledcWrite(servos[id].pwmChannel, duty);
}

static void init_servo(ServoID id, int pin, int minA, int maxA, int center, int ch) {
    servos[id].pin       = pin;
    servos[id].minAngle  = minA;
    servos[id].maxAngle  = maxA;
    servos[id].current   = center;
    servos[id].angle     = center;
    servos[id].speed     = DEFAULT_SPEED;
    servos[id].pwmChannel = ch;

    ledcSetup(ch, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(pin, ch);
    apply(id);
}

void servos_init() {
    init_servo(SERVO_EYES_PAN,  PIN_EYES_PAN,  EYES_PAN_MIN,  EYES_PAN_MAX,  EYES_PAN_CTR,  0);
    init_servo(SERVO_EYES_TILT, PIN_EYES_TILT, EYES_TILT_MIN, EYES_TILT_MAX, EYES_TILT_CTR, 1);
    init_servo(SERVO_LID_TL,    PIN_LID_TL,    LID_TL_MIN, LID_TL_MAX, LID_TL_OPEN, 2);
    init_servo(SERVO_LID_TR,    PIN_LID_TR,    LID_TR_MIN, LID_TR_MAX, LID_TR_OPEN, 3);
    init_servo(SERVO_LID_BL,    PIN_LID_BL,    LID_BL_MIN, LID_BL_MAX, LID_BL_OPEN, 4);
    init_servo(SERVO_LID_BR,    PIN_LID_BR,    LID_BR_MIN, LID_BR_MAX, LID_BR_OPEN, 5);
    init_servo(SERVO_MOUTH,     PIN_MOUTH,     MOUTH_MIN, MOUTH_MAX, MOUTH_MIN, 6);
}

void servos_update() {
    for (int i = 0; i < SERVO_COUNT; i++) {
        float diff = servos[i].angle - servos[i].current;
        if (abs(diff) < 0.5f) {
            servos[i].current = servos[i].angle;
        } else {
            float step = constrain(diff, -servos[i].speed, servos[i].speed);
            servos[i].current += step;
        }
        apply((ServoID)i);
    }
}

void servo_set_target(ServoID id, float angle) {
    servos[id].angle = constrain(angle, (float)servos[id].minAngle, (float)servos[id].maxAngle);
}

void servo_set_all(float angles[SERVO_COUNT]) {
    for (int i = 0; i < SERVO_COUNT; i++) {
        servo_set_target((ServoID)i, angles[i]);
    }
}

void servos_center() {
    servo_set_target(SERVO_EYES_PAN,  EYES_PAN_CTR);
    servo_set_target(SERVO_EYES_TILT, EYES_TILT_CTR);
    servo_set_target(SERVO_LID_TL,   LID_TL_OPEN);
    servo_set_target(SERVO_LID_TR,   LID_TR_OPEN);
    servo_set_target(SERVO_LID_BL,   LID_BL_OPEN);
    servo_set_target(SERVO_LID_BR,   LID_BR_OPEN);
    servo_set_target(SERVO_MOUTH,    MOUTH_MIN);
}

