#define SOURCE_FILE "CONFIGURE-HWTEST"

#include <malloc.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "hardware/spi.h"
#include "pico/stdio.h"
#include "pico/stdlib.h"

#include "Common.h"
#include "Esp.h"
#include "Flash.h"
#include "FpgaConfigurationHandler.h"
#include "Network.h"
#include "Spi.h"
#include "enV5HwController.h"

networkCredentials_t networkCredentials = {.ssid = "SSID", .password = "PWD"};

spi_t spiConfiguration = {
    .spi = spi0, .baudrate = 5000000, .misoPin = 0, .mosiPin = 3, .sckPin = 2};
uint8_t csPin = 1;
const char *baseUrl = "http://192.168.178.24:5000";
uint32_t startAddressConfiguration1 = 0x00000000;
uint32_t startAddressConfiguration2 = 0x00015201;

void initHardwareTest(void) {
    // initialize the serial output
    stdio_init_all();
    while ((!stdio_usb_connected())) {
        // wait for serial connection
    }

    // connect to Wi-Fi network
    espInit();
    networkTryToConnectToNetworkUntilSuccessful(networkCredentials);

    // initialize the Flash and FPGA
    flashInit(&spiConfiguration, csPin);
    env5HwFpgaInit();
    fpgaConfigurationHandlerInitialize();
}

void downloadConfiguration(uint32_t startAddress) {
    fpgaConfigurationHandlerError_t error;
    char url[125];
    strcpy(url, baseUrl);

    if (startAddress == startAddressConfiguration1) {
        strcat(url, "/getfast");
        PRINT_DEBUG("URL: %s", url)

        error = fpgaConfigurationHandlerDownloadConfigurationViaHttp(url, 86116,
                                                                     startAddressConfiguration1);
        if (error != FPGA_RECONFIG_NO_ERROR) {
            PRINT("Error 0x%02X occurred during download.", error)
            return;
        }
    } else {
        strcat(url, "/getslow");
        PRINT_DEBUG("URL: %s", url)

        error = fpgaConfigurationHandlerDownloadConfigurationViaHttp(url, 85540,
                                                                     startAddressConfiguration2);
        if (error != FPGA_RECONFIG_NO_ERROR) {
            PRINT("Error 0x%02X occurred during download.", error)
            return;
        }
    }
    PRINT_DEBUG("Download Successful!")
}
void readConfiguration(uint32_t startAddress) {
    size_t numberOfPages = 1, page = 0;
    if (startAddress == startAddressConfiguration1) {
        numberOfPages = (size_t)ceilf((float)86116 / FLASH_BYTES_PER_PAGE);
    } else if (startAddress == startAddressConfiguration2) {
        numberOfPages = (size_t)ceilf((float)85540 / FLASH_BYTES_PER_PAGE);
    }

    data_t pageBuffer = {.data = NULL, .length = FLASH_BYTES_PER_PAGE};
    do {
        pageBuffer.data = calloc(FLASH_BYTES_PER_PAGE, sizeof(uint8_t));
        flashReadData(startAddress + (page * FLASH_BYTES_PER_PAGE), &pageBuffer);
        PRINT_BYTE_ARRAY("Configuration: ", pageBuffer.data, pageBuffer.length)
        free(pageBuffer.data);
        page++;
    } while (page < numberOfPages);
}
void configureFpga(uint32_t startAddress) {
    fpgaConfigurationHandlerError_t error = fpgaConfigurationFlashFpga(startAddress);
    if (error != FPGA_RECONFIG_NO_ERROR) {
        PRINT("Reconfiguration failed! (0x%02X)", error)
        return;
    }
    PRINT("Reconfiguration successful!")
}
_Noreturn void configurationTest(void) {
    PRINT("===== START TEST =====")

    while (1) {
        char input = getchar_timeout_us(UINT32_MAX);

        switch (input) {
        case 'P':
            env5HwFpgaPowersOn();
            PRINT("FPGA Power: ON")
            break;
        case 'p':
            env5HwFpgaPowersOff();
            PRINT("FPGA Power:OFF")
            break;
        case 'd':
            downloadConfiguration(startAddressConfiguration1);
            break;
        case 'r':
            readConfiguration(startAddressConfiguration1);
            break;
        case 'f':
            configureFpga(startAddressConfiguration1);
            break;
        case 'D':
            downloadConfiguration(startAddressConfiguration2);
            break;
        case 'R':
            readConfiguration(startAddressConfiguration2);
            break;
        case 'F':
            configureFpga(startAddressConfiguration2);
            break;
        default:
            PRINT("Waiting ...")
        }
    }
}

int main() {
    initHardwareTest();
    configurationTest();
}