from organizer import organize_downloads


def main() -> None:
	"""Punto de entrada de la aplicación."""
	moved_files = organize_downloads()

	for source, destination in moved_files:
		print(source.name, "->", destination.parent.name)


if __name__ == "__main__":
	main()