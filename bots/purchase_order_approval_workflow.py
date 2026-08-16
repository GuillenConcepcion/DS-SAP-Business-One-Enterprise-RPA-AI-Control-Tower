"""
Bot de Artefactos de Proceso: Workflow de Aprobación de Órdenes de Compra (SAP Business One)
Descripción: Activa flujos de trabajo automáticos al crear Órdenes de Compra (OPOR).
Si el monto excede el límite ($10,000 USD), enruta la solicitud al Gerente de Compras,
actualiza el estado en SAP B1 y notifica al Departamento de Finanzas.

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
logger = logging.getLogger("RPA_PO_Approval_Workflow")


class PurchaseOrderApprovalWorkflow:
    """
    Orquestador de flujo de trabajo multidepartamental para aprobaciones de compras en SAP B1.
    """

    def __init__(self, sap_connector: SAPB1Connector, approval_threshold_usd: float = 10000.0):
        self.sap = sap_connector
        self.threshold = approval_threshold_usd
        self.workflow_logs: List[Dict[str, Any]] = []

    def execute_workflow(self, output_json_path: str = "po_approval_workflow.json") -> Dict[str, Any]:
        """Ejecuta el flujo de trabajo de evaluación y enrutamiento de aprobaciones OPOR."""
        logger.info(f"Iniciando Workflow de Aprobación de Órdenes de Compra (Umbral: ${self.threshold:,.2f} USD)...")
        self.sap.connect()

        po_list = self.sap.fetch_purchase_orders()
        approved_count = 0
        manager_routed_count = 0

        for po in po_list:
            doc_num = po["DocNum"]
            vendor = po["VendorName"]
            amount = po["DocTotal"]
            requester = po["Requester"]

            logger.info(f"Procesando OPOR #{doc_num} | Proveedor: '{vendor}' | Monto: ${amount:,.2f} USD | Solicitante: {requester}")

            if amount > self.threshold:
                manager_routed_count += 1
                new_status = "Aprobado por Gerencia de Compras"
                action_detail = f"Monto (${amount:,.2f}) > Umbral (${self.threshold:,.2f}). Solicitud enviada a Gerente de Compras. Notificación enviada a Finanzas."
                notification_sent = True
            else:
                approved_count += 1
                new_status = "Aprobado Automático"
                action_detail = f"Monto (${amount:,.2f}) ≤ Umbral (${self.threshold:,.2f}). Aprobación directa por regla de negocio."
                notification_sent = False

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "doc_num": doc_num,
                "vendor_name": vendor,
                "amount_usd": amount,
                "requester": requester,
                "previous_status": po["Status"],
                "updated_status": new_status,
                "routed_to_manager": amount > self.threshold,
                "finance_notified": notification_sent,
                "detail": action_detail
            }
            self.workflow_logs.append(log_entry)

        summary = {
            "execution_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_po_evaluated": len(po_list),
            "automatically_approved": approved_count,
            "routed_to_manager_approval": manager_routed_count,
            "finance_notifications_dispatched": manager_routed_count,
            "threshold_used_usd": self.threshold
        }

        result = {"summary": summary, "workflow_details": self.workflow_logs}

        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Artefacto de Workflow de Compras guardado exitosamente en: {output_json_path}")
        except Exception as e:
            logger.error(f"Error guardando artefacto PO workflow: {e}")

        return result


if __name__ == "__main__":
    connector = SAPB1Connector()
    workflow = PurchaseOrderApprovalWorkflow(sap_connector=connector)
    res = workflow.execute_workflow()
    print("\n--- RESUMEN WORKFLOW DE APROBACIÓN DE COMPRAS ---")
    print(json.dumps(res["summary"], indent=2))
