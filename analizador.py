import re

def analizar_ticket_ocr(texto_ocr):
    resultados_extraidos = {}

    # DICCIONARIO V5: Ordenado, con NT-proBNP, Iones arreglados y sin HBDH
    patrones_de_busqueda = {
        # ==========================================
        # 1. HEMOGRAMA
        # ==========================================
        "WBC": ("Leucocitos", r"WBC[^\d\n]*([\d\.,]+)", "4.00 - 10.00", 1, "Hematología", "x10³/µL"),
        "RBC": ("Hematíes", r"RBC[^\d\n]*([\d\.,]+)", "4.00 - 5.50", 2, "Hematología", "x10⁶/µL"),
        "HGB": ("Hemoglobina", r"HGB[^\d\n]*([\d\.,]+)", "12.0 - 16.0", 3, "Hematología", "g/dL"),
        "HCT": ("Hematocrito", r"HCT[^\d\n]*([\d\.,]+)", "36.0 - 48.0", 4, "Hematología", "%"),
        "MCV": ("VCM", r"MCV[^\d\n]*([\d\.,]+)", "80.0 - 99.0", 5, "Hematología", "fL"),
        "MCH": ("HCM", r"MCH[^\d\n]*([\d\.,]+)", "26.0 - 32.0", 6, "Hematología", "pg"),
        "MCHC": ("CHCM", r"MCHC[^\d\n]*([\d\.,]+)", "32.0 - 36.0", 7, "Hematología", "g/dL"),
        "PLT": ("Plaquetas", r"PLT[^\d\n]*([\d\.,]+)", "100 - 300", 8, "Hematología", "x10³/µL"),
        "LYM%": ("Linfocitos (%)", r"LYM%[^\d\n]*([\d\.,]+)", "20.0 - 40.0", 9, "Hematología", "%"),
        "MXD%": ("Monocitos (%)", r"MXD%[^\d\n]*([\d\.,]+)", "1.0 - 15.0", 10, "Hematología", "%"),
        "NEUT%": ("Neutrófilos (%)", r"NEUT%[^\d\n]*([\d\.,]+)", "50.0 - 70.0", 11, "Hematología", "%"),
        "RDW-SD": ("RDW", r"RDW-SD[^\d\n]*([\d\.,]+)", "35.0 - 56.0", 15, "Hematología", "fL"),
        "MPV": ("VPM", r"MPV[^\d\n]*([\d\.,]+)", "7.0 - 11.0", 18, "Hematología", "fL"),

        # ==========================================
        # 2. BIOQUÍMICA SÉRICA Y MARCADORES
        # ==========================================
        "GLU": ("Glucemia", r"GLU[^\d\n]*([\d\.,]+)", "70.1 - 110.1", 30, "Bioquímica Sérica", "mg/dL"),
        "BUN": ("Urea", r"BUN[^\d\n]*([\d\.,]+)", "15.0 - 40.0", 31, "Bioquímica Sérica", "mg/dL"), 
        "Crea": ("Creatinina", r"Crea[^\d\n]*([\d\.,]+)", "0.5 - 1.2", 32, "Bioquímica Sérica", "mg/dL"),
        "eGFRcr": ("Filtrado Glomerular (FGE)", r"eGFRcr[^\d\n]*([\d\.,]+)", "> 60", 33, "Bioquímica Sérica", "mL/min"),
        "UA": ("Ácido Úrico", r"UA[^\d\n]*([\d\.,]+)", "3.0 - 7.0", 35, "Bioquímica Sérica", "mg/dL"),
        "AST": ("GOT (AST)", r"AST[^\d\n]*([\d\.,]+)", "20 - 110", 36, "Bioquímica Sérica", "U/L"),
        "LDH": ("LDH", r"LDH[^\d\n]*([\d\.,]+)", "109 - 245", 37, "Bioquímica Sérica", "U/L"),
        
        # Marcadores Cardíacos y Dímero D (Agrupados)
        "CK": ("Creatincinasa (CK)", r"CK[^\d\n]*([\d\.,]+)", "20 - 200", 38, "Bioquímica Sérica", "U/L"),
        "CK-MB": ("CK-MB", r"CK-MB[^\d\n]*([\d\.,]+)", "0 - 25", 39, "Bioquímica Sérica", "U/L"),
        "hs-cTnT": ("Troponina T (hs-cTnT)", r"hs-cTnT[\s\S]*?Resultado:\s*([\d\.,]+)", "< 0.014", 40, "Bioquímica Sérica", "ng/mL"),
        "NT-proBNP": ("NT-proBNP", r"NT-proBNP[\s\S]*?Resultado:\s*([\d\.,]+)", "< 125", 41, "Bioquímica Sérica", "pg/mL"),
        "D-Dimer": ("Dímero D", r"D-Dimer[^\d\n]*([\d\.,]+)", "0.0 - 0.5", 42, "Bioquímica Sérica", "mg/L"),

        "AMY": ("Amilasa", r"AMY[^\d\n]*([\d\.,]+)", "1 - 60", 43, "Bioquímica Sérica", "U/L"),
        "LPS": ("Lipasa", r"LPS[^\d\n]*([\d\.,]+)", "1 - 60", 44, "Bioquímica Sérica", "U/L"),
        "CRP": ("PCR (Proteína C Reactiva)", r"CRP[^\d\n]*([\d\.,]+)", "0.0 - 1.0", 45, "Bioquímica Sérica", "mg/dL"),

        # Iones con Regex mejorado para detectar los signos + y -
        "Na+": ("Sodio", r"Na\+?[^\d\n]*([\d\.,]+)", "135 - 147", 46, "Bioquímica Sérica", "mmol/L"),
        "K+": ("Potasio", r"K\+?[^\d\n]*([\d\.,]+)", "3.4 - 5.3", 47, "Bioquímica Sérica", "mmol/L"),
        "Cl-": ("Cloro", r"Cl-?[^\d\n]*([\d\.,]+)", "99 - 112", 48, "Bioquímica Sérica", "mmol/L"),
        "Ca": ("Calcio", r"Ca[^\d\n]*([\d\.,]+)", "8.0 - 10.3", 49, "Bioquímica Sérica", "mg/dL"),
        "PHOS": ("Fósforo", r"PHOS[^\d\n]*([\d\.,]+)", "2.8 - 4.7", 50, "Bioquímica Sérica", "mg/dL"),
        "Mg": ("Magnesio", r"Mg[^\d\n]*([\d\.,]+)", "0.65 - 1.25", 51, "Bioquímica Sérica", "mmol/L"),

        # ==========================================
        # 3. COAGULACIÓN
        # ==========================================
        "INR": ("INR", r"INR[^\d\n]*([\d\.,]+)", "0.8 - 1.2", 60, "Coagulación", ""),
        "APTT": ("TTPA", r"APTT[^\d\n]*(Curva|[\d\.,]+)", "25.2 - 38.4", 61, "Coagulación", "s"),
        "PT": ("Tiempo de Protrombina", r"PT[^\d\n]*([\d\.,]+)", "9.4 - 14.0", 62, "Coagulación", "s"),
        "TT": ("Tiempo de Trombina", r"TT[^\d\n]*([\d\.,]+)", "13.3 - 21.0", 63, "Coagulación", "s"),
        "Fib": ("Fibrinógeno", r"Fib[^\d\n]*([\d\.,]+)", "180 - 370", 64, "Coagulación", "mg/dL")
    }

    for sigla_inglesa, (nombre_espanol, patron, rango_ref, orden, categoria, unidad) in patrones_de_busqueda.items():
        if nombre_espanol is None:
            continue

        coincidencia = re.search(patron, texto_ocr, re.IGNORECASE)
        
        if coincidencia:
            valor_crudo = coincidencia.group(1).replace(',', '.')
            
            if sigla_inglesa == "BUN":
                try:
                    bun_numerico = float(valor_crudo)
                    urea_calculada = round(bun_numerico * 2.14, 2)
                    valor_final = str(urea_calculada)
                except ValueError:
                    valor_final = valor_crudo
            else:
                valor_final = valor_crudo

            es_alterado = False
            texto_siguiente = texto_ocr[coincidencia.end():coincidencia.end()+6].upper()
            if re.match(r'\s+[HL↑↓](?:\s|$)', texto_siguiente):
                es_alterado = True
            
            resultados_extraidos[nombre_espanol] = {
                "valor": valor_final,
                "alterado": es_alterado,
                "rango": rango_ref,
                "orden": orden,
                "categoria": categoria,
                "unidad": unidad
            }

    return resultados_extraidos
