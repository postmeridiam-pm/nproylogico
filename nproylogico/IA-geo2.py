import socket
from geopy.geocoders import Nominatim

# Crear servidor socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5000))
server_socket.listen(1)

geolocator = Nominatim(user_agent="geoapiExercises")

while True:
    client_socket, addr = server_socket.accept()
    data = client_socket.recv(1024).decode()
    if data:
        lat, lon = map(float, data.split(","))
        location = geolocator.reverse((lat, lon))
        client_socket.send(f"Dirección: {location.address}".encode())
    client_socket.close()
