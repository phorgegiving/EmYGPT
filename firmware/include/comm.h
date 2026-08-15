#pragma once
#include <Arduino.h>

void comm_init();
bool comm_has_command();          // проверить команду от хоста
String comm_get_command();        // забрать команду
void comm_send(const char* msg);  // отправить хосту
// мне не понравился С