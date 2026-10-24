# Schema Design

Star schema in `marts_nds`: one fact table and seven dimensions, built in dbt from `stg_contract_transactions`. Surrogate keys are `dbt_utils.generate_surrogate_key` hashes.

## fct_transaction

**Grain:** one row per contract transaction (a single action or modification on a contract or IDV).
**Primary key:** `contract_transaction_unique_key`

| Column                                    | Role                                                                                         |
| ----------------------------------------- | -------------------------------------------------------------------------------------------- |
| `contract_transaction_unique_key`         | primary key                                                                                  |
| `contract_award_unique_key`               | degenerate dim, identifies the award                                                         |
| `award_id_piid`                           | degenerate dim                                                                               |
| `parent_award_id_piid`                    | degenerate dim, PIID of the parent IDV an order was placed under. Null for standalone awards |
| `transaction_number`                      | degenerate dim                                                                               |
| `modification_number`                     | degenerate dim                                                                               |
| `action_type_code` / `action_type`        | degenerate dim                                                                               |
| `action_date_key`                         | FK to dim_date, role: action date                                                            |
| `pop_start_date_key`                      | FK to dim_date, role: period of performance start                                            |
| `pop_end_date_key`                        | FK to dim_date, role: period of performance current end                                      |
| `solicitation_date_key`                   | FK to dim_date, role: solicitation date                                                      |
| `awarding_agency_key`                     | FK to dim_agency, role: awarding                                                             |
| `funding_agency_key`                      | FK to dim_agency, role: funding                                                              |
| `recipient_key`                           | FK to dim_recipient, version in effect on the action date                                    |
| `location_key`                            | FK to dim_location                                                                           |
| `product_key`                             | FK to dim_product                                                                            |
| `award_key`                               | FK to dim_award                                                                              |
| `competition_key`                         | FK to dim_competition                                                                        |
| `federal_action_obligation`               | measure, additive                                                                            |
| `total_dollars_obligated`                 | measure, award-level snapshot, not additive                                                  |
| `total_outlayed_amount_for_overall_award` | measure, award-level snapshot, not additive                                                  |
| `current_total_value_of_award`            | measure, award-level snapshot, not additive                                                  |
| `potential_total_value_of_award`          | measure, award-level snapshot, not additive                                                  |
| `number_of_offers_received`               | measure, average it, don't sum it                                                            |

