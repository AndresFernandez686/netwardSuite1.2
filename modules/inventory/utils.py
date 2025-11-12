#Utilidades generales (conversiones de datos y helpers)
import pandas as pd
import io

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes en formato CSV"""
    return df.to_csv(index=False).encode("utf-8")

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Convierte un DataFrame a bytes en formato Excel (xlsx)"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Puedes agregar aquí más utilidades generales 
