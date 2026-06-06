#!/usr/bin/env python3
"""
Script de polling para consultar el estado de un CDC en SIFEN.

Útil como herramienta de monitoreo o para esperar a que un documento
pase de "SOL.APROBACION" / "ENVIADO_A_SIFEN" a un estado final.

Ejemplo de uso:
    python examples/poll_cdc_status.py \
        --email tu-email@ejemplo.com \
        --password tu-password \
        --cdc 01009643435001001100000222026060612022117504 \
        --ruc 964343 \
        --interval 10 \
        --max-seconds 120
"""

import argparse
import os
import requests
import time
import json
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://apitest.facturasegura.com.py")


def get_token(email: str, password: str) -> str:
    url = f"{BASE_URL}/login?include_auth_token"
    resp = requests.post(url, json={"email": email, "password": password}, timeout=30)
    resp.raise_for_status()
    return resp.json()["response"]["user"]["authentication_token"]


def get_estado(token: str, cdc: str, dRucEm: str) -> dict:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authentication-Token": token
    }
    payload = {
        "operation": "get_estado_sifen",
        "params": {"CDC": cdc, "dRucEm": dRucEm}
    }
    resp = requests.post(
        f"{BASE_URL}/misife00/v1/esi",
        headers=headers,
        json=payload,
        timeout=15
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Polling de estado de CDC en SIFEN")
    parser.add_argument("--email", default=os.getenv("ESI_EMAIL"), help="Email del usuario ESI (o ESI_EMAIL en .env)")
    parser.add_argument("--password", default=os.getenv("ESI_PASSWORD"), help="Password del usuario ESI (o ESI_PASSWORD en .env)")
    parser.add_argument("--cdc", required=True, help="CDC a consultar")
    parser.add_argument("--ruc", default="964343", help="RUC del emisor (sin DV)")
    parser.add_argument("--interval", type=int, default=10, help="Segundos entre consultas")
    parser.add_argument("--max-seconds", type=int, default=120, help="Tiempo máximo de polling")
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error("--email y --password son requeridos (o defínelos en .env)")

    print("Obteniendo token...")
    token = get_token(args.email, args.password)
    print(f"Token obtenido: {token[:30]}...")

    print(f"\nIniciando polling del CDC {args.cdc} (cada {args.interval}s, máx {args.max_seconds}s)...\n")

    max_iterations = (args.max_seconds // args.interval) + 1
    final_states = ["Aprobado", "Aprobado con observación", "Rechazado"]

    for i in range(max_iterations):
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            data = get_estado(token, args.cdc, args.ruc)
            if data.get("code") == 0 and data.get("results"):
                res = data["results"][0]
                estado = res.get("estado_sifen", "N/A")
                desc = res.get("desc_sifen", "")
                print(f"[{ts}] {estado}")
                if desc:
                    print(f"         {desc}")

                if estado in final_states:
                    print(f"\n✅ Estado final alcanzado: {estado}")
                    break
            else:
                print(f"[{ts}] Error en respuesta: {data}")
        except requests.exceptions.RequestException as e:
            print(f"[{ts}] Error de red/HTTP: {e}")
        except Exception as e:
            print(f"[{ts}] Error: {e}")

        if i < max_iterations - 1:
            time.sleep(args.interval)

    print("\nPolling finalizado.")


if __name__ == "__main__":
    main()
