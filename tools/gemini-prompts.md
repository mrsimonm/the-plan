# Pasteable Gemini prompts

Attach `plant-data-spec.md` and `existing-names.txt` to every one of these.
Regenerate the names file before each session:

    python3 tools/merge_plants.py --names

---

## Prompt A — bulk cultivars, one genus at a time  ← use this most

Use **Canvas**. One genus per run keeps it focused, avoids duplicates, and
naturally lands near 40 records.

> You are compiling houseplant care data for an app. The attached
> `plant-data-spec.md` defines the exact JSON schema, the allowed values, and
> the writing style. Follow it precisely.
>
> Generate records for **every _____ cultivar and variety in general
> commercial cultivation**, including named cultivars, variegated forms and
> common trade names.
>
> Required fields only, plus `colour` — do not write `lore`, `size`,
> `propagation`, `tags` or `picto` for this batch.
>
> Fill `colour` carefully for every record. It is what distinguishes one
> cultivar from another, so be specific and descriptive rather than
> promotional.
>
> Exclude any name that appears in the attached `existing-names.txt`.
>
> Where cultivars genuinely share care requirements, give them the same
> numbers rather than inventing spurious variation between them.
>
> If you are not confident about a plant's toxicity, leave that plant out
> entirely rather than guessing.
>
> Output the JSON object and nothing else — no preamble, no explanation, no
> markdown code fence.

Good genera to work through: Philodendron · Monstera · Epipremnum/Scindapsus ·
Anthurium · Alocasia · Calathea/Goeppertia · Syngonium · Hoya · Begonia ·
Peperomia · Sansevieria/Dracaena · Ficus · Echeveria · Haworthia · Sedum ·
Aeonium · Euphorbia · Orchidaceae · Tradescantia · Aglaonema · Maranta.

---

## Prompt B — researched depth, for headline species

Two stages. **Stage 1 in Deep Research** — do not mention JSON:

> Research the following houseplants and write a detailed brief on each:
>
> [paste 20–40 plant names]
>
> For each plant cover, with sources:
> - realistic indoor watering interval in days for a mature plant in an average
>   heated room in spring and summer
> - realistic feeding interval in days during the growing season
> - light requirement, and humidity requirement
> - whether it is toxic to cats and dogs, according to published toxicity lists
> - mature size indoors, and the usual propagation method
> - the colour and markings of the foliage or flowers
> - its botanical identity and geographic origin
> - the single mistake that most often kills it indoors
> - one genuinely surprising, verifiable fact about it
>
> Be honest where sources disagree, and say so rather than averaging them.

**Stage 2 in Canvas** — paste the report in with the spec attached:

> Convert the research below into the JSON format defined in the attached
> `plant-data-spec.md`. Include all optional fields, including the three `lore`
> entries, using only facts present in the research — do not add anything from
> your own knowledge, and drop any plant the research does not cover properly.
>
> Match the writing style section of the spec exactly: British English, plain
> declarative sentences, no exclamation marks, no promotional adjectives.
>
> Output the JSON object and nothing else.
>
> ---
> [paste the Stage 1 report]

---

## Prompt C — filling gaps in plants already added

When a batch went in without the optional fields and you want to enrich it:

> For each plant name below, return a JSON object in the format defined in the
> attached `plant-data-spec.md`, containing **only** these fields: `name`,
> `category`, `water`, `feed`, `light`, `humidity`, `toxic`, `tip`, plus
> `size`, `propagation`, `tags` and `lore`.
>
> The `name` and `category` must match exactly what I give you. The other
> required fields must repeat the values I give you, unchanged.
>
> Output the JSON object and nothing else.
>
> ---
> [paste the records as they currently stand]

Re-running the merge replaces the whole generated block, so an enriched batch
file simply overwrites the thinner one — keep the same filename.

---

## Then

1. Save the JSON as `tools/batches/<genus>.json`.
2. Ask Claude to merge it. Claude runs:
   `python3 tools/merge_plants.py tools/batches/*.json`
3. The validator either merges, or prints exactly which records are wrong.
   Paste those errors back into Gemini and ask it to fix only those records.
