"""
Bot RPA: Visibilidad de Procesos de Ventas & Trazabilidad de Cuellos de Botella (SAP Business One)
Descripción: Monitorea en tiempo real el ciclo de vida de órdenes de venta (ORDR -> ODLN -> OINV),
identificando aprobaciones pendientes, retrasos en almacén y restricciones de inventario.

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
logger = logging.getLogger("RPA_Sales_Process_Visibility")


class SalesProcessVisibilityBot:
    """
    Bot autónomo de análisis y trazabilidad del flujo de ventas (Pipeline & Bottlenecks) en SAP B1.
    """

    def __init__(self, sap_connector: SAPB1Connector):
        self.sap = sap_connector

    def analyze_pipeline(self) -> Dict[str, Any]:
        """Extrae y analiza las órdenes de venta y detecta cuellos de botella en tiempo real."""
        logger.info("Iniciando análisis de visibilidad de procesos de venta en SAP Business One...")
        self.sap.connect()

        orders = self.sap.fetch_sales_orders_pipeline()
        df = pd.DataFrame(orders)

        total_orders = len(df)
        total_pipeline_val = df["DocTotal"].sum() if not df.empty else 0.0

        bottlenecks = df[df["IsBottleneck"] == True] if not df.empty else pd.DataFrame()
        bottleneck_count = len(bottlenecks)
        bottleneck_amount = bottlenecks["DocTotal"].sum() if not bottlenecks.empty else 0.0

        # Conteo por etapa del proceso
        stages_summary = df["Stage"].value_counts().to_dict() if not df.empty else {}
        avg_aging_days = round(df["AgingDays"].mean(), 1) if not df.empty else 0.0

        bottleneck_details = []
        if not bottlenecks.empty:
            for _, row in bottlenecks.iterrows():
                bottleneck_details.append({
                    "doc_num": row["DocNum"],
                    "client": row["CardName"],
                    "doc_total_usd": row["DocTotal"],
                    "stage": row["Stage"],
                    "aging_days": row["AgingDays"],
                    "reason": row["BottleneckReason"],
                    "warehouse": row["Warehouse"]
                })

        summary = {
            "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_orders_in_pipeline": total_orders,
            "total_pipeline_value_usd": round(total_pipeline_val, 2),
            "bottlenecks_detected": bottleneck_count,
            "bottlenecks_value_usd": round(bottleneck_amount, 2),
            "average_aging_days": avg_aging_days,
            "stages_breakdown": stages_summary,
            "bottleneck_alerts": bottleneck_details
        }

        logger.info(f"Análisis finalizado: {bottleneck_count}/{total_orders} órdenes presentan cuellos de botella (${bottleneck_amount:,.2f} USD retenidos).")
        return {"summary": summary, "raw_orders": orders}

    def run_automation(self, output_json_path: str = "sales_process_visibility.json") -> Dict[str, Any]:
        """Ejecuta el análisis y guarda el artefacto de visibilidad de procesos."""
        start_time = time.time()
        res = self.analyze_pipeline()

        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2, ensure_ascii=False)
            logger.info(f"Artefacto de Visibilidad de Procesos guardado en: {output_json_path}")
        except Exception as e:
            logger.error(f"Error al guardar el archivo de visibilidad: {e}")

        res["execution_time_sec"] = round(time.time() - start_time, 2)
        return res


if __name__ == "__main__":
    connector = SAPB1Connector()
    bot = SalesProcessVisibilityBot(sap_connector=connector)
    result = bot.run_automation()
    print("\n--- ARTEFACTO DE VISIBILIDAD DE PROCESOS DE VENTA ---")
    print(json.dumps(result["summary"], indent=2))
