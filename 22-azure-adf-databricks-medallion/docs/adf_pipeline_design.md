# Diseño del pipeline ADF-style

Actividades: `GenerateSourceData` → `LandingToBronze` → `BronzeToSilver` → `SilverToGold` → `QualityChecks`. Cada actividad registra dependencia, estado, duración y error. En Azure, las cargas serían Copy Activities y las transformaciones ejecutarían notebooks parametrizados mediante linked services autenticados con managed identity.
