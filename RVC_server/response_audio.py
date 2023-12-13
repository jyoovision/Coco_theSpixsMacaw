import os
from dotenv import load_dotenv
from google.cloud import firestore, storage

load_dotenv()
google_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")


# GCS 업로드 함수 (오디오 저장)
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Google Cloud Storage에 파일을 업로드하고, 파일의 GCS URL을 반환하는 함수."""

    storage_client = storage.Client.from_service_account_json(google_path)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    return f"gs://{bucket_name}/{destination_blob_name}"


# Firestore 업로드 함수 (URL 저장)
def add_audio_url_to_firestore(collection_name, document_id, audio_url):
    """Firebase Firestore에 오디오 파일의 URL을 저장하는 함수."""

    db = firestore.Client.from_service_account_json(google_path)
    doc_ref = db.collection(collection_name).document(document_id)

    # 문서 존재 여부 확인 후 새로운 문서 생성 또는 업데이트
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"audio_urls": firestore.ArrayUnion([audio_url])})
    else:
        doc_ref.set({"audio_urls": [audio_url]})


# 함수 실행 예시
gcs_url = upload_to_gcs(
    bucket_name="response_segments",
    source_file_name="../InputOutput/output_audio.wav",
    destination_blob_name="잘모르겠어",
)

add_audio_url_to_firestore(
    collection_name="response_segments", document_id="신기", audio_url=gcs_url
)
