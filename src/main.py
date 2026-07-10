from models.search_query import (
    SearchQuery,
    Source,
)

from scraper.google_maps.scraper import (
    search_businesses,
)

from services.export_service import (
    ExportFormat,
    ExportService,
)


keyword = input(
    "Palabra clave: "
)

location = input(
    "Ubicación: "
)

query = SearchQuery(
    source=Source.GOOGLE_MAPS,
    keyword=keyword,
    location=location,
)

result = search_businesses(
    query,
    limit=20,
)

print()

print(
    f"Se encontraron {result.total_found} negocios."
)

print(
    f"Tiempo de ejecución: {result.execution_time:.2f} segundos."
)

print()

for index, business in enumerate(
    result.businesses,
    start=1,
):

    print(f"{index}. {business.name}")
    print(f"   Categoría: {business.category}")
    print(f"   Dirección: {business.address}")
    print(f"   Teléfono: {business.phone}")
    print(f"   Sitio web: {business.website}")
    print()

print("----------------------------------------")
print("Formato de exportación")
print("1) Excel (.xlsx)")
print("2) CSV (.csv)")
print("----------------------------------------")

option = input("> ")

if option == "1":

    export_format = ExportFormat.EXCEL

elif option == "2":

    export_format = ExportFormat.CSV

else:

    print("\nFormato inválido.")
    raise SystemExit(1)

filename = ExportService.export(
    result=result,
    format=export_format,
)

print()

print(
    f"Archivo generado: {filename}"
)