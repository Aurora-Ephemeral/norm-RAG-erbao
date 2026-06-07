import request from '@/utils/request'
import type { Document, DocumentFilter, FileUploadResult } from '@/pages/knowledge_base/type'
import type { HTTPResponse, HTTPResponsePage } from '@/api/type'

/** GET /api/v1/document/listByPage/:current/:size */
export function listDocsByPage(
  current: number,
  size: number,
  filter: DocumentFilter,
): Promise<HTTPResponsePage<Document[]>> {
  return request({ url: `/document/listByPage/${current}/${size}`, method: 'get', params: filter })
}

/** DELETE /api/v1/document/delete/:id  →  returns document id */
export function deleteDocument(id: number): Promise<HTTPResponse<number>> {
  return request({ url: `/document/delete/${id}`, method: 'delete' })
}

/**
 * POST /api/v1/file/upload/:knowledge_base_id
 * Body: multipart/form-data — file, file_name, part_type?, standard_no?
 */
export function uploadFile(kbId: number, formData: FormData): Promise<HTTPResponse<FileUploadResult>> {
  return request({
    url: `/file/upload/${kbId}`,
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
