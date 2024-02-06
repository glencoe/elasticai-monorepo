/*
 * This is an autogenerated stub.
 * Do not change it manually.
 */

#include "flow_prediction.h"
#include "./middleware.h"
#include "Sleep.h"
#include <pico/stdlib.h>
#include <stdbool.h>
#include <stdint.h>

#define ADDR_SKELETON_INPUTS 0
#define ADDR_COMPUTATION_ENABLE 100

static void modelCompute(bool enable);
static uint8_t get_id(void);

static uint64_t accelerator_id = 47;
static uint32_t accelerator_addr = 4000;

bool flow_prediction_deploy(void) {
    middlewareInit();
    middlewareConfigureFpga(accelerator_addr);
    sleep_for_ms(200);
    bool is_deployed_successfully = (get_id() == accelerator_id);
    middlewareDeinit();
    return is_deployed_successfully;
}

int8_t flow_prediction_predict(int8_t *inputs) {
    int8_t _result;

    middlewareInit();
    middlewareUserlogicEnable();
    middlewareWriteBlocking(ADDR_SKELETON_INPUTS + 0, (uint8_t *)(inputs), 3);
    modelCompute(true);

    while (middlewareUserlogicGetBusyStatus())
        ;
    sleep_ms(1);

    middlewareReadBlocking(ADDR_SKELETON_INPUTS + 0, (uint8_t *)(&_result), 1);
    middlewareReadBlocking(ADDR_SKELETON_INPUTS + 0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    //    middlewareReadBlocking(ADDR_SKELETON_INPUTS+0, (uint8_t *)(&_result), 1);
    modelCompute(false);
    middlewareUserlogicDisable();
    middlewareDeinit();
    return _result;
}

static void modelCompute(bool enable) {
    uint8_t cmd = (enable ? 1 : 0);
    middlewareWriteBlocking(ADDR_COMPUTATION_ENABLE, &cmd, 1);
}

static uint8_t get_id(void) {
    middlewareUserlogicEnable();
    uint8_t id[1];
    middlewareReadBlocking(2000, id, 1);
    middlewareUserlogicDisable();
    return id[0];
}