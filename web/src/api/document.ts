import request from '@/utils/request'
import type { DocumentFilter } from '@/pages/knowledge_base/type'

/**
 * GET /api/v1/document/listByPage/:current/:size
 * Query params: DocumentFilter (knowledge_base_id required)
 */
export function listDocsByPage(current: number, size: number, filter: DocumentFilter) {
  return request({
    url: `/document/listByPage/${current}/${size}`,
    method: 'get',
    params: filter,
  })
}

/** DELETE /api/v1/document/delete/:id  →  returns document id */
export function deleteDocument(id: number) {
  return request({
    url: `/document/delete/${id}`,
    method: 'delete',
  })
}

/**
 * POST /api/v1/file/upload/:knowledge_base_id
 * Body: multipart/form-data — file, file_name, part_type?, standard_no?
 * Response data: FileUploadResult { file_exist, doc_exist, data: RawFile }
 */
export function uploadFile(kbId: number, formData: FormData) {
  return request({
    url: `/file/upload/${kbId}`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
