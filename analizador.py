import re

def auto_corregir_decimales(valor_crudo, sigla):
    """
    Inteligencia artificial básica para corregir los fallos típicos del OCR 
    (puntos decimales omitidos) basándose en rangos biológicos lógicos.
    """
    v = valor_crudo.replace(',', '.')
    
    # Si es un texto como "< 0.014" o "Curva", lo dejamos tal cual
    if '<' in v or '>' in v or 'Curva' in v:
        return v
        
    try:
        num = float(v)
        # Correcciones específicas por parámetro
        if sigla == "GLU" and num > 1000:
            return str(round(num / 100, 2))  # Ej: 12144 -> 121.44
        elif sigla == "Na+" and num > 500:
            return str(round(num / 10, 1))   # Ej: 1382 -> 138.2
        elif sigla == "K+" and num > 20:
            return str(round(num / 10, 1))   # Ej: 45 -> 4.5
        elif sigla == "Cl-" and num > 500:
            return str(round(num / 10, 1))   # Ej: 1010 -> 101.0
        elif ("MCH" in sigla or "MCV" in sigla) and num > 500:
            return None # Agarró un número de serie de la máquina, lo descartamos
    except ValueError:
        pass
        
    return v

def analizar_ticket_ocr(texto_ocr):
    resultados_extraidos = {}

    # DICCIONARIO DEFINITIVO V6: OCR a prueba de balas y Auto-Corrector
    patrones_de_busqueda = {
        # HEMOGRAMA
        "WBC": ("Leucocitos", r"WBC[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "4.00 - 10.00", 1, "Hematología", "x10³/µL"),
        "RBC": ("Hematíes", r"RBC[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "4.00 - 5.50", 2, "Hematología", "x10⁶/µL"),
        "HGB": ("Hemoglobina", r"HGB[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "12.0 - 16.0", 3, "Hematología", "g/dL"),
        "HCT": ("Hematocrito", r"HCT[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "36.0 - 48.0", 4, "Hematología", "%"),
        "MCV": ("VCM", r"MCV[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "80.0 - 99.0", 5, "Hematología", "fL"),
        "MCH": ("HCM", r"MCH[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "26.0 - 32.0", 6, "Hematología", "pg"),
        "MCHC": ("CHCM", r"MCHC[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "32.0 - 36.0", 7, "Hematología", "g/dL"),
        "PLT": ("Plaquetas", r"PLT[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "100 - 300", 8, "Hematología", "x10³/µL"),
        "LYM%": ("Linfocitos (%)", r"LYM%[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "20.0 - 40.0", 9, "Hematología", "%"),
        "MXD%": ("Monocitos (%)", r"MXD%[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "1.0 - 15.0", 10, "Hematología", "%"),
        "NEUT%": ("Neutrófilos (%)", r"NEUT%[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "50.0 - 70.0", 11, "Hematología", "%"),
        "RDW-SD": ("RDW", r"RDW-SD[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "35.0 - 56.0", 15, "Hematología", "fL"),
        "MPV": ("VPM", r"MPV[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "7.0 - 11.0", 18, "Hematología", "fL"),

        # BIOQUÍMICA SÉRICA
        "GLU": ("Glucemia", r"GLU[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "70.1 - 110.1", 30, "Bioquímica Sérica", "mg/dL"),
        "BUN": ("Urea", r"BUN[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "15.0 - 40.0", 31, "Bioquímica Sérica", "mg/dL"), 
        "Crea": ("Creatinina", r"Crea[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0.5 - 1.2", 32, "Bioquímica Sérica", "mg/dL"),
        "eGFRcr": ("Filtrado Glomerular (FGE)", r"eGFRcr[^\d\w]{0,8}([>0-9]+[\.,]?[0-9]*)", "> 60", 33, "Bioquímica Sérica", "mL/min"),
        "UA": ("Ácido Úrico", r"UA[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "3.0 - 7.0", 35, "Bioquímica Sérica", "mg/dL"),
        "AST": ("GOT (AST)", r"AST[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "20 - 110", 36, "Bioquímica Sérica", "U/L"),
        "LDH": ("LDH", r"LDH[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "109 - 245", 37, "Bioquímica Sérica", "U/L"),
        
        "CK": ("Creatincinasa (CK)", r"CK[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "20 - 200", 38, "Bioquímica Sérica", "U/L"),
        "CK-MB": ("CK-MB", r"CK-MB[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0 - 25", 39, "Bioquímica Sérica", "U/L"),
        
        # Marcadores Especiales (Permiten salto de línea en el ticket)
        "hs-cTnT": ("Troponina T (hs-cTnT)", r"hs-cTnT[\s\S]{0,60}?([<>\d]+[\.,]?[0-9]*)", "< 0.014", 40, "Bioquímica Sérica", "ng/mL"),
        "NT-proBNP": ("NT-proBNP", r"NT-proBNP[\s\S]{0,60}?([<>\d]+[\.,]?[0-9]*)", "< 125", 41, "Bioquímica Sérica", "pg/mL"),
        "D-Dimer": ("Dímero D", r"D-Dimer[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0.0 - 0.5", 42, "Bioquímica Sérica", "mg/L"),

        "AMY": ("Amilasa", r"AMY[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "1 - 60", 43, "Bioquímica Sérica", "U/L"),
        "LPS": ("Lipasa", r"LPS[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "1 - 60", 44, "Bioquímica Sérica", "U/L"),
        "CRP": ("PCR (Proteína C Reactiva)", r"CRP[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0.0 - 1.0", 45, "Bioquímica Sérica", "mg/dL"),

        # Iones (Regex especial para tolerar el signo + y - dañado por el OCR)
        "Na+": ("Sodio", r"Na[+*\.'-]?[^\d\w]{0,5}([0-9]+[\.,]?[0-9]*)", "135 - 147", 46, "Bioquímica Sérica", "mmol/L"),
        "K+": ("Potasio", r"K[+*\.'-]?[^\d\w]{0,5}([0-9]+[\.,]?[0-9]*)", "3.4 - 5.3", 47, "Bioquímica Sérica", "mmol/L"),
        "Cl-": ("Cloro", r"Cl[-*\.']?[^\d\w]{0,5}([0-9]+[\.,]?[0-9]*)", "99 - 112", 48, "Bioquímica Sérica", "mmol/L"),
        "Ca": ("Calcio", r"Ca[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "8.0 - 10.3", 49, "Bioquímica Sérica", "mg/dL"),
        "PHOS": ("Fósforo", r"PHOS[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "2.8 - 4.7", 50, "Bioquímica Sérica", "mg/dL"),
        "Mg": ("Magnesio", r"Mg[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0.65 - 1.25", 51, "Bioquímica Sérica", "mmol/L"),

        # COAGULACIÓN
        "INR": ("INR", r"INR[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "0.8 - 1.2", 60, "Coagulación", ""),
        "APTT": ("TTPA", r"APTT[^\d\w]{0,8}(Curva|[0-9]+[\.,]?[0-9]*)", "25.2 - 38.4", 61, "Coagulación", "s"),
        "PT": ("Tiempo de Protrombina", r"PT[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "9.4 - 14.0", 62, "Coagulación", "s"),
        "TT": ("Tiempo de Trombina", r"TT[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "13.3 - 21.0", 63, "Coagulación", "s"),
        "Fib": ("Fibrinógeno", r"Fib[^\d\w]{0,8}([0-9]+[\.,]?[0-9]*)", "180 - 370", 64, "Coagulación", "mg/dL")
    }

    for sigla_inglesa, (nombre_espanol, patron, rango_ref, orden, categoria, unidad) in patrones_de_busqueda.items():
        if nombre_espanol is None:
            continue

        coincidencia = re.search(patron, texto_ocr, re.IGNORECASE)
        
        if coincidencia:
            valor_crudo = coincidencia.group(1)
            valor_corregido = auto_corregir_decimales(valor_crudo, sigla_inglesa)
            
            # Si el auto-corrector detectó que era un número de serie falso, lo saltamos
            if valor_corregido is None:
                continue
                
            # Cálculo del BUN a Urea
            if sigla_inglesa == "BUN":
                try:
                    bun_numerico = float(valor_corregido)
                    valor_final = str(round(bun_numerico * 2.14, 2))
                except ValueError:
                    valor_final = valor_corregido
            else:
                valor_final = valor_corregido

            # Enviamos también si la máquina detectó H o L para mayor seguridad
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
