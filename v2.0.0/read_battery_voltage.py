import machine

def read_battery_voltage():
    adc = machine.ADC(29)  # ADC channel for battery voltage
    voltage = adc.read_u16() * (3.3 / 65535) * 2  # Convert ADC reading to voltage
    return voltage