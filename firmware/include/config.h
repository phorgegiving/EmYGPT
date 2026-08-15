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
#define EYES_PAN_MAX   120
#define EYES_PAN_CTR   90

#define EYES_TILT_MIN  70
#define EYES_TILT_MAX  110
#define EYES_TILT_CTR  90

#define LID_MIN        0
#define LID_MAX        45
#define LID_CTR        22

#define MOUTH_MIN      0
#define MOUTH_MAX      30

// BLE
#define BLE_DEVICE_NAME     "AnimatronicHead"
#define BLE_SERVICE_UUID    "12345678-1234-1234-1234-123456789abc"
#define BLE_CHAR_UUID       "abcdefab-cdef-abcd-efab-cdefabcdefab" //сложный UUID вау ахвха

// PWM (вращение)
#define PWM_FREQ       50    // (Гц)
#define PWM_RESOLUTION 16    // (бит)