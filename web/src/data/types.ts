/**
 * Data contracts and typed entities for bari-link web app.
 * Model-visible and structural types only.
 */

export interface RecordEntry {
  record_id: string;
  source_module: string;
  enrolment_date?: string;
  full_name_raw: string;
  guardian_name_raw: string;
  guardian_type_raw?: string | null;
  age_raw?: number | null;
  sex_raw?: string | null;
  phone_raw?: string | null;
  village_raw: string;
  union_raw?: string | null;
  upazila_raw?: string | null;
  district_raw?: string | null;
  group_id?: string | null;
}

export interface CandidatePair {
  record_id_l: string;
  record_id_r: string;
  match_weight: number;
  match_probability: number;
  [key: string]: any;
}

export interface WaterfallStep {
  name: string;
  label: string;
  log2_bf: number;
  running_weight: number;
  probability: number;
  is_positive: boolean;
}

export interface ClusterAssignment {
  t_link: number;
  record_id: string;
  cluster_id: string;
}

export interface HouseholdGolden {
  household_cluster_id: string;
  village?: string;
  village_mode?: string;
  union?: string;
  union_mode?: string;
  direct_reach: number;
  indirect_reach: number;
  est_household_size: number;
  enrolled_members: any;
  enrolled_modules?: string[];
  modules?: string[];
  roster_names_unenrolled: any;
  phones_all?: string[];
  pooled_phones?: string[];
  lineage?: string;
  field_lineage?: string;
}

export interface GraphNode {
  id: string;
  name: string;
  module?: string;
  village?: string;
  isHouseholdMember: boolean;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  evidence_type: string; // E1, E2, E3, E4, E5
  evidence_score: number;
  details?: string;
}

export interface HouseholdGraphData {
  nodes: GraphNode[];
  edges: GraphLink[];
}

export interface ModuleCount {
  source_module: string;
  count: number;
}
