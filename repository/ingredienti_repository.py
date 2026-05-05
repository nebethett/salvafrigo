from database.db import get_connection

def cerca_ingredienti(nome):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.id,
            i.nome,
            c.nome AS categoria
        FROM ingredienti i
        JOIN categorie c ON c.id = i.categoria_id
        WHERE LOWER(i.nome) LIKE LOWER(?)
        ORDER BY i.nome
    """, (f"%{nome}%",))

    risultati = cursor.fetchall()
    conn.close()

    return risultati


def get_categorie_con_ingredienti_db(nome_ingrediente):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            c.id AS categoria_id,
            c.nome AS categoria_nome,
            i.id AS ingrediente_id,
            i.nome AS ingrediente_nome,
            COALESCE(d.quantita_grammi, 0) AS quantita_grammi
        FROM categorie c
        LEFT JOIN ingredienti i ON i.categoria_id = c.id
        LEFT JOIN dispensa d ON d.ingrediente_id = i.id
        WHERE LOWER(i.nome) LIKE LOWER (?)
        ORDER BY c.nome, i.nome
    """, (f"{nome_ingrediente}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows