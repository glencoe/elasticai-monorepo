#include <sys/cdefs.h>
#ifndef ENV5_UART_INTERNAL_HEADER
#define ENV5_UART_INTERNAL_HEADER

/*! \brief RX interrupt handler
 *
 */
//_Noreturn void uartInternalCallbackUartRxInterrupt();

void uartInternalHandleNewLine(void);

void checkAndHandleNewChar(void);

void setNewUARTInterrupt(void);

#endif /* ENV5_UART_INTERNAL_HEADER */
