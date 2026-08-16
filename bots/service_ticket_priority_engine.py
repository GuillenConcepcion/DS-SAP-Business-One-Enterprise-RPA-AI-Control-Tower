"""
Bot de Artefactos de Decisión: Motor de Asignación de Prioridad de Tickets de Servicio (SAP Business One)
Descripción: Evalúa contratos SLA, criticidad y tipo de cliente en SAP B1 (Tabla OSCL) para
asignar automáticamente prioridad alta/crítica garantizando tiempos de respuesta inmediatos.

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
logger = logging.getLogger("RPA_Service_Ticket_Priority_Engine")


class ServiceTicketPriorityEngine:
    """
    Motor de reglas de decisión para priorización automática de tickets de servicio en SAP B1.
    """

    def __init__(self, sap_connector: SAPB1Connector):
        self.sap = sap_connector
        self.decision_logs: List[Dict[str, Any]] = []

    def evaluate_priority_rules(self, output_json_path: str = "service_ticket_priority_engine.json") -> Dict[str, Any]:
        """Evalúa los tickets de servicio pendientes (OSCL) y aplica la matriz SLA."""
        logger.info("Ejecutando Motor de Decisión de Priorización de Tickets de Servicio (OSCL)...")
        self.sap.connect()

        tickets = self.sap.fetch_service_tickets()
        critical_count = 0
        high_count = 0
        medium_count = 0

        for t in tickets:
            call_id = t["ServiceCallID"]
            client = t["CardName"]
            subject = t["Subject"]
            contract = t["ContractType"]
            criticality = t["Criticality"]

            # Matriz de Decisión de Prioridad & SLA
            if contract == "Platinum 24/7" or criticality == "Alta":
                assigned_priority = "CRÍTICA"
                sla_hours = 2
                sla_target = "Respuesta Inmediata (SLA 2 Horas)"
                critical_count += 1
                decision_reason = f"Contrato {contract} o criticidad {criticality}. Asignación inmediata a Soporte Nivel 3."
            elif contract == "Gold 8x5":
                assigned_priority = "ALTA"
                sla_hours = 4
                sla_target = "Respuesta Prioritaria (SLA 4 Horas)"
                high_count += 1
                decision_reason = f"Contrato {contract}. Asignación a Soporte Nivel 2."
            else:
                assigned_priority = "MEDIA"
                sla_hours = 24
                sla_target = "Respuesta Estándar (SLA 24 Horas)"
                medium_count += 1
                decision_reason = f"Contrato {contract} y criticidad {criticality}. Asignación a Mesa de Ayuda Nivel 1."

            entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "service_call_id": call_id,
                "client_name": client,
                "subject": subject,
                "contract_type": contract,
                "criticality": criticality,
                "assigned_priority": assigned_priority,
                "sla_target": sla_target,
                "sla_response_hours": sla_hours,
                "decision_reason": decision_reason
            }
            self.decision_logs.append(entry)
            logger.info(f"Ticket #{call_id} [{client}] -> Prioridad: {assigned_priority} ({sla_target})")

        summary = {
            "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tickets_evaluated": len(tickets),
            "critical_priority_assigned": critical_count,
            "high_priority_assigned": high_count,
            "medium_priority_assigned": medium_count
        }

        result = {"summary": summary, "ticket_decisions": self.decision_logs}

        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Artefacto de Priorización de Tickets guardado en: {output_json_path}")
        except Exception as e:
            logger.error(f"Error guardando artefacto ticket priority engine: {e}")

        return result


if __name__ == "__main__":
    connector = SAPB1Connector()
    engine = ServiceTicketPriorityEngine(sap_connector=connector)
    res = engine.evaluate_priority_rules()
    print("\n--- RESUMEN MOTOR DE PRIORIZACIÓN DE TICKETS DE SERVICIO ---")
    print(json.dumps(res["summary"], indent=2))
