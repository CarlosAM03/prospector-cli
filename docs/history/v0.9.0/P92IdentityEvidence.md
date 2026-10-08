# P92 — Limited live identity investigation (2026-10-07)

Authorization: owner decision resolving the investigation scope of STOP-09-IDENTITY-01. This is **not** G23 or general live acceptance. No Places API, API key, external website enrichment, exports or broad E2E were used. Browser: existing local `BrowserRuntime`/Chromium, headless. Local probes: `evidence/identity_probe.py` and `evidence/verify_place_id_url.py`. The probes only read the current Maps result feed/detail and official Maps URL result; they do not alter production code.

## Official semantics versus observed internal encoding

Google's [Place IDs documentation](https://developers.google.com/maps/documentation/places/web-service/place-id) states that a Place ID identifies a place in Google Maps/Places, may have multiple values for one place and may change over time. Google's [Maps URLs guide](https://developers.google.com/maps/documentation/urls/get-started) documents `query_place_id` as a Place ID and says `query` is fallback if the ID is not found. **Neither page documents `!1s` or `!19s` as a Place ID.** The association of observed `!19sChIJ…` with an official Place ID is therefore a *narrow inference from the live checks below*, not a general assertion about arbitrary Maps URL segments.

## Controlled observations

One initial exact-name search (`Starbucks Plaza Río`, Tijuana) opened Maps but timed out waiting for `/maps/search/`; no candidate or identity was observed. Three subsequent one-candidate searches through the existing feed/detail flow completed:

| Query | Candidate/panel | Address (public, abbreviated) | Candidate `!1s` | Candidate `!19s` |
|---|---|---|---|---|
| Starbucks / Tijuana | Starbucks | Paseo de los Héroes 95-5E, Local 19, Zona Río | `0x80d94840107994c1:0x95f9d1c6296e50c3` | `ChIJwZR5EEBI2YARw1BuKcbR-ZU` |
| Starbucks Zona Río / Tijuana | Starbucks | Paseo de los Héroes 95-5E, Local 19, Zona Río | **same as above** | **same as above** |
| Starbucks Otay / Tijuana | Starbucks OTAY DT | Blvd. Lázaro Cárdenas 16002, La Pechuga | `0x80d94795c4dfdb89:0xec6b16defc35d695` | `ChIJidvfxJVH2YARldY1_N4Wa-w` |

In each completed observation, the candidate href originated at `www.google.com/maps/place/`, contained both markers in the same link, and the clicked result reached a matching visible panel. The selected URL retained the candidate's exact `!1s` feature token. The `!1s` value is **not** promoted to the batch identity; it is only a conservative link/transition corroboration.

To distinguish a real Place ID from an arbitrary `ChIJ`-shaped string, both observed `!19s` values were supplied separately to Google's *documented* Maps URL form `https://www.google.com/maps/search/?api=1&query=__prospector_p92_unmatched_probe__&query_place_id=<ID>`. The intentionally nonexistent `query` prevents a plausible name fallback. The first resolved to panel `Starbucks` with the Zona Río address; the second to `Starbucks OTAY DT` with the Otay address. This supports that these two observed `!19s` values are valid Google Place IDs tied to **different establishments**, not a common Starbucks brand ID.

## Narrow proposed verification policy for P92

Only `https://www.google.com/maps/place/...` candidate hrefs with a **single** `!19sChIJ…` segment and a **single** structured `!3m6!1s0x…:0x…!8m2` candidate feature token qualify for evaluation. The detail click must verify the exact candidate target, URL transition to a selected `/maps/place/` URL carrying the **same structured feature token**, a fresh visible panel and equivalent candidate title. Only then may the observed `!19s` value become `VerifiedSourceIdentity(Source.GOOGLE_MAPS, "google_place_id", value)`. No `href`, `!1s`, `cid`, `!16s`, name or address alone is sufficient. Missing/multiple/unknown tokens, another domain, failed click/panel/transition or ambiguity => `UNVERIFIED` and retained exportability. No cross-namespace equivalence or extrapolation to other Place ID formats is approved by this evidence.

The official caveat that one place may have multiple IDs or a changing ID means this policy can yield **false negatives** (both observations remain exportable). It must not claim universal deduplication. It does not justify merging fields or matching by text.

## Gate boundary

The live observations and official documentation support implementing and testing this restricted namespace offline. Source sidecar propagation, failure-path negatives, cardinality/order checks and offline regression subsequently passed: 47 focused, 186 unit, 37 integration and 223 full PASS, one E2E deselected; compileall and diff check PASS. **P92 PASS** for this restricted namespace. G23 remains pending separate owner authorization.
