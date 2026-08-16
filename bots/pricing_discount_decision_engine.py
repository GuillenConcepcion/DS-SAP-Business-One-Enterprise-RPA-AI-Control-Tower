"""
Bot de Artefactos de Decisión: Motor de Reglas de Descuento y Precios Dinámicos (SAP Business One)
Descripción: Matriz de decisión automática que evalúa categorías VIP e historial de compras
del cliente en SAP B1 para aplicar descuentos especiales en ofertas (OQUT) y pedidos (ORDR).

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
logger = logging.getLogger("RPA_Pricing_Discount_Decision_Engine")


class PricingDiscountDecisionEngine:
    """
    Motor de reglas de decisión para aplicación condicional de precios y descuentos en SAP B1.
    """

    def __init__(self, sap_connector: SAPB1Connector):
        self.sap = sap_connector
        self.decision_logs: List[Dict[str, Any]] = []

    def evaluate_pricing_rules(self, output_json_path: str = "pricing_discount_decision_engine.json") -> Dict[str, Any]:
        """Aplica la tabla de decisiones de descuentos sobre los perfiles de clientes OCRD."""
        logger.info("Ejecutando Motor de Decisión de Precios y Descuentos Dinámicos...")
        self.sap.connect()

        customers = self.sap.fetch_customer_profiles()
        vip_platinum_discounts = 0
        vip_gold_discounts = 0
        standard_discounts = 0

        for cust in customers:
            card_code = cust["CardCode"]
            client_name = cust["CardName"]
            category = cust["CustomerCategory"]
            historical_sales = cust["HistoricalPurchasesUSD"]

            # Regla de Decisión
            if category == "VIP Platinum" or historical_sales >= 300000.0:
                discount_prcnt = 25.0
                tier = "PLATINUM VIP DISCOUNT"
                vip_platinum_discounts += 1
                decision_reason = f"Cliente clasificado como {category} o ventas acumuladas (${historical_sales:,.2f}) ≥ $300,000 USD. Descuento máximo asignado."
            elif category == "VIP Gold" or historical_sales >= 100000.0:
                discount_prcnt = 15.0
                tier = "GOLD VIP DISCOUNT"
                vip_gold_discounts += 1
                decision_reason = f"Cliente clasificado como {category} o ventas acumuladas (${historical_sales:,.2f}) ≥ $100,000 USD. Descuento intermedio asignado."
            else:
                discount_prcnt = 5.0
                tier = "STANDARD DISCOUNT"
                standard_discounts += 1
                decision_reason = f"Cliente Estándar con historial (${historical_sales:,.2f}) < $100,000 USD. Descuento comercial base asignado."

            entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "card_code": card_code,
                "client_name": client_name,
                "category": category,
                "historical_purchases_usd": historical_sales,
                "applied_discount_prcnt": discount_prcnt,
                "decision_tier": tier,
                "decision_reason": decision_reason
            }
            self.decision_logs.append(entry)
            logger.info(f"Cliente '{client_name}' ({card_code}) -> Descuento Aplicado: {discount_prcnt}% [{tier}]")

        summary = {
            "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_customers_evaluated": len(customers),
            "platinum_25pct_discounts": vip_platinum_discounts,
            "gold_15pct_discounts": vip_gold_discounts,
            "standard_5pct_discounts": standard_discounts
        }

        result = {"summary": summary, "decisions": self.decision_logs}

        try:
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Artefacto de Motor de Decisión de Precios guardado en: {output_json_path}")
        except Exception as e:
            logger.error(f"Error guardando artefacto pricing decision engine: {e}")

        return result


if __name__ == "__main__":
    connector = SAPB1Connector()
    engine = PricingDiscountDecisionEngine(sap_connector=connector)
    res = engine.evaluate_pricing_rules()
    print("\n--- RESUMEN MOTOR DE DECISIÓN DE DESCUENTOS Y PRECIOS ---")
    print(json.dumps(res["summary"], indent=2))
