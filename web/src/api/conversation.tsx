import request from "@/utils/request";

interface ConversationCreate {
    id: string;
    user_id?: number;
    knowledge_base_id?: number;
    title: string;
}

export function getConversationList() {
  return request({
    url: "/conversation/list/1",
    method: "get",
  });
}

export function getConversationDetail(id: number) {
  return request({
    url: `/conversation/detail/${id}`,
    method: "get",
  });
}

export function createConversation(data: ConversationCreate) {
  return request({
    url: "/conversation/create",
    method: "post",
    data,
  });
}