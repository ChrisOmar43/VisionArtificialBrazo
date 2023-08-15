import cv2
import numpy as np
import serial
import time

y1 = 0
y2 = 0
y3 = 0
paro = 0
COM = 'COM6'
BAUD = 9600
ser = serial.Serial(COM, BAUD)

cap = cv2.VideoCapture(1)

azulBajo = np.array([90, 100, 20], np.uint8)
azulAlto = np.array([120, 255, 255], np.uint8)

rojoBajo1 = np.array([0, 100, 20], np.uint8)
rojoAlto1 = np.array([5, 255, 255], np.uint8)
rojoBajo2 = np.array([175, 100, 20], np.uint8)
rojoAlto2 = np.array([180, 255, 255], np.uint8)

while True:
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Detectar color azul
        mascara_azul = cv2.inRange(frameHSV, azulBajo, azulAlto)
        contornos_azul, _ = cv2.findContours(mascara_azul, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame, contornos_azul, -1, (255, 0, 0), 4)


        # Detectar color rojo
        mascara_rojo1 = cv2.inRange(frameHSV, rojoBajo1, rojoAlto1)
        mascara_rojo2 = cv2.inRange(frameHSV, rojoBajo2, rojoAlto2)
        mascara_rojo = cv2.bitwise_or(mascara_rojo1, mascara_rojo2)
        contornos_rojo, _ = cv2.findContours(mascara_rojo, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(frame, contornos_rojo, -1, (0, 0, 255), 4)

        for c in contornos_azul:
            area = cv2.contourArea(c)
            if area > 500:
                M = cv2.moments(c)
                if M["m00"] == 0:
                    M["m00"] = 1
                x = int(M["m10"] / M["m00"])
                y = int(M['m01'] / M['m00'])
                x = x - 316
                y = (y * -1) + 473
                cv2.circle(frame, (x, y), 7, (0, 0, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, 'Azul: {},{}'.format(x, y), (x + 10, y + 20), font, 1.2, (255, 0, 0), 2, cv2.LINE_AA)
                nuevoContorno = cv2.convexHull(c)
                cv2.drawContours(frame, [nuevoContorno], 0, (255, 0, 0), 3)

                # Acciones correspondientes para el color azul
                color = "azul"
                if 10 <= x <= 30:
                    ser.write(b"centA\n")
                    time.sleep(1)
                    posicionx = x
                    posiciony = y
                    print(f"Color: {color}, Posición X: {posicionx}, Posición Y: {posiciony}")
                    while paro != 1:
                        while ser.in_waiting:
                            dato = ser.readline().decode().rstrip()  # Lee el dato y lo decodifica a texto
                            if dato == "1":
                             paro = 1  # Cambia el valor de 'paro' a 1
                    paro = 0

        for c in contornos_rojo:
            area = cv2.contourArea(c)
            if area > 1000:
                paro = 0
                M = cv2.moments(c)
                if M["m00"] == 0:
                    M["m00"] = 1
                x = int(M["m10"] / M["m00"])
                y = int(M['m01'] / M['m00'])
                x = x - 316
                y = (y * -1) + 473

                cv2.circle(frame, (x, y), 7, (0, 0, 255), -1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame, 'Rojo: {},{}'.format(x, y), (x + 10, y + 60), font, 1.2, (0, 0, 255), 2, cv2.LINE_AA)
                nuevoContorno = cv2.convexHull(c)
                cv2.drawContours(frame, [nuevoContorno], 0, (0, 0, 255), 3)

                # Acciones correspondientes para el color rojo
                color = "rojo"
                if 10 <= x <= 345:
                    ser.write(b"centN\n")
                    time.sleep(1)
                    posicionx = x
                    posiciony = y
                    print(f"Color: {color}, Posición X: {posicionx}, Posición Y: {posiciony}")
                    while paro != 1:
                        while ser.in_waiting:
                            dato = ser.readline().decode().rstrip()  # Lee el dato y lo decodifica a texto
                            if dato == "1":
                                paro = 1  # Cambia el valor de 'paro' a 1
                    paro = 0

        cv2.imshow('mascara_azul', mascara_azul)
        cv2.imshow('mascara_rojo', mascara_rojo)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            ser.close()
            break

cap.release()
cv2.destroyAllWindows()
