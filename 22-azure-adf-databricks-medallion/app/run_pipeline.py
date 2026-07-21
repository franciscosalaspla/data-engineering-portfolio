from adf_orchestrator import ADFStyleOrchestrator
from bronze_to_silver import bronze_to_silver
from generate_source_data import generate_source_data
from landing_to_bronze import landing_to_bronze
from quality_checks import run_quality_checks
from silver_to_gold import silver_to_gold

def run_pipeline():
    pipeline = ADFStyleOrchestrator()
    try:
        pipeline.activity("GenerateSourceData", [], generate_source_data)
        pipeline.activity("LandingToBronze", ["GenerateSourceData"], landing_to_bronze, pipeline.run_id)
        pipeline.activity("BronzeToSilver", ["LandingToBronze"], bronze_to_silver)
        gold = pipeline.activity("SilverToGold", ["BronzeToSilver"], silver_to_gold)
        quality = pipeline.activity("QualityChecks", ["SilverToGold"], run_quality_checks)
        summary = pipeline.write_summary("PASSED")
        print(f"Pipeline {summary['final_status']}: {quality['passed_checks']}/8 checks, {len(gold)} Gold datamarts")
        return summary
    except Exception:
        pipeline.write_summary("FAILED")
        raise

if __name__ == "__main__":
    run_pipeline()
