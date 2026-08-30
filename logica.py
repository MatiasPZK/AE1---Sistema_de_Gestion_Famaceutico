import pandas as pd
from datetime import datetime

def iniciar_tabla_ventas():
    """Crea una tabla vacía para registrar las ventas del día."""
    columnas = [
        "id_venta",
        "fecha_hora",
        "id_med",
        "nombre",
        "cantidad",
        "precio_unitario",
        "total",
        "vendedor",
        "comision"
    ]
    return pd.DataFrame(columns=columnas)

def registrar_venta(df_inventario, df_ventas, id_med, cantidad, vendedor, tasa_comision=0.10):
    """
    Intenta realizar una venta.
    Devuelve: (True, mensaje_exito) si se pudo vender, o (False, mensaje_error) si falló.
    """
    # 1. Filtramos la fila del medicamento por su ID
    fila = df_inventario[df_inventario["id_med"] == id_med]
    
    if fila.empty:
        return False, "Error: El medicamento no existe en el inventario."
    
    # Obtenemos el índice real de la fila en el DataFrame
    idx = fila.index[0]
    stock_actual = df_inventario.loc[idx, "stock"]
    
    # 2. Validar stock
    if cantidad > stock_actual:
        return False, f"Stock insuficiente. Stock actual: {stock_actual} unidades."
    
    if cantidad <= 0:
        return False, "La cantidad a vender debe ser mayor a 0."

    # 3. Descontar stock
    df_inventario.loc[idx, "stock"] = stock_actual - cantidad
    
    # 4. Cálculos
    nombre = df_inventario.loc[idx, "nombre"]
    precio = df_inventario.loc[idx, "precio"]
    total = cantidad * precio
    comision = total * tasa_comision
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_venta = len(df_ventas) + 1

    # 5. Crear la nueva fila de venta
    nueva_venta = {
        "id_venta": id_venta,
        "fecha_hora": fecha_actual,
        "id_med": id_med,
        "nombre": nombre,
        "cantidad": cantidad,
        "precio_unitario": precio,
        "total": total,
        "vendedor": vendedor,
        "comision": comision
    }
    
    # Concatenamos la nueva fila al DataFrame de ventas
    df_ventas.loc[len(df_ventas)] = nueva_venta
    
    return True, f"Venta exitosa! Total: ${total:,.2f} | Comisión: ${comision:,.2f}"

def actualizar_stock(df_inventario, id_med, cantidad_a_sumar):
    """Suma unidades al stock existente de un medicamento."""
    fila = df_inventario[df_inventario["id_med"] == id_med]
    
    if fila.empty:
        return False, "Medicamento no encontrado."
    
    if cantidad_a_sumar <= 0:
        return False, "La cantidad a reponer debe ser mayor a 0."
        
    idx = fila.index[0]
    df_inventario.loc[idx, "stock"] += cantidad_a_sumar
    return True, f"Stock actualizado con éxito. Nuevo stock: {df_inventario.loc[idx, 'stock']}"

def obtener_metricas_dia(df_ventas):
    """Devuelve el total de ingresos, comisiones y comisiones por vendedor."""
    if df_ventas.empty:
        return {
            "total_ingresos": 0.0,
            "total_comisiones": 0.0,
            "por_vendedor": {}
        }
    
    total_ingresos = df_ventas["total"].sum()
    total_comisiones = df_ventas["comision"].sum()
    
    # Agrupamos por vendedor para saber cuánto ganó cada uno
    comisiones_vendedor = df_ventas.groupby("vendedor")["comision"].sum().to_dict()
    
    return {
        "total_ingresos": total_ingresos,
        "total_comisiones": total_comisiones,
        "por_vendedor": comisiones_vendedor
    }