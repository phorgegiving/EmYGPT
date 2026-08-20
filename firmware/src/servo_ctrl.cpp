#include "config.h"
#include "servo_ctrl.h"
#include <Arduino.h>
#include <esp_system.h>

#define DEFAULT_SPEED 3.0f

static ServoTarget servos[SERVO_COUNT];

static float lidBaseAngle[4];

static const float LID_CLOSED[4] = {
    LID_TL_CLOSED, LID_TR_CLOSED, LID_BL_CLOSED, LID_BR_CLOSED
};

static void set_lids_raw(const float angles[4]) {
    servos[SERVO_LID_TL].angle = angles[0];
    servos[SERVO_LID_TR].angle = angles[1];
    servos[SERVO_LID_BL].angle = angles[2];
    servos[SERVO_LID_BR].angle = angles[3];
}

static void schedule_next_idle_blink();

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
    randomSeed(esp_random());

    init_servo(SERVO_EYES_PAN,  PIN_EYES_PAN,  EYES_PAN_MIN,  EYES_PAN_MAX,  EYES_PAN_CTR,  0);
    init_servo(SERVO_EYES_TILT, PIN_EYES_TILT, EYES_TILT_MIN, EYES_TILT_MAX, EYES_TILT_CTR, 1);

    init_servo(SERVO_LID_TL,    PIN_LID_TL,    LID_TL_MIN, LID_TL_MAX, LID_TL_OPEN, 2);
    init_servo(SERVO_LID_TR,    PIN_LID_TR,    LID_TR_MIN, LID_TR_MAX, LID_TR_OPEN, 3);
    init_servo(SERVO_LID_BL,    PIN_LID_BL,    LID_BL_MIN, LID_BL_MAX, LID_BL_OPEN, 4);
    init_servo(SERVO_LID_BR,    PIN_LID_BR,    LID_BR_MIN, LID_BR_MAX, LID_BR_OPEN, 5);
    init_servo(SERVO_MOUTH,     PIN_MOUTH,     MOUTH_MIN, MOUTH_MAX, MOUTH_MIN, 6);

    lidBaseAngle[0] = LID_TL_OPEN;
    lidBaseAngle[1] = LID_TR_OPEN;
    lidBaseAngle[2] = LID_BL_OPEN;
    lidBaseAngle[3] = LID_BR_OPEN;

    schedule_next_idle_blink();
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
    float clamped = constrain(angle, (float)servos[id].minAngle, (float)servos[id].maxAngle);
    servos[id].angle = clamped;

    if (id >= SERVO_LID_TL && id <= SERVO_LID_BR) {
        lidBaseAngle[id - SERVO_LID_TL] = clamped;
    }
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

// далее моргание

#define BLINK_CLOSE_MS      80
#define BLINK_HOLD_CLOSED_MS 60
#define BLINK_OPEN_MS       100
#define BLINK_HOLD_OPEN_MS  90
#define IDLE_BLINK_MIN_MS   3000
#define IDLE_BLINK_MAX_MS   7000

enum BlinkPhase { BLINK_IDLE, BLINK_CLOSING, BLINK_HOLD_CLOSED, BLINK_OPENING, BLINK_HOLD_OPEN };

static BlinkPhase blinkPhase = BLINK_IDLE;
static unsigned long blinkPhaseStart = 0;
static int blinkRepeatsLeft = 0;
static unsigned long nextIdleBlinkAt = 0;

static void schedule_next_idle_blink() {
    unsigned long delay = IDLE_BLINK_MIN_MS + random(IDLE_BLINK_MAX_MS - IDLE_BLINK_MIN_MS);
    nextIdleBlinkAt = millis() + delay;
}

void servo_start_blink(int times) {
    if (times < 1) times = 1;
    blinkRepeatsLeft = times;
    blinkPhase = BLINK_CLOSING;
    blinkPhaseStart = millis();
    set_lids_raw(LID_CLOSED);
}

void servo_blink_update() {
    unsigned long now = millis();

    switch (blinkPhase) {
        case BLINK_IDLE:
            if (now >= nextIdleBlinkAt) {
                servo_start_blink(1);
                schedule_next_idle_blink();
            }
            break;

        case BLINK_CLOSING:
            if (now - blinkPhaseStart >= BLINK_CLOSE_MS) {
                blinkPhase = BLINK_HOLD_CLOSED;
                blinkPhaseStart = now;
            }
            break;

        case BLINK_HOLD_CLOSED:
            if (now - blinkPhaseStart >= BLINK_HOLD_CLOSED_MS) {
                set_lids_raw(lidBaseAngle);
                blinkPhase = BLINK_OPENING;
                blinkPhaseStart = now;
            }
            break;

        case BLINK_OPENING:
            if (now - blinkPhaseStart >= BLINK_OPEN_MS) {
                blinkRepeatsLeft--;
                if (blinkRepeatsLeft > 0) {
                    blinkPhase = BLINK_HOLD_OPEN;
                    blinkPhaseStart = now;
                } else {
                    blinkPhase = BLINK_IDLE;
                    schedule_next_idle_blink();
                }
            }
            break;

        case BLINK_HOLD_OPEN:
            if (now - blinkPhaseStart >= BLINK_HOLD_OPEN_MS) {
                set_lids_raw(LID_CLOSED);
                blinkPhase = BLINK_CLOSING;
                blinkPhaseStart = now;
            }
            break;
    }
}