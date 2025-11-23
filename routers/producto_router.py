from fastapi import APIRouter, HTTPException, Query
from database import Database
from models.producto import Producto, ProductoResponse, ProductoUpdateStock
from typing import List


router = APIRouter(prefix="/productos", tags=["Productos"])

# 🔹 POST: crear nuevo producto
@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: Producto):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Producto (Nombre, Descripcion, Stock, Precio) OUTPUT INSERTED.ID VALUES (?, ?, ?, ?)",
            producto.Nombre, producto.Descripcion, producto.Stock, producto.Precio
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        return ProductoResponse(
            ID=nuevo_id,
            Nombre=producto.Nombre,
            descripcion=producto.Descripcion,
            Stock=producto.Stock,
            Precio=float(producto.Precio)
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")
    finally:
        conn.close()

# 🔹 PATCH: sumar inventario
@router.patch("/{id}/sumar", response_model=ProductoResponse)
def sumar_stock(id: int, datos: ProductoUpdateStock):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Stock FROM Producto WHERE ID = ?", id)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        stock_actual = row[0]
        nuevo_stock = stock_actual + datos.Stock

        cursor.execute(
            "UPDATE Producto SET Stock = ? OUTPUT INSERTED.ID, INSERTED.Nombre, INSERTED.Descripcion, INSERTED.Stock, INSERTED.Precio WHERE ID = ?",
            nuevo_stock, id
        )
        actualizado = cursor.fetchone()
        conn.commit()

        return ProductoResponse(
            ID=actualizado[0],
            Nombre=actualizado[1],
            Descripcion=actualizado[2],
            Stock=actualizado[3],
            Precio=float(actualizado[4])
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al sumar stock: {str(e)}")
    finally:
        conn.close()

# 🔹 DELETE: eliminar artículo
@router.delete("/{id}")
def eliminar_producto(id: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Producto WHERE ID = ?", id)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        conn.commit()
        return {"mensaje": f"Producto con ID {id} eliminado exitosamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(e)}")
    finally:
        conn.close()

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(
    nombre: str = Query(default=None, description="Filtrar por nombre parcial"),
    stock_min: int = Query(default=None, description="Filtrar por stock mínimo"),
    skip: int = Query(default=0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(default=10, ge=1, le=100, description="Número máximo de registros a devolver")
):
    conn = Database.get_connection()
    cursor = conn.cursor()

    # Construir consulta dinámica
    query_base = "SELECT ID, Nombre, Descripcion, Stock, Precio FROM Producto WHERE 1=1"
    params = []

    if nombre:
        query_base += " AND Nombre LIKE ?"
        params.append(f"%{nombre}%")

    if stock_min is not None:
        query_base += " AND Stock >= ?"
        params.append(stock_min)

    query_base += " ORDER BY ID OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
    params.extend([skip, limit])

    cursor.execute(query_base, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        ProductoResponse(
            ID=row[0],
            Nombre=row[1],
            Descripcion=row[2],
            Stock=row[3],
            Precio=float(row[4])
        )
        for row in rows
    ]

@router.put("/{id}/restar/{cantidad}", response_model=ProductoResponse)
def restar_stock(id: int, cantidad: int):
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRAN")
        cursor.execute("SELECT ID, Nombre, Descripcion, Stock, Precio FROM Producto WHERE ID = ?", id)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        stock_actual = row[3]
        if stock_actual < cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")

        cursor.execute("UPDATE Producto SET Stock = Stock - ? WHERE ID = ?", cantidad, id)
        cursor.execute("COMMIT")
        conn.commit()

        return ProductoResponse(
            ID=row[0],
            Nombre=row[1],
            Descripcion=row[2],
            Stock=stock_actual - cantidad,
            Precio=float(row[4])
        )
    except Exception as e:
        cursor.execute("ROLLBACK")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error en la transacción: {str(e)}")
    finally:
        conn.close()


