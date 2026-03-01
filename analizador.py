import re

def analizar_ticket_ocr(texto_ocr):
    resultados_extraidos = {}

    # DICCIONARIO DE BÚSQUEDA Y TRADUCCIÓN MÁGICA
    # Formato: "Nombre en Ticket": ("Nombre en Español", "Patrón Regex")
    # Si el "Nombre en Español" es None, el motor lo ignorará (No aparecerá en el PDF)
    patrones_de_busqueda = {
        # --- HEMATOGRAMA ---
        "WBC": ("Leucocitos", r"WBC\s+([\d\.,]+)\s*([HL↑↓])?"),
        "RBC": ("Hematíes", r"RBC\s+([\d\.,]+)\s*([HL↑↓])?"),
        "HGB": ("Hemoglobina", r"HGB\s+([\d\.,]+)\s*([HL↑↓])?"),
        "HCT": ("Hematocrito", r"HCT\s+([\d\.,]+)\s*([HL↑↓])?"),
        "MCV": ("VCM (Volumen Corpuscular Medio)", r"MCV\s+([\d\.,]+)\s*([HL↑↓])?"),
        "MCH": ("HCM (Hemoglobina Corpuscular Media)", r"MCH\s+([\d\.,]+)\s*([HL↑↓])?"),
        "MCHC": ("CHCM", r"MCHC\s+([\d\.,]+)\s*([HL↑↓])?"),
        "PLT": ("Plaquetas", r"PLT\s+([\d\.,]+)\s*([HL↑↓])?"),
        "LYM%": ("Linfocitos (%)", r"LYM%\s+([\d\.,]+)\s*([HL↑↓])?"),
        "MXD%": ("Monocitos (%)", r"MXD%\s+([\d\.,]+)\s*([HL↑↓])?"),
        "NEUT%": ("Neutrófilos (%)", r"NEUT%\s+([\d\.,]+)\s*([HL↑↓])?"),
        "LYM#": (None, r"LYM#\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto
        "MXD#": (None, r"MXD#\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto
        "NEUT#": (None, r"NEUT#\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto
        "RDW-SD": ("RDW (Amplitud Dist. Eritrocitaria)", r"RDW-SD\s+([\d\.,]+)\s*([HL↑↓])?"),
        "RDW-CV": (None, r"RDW-CV\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto
        "PDW": (None, r"PDW\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto
        "MPV": ("VPM (Volumen Plaquetario Medio)", r"MPV\s+([\d\.,]+)\s*([HL↑↓])?"),
        "P-LCR": (None, r"P-LCR\s+([\d\.,]+)\s*([HL↑↓])?"), # Oculto

        # --- COAGULACIÓN Y MARCADORES ---
        "INR": ("INR", r"INR\s+([\d\.,]+)\s*([HL↑↓])?"),
        "APTT": ("TTPA", r"APTT\s+(Curva|[\d\.,]+)\s*([HL↑↓])?"),
        "PT": ("Tiempo de Protrombina", r"PT\s+([\d\.,]+)\s*([HL↑↓])?"),
        "TT": ("Tiempo de Trombina", r"TT\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Fib": ("Fibrinógeno", r"Fib\s+([\d\.,]+)\s*([HL↑↓])?"),
        "D-Dimer": ("Dímero D", r"D-Dimer\s+([\d\.,]+)[a-zA-Z/]+\s*([HL↑↓])?"),
        "hs-cTnT": ("Troponina T alta sensibilidad", r"hs-cTnT[\s\S]*?Resultado:\s*([\d\.,]+)[a-zA-Z/]+\s*([HL↑↓])?"),

        # --- BIOQUÍMICA SÉRICA ---
        "AST": ("GOT (AST)", r"AST\s+([\d\.,]+)\s*([HL↑↓])?"),
        "AMY": ("Amilasa", r"AMY\s+([\d\.,]+)\s*([HL↑↓])?"),
        "LPS": ("Lipasa", r"LPS\s+([\d\.,]+)\s*([HL↑↓])?"),
        "LDH": ("LDH", r"LDH\s+([\d\.,]+)\s*([HL↑↓])?"),
        "CK": ("Creatincinasa (CK)", r"CK\s+([\d\.,]+)\s*([HL↑↓])?"),
        "CK-MB": ("CK-MB", r"CK-MB\s+([\d\.,]+)\s*([HL↑↓])?"),
        "HBDH": ("HBDH", r"HBDH\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Crea": ("Creatinina", r"Crea\s+([\d\.,]+)\s*([HL↑↓])?"),
        "eGFRcr": ("Filtrado Glomerular (FGE)", r"eGFRcr\s+([\d\.,]+)\s*([HL↑↓])?"),
        "UA": ("Ácido Úrico", r"UA\s+([\d\.,]+)\s*([HL↑↓])?"),
        "BUN": ("Urea (Cálculo BUNx2.14)", r"BUN\s+([\d\.,]+)\s*([HL↑↓])?"), # Lee BUN pero lo llamará Urea
        "BUN/CREA": ("Relación BUN/Creatinina", r"BUN/CREA\s+([\d\.,]+)\s*([HL↑↓])?"),
        "GLU": ("Glucemia", r"GLU\s+([\d\.,]+)\s*([HL↑↓])?"),
        "tCO2": ("Bicarbonato (CO2 Total)", r"tCO2\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Ca": ("Calcio", r"Ca\s+([\d\.,]+)\s*([HL↑↓])?"),
        "PHOS": ("Fósforo", r"PHOS\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Mg": ("Magnesio", r"Mg\s+([\d\.,]+)\s*([HL↑↓])?"),
        "K+": ("Potasio", r"K\+\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Na+": ("Sodio", r"Na\+\s+([\d\.,]+)\s*([HL↑↓])?"),
        "Cl-": ("Cloro", r"Cl-\s+([\d\.,]+)\s*([HL↑↓])?"),
        "CRP": ("PCR (Proteína C Reactiva)", r"CRP\s+([\d\.,]+)\s*([HL↑↓])?")
    }

    # PROCESO DE LECTURA Y EXTRACCIÓN
    for sigla_inglesa, (nombre_espanol, patron) in patrones_de_busqueda.items():
        # Si el nombre en español es None, saltamos esta prueba y no la guardamos
        if nombre_espanol is None:
            continue

        coincidencia = re.search(patron, texto_ocr, re.IGNORECASE)
        
        if coincidencia:
            valor_crudo = coincidencia.group(1).replace(',', '.')
            
            # --- CÁLCULO MÁGICO DEL BUN A UREA ---
            if sigla_inglesa == "BUN":
                try:
                    # Intentamos convertir el texto a número decimal
                    bun_numerico = float(valor_crudo)
                    # Multiplicamos por 2.14 y redondeamos a 2 decimales
                    urea_calculada = round(bun_numerico * 2.14, 2)
                    # Convertimos de nuevo a texto para mostrarlo
                    valor_final = str(urea_calculada)
                except ValueError:
                    # Si falla (ej. si leyó letras por error), devolvemos lo que leyó
                    valor_final = valor_crudo
            else:
                valor_final = valor_crudo
            # -------------------------------------

            alerta = coincidencia.group(2) if len(coincidencia.groups()) > 1 else None
            es_alterado = True if alerta in ['H', 'L', '↑', '↓'] else False
            
            # Guardamos usando el nombre bonito en español como clave principal
            resultados_extraidos[nombre_espanol] = {
                "valor": valor_final,
                "alterado": es_alterado,
                "incluir_en_pdf": True 
            }

    return resultados_extraidos
