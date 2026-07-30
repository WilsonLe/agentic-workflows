# Evidence and scoring

Normalize every source to evidence records with stable IDs, adapter versions,
observed/published timestamps, market and region status, signal type, metrics,
source URL/item ID, digest, confidence, rights/personal-data status, and
limitations. Deduplicate by source ID, canonical URL, and digest; cluster
syndicated copies without deleting underlying provenance.

Trend score weights: momentum 20, cross-platform spread 15, target relevance
10, remixability 10, product/visual suitability 15, shopping intent 10,
competition gap 10, useful lifespan 5, evidence quality 5. Hard safety gates
override scores. Below 60 ignore, 60–69 watch, 70–79 inexpensive test, and
80–100 launch candidate. Version weights in the project contract.
