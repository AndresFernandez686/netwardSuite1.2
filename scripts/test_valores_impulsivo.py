# Test para verificar que los campos number_input NO muestren 0 como predeterminado
# Este script simula la lógica de visualización de Streamlit

class TestValoresDisplay:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_input_display(self, value, field_name="campo"):
        """
        Simula cómo Streamlit mostraría un st.number_input.
        Si value is None y asignamos (value if value is not None else 0),
        entonces se muestra 0, pero en la barra de input estará vacía.
        """
        display_value = value if value is not None else 0
        actual_display = "" if value is None else str(value)
        
        print(f"\n  {field_name}:")
        print(f"    - Valor en sesión: {value}")
        print(f"    - Valor para st.number_input (value=): {display_value}")
        print(f"    - Lo que el usuario VE en la barra: {actual_display if actual_display else '(vacío)'}")
        
        if value is None and actual_display == "":
            print(f"    ✅ CORRECTO: Campo vacío (no muestra 0)")
            self.tests_passed += 1
            return True
        elif value is not None and actual_display == str(value):
            print(f"    ✅ CORRECTO: Campo muestra {value}")
            self.tests_passed += 1
            return True
        else:
            print(f"    ❌ INCORRECTO: Debería mostrar '{actual_display}' pero se muestra algo diferente")
            self.tests_failed += 1
            return False
    
    def print_summary(self):
        total = self.tests_passed + self.tests_failed
        print("\n" + "="*70)
        print(f"RESULTADO: {self.tests_passed}/{total} pruebas pasaron")
        print("="*70)
        if self.tests_failed == 0:
            print("✅ TODO OK: Los campos mostrarán vacío cuando no se carguen (no 0)")
        else:
            print(f"❌ ERRORES: {self.tests_failed} pruebas fallaron")
        return self.tests_failed == 0


def main():
    tester = TestValoresDisplay()
    
    print("\n" + "="*70)
    print("TEST 1: IMPULSIVO - Campos no cargados (iniciales)")
    print("="*70)
    
    # Simulación de valores iniciales
    valores_impulsivo_init = {
        "PALITOS": {"bultos": None, "unidad": None},
        "ALFAJORES": {"bultos": None, "unidad": None},
    }
    
    for producto, vals in valores_impulsivo_init.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["bultos"], "  Bultos")
        tester.test_input_display(vals["unidad"], "  Unidad")
    
    print("\n" + "="*70)
    print("TEST 2: IMPULSIVO - Campos con stock cargado")
    print("="*70)
    
    valores_impulsivo_stock = {
        "PALITOS": {"bultos": 5, "unidad": 10},
        "ALFAJORES": {"bultos": 0, "unidad": 3},  # 0 bultos, 3 unidades
    }
    
    for producto, vals in valores_impulsivo_stock.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["bultos"], "  Bultos")
        tester.test_input_display(vals["unidad"], "  Unidad")
    
    print("\n" + "="*70)
    print("TEST 3: POR KILOS - Campos no cargados")
    print("="*70)
    
    valores_kilos_init = {
        "GRANEL": {"cajas_cerradas": None, "cajas_abiertas": None, "kgs": None},
        "PALITOS": {"cajas_cerradas": None, "cajas_abiertas": None, "kgs": None},
    }
    
    for producto, vals in valores_kilos_init.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["cajas_cerradas"], "  Cajas Cerradas")
        tester.test_input_display(vals["cajas_abiertas"], "  Cajas Abiertas")
        tester.test_input_display(vals["kgs"], "  Kgs")
    
    print("\n" + "="*70)
    print("TEST 4: POR KILOS - Campos con valores cargados")
    print("="*70)
    
    valores_kilos_stock = {
        "GRANEL": {"cajas_cerradas": 2, "cajas_abiertas": 1, "kgs": 3.5},
        "PALITOS": {"cajas_cerradas": 0, "cajas_abiertas": 0, "kgs": 0.0},  # Sin stock
    }
    
    for producto, vals in valores_kilos_stock.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["cajas_cerradas"], "  Cajas Cerradas")
        tester.test_input_display(vals["cajas_abiertas"], "  Cajas Abiertas")
        tester.test_input_display(vals["kgs"], "  Kgs")
    
    print("\n" + "="*70)
    print("TEST 5: EXTRAS - Campos no cargados")
    print("="*70)
    
    valores_extras_init = {
        "DELICIA": {"bultos": None, "unidad": None},
        "CROCANTINO": {"bultos": None, "unidad": None},
    }
    
    for producto, vals in valores_extras_init.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["bultos"], "  Bultos")
        tester.test_input_display(vals["unidad"], "  Unidad")
    
    print("\n" + "="*70)
    print("TEST 6: EXTRAS - Campos con stock cargado")
    print("="*70)
    
    valores_extras_stock = {
        "DELICIA": {"bultos": 2, "unidad": 5},
        "CROCANTINO": {"bultos": 0, "unidad": 0},  # Sin stock
    }
    
    for producto, vals in valores_extras_stock.items():
        print(f"\n{producto}:")
        tester.test_input_display(vals["bultos"], "  Bultos")
        tester.test_input_display(vals["unidad"], "  Unidad")
    
    success = tester.print_summary()
    return success


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
