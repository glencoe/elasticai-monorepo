#ifndef ENV5_I2C_HEADER
#define ENV5_I2C_HEADER

#include "I2cTypedefs.h"
#include <stdbool.h>
#include <stdint.h>

/*!
 * @brief initializes the ports for the I2C interfaces
 *
 * \IMPORTANT We highly recommend using Env5HwConfig.c
 *
 * @param i2cConfiguration[I2CDevice]: struct that contains the I2C configuration
 * @return              return the error code (0 if everything passed)
 */
i2cErrorCode_t i2cInit(i2cConfiguration_t *i2cConfiguration);

/*!
 * @brief sends a byte array to the slave
 *
 * \IMPORTANT We highly recommend using Env5HwConfig.c
 *
 * @param hostAddress: address of the I2C host (Controller)
 * @param slaveAddress: address of the I2C slave (Sensor)
 * @param commandBuffer: uint8_t array that holds the commands to be send to slave
 * @return              return the error code (0 if everything passed)
 */
i2cErrorCode_t i2cWriteCommand(i2c_inst_t *hostAddress, uint8_t slaveAddress,
                               const uint8_t *commandBuffer, uint16_t sizeOfCommandBuffer);

/*!
 * @brief reads bytes from slave
 *
 * \IMPORTANT We highly recommend using Env5HwConfig.c
 *
 * * @param hostAddress: address of the I2C host (Controller)
 * @param slaveAddress:  address of the I2C slave (Sensor)
 * @param readBuffer:  pointer to uint8_t array that stores the received data
 * @return              return the error code (0 if everything passed)
 */
i2cErrorCode_t i2cReadData(i2c_inst_t *hostAddress, uint8_t slaveAddress, uint8_t *readBuffer,
                           uint8_t sizeOfReadBuffer);

#endif /* ENV5_I2C_HEADER */
