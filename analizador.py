import re
import json

def analizar_ticket_ocr(texto_ocr):
    """
    Esta función recibe el texto crudo del ticket y extrae los resultados médicos.
    """
    resultados_extraidos = {}

    # 1. EL DICCIONARIO DE BÚSQUEDA (Expresiones Regulares)
    # Le enseñamos al programa cómo buscar cada prueba específica.
    # Busca el nombre, luego el valor (número o palabra como 'Curva'), y opcionalmente las alertas (H, L, ↑, ↓)
    patrones_de_busqueda = {
        # --- HEMATOLOGÍA ---
        "WBC": r"WBC\s+([\d\.]+)\s*([HL↑↓])?",
        "RBC": r"RBC\s+([\d\.]+)\s*([HL↑↓])?",
        "HGB": r"HGB\s+([\d\.]+)\s*([HL↑↓])?",
        
        # --- BIOQUÍMICA ---
        "GLU": r"GLU\s+([\d\.]+)\s*([HL↑↓])?",
        "AST": r"AST\s+([\d\.]+)\s*([HL↑↓])?",
        "Crea": r"Crea\s+([\d\.]+)\s*([HL↑↓])?",
        "CK-MB": r"CK-MB\s+([\d\.]+)\s*([HL↑↓])?",
        
        # --- COAGULACIÓN ---
        "INR": r"INR\s+([\d\.]+)\s*([HL↑↓])?",
        "APTT": r"APTT\s+(Curva|[\d\.]+)\s*([HL↑↓])?", # Acepta la palabra "Curva"
        "PT": r"PT\s+([\d\.]+)\s*([HL↑↓])?",
        "Fib": r"Fib\s+([\d\.]+)\s*([HL↑↓])?",
        
        # --- MARCADORES ESPECÍFICOS ---
        # Troponina (Formato lista: Elemento: hs-cTnT \n Resultado: 0.187ng/mL ↑)
        "hs-cTnT": r"hs-cTnT[\s\S]*?Resultado:\s*([\d\.]+)[a-zA-Z/]+\s*([HL↑↓])?",
        # Dímero D (Formato con unidades pegadas: 6.55mg/L ↑)
        "D-Dimer": r"D-Dimer\s+([\d\.]+)[a-zA-Z/]+\s*([HL↑↓])?"
    }

    # 2. EL PROCESO DE BÚSQUEDA
    # El programa revisa el texto buscando cada patrón de nuestro diccionario
    for prueba, patron in patrones_de_busqueda.items():
        coincidencia = re.search(patron, texto_ocr, re.IGNORECASE)
        
        if coincidencia:
            # Si encuentra la prueba, guarda el valor (Grupo 1)
            valor = coincidencia.group(1)
            
            # Comprueba si la máquina imprimió una alerta (Grupo 2)
            alerta = coincidencia.group(2) if len(coincidencia.groups()) > 1 else None
            
            # Si hay una H, L, ↑ o ↓, lo marcamos como alterado para ponerlo en negrita
            es_alterado = True if alerta in ['H', 'L', '↑', '↓'] else False
            
            # Guardamos el resultado en nuestra lista limpia
            resultados_extraidos[prueba] = {
                "valor": valor,
                "alterado": es_alterado,
                "incluir_en_pdf": True # Por defecto, todo se incluye hasta que tú digas lo contrario
            }

    return resultados_extraidos

# ==========================================
# 🧪 PRUEBA DEL CÓDIGO (Simulando la lectura de la foto)
# ==========================================

texto_simulado_del_ocr = """
GLU 121.44 H
Crea 0.9
APTT Curva
D-Dimer 6.55mg/L ↑
Elemento:hs-cTnT
Resultado:0.187ng/mL ↑
"""

# Ejecutamos nuestra función
datos_listos = analizar_ticket_ocr(texto_simulado_del_ocr)

# Mostramos el resultado que se enviaría a la web
print(json.dumps(datos_listos, indent=4, ensure_ascii=False))