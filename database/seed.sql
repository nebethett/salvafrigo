INSERT OR IGNORE INTO categorie (id, nome) VALUES
(1, 'Verdure'),
(2, 'Proteine'),
(3, 'Carboidrati'),
(4, 'Latticini'),
(5, 'Condimenti & Erbe');

INSERT OR IGNORE INTO ingredienti (nome, categoria_id) VALUES
('Pomodori', 1),
('Zucchine', 1),
('Cipolla', 1),
('Aglio', 1),
('Carote', 1),
('Spinaci', 1),
('Peperoni', 1),
('Melanzane', 1),
('Funghi', 1),

('Pollo', 2),
('Uova', 2),
('Tonno', 2),
('Salmone', 2),
('Manzo', 2),
('Tofu', 2),
('Ceci', 2),
('Lenticchie', 2),

('Pasta', 3),
('Patate', 3),
('Riso', 3),
('Pane', 3),
('Farina', 3),
('Couscous', 3),

('Mozzarella', 4),
('Parmigiano', 4),
('Ricotta', 4),
('Latte', 4),
('Burro', 4),
('Yogurt', 4),

('Olio EVO', 5),
('Basilico', 5),
('Prezzemolo', 5),
('Limone', 5),
('Capperi', 5),
('Olive', 5),
('Peperoncino', 5),
('Origano', 5);