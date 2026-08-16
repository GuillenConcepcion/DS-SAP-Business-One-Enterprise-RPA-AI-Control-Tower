"""
Suite de Pruebas Automatizadas (Pytest / Unittest) para SAP Business One RPA Suite

Autor: Guillén Concepción - Senior Data Scientist & MLOps Engineer
Contacto: guillenconcepcion@gmail.com | https://github.com/GuillenConcepcion | https://www.linkedin.com/in/guillen-concepcion-25266b127
"""

import os
import sys
import unittest
import json
import pandas as pd

# Añadir ruta raíz y bots al PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../bots")))

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


class TestSAPB1RPASuite(unittest.TestCase):

    def setUp(self):
        self.connector = SAPB1Connector()
        self.test_excel = "test_items_temp.xlsx"

    def tearDown(self):
        for f in ["test_items_temp.xlsx", "test_audit_log.json", "test_Informe_Mensual.xlsx",
                  "test_email_report.html", "test_sales_process_visibility.json",
                  "test_po_approval.json", "test_sales_opp.json",
                  "test_pricing.json", "test_ticket_priority.json",
                  "test_cognitive_ai.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_sap_b1_connector_connection(self):
        """Prueba autenticación y fallback a simulación en el conector SAP B1."""
        connected = self.connector.connect()
        self.assertTrue(connected)
        self.assertTrue(self.connector.is_connected)

    def test_sap_b1_connector_financial_data(self):
        """Prueba extracción multimodular de ventas, contabilidad e inventario."""
        sales = self.connector.fetch_module_financials("ventas")
        self.assertGreater(len(sales), 0)
        acc = self.connector.fetch_module_financials("contabilidad")
        self.assertGreater(len(acc), 0)
        inv = self.connector.fetch_module_financials("inventario")
        self.assertGreater(len(inv), 0)
        pipeline = self.connector.fetch_sales_orders_pipeline()
        self.assertGreater(len(pipeline), 0)
        po = self.connector.fetch_purchase_orders()
        self.assertGreater(len(po), 0)
        tickets = self.connector.fetch_service_tickets()
        self.assertGreater(len(tickets), 0)

    def test_item_mass_update_bot(self):
        """Prueba la automatización de actualización masiva con Excel."""
        generate_sample_excel(self.test_excel, num_records=10)
        bot = ItemMassUpdateBot(excel_path=self.test_excel, sap_connector=self.connector)
        res = bot.run_automation(output_audit_json="test_audit_log.json")
        self.assertIn("summary", res)
        self.assertEqual(res["summary"]["total_processed"], 10)

    def test_monthly_report_bot(self):
        """Prueba extracción, consolidación de KPIs y generación de informes Excel / HTML."""
        bot = MonthlyFinancialReportBot(sap_connector=self.connector)
        raw = bot.extract_all_modules()
        kpis = bot.compute_kpis(raw)
        self.assertGreater(kpis["total_gross_sales_usd"], 0)
        excel_path = bot.generate_excel_report(raw, kpis, output_path="test_Informe_Mensual.xlsx")
        html_path = bot.generate_html_email_report(kpis, raw, output_html_path="test_email_report.html")
        self.assertTrue(os.path.exists(excel_path))
        self.assertTrue(os.path.exists(html_path))

    def test_sales_process_visibility_bot(self):
        """Prueba trazabilidad de pipeline de ventas y detección de cuellos de botella."""
        bot = SalesProcessVisibilityBot(sap_connector=self.connector)
        res = bot.run_automation(output_json_path="test_sales_process_visibility.json")
        self.assertIn("summary", res)
        self.assertEqual(res["summary"]["bottlenecks_detected"], 3)

    def test_process_workflows(self):
        """Prueba Workflows de Aprobación PO y Oportunidad a Pedido."""
        po_bot = PurchaseOrderApprovalWorkflow(sap_connector=self.connector)
        po_res = po_bot.execute_workflow(output_json_path="test_po_approval.json")
        self.assertEqual(po_res["summary"]["total_po_evaluated"], 3)

        opp_bot = SalesOpportunityWorkflow(sap_connector=self.connector)
        opp_res = opp_bot.execute_workflow(output_json_path="test_sales_opp.json")
        self.assertEqual(opp_res["summary"]["total_opportunities_evaluated"], 2)

    def test_decision_engines(self):
        """Prueba Motores de Decisión de Descuentos VIP y Prioridad de Tickets SLA."""
        pricing_bot = PricingDiscountDecisionEngine(sap_connector=self.connector)
        pricing_res = pricing_bot.evaluate_pricing_rules(output_json_path="test_pricing.json")
        self.assertEqual(pricing_res["summary"]["total_customers_evaluated"], 4)

        ticket_bot = ServiceTicketPriorityEngine(sap_connector=self.connector)
        ticket_res = ticket_bot.evaluate_priority_rules(output_json_path="test_ticket_priority.json")
        self.assertEqual(ticket_res["summary"]["total_tickets_evaluated"], 3)

    def test_cognitive_ai_agent(self):
        """Prueba Agente Cognitivo de IA, inferencia de anomalías y predicción de riesgo."""
        ai_agent = SAPCognitiveAIAgent(sap_connector=self.connector)
        ai_res = ai_agent.run_agent(output_json_path="test_cognitive_ai.json")
        self.assertIn("executive_brief_nl", ai_res)
        self.assertGreater(ai_res["anomalies_flagged_count"], 0)
        self.assertGreater(ai_res["stockout_risks_predicted_count"], 0)
        self.assertTrue(os.path.exists("test_cognitive_ai.json"))


if __name__ == "__main__":
    unittest.main()
