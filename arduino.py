import serial
from resources import letters

ser = serial.Serial('COM3', 9600)

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        number = int(line)
        if number != 0:
            letters[number].play_sound()
        else:
            print(number)
    except ValueError:
        print("Ошибка преобразования")
    except KeyboardInterrupt:
        print("Прерывание программы")
        break
ser.close()