Dimension keys are recomputed by hashing the same staging columns, in the same order, as each dimension, instead of joining (a join can't match NULLs). Two exceptions: `recipient_key` is joined by action date within the version's date range, and date keys are joined to dim_date, so dates outside its window are NULL.

## dim_date

**Grain:** one row per calendar date, 1950-01-01 to 2079-12-31.
**Primary key:** `date_day` (natural key)

| Column        | Description                                          |
| ------------- | ---------------------------------------------------- |
| `date_day`    | calendar date, referenced 4 ways from the fact table |
| `fiscal_year` | federal fiscal year (starts Oct 1)                   |

Entry errors in the non-action date roles (years like 1919 or 3019) fall outside the window and get a NULL key. Action dates are always in range.

Planned: `cpi_index` for the inflation-adjusted trends question, added as a dbt seed (CPI-U or the BEA national defense price index, not chosen yet).

## dim_agency

**Grain:** one row per agency + sub-agency, combined from awarding and funding values.
**Primary key:** `agency_key`; natural key `agency_code` + `sub_agency_name`

| Column               | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agency_code`        | toptier agency code                                                                         |
| `agency_name`        | toptier agency name                                                                         |
| `sub_agency_name`    | sub-agency name                                                                             |
| `budget_subfunction` | derived: 097 (DoD) to 051, 089 (DOE) to 053, 069 (DOT) and 070 (DHS) to 054, NULL otherwise |

- One table, two roles. Awarding and funding only exist as FK names on the fact table.
- `budget_subfunction` describes the awarding scope. Agencies that only appear as funders are NULL.
- NPPD (the pre-2018 name) is mapped to CISA in staging.
- Some agency codes are 4 digits (`1601` Labor, `3300` Smithsonian). These are real codes, not errors.

## dim_recipient (SCD Type 2)

**Grain:** one row per recipient per version.
**Primary key:** `recipient_key` (hash of `recipient_uei` and the version's start fiscal year); business key `recipient_uei`

| Column                                                           | Type                                                                |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| `recipient_uei`                                                  | business key                                                        |
| `recipient_name`                                                 | Type 1 (latest)                                                     |
| `recipient_parent_uei`                                           | versioned                                                           |
| `recipient_parent_name`                                          | Type 1 (latest per parent UEI)                                      |
| `recipient_state_code`                                           | versioned, registered state (where the company is based)            |
| `veteran_owned_business`                                         | Type 1                                                              |
| `woman_owned_business`                                           | Type 1                                                              |
| `women_owned_small_business`                                     | Type 1                                                              |
| `minority_owned_business`                                        | Type 1                                                              |
| `small_disadvantaged_business`                                   | Type 1                                                              |
| `c8a_program_participant`                                        | Type 1                                                              |
| `historically_underutilized_business_zone_hubzone_firm`          | Type 1                                                              |
| `domestic_or_foreign_entity_code` / `domestic_or_foreign_entity` | Type 1                                                              |
| `effective_start_date`                                           | Oct 1 of the version's first fiscal year                            |
| `effective_end_date`                                             | Sep 30 before the next version starts. NULL for the current version |
| `is_current`                                                     | true for the current version                                        |

Version rule: for each recipient and fiscal year, take the parent UEI and registered state with the most absolute obligated dollars that year (ties by count, then value). A new version starts when that pair changes from the prior year.

- Per-transaction change detection was rejected. Parent UEI reporting flaps between entities of the same corporate family and produced about 459,000 versions (one recipient alone had 200,776). The yearly rule gives 153,257 versions for 128,652 recipients.
- Known limitation: large companies can still switch between entities in one family across years.
- USASpending overwrites recipient and parent names with current names, so name history isn't recoverable.

## dim_location

**Grain:** one row per place of performance.
**Primary key:** `location_key`; natural key country + state code + county + city, in that order (fct_transaction hashes the same order)

| Column                                      |
| ------------------------------------------- |
| `primary_place_of_performance_country_name` |
| `primary_place_of_performance_state_code`   |
| `primary_place_of_performance_state_name`   |
| `primary_place_of_performance_county_name`  |
| `primary_place_of_performance_city_name`    |

State name is the latest spelling per code.

## dim_product

**Grain:** one row per NAICS + PSC combination.
**Primary key:** `product_key`; natural key `naics_code` + `product_or_service_code`

| Column                                |
| ------------------------------------- |
| `naics_code`                          |
| `naics_description`                   |
| `product_or_service_code`             |
| `product_or_service_code_description` |
| `psc_portfolio_group`                 |

- Descriptions use the latest wording per code (NAICS 2017 and 2022 revisions reworded titles).
- `psc_portfolio_group` from the first character of the PSC: digit = Supplies/Equipment, A = R&D, Y or Z = Construction, other letters = Services.

## dim_award

**Grain:** one row per award type combination.
**Primary key:** `award_key`; natural key is all seven code columns

| Column                                                       |
| ------------------------------------------------------------ |
| `award_or_idv_flag`                                          |
| `award_type_code` / `award_type`                             |
| `idv_type`                                                   |
| `parent_award_type`                                          |
| `multiple_or_single_award_idv`                               |
| `type_of_idc`                                                |
| `type_of_contract_pricing_code` / `type_of_contract_pricing` |

- Descriptions use the most common wording per code.
- `parent_award_id_piid` is on the fact table, not here. It identifies a specific vehicle (thousands of values), not a type, and would make this table almost one row per contract.

## dim_competition (junk dimension)

**Grain:** one row per competition/set-aside combination observed in the data.
**Primary key:** `competition_key`; natural key is all four columns

| Column                                                |
| ----------------------------------------------------- |
| `extent_competed`                                     |
| `type_of_set_aside`                                   |
| `other_than_full_and_open_competition`                |
| `contracting_officers_determination_of_business_size` |

- `other_than_full_and_open_competition` is standardized in staging: 33 source values collapse to 17 (each justification appeared with and without its FAR citation).
- Business size is decided per contract against that contract's NAICS size standard, so it describes the contract, not the company.
- `number_of_offers_received` is a measure on the fact table.