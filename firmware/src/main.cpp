#include <Arduino.h>
#include <ArduinoJson.h>
#include "config.h"
#include "servo_ctrl.h"
#include "comm.h"

#define LOOP_INTERVAL_MS 20   // 50 герц

static unsigned long lastLoop = 0;

// парсинг пакета от хоста формата:
// {"s": [90, 90, 22, 22, 22, 22, 0]}
// индексы: pan, tilt, lid_tl, lid_tr, lid_bl, lid_br, mouth
void handle_command(const String& json) {
    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, json);

    if (err) {
        Serial.print("[JSON] ошибка парсинга: ");
        Serial.println(err.c_str());
        comm_send("{\"ok\":false,\"err\":\"json\"}");
        return;
    }

    // углы делаются тут
    if (doc["s"].is<JsonArray>()) {
        JsonArray arr = doc["s"].as<JsonArray>();
        if (arr.size() == SERVO_COUNT) {
            float angles[SERVO_COUNT];
            for (int i = 0; i < SERVO_COUNT; i++) {
                angles[i] = arr[i].as<float>();
            }
            servo_set_all(angles);
            comm_send("{\"ok\":true}");
            return;
        }
    }

    // одиночные команды
    if (doc["cmd"].is<const char*>()) {
        String cmd = doc["cmd"].as<String>();
        if (cmd == "center") {
            servos_center();
            comm_send("{\"ok\":true,\"cmd\":\"center\"}");
            return;
        }
        if (cmd == "blink") {
            int times = doc["times"] | 1;
            servo_start_blink(times);
            comm_send("{\"ok\":true,\"cmd\":\"blink\"}");
            return;
        }
    }

    comm_send("{\"ok\":false,\"err\":\"unknown\"}");
}

void setup() {
    Serial.begin(115200);
    Serial.println("[BOOT] animatronic-head fw v0.1");

    servos_init();
    servos_center();
    Serial.println("[SERVO] инициализированы, в центре");

    comm_init();
}

void loop() {
    unsigned long now = millis();
    if (now - lastLoop < LOOP_INTERVAL_MS) return;
    lastLoop = now;

    // ВХОДЯЩИЕ КОМАНДЫ
    if (comm_has_command()) {
        String cmd = comm_get_command();
        Serial.print("[CMD] ");
        Serial.println(cmd);
        handle_command(cmd);
    }

    servos_update();

    servo_blink_update();
}