export interface NewsItem {
  title: string
  content: string
  source: string
  published_at: string
  url: string
}

export interface NewsResponse {
  status: string
  total: number
  data: NewsItem[]
}
