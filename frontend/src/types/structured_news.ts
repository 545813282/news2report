export interface Source {
  name: string
  name_en: string | null
  type: string
  url: string
}

export interface AIOpinion {
  viewpoint: string
  significance: string
  impact_direction: string
}

export interface Entity {
  name: string
  type: string
}

export interface Sentiment {
  overall: string
  score: number
  reason: string
}

export interface Relation {
  subject: string
  predicate: string
  object: string
}

export interface ProcessingMeta {
  extracted_at: string
  model: string
  batch_id: string
  status: string
  retry_count: number
  error_msg: string | null
}

export interface StructuredNewsItem {
  id: string
  title: string
  title_en: string | null
  category: string
  tags: string[]
  source: Source
  author: string | null
  publish_time: string
  language: string
  original_text: string
  translated_text: string | null
  original_summary: string | null
  ai_summary: string
  ai_opinion: AIOpinion
  entities: Entity[]
  technologies: string[]
  event_type: string
  sentiment: Sentiment
  key_points: string[]
  relations: Relation[]
  processing: ProcessingMeta
}

export interface StructuredNewsResponse {
  status: string
  total: number
  data: StructuredNewsItem[]
}
