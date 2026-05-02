from app.domain.file.task import processing_document_task, embed_document_task

if __name__ == "__main__":
    # processing_document_task.apply(args=["4", "5"])
    embed_document_task.apply(args=["5"])