#pragma once
#include <Arduino.h>

// индексы серваков
enum ServoID {
    SERVO_EYES_PAN = 0,
    SERVO_EYES_TILT,
    SERVO_LID_TL,
    SERVO_LID_TR,
    SERVO_LID_BL,
    SERVO_LID_BR,
    SERVO_MOUTH,
    SERVO_COUNT
};

struct ServoTarget {
    float angle;      // цель.угол
    float current;    // текущий
    float speed;      // easing speed 
    int   pin;
    int   minAngle;
    int   maxAngle;
    int   pwmChannel;
};

void servos_init();
void servos_update();                          // луп!!!
void servo_set_target(ServoID id, float angle);
void servo_set_all(float angles[SERVO_COUNT]);
void servos_center();                          // сбросить все сервы в центральное положение