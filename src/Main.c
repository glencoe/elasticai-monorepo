#define SOURCE_FILE "MAIN"

// src headers
#include "Common.h"
#include "Esp.h"
#include "FreeRtosQueueWrapper.h"
#include "FreeRtosTaskWrapper.h"
#include "I2c.h"
#include "MqttBroker.h"
#include "Network.h"
#include "NetworkConfiguration.h"
#include "Pac193x.h"
#include "hardware/i2c.h"

// external headers
#include <hardware/watchdog.h>
#include <pico/bootrom.h>
#include <pico/stdlib.h>

static pac193xSensorConfiguration_t sensor1 = {
    .i2c_host = i2c1,
    .i2c_slave_address = PAC193X_I2C_ADDRESS_499R,
    .powerPin = -1,
    .usedChannels = {.uint_channelsInUse = 0b00001111},
    .rSense = {0.82f, 0.82f, 0.82f, 0.82f},
};
#define PAC193X_CHANNEL_SENSORS PAC193X_CHANNEL01
#define PAC193X_CHANNEL_RAW PAC193X_CHANNEL02
#define PAC193X_CHANNEL_MCU PAC193X_CHANNEL03
#define PAC193X_CHANNEL_WIFI PAC193X_CHANNEL04

float measureValue(pac193xSensorConfiguration_t sensor, pac193xChannel_t channel) {
    float measurement;

    pac193xErrorCode_t errorCode =
        pac193xGetMeasurementForChannel(sensor, channel, PAC193X_VSOURCE_AVG, &measurement);
    if (errorCode != PAC193X_NO_ERROR) {
        PRINT("  \033[0;31mFAILED\033[0m; pac193x_ERROR: %02X", errorCode)
        return -1;
    }
    return measurement;
}

_Noreturn void mainTask(void) {
    networkTryToConnectToNetworkUntilSuccessful(networkCredentials);
    mqttBrokerConnectToBrokerUntilSuccessful(mqttHost, "eip://uni-due.de/es", "enV5");

    PRINT("===== INIT SENSOR 1 =====")
    pac193xErrorCode_t errorCode;
    while (1) {
        errorCode = pac193xInit(sensor1);
        if (errorCode == PAC193X_NO_ERROR) {
            PRINT("Initialised PAC193X sensor 1.\n")
            break;
        }
        PRINT("Initialise PAC193X failed; pac193x_ERROR: %02X\n", errorCode)
        sleep_ms(500);
    }

    while (true) {
        float channelWifiValue = measureValue(sensor1, PAC193X_CHANNEL_WIFI);
        sleep_ms(1000);
        float channelSensorValue = measureValue(sensor1, PAC193X_CHANNEL_SENSORS);
        sleep_ms(1000);
    }
}

// Goes into bootloader mode when 'r' is pressed
_Noreturn void enterBootModeTask(void) {
    while (true) {
        if (getchar_timeout_us(10) == 'r' || !stdio_usb_connected()) {
            reset_usb_boot(0, 0);
        }
        // Watchdog update needs to be performed frequent, otherwise the device
        // will crash
        watchdog_update();
        freeRtosTaskWrapperTaskSleep(1000);
    }
}

void init(void) {
    // First check if we crash last time -> reboot into boot rom mode
    if (watchdog_enable_caused_reboot()) {
        reset_usb_boot(0, 0);
    }
    // init usb, queue and watchdog
    stdio_init_all();
    // waits for usb connection, REMOVE to continue without waiting for
    // connection
    while ((!stdio_usb_connected()))
        ;
    // Checks connection to ESP and initializes
    espInit();
    // Create FreeRTOS task queue
    freeRtosQueueWrapperCreate();
    // enables watchdog to check for reboots
    watchdog_enable(2000, 1);
}

int main() {
    init();
    freeRtosTaskWrapperRegisterTask(enterBootModeTask, "enterBootModeTask");
    freeRtosTaskWrapperRegisterTask(mainTask, "mainTask");
    // Starts FreeRTOS tasks
    freeRtosTaskWrapperStartScheduler();
}
