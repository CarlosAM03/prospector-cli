from scraper.google_maps import search_businesses

input_query = input("Ingrese la consulta de búsqueda: ")
empresas = search_businesses(
    input_query,
    20
)


print(empresas)