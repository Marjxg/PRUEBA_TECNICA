from fastapi import FastAPI, HTTPException
from schemas import TicketCreate, TicketUpdate, TicketOut
from database import get_connection

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tickets", response_model=list[TicketOut])
def get_tickets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tickets
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": row[0],
            "titulo": row[1],
            "descripcion": row[2],
            "estado": row[3]
        }
        for row in rows
    ]


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, titulo, descripcion, estado
        FROM tickets
        WHERE id = :id
    """, {"id": ticket_id})

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    return {
        "id": row[0],
        "titulo": row[1],
        "descripcion": row[2],
        "estado": row[3]
    }


@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(ticket: TicketCreate):
    conn = get_connection()
    cursor = conn.cursor()

    new_id = cursor.var(int)

    cursor.execute("""
        INSERT INTO tickets (titulo, descripcion)
        VALUES (:titulo, :descripcion)
        RETURNING id INTO :id
    """, {
        "titulo": ticket.titulo,
        "descripcion": ticket.descripcion,
        "id": new_id
    })

    conn.commit()

    ticket_id = int(new_id.getvalue()[0])

    cursor.close()
    conn.close()

    return {
        "id": ticket_id,
        "titulo": ticket.titulo,
        "descripcion": ticket.descripcion,
        "estado": "ABIERTO"
    }


@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(ticket_id: int, ticket: TicketUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT titulo, descripcion, estado
        FROM tickets
        WHERE id = :id
    """, {"id": ticket_id})

    row = cursor.fetchone()

    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    titulo = ticket.titulo if ticket.titulo is not None else row[0]
    descripcion = (
        ticket.descripcion
        if ticket.descripcion is not None
        else row[1]
    )
    estado = ticket.estado if ticket.estado is not None else row[2]

    cursor.execute("""
        UPDATE tickets
        SET titulo = :titulo,
            descripcion = :descripcion,
            estado = :estado
        WHERE id = :id
    """, {
        "titulo": titulo,
        "descripcion": descripcion,
        "estado": estado,
        "id": ticket_id
    })

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "id": ticket_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "estado": estado
    }


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM tickets
        WHERE id = :id
    """, {"id": ticket_id})

    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    conn.commit()

    cursor.close()
    conn.close()