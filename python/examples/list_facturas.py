#!/usr/bin/env python3
"""
Listar documentos electrónicos (DE) emitidos — operación complementaria al ESI.

El Manual Técnico del ESI (External System Integration) de Factura Segura no incluye
una operación de listado en `/misife00/v1/esi`. Para consultar facturas ya emitidas
se usa el endpoint MSF con la operación `lst_de`, con el mismo `Authentication-Token`
obtenido en el login.

Requisitos del usuario:
  - Login exitoso (cuenta activa).
  - Rol que permita invocar `/misife00/v1/msf` (p. ej. api_client en ambiente de pruebas).
  - Autorización sobre el Registro Único de Contribuyente (RUC) emisor consultado.

Uso básico:
    python examples/list_facturas.py

    python examples/list_facturas.py --ruc 964343 --page 1

    python examples/list_facturas.py --ruc 964343 --page 2 --json

Tipo de documento electrónico (iTiDE), valores habituales:
  1 = Factura electrónica
  4 = Autofactura
  5 = Nota de crédito electrónica
  6 = Nota de débito electrónica
  7 = Nota de remisión electrónica
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://apitest.facturasegura.com.py")

# Etiquetas didácticas de iTiDE (no exhaustivo; ver manual SIFEN / Factura Segura)
ITI_DE_LABELS = {
    "1": "Factura electrónica",
    "4": "Autofactura",
    "5": "Nota de crédito electrónica",
    "6": "Nota de débito electrónica",
    "7": "Nota de remisión electrónica",
}


def login(email: str, password: str) -> str:
    """Realiza login y devuelve el authentication_token."""
    url = f"{BASE_URL}/login?include_auth_token"
    payload = {"email": email, "password": password}

    try:
        resp = requests.post(url, json=payload, timeout=30)
    except requests.exceptions.Timeout:
        print("❌ Timeout al hacer login.")
        raise
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión con la API de Factura Segura.")
        raise

    if resp.status_code == 400:
        try:
            errors = resp.json().get("response", {}).get("errors", [])
            print(f"❌ Login rechazado: {errors or resp.text}")
        except Exception:
            print(f"❌ Login rechazado (HTTP 400): {resp.text[:300]}")
        sys.exit(1)

    if resp.status_code == 401:
        print("❌ Credenciales inválidas (401).")
        sys.exit(1)

    resp.raise_for_status()
    data = resp.json()
    token = data["response"]["user"]["authentication_token"]
    print(f"✅ Login exitoso. Token: {token[:30]}...")
    return token


def call_msf(token: str, operation: str, params: dict) -> dict:
    """Llama a una operación del endpoint MSF (`/misife00/v1/msf`)."""
    url = f"{BASE_URL}/misife00/v1/msf"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authentication-Token": token,
    }
    payload = {"operation": operation, "params": params}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 401:
            print("❌ Error de autenticación (401). Verifica token, rol o permisos MSF.")
            sys.exit(1)
        if resp.status_code == 403:
            print("❌ Acceso denegado (403). El usuario puede no tener rol para /msf.")
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


def print_table(page_result: dict) -> None:
    """Imprime un resumen tabular de la página de resultados."""
    total = page_result.get("total", 0)
    page = page_result.get("page", "?")
    page_size = page_result.get("page_size", 0)
    rows = page_result.get("list") or []

    print(f"\n📄 Total en emisor/tipo: {total}  |  página {page}  |  en esta página: {page_size}\n")
    if not rows:
        print("(sin documentos en esta página)")
        return

    header = (
        f"{'#':<4} {'NumDoc':<10} {'Est-Pto':<9} {'Fecha':<20} "
        f"{'Receptor':<28} {'Total':>12} {'Estado':<16} CDC"
    )
    print(header)
    print("-" * min(len(header) + 40, 140))

    for i, row in enumerate(rows, 1):
        num = str(row.get("dNumDoc", "") or "")
        est = f"{row.get('dEst', '')}-{row.get('dPunExp', '')}"
        fecha = str(row.get("dFeEmiDe", "") or "")[:19]
        receptor = str(row.get("dNomRec", "") or "")[:27]
        total_op = str(row.get("dtotgralope", "") or "")
        estado = str(row.get("estado_sifen", "") or "")[:15]
        cdc = str(row.get("cdc", "") or "")
        print(
            f"{i:<4} {num:<10} {est:<9} {fecha:<20} "
            f"{receptor:<28} {total_op:>12} {estado:<16} {cdc}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Listar facturas / DE emitidos vía MSF (lst_de). "
            "Complemento al flujo ESI de generación."
        )
    )
    parser.add_argument(
        "--email",
        default=os.getenv("ESI_EMAIL"),
        help="Email del usuario (o ESI_EMAIL en .env)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("ESI_PASSWORD"),
        help="Password del usuario (o ESI_PASSWORD en .env)",
    )
    parser.add_argument(
        "--ruc",
        default=os.getenv("EMISOR_RUC", "964343"),
        help="RUC del emisor sin dígito verificador (default: EMISOR_RUC o 964343)",
    )
    parser.add_argument(
        "--i-tide",
        default="1",
        dest="i_tide",
        help="Tipo de DE (iTiDE). Default 1 = factura electrónica",
    )
    parser.add_argument(
        "--page",
        default="1",
        help="Número de página (entero positivo, default 1). Tamaño de página lo define el servidor.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Imprimir la respuesta JSON completa (además del resumen si hay resultados)",
    )
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error(
            "--email y --password son requeridos (o defínelos en .env como ESI_EMAIL / ESI_PASSWORD)"
        )

    if not str(args.page).isdigit() or int(args.page) <= 0:
        parser.error("--page debe ser un entero positivo")

    tipo_label = ITI_DE_LABELS.get(str(args.i_tide), f"iTiDE={args.i_tide}")
    print("=== LISTAR DE EMITIDOS (MSF lst_de) ===")
    print(f"BASE_URL : {BASE_URL}")
    print(f"Emisor   : RUC {args.ruc}")
    print(f"Tipo DE  : {args.i_tide} ({tipo_label})")
    print(f"Página   : {args.page}")
    print()
    print(
        "Nota: esta operación NO vive en /misife00/v1/esi; usa /misife00/v1/msf "
        "con el mismo Authentication-Token del login."
    )
    print()

    token = login(args.email, args.password)

    params = {
        "dRucEm": str(args.ruc),
        "iTiDE": str(args.i_tide),
        "page": str(args.page),
    }
    print("\n=== MSF: lst_de ===")
    print(f"params: {json.dumps(params, ensure_ascii=False)}")

    resp = call_msf(token, "lst_de", params)

    if args.json:
        print(json.dumps(resp, indent=2, ensure_ascii=False))

    code = resp.get("code")
    desc = resp.get("description", "")
    op_id = (resp.get("operation_info") or {}).get("id", "")
    print(f"\ncode={code}  description={desc}  operation_info.id={op_id}")

    if code != 0:
        print("❌ lst_de no devolvió code=0. Revisa permisos, RUC o parámetros.")
        if not args.json:
            print(json.dumps(resp, indent=2, ensure_ascii=False))
        sys.exit(1)

    results = resp.get("results") or []
    if not results:
        print("⚠️  results vacío.")
        sys.exit(0)

    page_result = results[0]
    print_table(page_result)

    total = int(page_result.get("total") or 0)
    page = int(page_result.get("page") or 1)
    page_size = int(page_result.get("page_size") or 0)
    if total > 0 and page_size > 0 and page * page_size < total:
        next_page = page + 1
        print(
            f"\n💡 Hay más resultados. Siguiente página: "
            f"python examples/list_facturas.py --ruc {args.ruc} --i-tide {args.i_tide} --page {next_page}"
        )

    print("\nListado completado.")


if __name__ == "__main__":
    main()
