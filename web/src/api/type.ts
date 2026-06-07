export interface HTTPResponse<T = unknown> {
  code: number
  message: string
  data: T
  success: boolean
}

export interface HTTPResponsePage<T = unknown> extends HTTPResponse<T> {
  total: number
  current: number
  size: number
}
