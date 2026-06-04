# Clases del juego
## Contenedor
**Dispositivo de metal no electrico que sirve para cocinar o contener comida, o un plato**
### Type
* Olla
* Sarten
* Freidora
* Plato
* Taza de batir
### Contendio
* Nada
* Un ingrediente
* Multiples ingredientes
### Maxima cantidad de ingredientes
* Plato: Multiples
* Todo lo demas: Uno
### Cooking Persentage
* cook % (0%-100%)
* burn % (100%-200%)
### Metodos
* isEmpty
* Clear
* AddIngredient
* isInFire
* isDirty (Para el plato)
* isPlaced (si esta en el lugar que lo hace funcionar)
## Ingrediente
### Name
* Nombre del ingrediente (String)
### Status
**Booleanos**
* isCut
* isTrash
* isMixed
* isFried
* isDeepFried
* isBoiled
* canCut
* canMix
* canFry
* canDeepFry
* canBoil
## Mix
* Todos los status de los ingredientes
* Lista de los nombres de los ingredientes
## Muebles
### Type
* Mesa
* Cocina
* Aceite (para la freidora)
* Batidora
* Pila
* Tabla de picar
* Entrega
* Spawner de platos sucios
* Caja de ingredientes
    ### Caja de ingredientes
    si se agarra y no tiene nada encima se agarra el ingrediente designado
    * contenido
    * ingrediente
### Accept
* Cocina: Olla & Sarten
* Aceite: Freidora
* Batidora: Taza de batir
* Pila: Plato
* Mesa: Cualquiera
* Tabla de picar: Ingredientes
* Entrega: Receta completa
### Status
* isUsed (si tiene algo encima)
* isInFire
### Metodos
* placeObject
* Contains
* removeObject
## Receta
**Que salgan desde un archivo json que digan todos los ingredientes que puedan haber disponibles (arroz, pezcado, papa, alga, etc.). Todos los ingredientes tienen que tener sus estados, por ejemplo, el pezcado puede ser cortado y cocinado, la papa cortada y cocinada (en la freidora), pero por ejemplo el alga no se le puede hacer nada, todos los ingredientes pueden ser quemados**
* Lista de ingredientes
* Estado de los ingredientes
* canDeliver  (La receta es el producto final, entregable. Una receta no entregable puede ser ingrediente de otra receta)
## Estado del juego (Kitchen)
* Lista de Ordenes
* Tiempo Restante
* Puntaje
    ### Orden
    * receta
    * status (isDone [si esta entregada])
