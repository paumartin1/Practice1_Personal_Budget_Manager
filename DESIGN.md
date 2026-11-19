
# Design Rationale

I separated the project into different modules to keep the code organized and easier to test.

The CLI handles user interaction, services.py handles financial calculations, validation.py checks transaction data, and storage.py manages the CSV files.

I used CSV because it is simple to read and works well for a small local project.

One limitation is that CSV is not designed for concurrent updates, so this version is intended for a single user.

The separation also makes it easier to change the storage format or add new features later.
