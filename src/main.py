from scraper.google_maps.scraper import search_businesses

input_query = input("Ingrese la consulta de búsqueda: ")

empresas = search_businesses(
    input_query,
    20
)


for index, empresa in enumerate(empresas, start=1):

    print(
        f"{index}. {empresa.name}"
    )

    print(
        f"   Categoría: {empresa.category}"
    )

    print(
        f"   Dirección: {empresa.address}"
    )

    print(
        f"   Teléfono: {empresa.phone}"
    )
    
    print(
        f"   Sitio web: {empresa.website}"
    )

    print()