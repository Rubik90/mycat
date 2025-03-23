/**
 * @file 1.c
 * @brief Implementation of HVIL status reading on INTLOCK_UP pin
 * @requirement The MCU shall read HVIL status on the pin INTLOCK_UP every 10 ms
 */

#include <stdint.h>
#include <stdbool.h>

/* Pin definitions */
#define INTLOCK_UP_PORT      GPIOA  /* Adjust based on actual MCU port */
#define INTLOCK_UP_PIN       GPIO_PIN_0  /* Adjust based on actual MCU pin */

/* Timer definitions */
#define HVIL_SAMPLING_PERIOD_MS  10

/* HVIL status type */
struct HVILStatus {
    bool currentState;
    uint32_t lastReadTime;
};

static struct HVILStatus gHvilStatus;

/**
 * @brief Initialize GPIO pin for INTLOCK_UP reading
 * @return true if initialization successful, false otherwise
 */
bool HVIL_InitPin(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    /* Enable GPIO clock */
    __HAL_RCC_GPIOA_CLK_ENABLE();  /* Adjust based on actual port */
    
    /* Configure GPIO pin */
    GPIO_InitStruct.Pin = INTLOCK_UP_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(INTLOCK_UP_PORT, &GPIO_InitStruct);
    
    return true;
}

/**
 * @brief Initialize timer for periodic HVIL status reading
 * @return true if initialization successful, false otherwise
 */
bool HVIL_InitTimer(void) {
    /* Configure timer for 10ms period */
    htim.Instance = TIM2;  /* Adjust based on available timer */
    htim.Init.Period = (HVIL_SAMPLING_PERIOD_MS * 1000) - 1;
    htim.Init.Prescaler = (SystemCoreClock / 1000000) - 1;
    htim.Init.ClockDivision = 0;
    htim.Init.CounterMode = TIM_COUNTERMODE_UP;
    
    if (HAL_TIM_Base_Init(&htim) != HAL_OK) {
        return false;
    }
    
    /* Start timer */
    if (HAL_TIM_Base_Start_IT(&htim) != HAL_OK) {
        return false;
    }
    
    return true;
}

/**
 * @brief Read current HVIL status from INTLOCK_UP pin
 * @return Current pin state
 */
bool HVIL_ReadStatus(void) {
    return (bool)HAL_GPIO_ReadPin(INTLOCK_UP_PORT, INTLOCK_UP_PIN);
}

/**
 * @brief Timer interrupt handler for periodic HVIL status reading
 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
    /* Update HVIL status */
    gHvilStatus.currentState = HVIL_ReadStatus();
    gHvilStatus.lastReadTime = HAL_GetTick();
}

/**
 * @brief Initialize HVIL monitoring system
 * @return true if initialization successful, false otherwise
 */
bool HVIL_Init(void) {
    if (!HVIL_InitPin()) {
        return false;
    }
    
    if (!HVIL_InitTimer()) {
        return false;
    }
    
    /* Initialize status structure */
    gHvilStatus.currentState = false;
    gHvilStatus.lastReadTime = 0;
    
    return true;
}