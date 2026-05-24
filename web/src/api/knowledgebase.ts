import request from '@/utils/request'
import type { KnowledgeBaseCreate, KnowledgeBaseUpdate } from '@/pages/knowledge_base/type'

/** GET /api/v1/knowledge_base/listAll */
export function listAllKB() {
  return request({
    url: '/knowledge_base/listAll',
    method: 'get',
  })
}

/** POST /api/v1/knowledge_base/create  →  returns new KB id */
export function createKB(data: KnowledgeBaseCreate) {
  return request({
    url: '/knowledge_base/create',
    method: 'post',
    data,
  })
}

/** PATCH /api/v1/knowledge_base/update/:id  →  returns KB id */
export function updateKB(id: number, data: KnowledgeBaseUpdate) {
  return request({
    url: `/knowledge_base/update/${id}`,
    method: 'patch',
    data,
  })
}

/** DELETE /api/v1/knowledge_base/delete/:id  →  returns KB id */
export function deleteKB(id: number) {
  return request({
    url: `/knowledge_base/delete/${id}`,
    method: 'delete',
  })
}
