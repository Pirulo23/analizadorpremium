import re

def analizar_ticket_ocr(texto_ocr):
    resultados_extraidos = {}

    # DICCIONARIO MÁGICO V3 (Con Rangos de Referencia y Orden Estricto)
    # Formato: "Nombre en Ticket": ("Nombre en Español", "Patrón Regex", "Rango Ref", Orden_Impresion)
    patrones_de_busqueda = {
        # --- HEMOGRAMA (Orden 1 al 19) ---
        "WBC": ("Leucocitos", r"WBC[^\d\n]*([\d\.,]+)", "4.00 - 10.00", 1),
        "RBC": ("Hematíes", r"RBC[^\d\n]*([\d\.,]+)", "4.00 - 5.50", 2),
        "HGB": ("Hemoglobina", r"HGB[^\d\n]*([\d\.,]+)", "12.0 - 16.0", 3),
        "HCT": ("Hematocrito", r"HCT[^\d\n]*([\d\.,]+)", "36.0 - 48.0", 4),
        "MCV": ("VCM (Volumen Corpuscular Medio)", r"MCV[^\d\n]*([\d\.,]+)", "80.0 - 99.0", 5),
        "MCH": ("HCM (Hemoglobina Corpuscular Media)", r"MCH[^\d\n]*([\d\.,]+)", "26.0 - 32.0", 6),
        "MCHC": ("CHCM", r"MCHC[^\d\n]*([\d\.,]+)", "32.0 - 36.0", 7),
        "PLT": ("Plaquetas", r"PLT[^\d\n]*([\d\.,]+)", "100 - 300", 8),
        "LYM%": ("Linfocitos (%)", r"LYM%[^\d\n]*([\d\.,]+)", "20.0 - 40.0", 9),
        "MXD%": ("Monocitos (%)", r"MXD%[^\d\n]*([\d\.,]+)", "1.0 - 15.0", 10),
        "NEUT%": ("Neutrófilos (%)", r"NEUT%[^\d\n]*([\d\.,]+)", "50.0 - 70.0", 11),
        "LYM#": (None, r"LYM#[^\d\n]*([\d\.,]+)", "", 12),
        "MXD#": (None, r"MXD#[^\d\n]*([\d\.,]+)", "", 13),
        "NEUT#": (None, r"NEUT#[^\d\n]*([\d\.,]+)", "", 14),
        "RDW-SD": ("RDW (Amplitud Dist. Eritrocitaria)", r"RDW-SD[^\d\n]*([\d\.,]+)", "35.0 - 56.0", 15),
        "RDW-CV": (None, r"RDW-CV[^\d\n]*([\d\.,]+)", "", 16),
        "PDW": (None, r"PDW[^\d\n]*([\d\.,]+)", "", 17),
        "MPV": ("VPM (Volumen Plaquetario Medio)", r"MPV[^\d\n]*([\d\.,]+)", "7.0 - 11.0", 18),
        "P-LCR": (None, r"P-LCR[^\d\n]*([\d\.,]+)", "", 19),

        # --- COAGULACIÓN Y MARCADORES (Orden 20 al 29) ---
        "INR": ("INR", r"INR[^\d\n]*([\d\.,]+)", "0.8 - 1.2", 20),
        "APTT": ("TTPA", r"APTT[^\d\n]*(Curva|[\d\.,]+)", "25.2 - 38.4", 21),
        "PT": ("Tiempo de Protrombina", r"PT[^\d\n]*([\d\.,]+)", "9.4 - 14.0", 22),
        "TT": ("Tiempo de Trombina", r"TT[^\d\n]*([\d\.,]+)", "13.3 - 21.0", 23),
        "Fib": ("Fibrinógeno", r"Fib[^\d\n]*([\d\.,]+)", "180 - 370", 24),
        "D-Dimer": ("Dímero D", r"D-Dimer[^\d\n]*([\d\.,]+)", "0.0 - 0.5", 25),
        "hs-cTnT": ("Troponina T alta sensibilidad", r"hs-cTnT[\s\S]*?Resultado:\s*([\d\.,]+)", "< 0.014", 26),

        # --- BIOQUÍMICA SÉRICA (Orden 30 en adelante) ---
        "AST": ("GOT (AST)", r"AST[^\d\n]*([\d\.,]+)", "20 - 110", 30),
        "AMY": ("Amilasa", r"AMY[^\d\n]*([\d\.,]+)", "1 - 60", 31),
        "LPS": ("Lipasa", r"LPS[^\d\n]*([\d\.,]+)", "1 - 60", 32),
        "LDH": ("LDH", r"LDH[^\d\n]*([\d\.,]+)", "109 - 245", 33),
        "CK": ("Creatincinasa (CK)", r"CK[^\d\n]*([\d\.,]+)", "20 - 200", 34),
        "CK-MB": ("CK-MB", r"CK-MB[^\d\n]*([\d\.,]+)", "0 - 25", 35),
        "HBDH": ("HBDH", r"HBDH[^\d\n]*([\d\.,]+)", "72 - 182", 36),
        "Crea": ("Creatinina", r"Crea[^\d\n]*([\d\.,]+)", "0.5 - 1.2", 37),
        "eGFRcr": ("Filtrado Glomerular (FGE)", r"eGFRcr[^\d\n]*([\d\.,]+)", "> 60", 38),
        "UA": ("Ácido Úrico", r"UA[^\d\n]*([\d\.,]+)", "3.0 - 7.0", 39),
        "BUN": ("Urea", r"BUN[^\d\n]*([\d\.,]+)", "15.0 - 40.0", 40), 
        "BUN/CREA": ("Relación BUN/Creatinina", r"BUN/CREA[^\d\n]*([\d\.,]+)", "24 - 155", 41),
        "GLU": ("Glucemia", r"GLU[^\d\n]*([\d\.,]+)", "70.1 - 110.1", 42),
        "tCO2": ("Bicarbonato (CO2 Total)", r"tCO2[^\d\n]*([\d\.,]+)", "22.0 - 29.0", 43),
        "Ca": ("Calcio", r"Ca[^\d\n]*([\d\.,]+)", "8.0 - 10.3", 44),
        "PHOS": ("Fósforo", r"PHOS[^\d\n]*([\d\.,]+)", "2.8 - 4.7", 45),
        "Mg": ("Magnesio", r"Mg[^\d\n]*([\d\.,]+)", "0.65 - 1.25", 46),
        "K+": ("Potasio", r"K\+[^\d\n]*([\d\.,]+)", "3.4 - 5.3", 47),
        "Na+": ("Sodio", r"Na\+[^\d\n]*([\d\.,]+)", "135 - 147", 48),
        "Cl-": ("Cloro", r"Cl-[^\d\n]*([\d\.,]+)", "99 - 112", 49),
        "CRP": ("PCR (Proteína C Reactiva)", r"CRP[^\d\n]*([\d\.,]+)", "0.0 - 1.0", 50)
    }

    # PROCESO DE LECTURA Y EXTRACCIÓN
    for sigla_inglesa, (nombre_espanol, patron, rango_ref, orden) in patrones_de_busqueda.items():
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
            
            # Guardamos la prueba con su orden y su rango
            resultados_extraidos[nombre_espanol] = {
                "valor": valor_final,
                "alterado": es_alterado,
                "rango": rango_ref,
                "orden": orden,
                "incluir_en_pdf": True 
            }

    return resultados_extraidos
