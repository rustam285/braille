import serial

ser = serial.Serial('COM3', 9600)

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        number = int(line)
        print(number)
    except ValueError:
        print("Ошибка преобразования")
    except KeyboardInterrupt:
        print("Прерывание программы")
        break
ser.close()
