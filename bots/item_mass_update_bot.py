"""
Bot RPA: Actualización Masiva de Datos de Artículos en SAP Business One
Descripción: Lee datos desde Excel/CSV, valida esquemas y tipos, interactúa con SAP B1
y genera reportes de auditoría eliminando errores de transcripción manual.

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import os
import sys
import json
import logging
import time
import pandas as pd
from typing import Dict, Any, List
from sap_b1_connector import SAPB1Connector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("RPA_Item_Mass_Update")


class ItemMassUpdateBot:
    def __init__(self, excel_path: str, sap_connector: SAPB1Connector):
        self.excel_path = excel_path
        self.sap = sap_connector
        self.audit_logs: List[Dict[str, Any]] = []

    def load_and_validate_data(self) -> pd.DataFrame:
        """Carga y valida el archivo Excel/CSV con los artículos a actualizar."""
        logger.info(f"Cargando archivo de artículos desde: {self.excel_path}")
        if not os.path.exists(self.excel_path):
            logger.warning("Archivo no encontrado en disco. Generando dataset de prueba sintético...")
            df = pd.DataFrame([
                {"ItemCode": "A00001", "ItemName": "Servidor Dell PowerEdge R750 Enterprise", "ForeignName": "Dell Server R750", "Price": 3450.00, "ItemsGroupCode": 100, "WarehouseCode": "01"},
                {"ItemCode": "A00002", "ItemName": "Licencia SAP Business One Cloud Professional", "ForeignName": "SAP B1 Cloud Pro", "Price": 490.00, "ItemsGroupCode": 101, "WarehouseCode": "01"},
                {"ItemCode": "A00003", "ItemName": "Switch Cisco Catalyst 9300 48-Port", "ForeignName": "Cisco Cat 9300", "Price": 1950.00, "ItemsGroupCode": 102, "WarehouseCode": "02"},
                {"ItemCode": "A00004", "ItemName": "Almacenamiento SAN NetApp FAS2750", "ForeignName": "NetApp SAN", "Price": 8200.00, "ItemsGroupCode": 100, "WarehouseCode": "01"},
                {"ItemCode": "A00005", "ItemName": "UPS APC Smart-UPS RT 10000VA", "ForeignName": "APC UPS 10K", "Price": 2800.00, "ItemsGroupCode": 103, "WarehouseCode": "02"}
            ])
            return df

        if self.excel_path.endswith('.csv'):
            df = pd.read_csv(self.excel_path)
        else:
            df = pd.read_excel(self.excel_path)
            
        required_cols = ["ItemCode", "ItemName", "Price"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Falta columna requerida '{col}' en el archivo.")
        return df

    def run_automation(self, output_audit_json: str = "audit_log_item_update.json") -> Dict[str, Any]:
        """Ejecuta la secuencia de automatización de actualización masiva."""
        start_time = time.time()
        logger.info("Iniciando Bot de Actualización Masiva en SAP Business One...")
        
        df = self.load_and_validate_data()
        total_records = len(df)
        success_count = 0
        error_count = 0

        self.sap.connect()

        for idx, row in df.iterrows():
            item_code = str(row["ItemCode"]).strip()
            item_name = str(row["ItemName"]).strip()
            try:
                price = float(row["Price"])
            except (ValueError, TypeError):
                price = 0.0
            
            update_payload = {
                "ItemName": item_name,
                "ForeignName": str(row.get("ForeignName", "")),
                "ItemPrices": [
                    {
                        "PriceList": 1,
                        "Price": price,
                        "Currency": "USD"
                    }
                ]
            }

            logger.info(f"[{idx+1}/{total_records}] Procesando Artículo '{item_code}' -> Precio: ${price:,.2f}")
            res = self.sap.update_item_master_data(item_code, update_payload)
            
            audit_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "record_index": idx + 1,
                "item_code": item_code,
                "item_name": item_name,
                "price_usd": price,
                "status": res.get("status"),
                "message": res.get("message")
            }
            self.audit_logs.append(audit_entry)
            
            if "SUCCESS" in res.get("status", ""):
                success_count += 1
            else:
                error_count += 1
                
            time.sleep(0.02)

        elapsed = time.time() - start_time
        summary = {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_processed": total_records,
            "success_count": success_count,
            "error_count": error_count,
            "time_elapsed_sec": round(elapsed, 2),
            "records_per_second": round(total_records / elapsed, 2) if elapsed > 0 else 0,
            "accuracy_rate": f"{(success_count / total_records) * 100:.1f}%" if total_records > 0 else "0.0%"
        }
        
        # Guardar registro de auditoría en JSON
        try:
            with open(output_audit_json, "w", encoding="utf-8") as f:
                json.dump({"summary": summary, "logs": self.audit_logs}, f, indent=2, ensure_ascii=False)
            logger.info(f"Informe de auditoría guardado exitosamente en: {output_audit_json}")
        except Exception as e:
            logger.error(f"No se pudo guardar el archivo de auditoría: {e}")

        logger.info(f"Automatización Finalizada: {summary['success_count']}/{summary['total_processed']} exitosos en {summary['time_elapsed_sec']}s.")
        return {"summary": summary, "logs": self.audit_logs}


if __name__ == "__main__":
    connector = SAPB1Connector()
    bot = ItemMassUpdateBot(excel_path="articulos_actualizacion.xlsx", sap_connector=connector)
    result = bot.run_automation()
    print("\n--- RESUMEN DE EJECUCIÓN RPA ---")
    print(json.dumps(result["summary"], indent=2))

