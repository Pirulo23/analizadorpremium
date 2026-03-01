import re

def analizar_ticket_ocr(texto_ocr):
    resultados_extraidos = {}

    # DICCIONARIO MÁGICO V4 (Con Orden Clínico, Categorías y Unidades)
    # Formato: "Sigla": ("Nombre ES", "Regex", "Rango", Orden, "Categoría", "Unidad")
    patrones_de_busqueda = {
        # ==========================================
        # HEMOGRAMA (Orden 1 al 19)
        # ==========================================
        "WBC": ("Leucocitos", r"WBC[^\d\n]*([\d\.,]+)", "4.00 - 10.00", 1, "Hematología", "x10³/µL"),
        "RBC": ("Hematíes", r"RBC[^\d\n]*([\d\.,]+)", "4.00 - 5.50", 2, "Hematología", "x10⁶/µL"),
        "HGB": ("Hemoglobina", r"HGB[^\d\n]*([\d\.,]+)", "12.0 - 16.0", 3, "Hematología", "g/dL"),
        "HCT": ("Hematocrito", r"HCT[^\d\n]*([\d\.,]+)", "36.0 - 48.0", 4, "Hematología", "%"),
        "MCV": ("VCM (Volumen Corpuscular Medio)", r"MCV[^\d\n]*([\d\.,]+)", "80.0 - 99.0", 5, "Hematología", "fL"),
        "MCH": ("HCM (Hemoglobina Corpuscular Media)", r"MCH[^\d\n]*([\d\.,]+)", "26.0 - 32.0", 6, "Hematología", "pg"),
        "MCHC": ("CHCM", r"MCHC[^\d\n]*([\d\.,]+)", "32.0 - 36.0", 7, "Hematología", "g/dL"),
        "PLT": ("Plaquetas", r"PLT[^\d\n]*([\d\.,]+)", "100 - 300", 8, "Hematología", "x10³/µL"),
        "LYM%": ("Linfocitos (%)", r"LYM%[^\d\n]*([\d\.,]+)", "20.0 - 40.0", 9, "Hematología", "%"),
        "MXD%": ("Monocitos (%)", r"MXD%[^\d\n]*([\d\.,]+)", "1.0 - 15.0", 10, "Hematología", "%"),
        "NEUT%": ("Neutrófilos (%)", r"NEUT%[^\d\n]*([\d\.,]+)", "50.0 - 70.0", 11, "Hematología", "%"),
        "LYM#": (None, r"LYM#[^\d\n]*([\d\.,]+)", "", 12, "Hematología", ""),
        "MXD#": (None, r"MXD#[^\d\n]*([\d\.,]+)", "", 13, "Hematología", ""),
        "NEUT#": (None, r"NEUT#[^\d\n]*([\d\.,]+)", "", 14, "Hematología", ""),
        "RDW-SD": ("RDW (Amplitud Dist. Eritrocitaria)", r"RDW-SD[^\d\n]*([\d\.,]+)", "35.0 - 56.0", 15, "Hematología", "fL"),
        "RDW-CV": (None, r"RDW-CV[^\d\n]*([\d\.,]+)", "", 16, "Hematología", "%"),
        "PDW": (None, r"PDW[^\d\n]*([\d\.,]+)", "", 17, "Hematología", "fL"),
        "MPV": ("VPM (Volumen Plaquetario Medio)", r"MPV[^\d\n]*([\d\.,]+)", "7.0 - 11.0", 18, "Hematología", "fL"),
        "P-LCR": (None, r"P-LCR[^\d\n]*([\d\.,]+)", "", 19, "Hematología", "%"),

        # ==========================================
        # COAGULACIÓN (Orden 20 al 29)
        # ==========================================
        "INR": ("INR", r"INR[^\d\n]*([\d\.,]+)", "0.8 - 1.2", 20, "Coagulación", ""),
        "APTT": ("TTPA", r"APTT[^\d\n]*(Curva|[\d\.,]+)", "25.2 - 38.4", 21, "Coagulación", "s"),
        "PT": ("Tiempo de Protrombina", r"PT[^\d\n]*([\d\.,]+)", "9.4 - 14.0", 22, "Coagulación", "s"),
        "TT": ("Tiempo de Trombina", r"TT[^\d\n]*([\d\.,]+)", "13.3 - 21.0", 23, "Coagulación", "s"),
        "Fib": ("Fibrinógeno", r"Fib[^\d\n]*([\d\.,]+)", "180 - 370", 24, "Coagulación", "mg/dL"),
        "D-Dimer": ("Dímero D", r"D-Dimer[^\d\n]*([\d\.,]+)", "0.0 - 0.5", 25, "Coagulación", "mg/L"),

        # ==========================================
        # BIOQUÍMICA SÉRICA (Orden Clínico Lógico: 30+)
        # ==========================================
        
        # 1. Glucosa
        "GLU": ("Glucemia", r"GLU[^\d\n]*([\d\.,]+)", "70.1 - 110.1", 30, "Bioquímica Sérica", "mg/dL"),
        
        # 2. Perfil Renal
        "BUN": ("Urea", r"BUN[^\d\n]*([\d\.,]+)", "15.0 - 40.0", 31, "Bioquímica Sérica", "mg/dL"), 
        "Crea": ("Creatinina", r"Crea[^\d\n]*([\d\.,]+)", "0.5 - 1.2", 32, "Bioquímica Sérica", "mg/dL"),
        "eGFRcr": ("Filtrado Glomerular (FGE)", r"eGFRcr[^\d\n]*([\d\.,]+)", "> 60", 33, "Bioquímica Sérica", "mL/min"),
        "BUN/CREA": ("Relación BUN/Creatinina", r"BUN/CREA[^\d\n]*([\d\.,]+)", "24 - 155", 34, "Bioquímica Sérica", ""),
        "UA": ("Ácido Úrico", r"UA[^\d\n]*([\d\.,]+)", "3.0 - 7.0", 35, "Bioquímica Sérica", "mg/dL"),
        
        # 3. Perfil Hepático / Tisular
        "AST": ("GOT (AST)", r"AST[^\d\n]*([\d\.,]+)", "20 - 110", 36, "Bioquímica Sérica", "U/L"),
        "LDH": ("LDH", r"LDH[^\d\n]*([\d\.,]+)", "109 - 245", 37, "Bioquímica Sérica", "U/L"),
        
        # 4. Marcadores Cardíacos y Musculares (AGRUPADOS COMO PEDISTE)
        "CK": ("Creatincinasa (CK)", r"CK[^\d\n]*([\d\.,]+)", "20 - 200", 38, "Bioquímica Sérica", "U/L"),
        "CK-MB": ("CK-MB", r"CK-MB[^\d\n]*([\d\.,]+)", "0 - 25", 39, "Bioquímica Sérica", "U/L"),
        "hs-cTnT": ("Troponina T alta sensibilidad", r"hs-cTnT[\s\S]*?Resultado:\s*([\d\.,]+)", "< 0.014", 40, "Bioquímica Sérica", "ng/mL"),
        "HBDH": ("HBDH", r"HBDH[^\d\n]*([\d\.,]+)", "72 - 182", 41, "Bioquímica Sérica", "U/L"),

        # 5. Enzimas Pancreáticas
        "AMY": ("Amilasa", r"AMY[^\d\n]*([\d\.,]+)", "1 - 60", 42, "Bioquímica Sérica", "U/L"),
        "LPS": ("Lipasa", r"LPS[^\d\n]*([\d\.,]+)", "1 - 60", 43, "Bioquímica Sérica", "U/L"),
        
        # 6. Reactantes de fase aguda
        "CRP": ("PCR (Proteína C Reactiva)", r"CRP[^\d\n]*([\d\.,]+)", "0.0 - 1.0", 44, "Bioquímica Sérica", "mg/dL"),

        # 7. Iones y Minerales
        "Na+": ("Sodio", r"Na\+[^\d\n]*([\d\.,]+)", "135 - 147", 45, "Bioquímica Sérica", "mmol/L"),
        "K+": ("Potasio", r"K\+[^\d\n]*([\d\.,]+)", "3.4 - 5.3", 46, "Bioquímica Sérica", "mmol/L"),
        "Cl-": ("Cloro", r"Cl-[^\d\n]*([\d\.,]+)", "99 - 112", 47, "Bioquímica Sérica", "mmol/L"),
        "Ca": ("Calcio", r"Ca[^\d\n]*([\d\.,]+)", "8.0 - 10.3", 48, "Bioquímica Sérica", "mg/dL"),
        "PHOS": ("Fósforo", r"PHOS[^\d\n]*([\d\.,]+)", "2.8 - 4.7", 49, "Bioquímica Sérica", "mg/dL"),
        "Mg": ("Magnesio", r"Mg[^\d\n]*([\d\.,]+)", "0.65 - 1.25", 50, "Bioquímica Sérica", "mmol/L"),
        "tCO2": ("Bicarbonato (CO2 Total)", r"tCO2[^\d\n]*([\d\.,]+)", "22.0 - 29.0", 51, "Bioquímica Sérica", "mmol/L")
    }

    # PROCESO DE LECTURA Y EXTRACCIÓN
    for sigla_inglesa, (nombre_espanol, patron, rango_ref, orden, categoria, unidad) in patrones_de_busqueda.items():
        if nombre_espanol is None:
            continue

        coincidencia = re.search(patron, texto_ocr, re.IGNORECASE)
        
        if coincidencia:
            valor_crudo = coincidencia.group(1).replace(',', '.')
            
            # --- CÁLCULO MÁGICO DEL BUN A UREA ---
            if sigla_inglesa == "BUN":
                try:
                    bun_numerico = float(valor_crudo)
                    urea_calculada = round(bun_numerico * 2.14, 2)
                    valor_final = str(urea_calculada)
                except ValueError:
                    valor_final = valor_crudo
            else:
                valor_final = valor_crudo
            # -------------------------------------

            # Buscamos de forma segura si hay una H o L justo después del número
            es_alterado = False
            texto_siguiente = texto_ocr[coincidencia.end():coincidencia.end()+6].upper()
            if re.match(r'\s+[HL↑↓](?:\s|$)', texto_siguiente):
                es_alterado = True
            
            # Guardamos la prueba con su categoría y sus unidades para que la web lo pinte perfecto
            resultados_extraidos[nombre_espanol] = {
                "valor": valor_final,
                "alterado": es_alterado,
                "rango": rango_ref,
                "orden": orden,
                "categoria": categoria,
                "unidad": unidad,
                "incluir_en_pdf": True 
            }

    return resultados_extraidos
