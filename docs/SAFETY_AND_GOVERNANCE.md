# Safety and governance

AgriAgent Nepal is designed so that critical system behavior is inspectable and testable.

## Rules encoded by the repository

- Language models do not select tools.
- Language models do not calculate areas, fertilizer masses, or unit conversions.
- Numeric values are produced by deterministic code.
- Fertilizer arithmetic accepts a nutrient recommendation as input; it does not invent the recommendation.
- Retrieval results retain source metadata.
- The bundled knowledge base is illustrative demo content, not a production agronomy corpus.
- Chemical-control text deliberately points users to locally registered products, current labels, and official/local extension guidance rather than hard-coding pesticide prescriptions.

## Production checklist

Before field deployment, replace the demo records with versioned content reviewed by agronomists and relevant Nepal authorities. Track jurisdiction, crop, agroecological zone, effective date, product-registration status, and reviewer. Add refusal/escalation rules for unclear diagnoses, severe crop loss, livestock/human poisoning, or requests that require current product-registration data.
