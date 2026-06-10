from database import create_tables
from organizer import organize_downloads


def main() -> None:
	"""Función principal del programa. Organiza los archivos de la carpeta Descargas"""
	create_tables()
	moved_files, errors = organize_downloads()

	for source, destination in moved_files:
		print("Archivo movido:", source.name, "a", destination.parent.name)

	if errors:
		print("\nErrores registrados:")
		for item in errors:
			origin = item[0]
			type_ = item[1]
			msg = item[2]
			print(f"{origin.name} : {type_} - {msg}")


if __name__ == "__main__":
	main()