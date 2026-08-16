"""
Orquestador Principal CLI: SAP Business One Enterprise RPA Suite
Descripción: Consola interactiva de orquestación de bots RPA automatizados para SAP Business One.

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import os
import sys
import json
import time

# Añadir directorio bots al PATH de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "bots"))

from sap_b1_connector import SAPB1Connector
from item_mass_update_bot import ItemMassUpdateBot
from monthly_report_bot import MonthlyFinancialReportBot
from sales_process_visibility_bot import SalesProcessVisibilityBot
from purchase_order_approval_workflow import PurchaseOrderApprovalWorkflow
from sales_opportunity_workflow import SalesOpportunityWorkflow
from pricing_discount_decision_engine import PricingDiscountDecisionEngine
from service_ticket_priority_engine import ServiceTicketPriorityEngine
from cognitive_ai_agent import SAPCognitiveAIAgent
from generate_sample_data import generate_sample_excel


def print_banner():
    print("=" * 75)
    print("=== SAP BUSINESS ONE ENTERPRISE RPA & AI CONTROL TOWER ===")
    print("   Arquitectura de Automatización, IA Cognitiva, Procesos y Decisión")
    print("   Lead MLOps Engineer: Guillén Concepción (guillenconcepcion@gmail.com)")
    print("=" * 75)


def run_item_mass_update():
    print("\n[RPA Task 1] Ejecutando Actualización Masiva de Artículos en SAP B1...")
    excel_file = "articulos_actualizacion.xlsx"
    if not os.path.exists(excel_file):
        generate_sample_excel(excel_file, num_records=25)

    connector = SAPB1Connector()
    bot = ItemMassUpdateBot(excel_path=excel_file, sap_connector=connector)
    result = bot.run_automation()
    print("\n--- RESUMEN DE ACTUALIZACIÓN MASIVA ---")
    print(json.dumps(result["summary"], indent=2))
    return result


def run_monthly_report():
    print("\n[RPA Task 2] Ejecutando Bot de Generación de Informes Mensuales Financieros...")
    connector = SAPB1Connector()
    bot = MonthlyFinancialReportBot(sap_connector=connector)
    result = bot.run_automation()
    print("\n--- RESUMEN DE INFORME MENSUAL FINANCIERO ---")
    print(json.dumps(result["kpis_summary"], indent=2))
    return result


def run_sales_process_visibility():
    print("\n[RPA Task 3] Ejecutando Bot de Visibilidad de Procesos de Ventas...")
    connector = SAPB1Connector()
    bot = SalesProcessVisibilityBot(sap_connector=connector)
    result = bot.run_automation()
    print("\n--- RESUMEN DE VISIBILIDAD DE PROCESOS DE VENTA ---")
    print(json.dumps(result["summary"], indent=2))
    return result


def run_process_workflows():
    print("\n[RPA Task 4] Ejecutando Artefactos de Proceso (Workflows Multidepartamentales)...")
    connector = SAPB1Connector()
    po_bot = PurchaseOrderApprovalWorkflow(sap_connector=connector)
    po_res = po_bot.execute_workflow()

    opp_bot = SalesOpportunityWorkflow(sap_connector=connector)
    opp_res = opp_bot.execute_workflow()

    print("\n--- RESUMEN WORKFLOWS DE PROCESO ---")
    print("Aprobaciones OPOR:", json.dumps(po_res["summary"], indent=2))
    print("Conversión Oportunidades:", json.dumps(opp_res["summary"], indent=2))
    return {"po_approval": po_res, "sales_opportunity": opp_res}


def run_decision_engines():
    print("\n[RPA Task 5] Ejecutando Artefactos de Decisión (Motores de Reglas de Negocio)...")
    connector = SAPB1Connector()
    pricing_bot = PricingDiscountDecisionEngine(sap_connector=connector)
    pricing_res = pricing_bot.evaluate_pricing_rules()

    ticket_bot = ServiceTicketPriorityEngine(sap_connector=connector)
    ticket_res = ticket_bot.evaluate_priority_rules()

    print("\n--- RESUMEN MOTORES DE DECISIÓN ---")
    print("Reglas Descuentos:", json.dumps(pricing_res["summary"], indent=2))
    print("Prioridad Tickets:", json.dumps(ticket_res["summary"], indent=2))
    return {"pricing": pricing_res, "tickets": ticket_res}


def run_cognitive_ai_agent():
    print("\n[RPA Task 6] Ejecutando Agente Cognitivo de IA (Inferencia de Anomalías & Riesgo)...")
    connector = SAPB1Connector()
    ai_agent = SAPCognitiveAIAgent(sap_connector=connector)
    ai_res = ai_agent.run_agent()

    print("\n--- RESUMEN AGENTE COGNITIVO DE IA ---")
    print(ai_res["executive_brief_nl"])
    return ai_res


def main():
    print_banner()
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--bot1", "items", "1"):
            run_item_mass_update()
            return
        elif arg in ("--bot2", "reports", "2"):
            run_monthly_report()
            return
        elif arg in ("--bot3", "visibility", "3"):
            run_sales_process_visibility()
            return
        elif arg in ("--workflows", "process", "4"):
            run_process_workflows()
            return
        elif arg in ("--decisions", "rules", "5"):
            run_decision_engines()
            return
        elif arg in ("--ai", "cognitive", "6"):
            run_cognitive_ai_agent()
            return
        elif arg in ("--all", "full"):
            run_item_mass_update()
            run_monthly_report()
            run_sales_process_visibility()
            run_process_workflows()
            run_decision_engines()
            run_cognitive_ai_agent()
            return

    # Menú interactivo CLI
    while True:
        print("\nSeleccione una opción de automatización:")
        print(" [1] Bot Actualización Masiva de Datos de Artículos (Excel -> SAP B1)")
        print(" [2] Bot Generación de Informes Mensuales Financieros (SAP B1 -> Excel + HTML Email)")
        print(" [3] Bot Visibilidad de Procesos de Ventas (Pipeline & Cuellos de Botella)")
        print(" [4] Artefactos de Proceso (Aprobación OPOR & Oportunidad a Pedido)")
        print(" [5] Artefactos de Decisión (Reglas de Descuentos VIP & Priorización Tickets SLA)")
        print(" [6] Agente Cognitivo de IA (Detección de Anomalías & Predicción de Desabastecimiento)")
        print(" [7] Ejecutar Suite Completa RPA + IA + Visibilidad + Procesos + Decisiones")
        print(" [0] Salir")
        
        choice = input("\nIngrese su opción [0-7]: ").strip()
        if choice == "1":
            run_item_mass_update()
        elif choice == "2":
            run_monthly_report()
        elif choice == "3":
            run_sales_process_visibility()
        elif choice == "4":
            run_process_workflows()
        elif choice == "5":
            run_decision_engines()
        elif choice == "6":
            run_cognitive_ai_agent()
        elif choice == "7":
            print("\n[RUN] Ejecutando Suite Completa Enterprise con Agente IA...")
            t0 = time.time()
            run_item_mass_update()
            run_monthly_report()
            run_sales_process_visibility()
            run_process_workflows()
            run_decision_engines()
            run_cognitive_ai_agent()
            print(f"\n[SUCCESS] Suite Enterprise ejecutada con éxito en {round(time.time() - t0, 2)}s.")
        elif choice == "0":
            print("Finalizando Suite RPA. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intente de nuevo.")






if __name__ == "__main__":
    main()
