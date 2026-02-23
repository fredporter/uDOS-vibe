# HubSpot Schema Expansion (Design)

This document defines the extended HubSpot-aligned schema for Empire. It is a design spec only (no code changes).

## Goals
- Cover common HubSpot contact defaults + high‑value business fields.
- Keep fields compatible with CSV export/import and API property names.
- Support future company and deal linkage without migration churn.

## Entity: Contact (records table)
Existing columns (already in Empire):
- `hs_object_id` (HubSpot record id)
- `email`, `firstname`, `lastname`
- `phone`, `mobilephone`, `fax`
- `jobtitle`, `company`, `website`
- `address`, `city`, `state`, `zip`, `country`
- `lifecyclestage`
- `createdate`, `lastmodifieddate`
- `source`, `record_id`, `raw_json`

Proposed additions:
- `lead_status` (HubSpot: `hs_lead_status`)
- `owner_id` (HubSpot: `hubspot_owner_id`)
- `timezone` (HubSpot: `timezone`)
- `language` (HubSpot: `hs_language`)
- `linkedin_url` (HubSpot: `linkedin_url`)
- `twitter_handle` (HubSpot: `twitterhandle`)
- `industry` (HubSpot: `industry`)
- `annual_revenue` (HubSpot: `annualrevenue`)
- `num_employees` (HubSpot: `numemployees`)
- `notes_last_contacted` (HubSpot: `notes_last_contacted`)
- `notes_last_updated` (HubSpot: `notes_last_updated`)
- `notes_next_activity_date` (HubSpot: `notes_next_activity_date`)
- `last_activity_date` (HubSpot: `last_activity_date`)
- `hs_analytics_source` (HubSpot: `hs_analytics_source`)
- `hs_analytics_source_data_1`, `hs_analytics_source_data_2`
- `hs_email_optout` (HubSpot: `hs_email_optout`)
- `hs_marketable_status` (HubSpot: `hs_marketable_status`)

## Entity: Company (companies table)
Proposed `companies` table:
- `hs_object_id` (HubSpot company id)
- `name`
- `domain`
- `website`
- `phone`
- `address`, `city`, `state`, `zip`, `country`
- `industry`
- `annual_revenue`
- `num_employees`
- `owner_id`
- `createdate`, `lastmodifieddate`
- `raw_json`

## Entity: Deal (future table)
Proposed `deals` table:
- `hs_object_id`
- `dealname`
- `dealstage`
- `pipeline`
- `amount`
- `closedate`
- `createdate`, `lastmodifieddate`
- `owner_id`
- `raw_json`

## Entity: Engagement / Event
Existing `events` table is sufficient. Optional additions:
- `direction` (inbound/outbound)
- `channel` (email, call, meeting)
- `source_system` (gmail, places, hubspot)

## Mapping Notes
- Use HubSpot property names in ingestion to preserve parity (`hs_lead_status`, `hubspot_owner_id`, etc.).
- Preserve unknown properties in `raw_json` for future backfill.
- Prefer nullable columns for incremental ingestion.

## Migration Plan (when implemented)
1. Add new nullable columns to `records`.
2. Add `companies`, `deals` tables.
3. Update normalization + ingestion mapping.
4. Add UI badges and filters (lead status, lifecycle stage).
