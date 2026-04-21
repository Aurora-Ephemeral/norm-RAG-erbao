from app.core.celery import celery_app

@celery_app.task(bind=True, name="split_file_to_chunk")
def split_file_to_chunk(self, file_id: str, document_id: str):
    pass