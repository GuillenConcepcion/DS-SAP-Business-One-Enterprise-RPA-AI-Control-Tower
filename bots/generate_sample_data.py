"""
Utility Script: Generador de Data Sintética de Artículos SAP Business One
Descripción: Crea un archivo Excel ('articulos_actualizacion.xlsx') con cientos de registros
de prueba para la automatización de actualización masiva.

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import os
import pandas as pd
import random

def generate_sample_excel(output_filename: str = "articulos_actualizacion.xlsx", num_records: int = 50):
    print(f"Generando {num_records} artículos de prueba en '{output_filename}'...")

    categories = [
        ("Servidor Enterprise Dell PowerEdge", "Dell Server", 2500, 9500),
        ("Licencia Software ERP SAP B1", "SAP B1 License", 350, 1200),
        ("Switch de Red Cisco Catalyst", "Cisco Switch", 800, 3500),
        ("Almacenamiento SAN NetApp FAS", "NetApp Storage", 5000, 18000),
        ("Sistema de Respaldo UPS APC Smart", "APC UPS", 1200, 4500),
        ("Monitor Profesional Dell UltraSharp", "Dell Monitor", 300, 850),
        ("Firewall Fortinet FortiGate", "Fortinet Appliance", 1500, 6000)
    ]

    records = []
    for i in range(1, num_records + 1):
        cat_name, cat_alias, min_price, max_price = random.choice(categories)
        item_code = f"A{i:05d}"
        item_name = f"{cat_name} Model v{random.randint(1, 9)}.{random.randint(0, 9)}"
        foreign_name = f"{cat_alias} {i}"
        price = round(random.uniform(min_price, max_price), 2)
        group_code = random.randint(100, 105)
        wh_code = random.choice(["01", "02", "03"])

        records.append({
            "ItemCode": item_code,
            "ItemName": item_name,
            "ForeignName": foreign_name,
            "Price": price,
            "ItemsGroupCode": group_code,
            "WarehouseCode": wh_code
        })

    df = pd.DataFrame(records)
    df.to_excel(output_filename, index=False)
    print(f"[OK] Archivo Excel generado exitosamente con {len(df)} registros en '{output_filename}'.")
    return output_filename

if __name__ == "__main__":
    generate_sample_excel()
