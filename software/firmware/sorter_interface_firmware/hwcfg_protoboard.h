// Protoboard — hand-wired Pico following the basically V1-2 pinout, but only
// channel 0 (the chute stepper) is actually populated. The other four
// channels V1-2 would define live on a separate SKR Pico feeder board
// instead; both boards are discovered over USB and matched by stepper name
// in the same pool (see machine_platform/control_board.py), so this board
// must report ONLY "chute_stepper" — reporting the other four V1-2 names
// too would collide with the SKR Pico's feeder names.
//
// UART is NOT physically wired on this board. TMC_UART_BUS_COUNT is kept at
// 1 and a bus is still defined so the code compiles and TMC2209::initialize()
// has somewhere to write its (unreceived) register writes, but nothing here
// may assume those writes take effect or call readRegister() at startup —
// current is set by the driver module's trimmer pot instead.

const char* const HW_ID = "protoboard";

const uint8_t STEPPER_COUNT = 1;
const uint8_t STEPPER_STEP_PINS[] = {28};
const uint8_t STEPPER_DIR_PINS[]  = {27};

// Same name on both role branches: this board only ever drives the chute,
// regardless of FIRMWARE_ROLE.
#ifdef FIRMWARE_ROLE_DISTRIBUTION
const char* const STEPPER_NAMES[] = {
    "chute_stepper"
};
#else
const char* const STEPPER_NAMES[] = {
    "chute_stepper"
};
#endif

// Preprocessor macro, not a const — gates `#if TMC_UART_BUS_COUNT > 1` (see
// hwcfg_basically_v1_2.h). Bus/pins/address match V1-2's channel 0 (chute)
// wiring even though nothing is physically connected to it.
#define TMC_UART_BUS_COUNT 1
uart_inst_t* const TMC_UART_BUSES[] = {uart0};
const int TMC_UART_BUS_TX_PINS[] = {16};
const int TMC_UART_BUS_RX_PINS[] = {17};
const int TMC_UART_BAUDRATE = 400000;

const uint8_t TMC_UART_BUS_INDEX[] = {0};
const uint8_t TMC_UART_ADDRESSES[] = {0};

const int STEPPER_nEN_PINS[] = {0}; // Shared EN line, as on V1-2
const int STEPPER_DIAG_PINS[] = {12};

const uint8_t DIGITAL_INPUT_COUNT = 1;
const int digital_input_pins[] = {3}; // Chute home / limit switch

const uint8_t DIGITAL_OUTPUT_COUNT = 0;
const int digital_output_pins[] = {-1}; // Unused: no output pins wired on this board
const int FAN0_OUTPUT_CHANNEL = -1;
const uint8_t LED_OUTPUT_COUNT = 0; // No LED MOSFETs fitted on this board

i2c_inst_t* const I2C_PORT = i2c1;
const int I2C_SDA_PIN = 10;
const int I2C_SCL_PIN = 11;

const uint8_t SERVO_I2C_ADDRESS = 0x40;
