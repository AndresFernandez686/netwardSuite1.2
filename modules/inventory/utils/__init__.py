# Módulo de utilidades
try:
    from ..utils import df_to_csv_bytes, df_to_excel_bytes
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from utils import df_to_csv_bytes, df_to_excel_bytes
    except ImportError:
        def df_to_csv_bytes(df):
            return df.to_csv(index=False).encode('utf-8')
        
        def df_to_excel_bytes(df):
            return b"Excel not available"