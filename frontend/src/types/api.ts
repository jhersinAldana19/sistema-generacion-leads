export interface User {
  id: number
  name: string
  email: string
}

export interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  metadata_json: Record<string, unknown> | null
  created_at: string
}

export type EntityType = 'person' | 'company' | 'supplier' | 'institution' | 'professional' | 'product'
export type RequiredContact = 'email' | 'phone' | 'linkedin' | 'website'

export interface SearchCriteria {
  entity_type: EntityType
  job_levels: string[]
  areas: string[]
  industries: string[]
  countries: string[]
  cities: string[]
  products_or_services: string[]
  required_contacts: RequiredContact[]
  conditions: string[]
  max_results: number
  summary_es: string
}

export interface InterpretResponse {
  criteria: SearchCriteria
  change_summary_es: string | null
}

export type SearchStatusValue = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface Search {
  id: number
  conversation_id: number
  original_query: string
  search_type: string
  status: SearchStatusValue
  criteria_json: SearchCriteria
  max_results: number
  is_favorite: boolean
  created_at: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

export interface SearchListItem extends Search {
  result_count: number
}

export interface SearchProgress {
  companies_reviewed: number
  pages_analyzed: number
  pages_inaccessible: number
  results_found: number
}

export interface SearchStatusOut {
  id: number
  status: SearchStatusValue
  progress: SearchProgress
}

export type ResultStatus = 'candidate' | 'probable' | 'confirmed' | 'outdated' | 'needs_review' | 'discarded'
export type ReviewStatus = 'pending' | 'confirmed' | 'discarded' | 'flagged'

export interface PersonResultData {
  entity_type: 'person'
  full_name: string
  job_title: string
  area: string | null
  company_name: string
  industry: string | null
  country: string | null
  city: string | null
  linkedin_url: string | null
  direct_email: string | null
  direct_email_type: string | null
  direct_email_status: string | null
  direct_phone: string | null
  direct_phone_type: string | null
  company_email: string | null
  company_phone: string | null
  company_website: string | null
  source_url: string
  source_date: string | null
  evidence_text: string
  verification_status: ResultStatus
  missing_fields: string[]
}

export interface SearchResultItem {
  id: number
  search_id: number
  result_data_json: PersonResultData
  match_score: number | null
  status: ResultStatus
  review_status: ReviewStatus
  created_at: string
  reviewed_at: string | null
}

export interface SearchResultsOut {
  id: number
  status: SearchStatusValue
  results: SearchResultItem[]
}

export interface SavedList {
  id: number
  name: string
  description: string | null
  created_at: string
}

export interface SavedListItem {
  id: number
  list_id: number
  search_result_id: number
  notes: string | null
  created_at: string
}

export interface SavedListItemDetail extends SavedListItem {
  result_data_json: PersonResultData
  result_status: ResultStatus
}
