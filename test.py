import time
from machine import Pin, ADC
min_value = None 
max_value = 0

start_time = time.time()
end_time = 5
interval = 0
rising = True

rising_edge_samples = 0

frequency = 1 / end_time

heart_rate = ADC(Pin(26, Pin.IN))

while True:
    time.sleep(0.05)

    if time.time() - start_time >= 5:
        break

    try:
        num = heart_rate.read_u16()
        print(num)

        if min_value is None or num < min_value:
            min_value = num

        elif num > max_value:
            max_value = num

    except ValueError:
        continue

ppi_list = []
threshold = (max_value + min_value) / 2

while True:
    num = heart_rate.read_u16()
    time.sleep(0.01)
    if num > threshold and rising:
        rising_edge_samples += 1
        rising = False
        nyt = time.time_ns() 

    if not rising and num < threshold:
        rising = True
        closing_time = (time.time_ns() - nyt) / (10**6)
        ppi_list.append(closing_time)

    if time.time() - start_time >= end_time:
        break

average_ppi_in_ms = sum(ppi_list) / len(ppi_list)
frequency = round(1000 / average_ppi_in_ms, 3)

print(f"RE-samples: [{rising_edge_samples}]")
print(f"AVG PPI in (MS): {average_ppi_in_ms}")
print(f"Frequency in (S): {frequency}")
