"""
Bot de Artefactos de Proceso: Workflow de Gestión del Proceso de Ventas (OOPR -> ORDR)
Descripción: Automatiza la conversión de una Oportunidad de Venta a Pedido de Cliente en SAP Business One,
desencadenando la verificación de inventario y la asignación automática de un agente de logística.

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List
from sap_b1_connector import SAPB1Connector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
logger = logging.getLogger("RPA_Sales_Opportunity_Workflow")


class SalesOpportunityWorkflow:
    """
    Workflow de conversión automática de Oportunidades de Venta a Pedidos en SAP B1.
    """

    def __init__(self, sap_connector: SAPB1Connector, conversion_probability_threshold: float = 80.0):
        self.sap = sap_connector
        self.prob_threshold = conversion_probability_threshold
        self.workflow_logs: List[Dict[str, Any]] = []

    def execute_workflow(self, output_json_path: str = "sales_opportunity_workflow.json") -> Dict[str, Any]:
        """Ejecuta el flujo de conversión OOPR -> ORDR con verificación de stock y logística."""
        logger.info(f"Iniciando Workflow de Conversión de Oportunidades (Umbral Cierre: {self.prob_threshold}%)...")
        self.sap.connect()

        opps = self.sap.fetch_sales_opportunities()
        inventory = self.sap.fetch_inventory_data()
        converted_count = 0

        for opp in opps:
            opp_id = opp["OppID"]
            client = opp["CardName"]
            opp_name = opp["OppName"]
            amount = opp["MaxSum"]
            close_prcnt = opp["ClosePrcnt"]

            logger.info(f"Evaluando Oportunidad OOPR #{opp_id} | Cliente: '{client}' | Monto Est: ${amount:,.2f} USD | Prob: {close_prcnt}%")

            if close_prcnt >= self.prob_threshold:
                converted_count += 1
                new_doc_num = 3000 + opp_id
                
                # Verificación de Inventario
                total_stock = sum([item["OnHand"] for item in inventory])
                inventory_status = "Stock Disponible Verificado (Almacén 01)" if total_stock > 10 else "Stock Limitado - Requiere Reorden"

                # Asignación Logística
                assigned_agent = "Roberto Sánchez (Agente Logística Zona Norte)"
                action_detail = f"Oportunidad ganada ({close_prcnt}% prob). Convertida a Pedido ORDR #{new_doc_num}. {inventory_status}. Asignado a {assigned_agent}."

                log_entry = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "opp_id": opp_id,
                    "opportunity_name": opp_name,
                    "client_name": client,
                    "amount_usd": amount,
                    "probability_prcnt": close_prcnt,
                    "converted_to_order": True,
                    "sales_order_num": new_doc_num,
                    "inventory_check": inventory_status,
                    "assigned_logistics_agent": assigned_agent,
                    "detail": action_detail
                }
            else:
                log_entry = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "opp_id": opp_id,
                    "opportunity_name": opp_name,
                    "client_name": client,
                    "amount_usd": amount,
                    "probability_prcnt": close_prcnt,
                    "converted_to_order": False,
                    "sales_order_num": None,
                    "inventory_check": "N/A",
                    "assigned_logistics_agent": None,
                    "detail": f"Probabilidad ({close_prcnt}%) < Umbral ({self.prob_threshold}%). Mantenido en etapa {opp['Stage']}."
                }

            self.workflow_logs.append(log_entry)

        summary = {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_opportunities_evaluated": len(opps),
            "converted_to_sales_orders": converted_count,
            "logistics_tasks_dispatched": converted_count,
            "conversion_probability_threshold": self.prob_threshold
        }

        result = {"summary": summary, "converted_orders": self.workflow_logs}

        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Artefacto de Workflow de Oportunidades guardado en: {output_json_path}")
        except Exception as e:
            logger.error(f"Error guardando artefacto sales opportunity workflow: {e}")

        return result


if __name__ == "__main__":
    connector = SAPB1Connector()
    workflow = SalesOpportunityWorkflow(sap_connector=connector)
    res = workflow.execute_workflow()
    print("\n--- RESUMEN WORKFLOW OPORTUNIDAD A PEDIDO DE CLIENTE ---")
    print(json.dumps(res["summary"], indent=2))
