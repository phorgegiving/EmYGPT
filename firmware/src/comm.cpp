#include "config.h"
#include "comm.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

static BLECharacteristic* pCharacteristic = nullptr;
static bool deviceConnected = false;
static volatile bool hasCommand = false;
static String pendingCommand = "";

// Колбеки
class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer*) override {
        deviceConnected = true;
        Serial.println("[BLE] клиент подключился!");
    }
    void onDisconnect(BLEServer* pServer) override {
        deviceConnected = false;
        Serial.println("[BLE] клиент отключился...");
        pServer->startAdvertising();
    }
};

// Колбек для получения данных
class CharCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic* pChar) override {
        std::string value = pChar->getValue();
        if (!value.empty()) {
            pendingCommand = String(value.c_str());
            hasCommand = true;
        }
    }
};

void comm_init() {
    BLEDevice::init(BLE_DEVICE_NAME);
    BLEServer* pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    BLEService* pService = pServer->createService(BLE_SERVICE_UUID);

    pCharacteristic = pService->createCharacteristic(
        BLE_CHAR_UUID,
        BLECharacteristic::PROPERTY_READ    |
        BLECharacteristic::PROPERTY_WRITE   |
        BLECharacteristic::PROPERTY_WRITE_NR |
        BLECharacteristic::PROPERTY_NOTIFY
    );
    pCharacteristic->addDescriptor(new BLE2902());
    pCharacteristic->setCallbacks(new CharCallbacks());

    pService->start();

    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    BLEDevice::startAdvertising();

    Serial.println("[BLE] запущен, ждем подключения...");
}

bool comm_has_command() {
    return hasCommand;
}

String comm_get_command() {
    hasCommand = false;
    return pendingCommand;
}

void comm_send(const char* msg) {
    if (deviceConnected && pCharacteristic) {
        pCharacteristic->setValue(msg);
        pCharacteristic->notify();
    }
}