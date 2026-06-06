#!/usr/bin/env python3
"""
Ejemplo completo de integración con el API ESI de Factura Segura (SIFEN).

Flujo:
  0. CANARY PRE-FLIGHT (get_estado_sifen) → Gate de salud antes de generar.
  1. Login → Obtiene Authentication-Token.
  2. calcular_de → Envía datos resumidos, recibe DE completo con cálculos.
  3. generar_de → Envía el DE completo a SIFEN.
  4. CANARY POST (get_estado_sifen) → Verifica el estado del CDC generado.
  5. REINTENTAR / REINGRESO (opcional con --retry / --reingreso).

Uso básico:
    python examples/test_esi.py --email tu-email@ejemplo.com --password tu-password

Reingreso (mismo número de documento):
    python examples/test_esi.py --email ... --password ... --retry --reingreso

Solo consultar estado:
    python examples/test_esi.py --email ... --password ... \
        --get-estado 01009643435001001100000222026060612022117504 --dRucEm 964343
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://apitest.facturasegura.com.py")


def login(email: str, password: str) -> str:
    """Realiza login y devuelve el authentication_token."""
    url = f"{BASE_URL}/login?include_auth_token"
    payload = {"email": email, "password": password}

    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    token = data["response"]["user"]["authentication_token"]
    print(f"✅ Login exitoso. Token: {token[:30]}...")
    return token


def call_esi(token: str, operation: str, params: dict) -> dict:
    """Llama a una operación del endpoint ESI con manejo básico de errores."""
    url = f"{BASE_URL}/misife00/v1/esi"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authentication-Token": token,
    }
    payload = {"operation": operation, "params": params}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 401:
            print("❌ Error de autenticación (401). Verifica tu token o credenciales.")
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print("❌ Timeout al llamar a la API de Factura Segura.")
        raise
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con la API de Factura Segura.")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de red al llamar '{operation}': {e}")
        raise


def build_resumido_de(num_doc: str = "1000002", fe_emi: str = None) -> dict:
    """
    Construye un DE resumido para calcular_de.

    IMPORTANTE:
    - gActEco debe usar EXACTAMENTE las descripciones oficiales registradas
      para el emisor en Factura Segura (no descripciones libres).
    - dFeIniT debe coincidir con la fecha de inicio del timbrado registrado.
    - Reemplaza los datos de emisor/receptor con los de tu ambiente de pruebas.
    """
    if fe_emi is None:
        fe_emi = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "iTipEmi": "1",
        "iTiDE": "1",
        "dNumTim": "00964343",
        "dFeIniT": "2024-04-02",   # ← Fecha real de inicio de vigencia del timbrado
        "dEst": "001",
        "dPunExp": "001",
        "dNumDoc": num_doc,
        "dFeEmiDE": fe_emi,
        "iTipTra": "1",
        "iTImp": "1",
        "cMoneOpe": "PYG",
        "dCondTiCam": "1",
        "dTiCam": "1",
        "dRucEm": "964343",
        "dDVEmi": "5",
        "iTipCont": "2",
        "dNomEmi": "EMISOR DE PRUEBA",
        "dDirEmi": "DIRECCION FISCAL DE PRUEBA",
        "dNumCas": "123",
        "cDepEmi": "1",
        "dDesDepEmi": "CAPITAL",
        "cCiuEmi": "1",
        "dDesCiuEmi": "ASUNCION (DISTRITO)",
        "dTelEmi": "021123456",
        "dEmailE": "emisor.pruebas@ejemplo.com",
        "gActEco": [
            {"cActEco": "62010", "dDesActEco": "Actividades de programación informática"},
            {"cActEco": "62020", "dDesActEco": "Actividades de consultoría y gestión de servicios informáticos"},
            {"cActEco": "74909", "dDesActEco": "Otras actividades profesionales, científicas y técnicas n.c.p."}
        ],
        "iNatRec": "1",
        "iTiOpe": "1",
        "cPaisRec": "PRY",
        "iTiContRec": "1",
        "dRucRec": "80056313",
        "dDVRec": "1",
        "iTipIDRec": "0",
        "dNumIDRec": "0",
        "dNomRec": "RECEPTOR DE PRUEBA S.A.",
        "dEmailRec": "receptor.pruebas@ejemplo.com",
        "iIndPres": "1",
        "iCondOpe": "2",           # Crédito
        "iCondCred": "1",
        "dPlazoCre": "30 dias",
        "gCamItem": [
            {
                "dCodInt": "DSW001",
                "dDesProSer": "Desarrollo de software",
                "cUniMed": "77",
                "dCantProSer": "1",
                "dPUniProSer": "5500000",
                "dDescItem": "0",
                "dDescGloItem": "0",
                "dAntPreUniIt": "0",
                "dAntGloPreUniIt": "0",
                "iAfecIVA": "1",
                "dPropIVA": "100",
                "dTasaIVA": "10"
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Flujo completo ESI + canary + reingreso")
    parser.add_argument("--email", default=os.getenv("ESI_EMAIL"), help="Email del usuario ESI (o usa ESI_EMAIL en .env)")
    parser.add_argument("--password", default=os.getenv("ESI_PASSWORD"), help="Password del usuario ESI (o usa ESI_PASSWORD en .env)")
    parser.add_argument("--get-estado", metavar="CDC", help="Solo consultar estado de un CDC")
    parser.add_argument("--dRucEm", default="964343", help="RUC emisor para --get-estado")
    parser.add_argument("--num-doc", help="Número de documento a usar (7 dígitos, ej: 1000005). Sobrescribe el valor por defecto y se usa para reintentos/reingresos.")
    parser.add_argument("--retry", action="store_true", help="Ejecutar el flujo de generación (con --reingreso para mantener mismo número)")
    parser.add_argument("--reingreso", action="store_true", help="Usar el MISMO número de documento (reingreso SIFEN). Requiere --retry.")
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error("--email y --password son requeridos (o defínelos en .env como ESI_EMAIL / ESI_PASSWORD)")

    token = login(args.email, args.password)

    # Modo solo consulta de estado
    if args.get_estado:
        print("\n=== CONSULTA DE ESTADO ===")
        resp = call_esi(token, "get_estado_sifen", {"CDC": args.get_estado, "dRucEm": args.dRucEm})
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        return

    # Construir DE base (permite override vía --num-doc)
    initial_num_doc = args.num_doc or "1000002"
    de_resumido = build_resumido_de(num_doc=initial_num_doc)

    # Lógica de reintento / reingreso
    if args.retry:
        if args.reingreso:
            print(f"\n=== MODO REINGRESO: mismo número {de_resumido['dNumDoc']} ===")
        else:
            # Solo incrementar si no se especificó --num-doc explícitamente
            if not args.num_doc:
                num = int(de_resumido["dNumDoc"])
                de_resumido["dNumDoc"] = f"{num + 1:07d}"
            print(f"\n=== MODO REINTENTO: usando número {de_resumido['dNumDoc']} ===")
        de_resumido["dFeEmiDE"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # === 0. CANARY PRE-FLIGHT (gate) ===
    print("\n=== 0. CANARY PRE-FLIGHT: get_estado_sifen ===")
    CANARY_CDC = "01009643435001001000003812024070716524190789"
    CANARY_RUC = "964343"
    canary_resp = call_esi(token, "get_estado_sifen", {"CDC": CANARY_CDC, "dRucEm": CANARY_RUC})
    print(json.dumps(canary_resp, indent=2, ensure_ascii=False))

    if canary_resp.get("code") != 0:
        print("❌ Canary pre-flight falló. Abortando.")
        sys.exit(1)

    print("✅ Canary pre-flight OK. Continuando...\n")

    # 2. CALCULAR_DE
    print("=== 2. CALCULAR_DE ===")
    calc_response = call_esi(token, "calcular_de", {"DE": de_resumido})
    print(json.dumps(calc_response, indent=2, ensure_ascii=False))

    if calc_response.get("code") != 0:
        print("❌ Error en calcular_de.")
        sys.exit(1)

    # 3. GENERAR_DE
    print("\n=== 3. GENERAR_DE ===")
    full_de = calc_response["results"][0]["DE"]
    full_de.setdefault("CDC", "0")
    full_de.setdefault("dCodSeg", "0")
    full_de.setdefault("dDVId", "0")
    full_de.setdefault("dSisFact", "1")
    full_de.setdefault("dInfAdic", "Ejemplo ESI HolaMundo - Factura de prueba")

    gen_response = call_esi(token, "generar_de", {"DE": full_de})
    print(json.dumps(gen_response, indent=2, ensure_ascii=False))

    if gen_response.get("code") != 0:
        print(f"❌ generar_de falló: {gen_response.get('description')}")
        sys.exit(1)

    cdc = gen_response["results"][0]["CDC"]
    print(f"\n✅ CDC generado: {cdc}")

    # 4. CANARY POST
    print("\n=== 4. CANARY POST: get_estado_sifen ===")
    status_resp = call_esi(token, "get_estado_sifen", {"CDC": cdc, "dRucEm": de_resumido["dRucEm"]})
    print(json.dumps(status_resp, indent=2, ensure_ascii=False))

    if status_resp.get("code") == 0:
        estado = status_resp["results"][0].get("estado_sifen", "")
        print(f"\n📊 Estado: {estado}")
        if "Rechazado" in str(estado) or "ERROR" in str(estado):
            print("⚠️  Rechazado. Puedes reingresar con el mismo número usando --retry --reingreso")
        elif "Aprobado" in str(estado):
            print("✅ Documento aprobado.")
        else:
            print("⏳ En procesamiento.")

    print("\n¡Flujo completado!")


if __name__ == "__main__":
    main()
