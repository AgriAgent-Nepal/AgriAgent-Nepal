# Data and conversion sources

## Nepal land units

The deterministic land-area calculator uses Nepal government conversion tables as the reference basis. The commonly published relationships include:

- 1 ropani = 16 aana = 5476 sq ft
- 1 bigha = 20 kattha = 72900 sq ft
- 1 kattha = 20 dhur = 3645 sq ft

Government references include the Department of Urban Development and Building Construction conversion table (official PDF: https://giwmscdntwo.gov.np/media/app/public/54/posts/1711001516_6.pdf) and Department of Land Management and Archive / land-revenue-office conversion tables (https://www.dolma.gov.np/).

Because published government tables sometimes round square-metre equivalents slightly differently, this repository keeps internally consistent relationships by deriving sub-units from the parent unit used in code. For cadastral/legal use, users should confirm the exact surveyed area with the responsible survey/land-revenue office.

## Fertilizer grades

The calculator includes common nominal fertilizer analyses (urea, DAP, and MOP) as configurable mass fractions for arithmetic. These grades are not crop recommendations. A production system should validate the actual product label/analysis available to the farmer before calculation.

## Demo agronomy corpus

`agriagent/data/knowledge.json` is intentionally small and illustrative. Source URLs identify plausible institutional provenance groups for architectural demonstration, but the text is not presented as a verbatim institutional publication. Replace it with audited, versioned documents before real deployment.
