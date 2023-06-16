#ifndef ENV5_SHT3X_HEADER
#define ENV5_SHT3X_HEADER

#include "Sht3xTypedefs.h"
#include <stdint.h>

/*! initializes the temperature sensor
 *  function has to be called before use of the sensor can be used \n
 *  \b IMPORTANT: needs max 1.5ms for idle state after power up
 *
 * @param[in] i2cHost i2c line to be used with sensor
 * @return            return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xInit(i2c_inst_t *i2cHost);

/*! function to read the value of the serial number from the sensor
 *
 * @param[out] serialNumber memory where the serial number is stored
 * @return                  return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xReadSerialNumber(uint32_t *serialNumber);

/*! function to read the status register (settings) from the sensor
 *
 * @param[out] statusRegister memory where the status register is stored
 * @return                    return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xReadStatusRegister(sht3xStatusRegister_t *statusRegister);

/*! function to read the temperature \b and the humidity from the sensor
 *
 * @param[out] temperature memory where the temperature is stored
 * @param[out] humidity    memory where the temperature is stored
 * @return                 return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xGetTemperatureAndHumidity(float *temperature, float *humidity);

/*! function to read \b only the temperature from the sensor
 *
 * @param temperature[out] memory where the temperature is stored
 * @return                 return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xGetTemperature(float *temperature);

/*! function to read \b only the humidity from the sensor \n
 *  CAUTION: due to hardware limitations the value of the temperature is read
 *           and processed, but not stored
 *
 * @param humidity[out] memory where the humidity is stored
 * @return              return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xGetHumidity(float *humidity);

/*! function to get the last measured value from the sensor buffer
 *
 * @param temperature[out] memory where the temperature is stored
 * @param humidity[out]    memory where the humidity is stored
 * @return                 return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xReadMeasurementBuffer(float *temperature, float *humidity);

/*! function to enable the heater module of the sensor \n
 *  the heater can be used to check the plausibility of the measured values \n
 *  the heater is automatically disabled after a reset
 *
 * @return return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xEnableHeater(void);

/*! function to manually disable the heater module of the sensor
 *
 * @return return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xDisableHeater(void);

/*! function to trigger a soft reset of the sensor which recalibrates the sensor
 * and resets the system controller \n \b IMPORTANT: Hard RESET can be triggered
 * by turning the power off and on again
 *
 * @return return the error code (0 if everything passed)
 */
sht3xErrorCode_t sht3xSoftReset(void);

#endif /*ENV5_SHT3X_HEADER */
