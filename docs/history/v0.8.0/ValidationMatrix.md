# v0.8.x Validation Matrix

Authority: Master Implementation Design, section 15. Status records observed evidence; future coverage does not imply a pass.

| ID | Requirement | Patch | Evidence | Status |
|---|---|---|---|---|
| N01 | Separate model | P81 | `tests/unit/test_normalized_business.py::test_normalized_business_is_separate_with_matching_fields_and_defaults` | PASS |
| N02 | Original preserved | P81/P83/P84 | `test_normalization_engine.py::test_complete_business_maps_without_mutating_original` | PASS |
| N03 | Independence | P81/P83 | Complete business and future mutable field tests in `test_normalization_engine.py` | PASS |
| N04 | Order unchanged | P83/P84 | Engine collection test and `test_global_normalization_pipeline.py::test_controlled_hundred_results_keep_order_and_count` | PASS |
| N05 | Cardinality unchanged | P83/P84 | Same 100-result public test | PASS |
| N06 | Name uppercase | P82 | `test_normalization_rules.py::test_name_rule` | PASS |
| N07 | Category uppercase | P82 | `test_normalization_rules.py::test_category_rule` | PASS |
| N08 | Address preserved | P82 | `test_normalization_rules.py::test_address_preserves_structure_and_case` | PASS |
| N09 | Phone 3-3-4 | P82 | `test_normalization_rules.py::test_phone_rule_is_conservative` | PASS |
| N10 | Explicit international | P82 | `test_normalization_rules.py::test_phone_rule_is_conservative` | PASS |
| N11 | Extensions preserved | P82 | `test_normalization_rules.py::test_phone_rule_is_conservative` | PASS |
| N12 | Safe website | P82 | `test_normalization_rules.py::test_website_keeps_sensitive_components` | PASS |
| N13 | Email lowercase | P82 | `test_normalization_rules.py::test_email_keeps_complete_value` | PASS |
| N14 | Language uppercase | P82 | `test_normalization_rules.py::test_language_keeps_subtags` | PASS |
| N15 | Metadata preserved | P82/P83 | Complete business and future mutable field tests in `test_normalization_engine.py` | PASS |
| N16 | Idempotence | P82/P83 | Rule cases and `test_normalization_engine.py::test_normalization_is_deterministic_and_idempotent` | PASS |
| N17 | Determinism | P82/P83 | Same engine repeatability test | PASS |
| N18 | Per-field recovery | P83 | `test_controlled_field_failure_preserves_field_and_continues` | PASS |
| N19 | Safe SearchIssue | P83/P84 | Engine field failure test and `test_global_normalization_pipeline.py::test_normalization_issue_follows_existing_issue` | PASS |
| N20 | Mandatory Engine | P84 | `test_global_normalization_pipeline.py::test_engine_and_wrapper_use_same_single_normalization` | PASS |
| N21 | Mandatory wrapper | P84 | Same integration test | PASS |
| N22 | Legacy compatibility | P84 | `test_legacy_limits_are_passed_through_without_engine_policy` plus existing wrapper/typed tests | PASS |
| N23 | Single normalization | P84 | Same integration test counts one call per public search and checks values | PASS |
| N24 | Normalized CLI | P85 | `test_cli_transitional_compatibility.py::test_cli_displays_normalized_view_and_safe_issue_context` checks displayed values and issue context | PASS |
| N25 | Normalized CSV | P85 | `test_export_service.py::test_export_service_writes_expected_csv_schema` checks normalized row values | PASS |
| N26 | Normalized XLSX | P85 | `test_export_service.py::test_export_service_writes_readable_xlsx` checks normalized row values | PASS |
| N27 | Seven columns | P85 | Both export service tests assert the seven approved headers and row values | PASS |
| N28 | No Google Maps regression | P84/P86 | `test_google_maps_pipeline_controlled.py` (8 controlled cases) plus full offline suite; no live source call | PASS_OFFLINE |
| N29 | Cleanup preserved | P84/P86 | `test_google_maps_pipeline_controlled.py::test_t_i06_normal_and_fatal_paths_close_once_preserving_exception` and `test_t_i01_fatal_navigation_closes_and_optional_partial_survives` | PASS_OFFLINE |
| N30 | Full offline suite | P86 | Final rerun: compileall PASS; 151 unit PASS, 34 integration PASS, 185 total PASS, 1 live E2E deselected; `git diff --check` PASS | PASS |
| N31 | Manual acceptance | Owner | Owner action after implementation | OWNER_PENDING |

P86 scope: N01–N30 have offline evidence. N28–N29 do not assert live Google Maps behavior; N31 remains exclusively with the owner. No live E2E or external search was performed.
