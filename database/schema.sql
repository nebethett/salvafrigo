CREATE TABLE IF NOT EXISTS categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS ingredienti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    FOREIGN KEY (categoria_id) REFERENCES categorie(id),
    UNIQUE(nome, categoria_id)
);

CREATE TABLE IF NOT EXISTS dispensa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingrediente_id INTEGER NOT NULL,
    quantita_grammi INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (ingrediente_id) REFERENCES ingredienti(id),
    UNIQUE(ingrediente_id)
);