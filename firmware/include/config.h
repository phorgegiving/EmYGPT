#pragma once

// ПИНЫ 
#define PIN_EYES_PAN   13   // горизонталь (глаза имеют одинаковую ось бтв)
#define PIN_EYES_TILT  12   // вертикаль
#define PIN_LID_TL     14   // веко: левый  верхнее
#define PIN_LID_TR     27   // веко: правый верхнее
#define PIN_LID_BL     26   // веко: левый  нижнее
#define PIN_LID_BR     25   // веко: правый нижнее
#define PIN_MOUTH      33   // рот

// ЛИМИТЫ (мкс)
#define SERVO_MIN_US   500
#define SERVO_MAX_US   2500

// УГЛЫ
#define EYES_PAN_MIN   60
#define EYES_PAN_MAX   90
#define EYES_PAN_CTR   75

#define EYES_TILT_MIN  70
#define EYES_TILT_MAX  110
#define EYES_TILT_CTR  90

#define LID_TL_MIN     0
#define LID_TL_MAX     60
#define LID_TL_OPEN    40
#define LID_TL_CLOSED  0
 
#define LID_TR_MIN     0
#define LID_TR_MAX     58
#define LID_TR_OPEN    20
#define LID_TR_CLOSED  58
 
#define LID_BL_MIN     0
#define LID_BL_MAX     50
#define LID_BL_OPEN    0
#define LID_BL_CLOSED  15
 
#define LID_BR_MIN     0
#define LID_BR_MAX     54
#define LID_BR_OPEN    40
#define LID_BR_CLOSED  0

#define MOUTH_MIN      0
#define MOUTH_MAX      40

// BLE
#define BLE_DEVICE_NAME     "AnimatronicHead"
#define BLE_SERVICE_UUID    "12345678-1234-1234-1234-123456789abc"
#define BLE_CHAR_UUID       "abcdefab-cdef-abcd-efab-cdefabcdefab" //сложный UUID вау ахвха

// PWM (вращение)
#define PWM_FREQ       50    // (Гц)
#define PWM_RESOLUTION 16    // (бит)