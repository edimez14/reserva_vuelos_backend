# documentacion de reserva vuelos backend

## rama dev

## feature/4-flight-api

En esta rama se integró una API externa de vuelos (AviationStack) para permitir búsquedas en tiempo real. Se creó un servicio que consume la API, se añadió el endpoint `/flights/search` y se implementaron filtros básicos.

### Endpoint creado

| Método | Endpoint               | Descripción                          | Autenticación |
|--------|------------------------|--------------------------------------|---------------|
| GET    | /flights/search        | Busca vuelos según parámetros        | Requiere JWT  |

### Parámetros de búsqueda

| Parámetro | Tipo    | Descripción                          | Ejemplo       |
|-----------|---------|--------------------------------------|---------------|
| origin    | string  | Código IATA del aeropuerto origen    | BOG           |
| destination| string | Código IATA del aeropuerto destino   | MDE           |
| date      | string  | Fecha del vuelo (YYYY-MM-DD)         | 2026-03-20    |
| airline   | string  | Nombre de la aerolínea (opcional)    | Avianca       |
| direct    | boolean | Solo vuelos directos (no implementado en API free) | true |

### Flujo de búsqueda

1. El cliente autenticado hace una petición GET al endpoint con los parámetros deseados.
2. El backend valida los parámetros con un serializer.
3. Se instancia el servicio `FlightAPIService` que consulta la API de AviationStack.
4. La respuesta de la API se transforma al formato interno de la aplicación (incluyendo precio simulado, ya que la API gratuita no proporciona tarifas reales).
5. Se devuelve un listado de vuelos con la información estandarizada.

### Dependencias añadidas

- `requests` (para llamadas HTTP a la API externa)
- `python-decouple` (para manejar variables de entorno, ya se usaba)

### Variables de entorno

Se debe agregar en el archivo `.env`:

```
AVIATIONSTACK_API_KEY=tu_api_key
```

### Notas

- La API gratuita de AviationStack tiene un límite de 100 peticiones por mes.
- Los precios son simulados con valores aleatorios entre 150 y 800 USD.
- El parámetro `direct` no se implementa porque la versión gratuita no lo soporta; se ignora.
- Solo usuarios autenticados pueden buscar vuelos (requiere token JWT en el header `Authorization`).

### Ejemplo de uso

```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/flights/search"
```