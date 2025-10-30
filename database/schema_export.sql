--
-- PostgreSQL database dump
--

\restrict Q3B2AgvjUd8fy0t2JZkN7uJVRyXG511khevQQbUM36aRJ1XdSbqretHIBXKj0C5

-- Dumped from database version 18.0 (Postgres.app)
-- Dumped by pg_dump version 18.0 (Postgres.app)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: fpds; Type: SCHEMA; Schema: -; Owner: raajthipparthy
--

CREATE SCHEMA fpds;


ALTER SCHEMA fpds OWNER TO raajthipparthy;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actions_clean; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.actions_clean (
    award_id text[],
    award_type text[],
    idv_id text[],
    idv_type text[],
    legal_business_name text,
    contracting_agency text,
    date_signed date,
    action_obligation numeric,
    referenced_idv text,
    contracting_office text,
    naics_code text,
    psc_code text,
    entity_city text,
    entity_state text,
    entity_zip text,
    unique_entity_id text,
    ultimate_parent_name text,
    ultimate_parent_uei text,
    cage_code text,
    view_link text
);


ALTER TABLE fpds.actions_clean OWNER TO raajthipparthy;

--
-- Name: agency_contractor_scores; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.agency_contractor_scores (
    unique_entity_id text,
    legal_business_name text,
    contracting_agency text,
    recent_dollars_12m double precision,
    touches_12m bigint,
    tenure_years double precision,
    recent_18m_flag boolean,
    rank_dollars double precision,
    rank_tenure double precision,
    rank_touches double precision,
    relationship_score double precision,
    vendor_key text
);


ALTER TABLE fpds.agency_contractor_scores OWNER TO raajthipparthy;

--
-- Name: agency_contractor_tiers; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.agency_contractor_tiers (
    unique_entity_id text,
    legal_business_name text,
    vendor_key text,
    contracting_agency text,
    recent_dollars_12m double precision,
    touches_12m bigint,
    tenure_years double precision,
    recent_18m_flag boolean,
    rank_dollars double precision,
    rank_tenure double precision,
    rank_touches double precision,
    relationship_score double precision,
    tier_label text,
    tier_rank bigint
);


ALTER TABLE fpds.agency_contractor_tiers OWNER TO raajthipparthy;

--
-- Name: agency_hhi; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.agency_hhi (
    contracting_agency text,
    hhi_0_1 double precision,
    hhi_0_10000 double precision
);


ALTER TABLE fpds.agency_hhi OWNER TO raajthipparthy;

--
-- Name: agency_market_12m; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.agency_market_12m (
    contracting_agency text,
    agency_recent_dollars_12m double precision,
    agency_share_of_total double precision
);


ALTER TABLE fpds.agency_market_12m OWNER TO raajthipparthy;

--
-- Name: agency_tier_summary; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.agency_tier_summary (
    contracting_agency text,
    tier_label text,
    vendors bigint,
    avg_score double precision,
    total_recent_dollars double precision
);


ALTER TABLE fpds.agency_tier_summary OWNER TO raajthipparthy;

--
-- Name: oppty_emerging_targets; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.oppty_emerging_targets (
    unique_entity_id text,
    legal_business_name text,
    contracting_agency text,
    recent_dollars_12m double precision,
    touches_12m bigint,
    tenure_years double precision,
    recent_18m_flag boolean,
    rank_dollars double precision,
    rank_tenure double precision,
    rank_touches double precision,
    relationship_score double precision,
    vendor_key text,
    tier_label text,
    vendor_share_12m double precision,
    hhi_0_10000 double precision,
    is_top_quartile_dollars boolean
);


ALTER TABLE fpds.oppty_emerging_targets OWNER TO raajthipparthy;

--
-- Name: oppty_greenfield_targets; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.oppty_greenfield_targets (
    unique_entity_id text,
    legal_business_name text,
    contracting_agency text,
    recent_dollars_12m double precision,
    touches_12m bigint,
    tenure_years double precision,
    recent_18m_flag boolean,
    rank_dollars double precision,
    rank_tenure double precision,
    rank_touches double precision,
    relationship_score double precision,
    vendor_key text,
    tier_label text,
    vendor_share_12m double precision,
    hhi_0_10000 double precision,
    is_top_quartile_dollars boolean
);


ALTER TABLE fpds.oppty_greenfield_targets OWNER TO raajthipparthy;

--
-- Name: oppty_reengage_targets; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.oppty_reengage_targets (
    unique_entity_id text,
    legal_business_name text,
    contracting_agency text,
    recent_dollars_12m double precision,
    touches_12m bigint,
    tenure_years double precision,
    recent_18m_flag boolean,
    rank_dollars double precision,
    rank_tenure double precision,
    rank_touches double precision,
    relationship_score double precision,
    vendor_key text,
    tier_label text,
    vendor_share_12m double precision,
    hhi_0_10000 double precision,
    is_top_quartile_dollars boolean
);


ALTER TABLE fpds.oppty_reengage_targets OWNER TO raajthipparthy;

--
-- Name: raw_actions; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.raw_actions (
    award_id_mod text[],
    award_type text[],
    idv_id text[],
    idv_type text[],
    legal_business_name text[],
    contracting_agency text[],
    date_signed text[],
    action_obligation text[],
    referenced_idv text[],
    contracting_office text[],
    naics_code text[],
    psc_code text[],
    entity_city text[],
    entity_state text[],
    entity_zip text[],
    unique_entity_id text[],
    ultimate_parent_name text[],
    ultimate_parent_uei text[],
    cage_code text[],
    view_link text[]
);


ALTER TABLE fpds.raw_actions OWNER TO raajthipparthy;

--
-- Name: top10_vendors_by_agency; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.top10_vendors_by_agency (
    contracting_agency text,
    vendor_key text,
    legal_business_name text,
    recent_dollars_12m double precision,
    agency_recent_dollars_12m double precision,
    agency_share_of_total double precision,
    vendor_share_12m double precision
);


ALTER TABLE fpds.top10_vendors_by_agency OWNER TO raajthipparthy;

--
-- Name: vendor_share_12m; Type: TABLE; Schema: fpds; Owner: raajthipparthy
--

CREATE TABLE fpds.vendor_share_12m (
    contracting_agency text,
    vendor_key text,
    legal_business_name text,
    recent_dollars_12m double precision,
    agency_recent_dollars_12m double precision,
    vendor_share_12m double precision
);


ALTER TABLE fpds.vendor_share_12m OWNER TO raajthipparthy;

--
-- PostgreSQL database dump complete
--

\unrestrict Q3B2AgvjUd8fy0t2JZkN7uJVRyXG511khevQQbUM36aRJ1XdSbqretHIBXKj0C5

