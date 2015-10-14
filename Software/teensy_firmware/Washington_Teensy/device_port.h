#include "teensy_unit.h"

class TeensyUnit::DevicePort{

	public:
	
		//~~constructor and destructor~~
		DevicePort(TeensyUnit& teensy_parent, const uint8_t Port_Id);
		~DevicePort();
		void init();

		//~~outputs~~
		void set_output_level(const uint8_t id, const uint8_t level);
		
		//~~inputs~~
		uint16_t read_analog_state(const uint8_t id);  //{IR 0, IR 1}
		bool read_acc_state(int16_t &accel_x, int16_t &accel_y, int16_t &accel_z);  // return array:{x, y, z}
		
		
		//~~configurations~~
		const uint8_t port_id;
		const bool is_all_slow;
		uint8_t output_pins[4];
		uint8_t analog_pins[2];
		uint8_t acc_pin;
		
	private:
	
		TeensyUnit& teensy_unit;
		
		
		//~~accelerometer configurations~~
			
		const uint8_t ACCEL = 0x53; //Accel I2C Address    

		const uint8_t  ACC_ACT_ADDR = 0x27; //ACC Activity/Inactivity control byte
		const uint8_t  ACC_ACT_VAL = 0x00;

		const uint8_t  ACC_BW_ADDR = 0x2C; //ACC BW control byte
		const uint8_t  ACC_BW_VAL = 0x0D; 

		const uint8_t  ACC_PWRCTRL_ADDR = 0x2D; //ACC Power control byte
		const uint8_t  ACC_PWRCTRL_SLEEP = 0x00; 
		const uint8_t  ACC_PWRCTRL_MEASURE = 0x08; 

		const uint8_t  ACC_INRPPT_ADDR = 0x2E; //ACC Interupt control byte
		const uint8_t  ACC_INRPPT_DISABLE = 0x00;  //disable interupt

		const uint8_t  ACC_DATAFORMAT_ADDR = 0x31; //ACC data format byte
		const uint8_t  ACC_DATAFORMAT_VALUE = 0x08;  //Set the range to +/- 2g Full Resolution and make the value right justified with sign extension

		const uint8_t  ACC_FIFO_ADDR = 0x38; //ACC FIFO byte
		const uint8_t  ACC_FIFO_VALUE = 0x00;  // Bypass FIFO

		const uint8_t  ACC_X_LSB_ADDR = 0x32;// ACC X axis LSB byte
						
		
		void switchToAccel(); // switching to the correct accelerometer
		void writeToAccel(const byte address, const byte val);
		
			
};
	