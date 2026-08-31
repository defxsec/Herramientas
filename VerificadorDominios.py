#!/usr/bin/env python3

import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "dominios.txt" #Lista de dominos
OUTPUT_FILE = "disponibles.txt" #Lista de dominios emcontrador

TIMEOUT = 5
THREADS = 20


def check_domain(domain):
    domain = domain.strip()

    if not domain or domain.startswith("#"):
        return None

    # Resolver DNS
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        return {
            "domain": domain,
            "ip": None,
            "status": "DNS_FAIL",
            "url": None
        }

    # Probar HTTPS primero
    for scheme in ["https", "http"]:
        url = f"{scheme}://{domain}"

        try:
            response = requests.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                verify=False
            )

            return {
                "domain": domain,
                "ip": ip,
                "status": response.status_code,
                "url": response.url
            }

        except requests.RequestException:
            continue

    return {
        "domain": domain,
        "ip": ip,
        "status": "DNS_OK_HTTP_FAIL",
        "url": None
    }


def main():

    # Desactivar warnings de certificados
    requests.packages.urllib3.disable_warnings()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        domains = sorted(set(
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ))

    print(f"[+] Dominios a verificar: {len(domains)}")
    print()

    results = []

    with ThreadPoolExecutor(max_workers=THREADS) as executor:

        futures = {
            executor.submit(check_domain, domain): domain
            for domain in domains
        }

        for future in as_completed(futures):

            result = future.result()

            if result is None:
                continue

            results.append(result)

            if isinstance(result["status"], int):
                print(
                    f"[+] {result['domain']:<35} "
                    f"{result['ip']:<16} "
                    f"{result['status']} "
                    f"{result['url']}"
                )

            elif result["status"] == "DNS_OK_HTTP_FAIL":
                print(
                    f"[~] {result['domain']:<35} "
                    f"{result['ip']:<16} "
                    f"DNS OK / HTTP FAIL"
                )

            else:
                print(
                    f"[-] {result['domain']:<35} "
                    f"DNS FAIL"
                )

    # Guardar solamente los que tienen servicio HTTP/HTTPS
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

        for result in results:

            if isinstance(result["status"], int):

                f.write(
                    f"{result['domain']} | "
                    f"{result['ip']} | "
                    f"{result['status']} | "
                    f"{result['url']}\n"
                )

    print()
    print(f"[+] Resultados guardados en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()