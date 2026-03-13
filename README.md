# documentacion de reserva vuelos backend

## rama dev

### rama feature/1-backend-setup

En esta rama se creo la estructura del proyecto

las apps que usara el backend son las siguientes:
- users (apps para el registro y login de los usuarios)
- flights (datos y consultas de los vuelos y mostrar los vuelos de la api externa)
- reservations (reservacion de vuelos, control de compras)
- tickets (generacion de ticketes de compra)
- emails (envio de emails)

Tambien se crearon los archivos de .env, y se realizo  la conexion a la base de datos de forma remota usando neon console

Tiene el dockerfile para prepararlo para el despligue en fly

### rama feature/2-database-models
