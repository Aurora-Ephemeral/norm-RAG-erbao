import request from '@/utils/request'
import type { KnowledgeBase, KnowledgeBaseCreate, KnowledgeBaseUpdate } from '@/pages/knowledge_base/type'
import type { HTTPResponse } from '@/api/type'

/** GET /api/v1/knowledge_base/listAll */
export function listAllKB(): Promise<HTTPResponse<KnowledgeBase[]>> {
  return request({ url: '/knowledge_base/listAll', method: 'get' })
}

/** POST /api/v1/knowledge_base/create  →  returns new KB id */
export function createKB(data: KnowledgeBaseCreate): Promise<HTTPResponse<number>> {
  return request({ url: '/knowledge_base/create', method: 'post', data })
}

/** PATCH /api/v1/knowledge_base/update/:id  →  returns KB id */
export function updateKB(id: number, data: KnowledgeBaseUpdate): Promise<HTTPResponse<number>> {
  return request({ url: `/knowledge_base/update/${id}`, method: 'patch', data })
}

/** DELETE /api/v1/knowledge_base/delete/:id  →  returns KB id */
export function deleteKB(id: number): Promise<HTTPResponse<number>> {
  return request({ url: `/knowledge_base/delete/${id}`, method: 'delete' })
}
