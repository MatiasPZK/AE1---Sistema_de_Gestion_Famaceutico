import os
import pandas as pd

def cargar_inventario(ruta_archivo="inventario.txt"):

    columnas = ["id_med", "nombre", "sucursal", "stock", "precio"]
    
    # Si no existe o tiene 0 bytes de tamaño
    if not os.path.exists(ruta_archivo) or os.path.getsize(ruta_archivo) == 0:
        return pd.DataFrame(columns=columnas)
    
    try:
        df = pd.read_csv(ruta_archivo)
        return df
    except EmptyDataError:
        return pd.DataFrame(columns=columnas)
    
    if os.path.exists(ruta_archivo):
        # Lee el archivo separado por comas directamente
        df = pd.read_csv(ruta_archivo)
    else:
        # Crea la tabla vacía con sus columnas
        columnas = ["id_med", "nombre", "sucursal", "stock", "precio"]
        df = pd.DataFrame(columns=columnas)
    return df

def guardar_inventario(df_inventario, ruta_archivo="inventario.txt"):
    """Guarda la tabla de inventario en el archivo .txt."""
    df_inventario.to_csv(ruta_archivo, index=False)


def exportar_ventas_excel(df_ventas, ruta_excel="ventas_del_dia.xlsx"):
    """Exporta el registro de ventas del día a un archivo Excel (.xlsx)."""
    df_ventas.to_excel(ruta_excel, index=False)