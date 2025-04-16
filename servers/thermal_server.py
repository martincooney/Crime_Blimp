#thermal code from Adafruit, server code adapted from various sources on google
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import socket
from numpy import random
import time
import ctypes
import board
import busio
import adafruit_mlx90640

#change these parameters as needed
HOST="192.168.1.211"  #server address
PORT=65432

PRINT_TEMPERATURES = True
PRINT_ASCIIART = False

i2c = busio.I2C(board.SCL, board.SDA, frequency=800000) 
mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C")
print([hex(i) for i in mlx.serial_number])
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ #REFRESH_2_HZ
frame = [0] * 768

try:
	mlx.getFrame(frame)
except ValueError:
	# these happen, no biggie - retry
	print("Error: can't read thermal sensor")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
	s.bind((HOST, PORT))
	s.listen(10)
	while True: #loop for connections (clients can reconnect)
		print("Thermal server: waiting for connection")
		conn, addr = s.accept()
		with conn:
			print(f"Connected at {addr}")
			while True: #loop listening for messages

				one_iteration_time_stamp = time.monotonic()

				data=conn.recv(1024)
				if not data:
					print("No data; break")
					break
				print(f"Received data {data}")

				if (data == b"0"):
					print("Received a request for thermal data")

					stamp = time.monotonic()
					try:
						mlx.getFrame(frame)
					except ValueError:
						print("Error: can't read thermal sensor")
						continue

					print("Time to read frame: %0.2f s" % (time.monotonic() - stamp))

					stamp = time.monotonic()
					int_frame= [int( (min( max( ((f - 20.0) / 20.0), 0.0), 1.0) )*255.0) for f in frame]
					y = str(int_frame)
					y += "\n"
					y = y.encode()
					conn.sendall(y) 
					print("Time to process and send frame: %0.2f s" % (time.monotonic() - stamp))

				print("Total time for one iteration: %0.2f s" % (time.monotonic() - one_iteration_time_stamp))

