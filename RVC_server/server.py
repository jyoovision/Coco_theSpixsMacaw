# import os
# import io
# import random
# import asyncio
# import websockets
# from simpleRVC import RVC
# from dotenv import load_dotenv
# from configs.config import Config
# from pydub import silence
# from infer.modules.vc.modules import VC
# from concurrent.futures import ThreadPoolExecutor
# from google.cloud import storage, speech, firestore
# from server_utils import modules, process
# from handtracker import HandTracker


# GCS_index = None


# # 클라이언트 딕셔너리 (tracker, unreal)
# connected_clients = {}


# # 언리얼 클라이언트와 웹소켓 서버 통신
# async def echo(websocket, path, vc, speech_client, bucket, GCS_index_file_path):
#     # 클라이언트 식별 메시지 수신 대기
#     client_type_message = await websocket.recv()
#     client_type = client_type_message.split(":")[1]
#     connected_clients[client_type] = websocket

#     try:
#         async for message in websocket:
#             # 메시지가 수신되면 출력
#             print(f"Received message from client: {message}")

#             # start RVC 메시지가 오면 is_rvc_running을 검사하여 RVC 수행
#             if message == "start RVC":
#                 # RVC start 보내기, RVC 함수 실행하기 작업 병렬 수행
#                 send_start_task = asyncio.create_task(websocket.send("RVC start"))
#                 rvc_task = asyncio.create_task(RVC(vc))
#                 _, audio = await asyncio.gather(send_start_task, rvc_task)

#                 # RVC complete 보내기, 마지막 단어를 추출하여 보내기, 각각의 단어 DB에 저장하기 병렬 수행
#                 send_complete_task = asyncio.create_task(websocket.send("RVC complete"))
#                 extract_send_last_word_task = asyncio.create_task(
#                     extract_send_last_word(websocket, audio)
#                 )
#                 splite_save_to_DB_task = asyncio.create_task(
#                     splite_save_to_DB(
#                         websocket,
#                         audio,
#                         bucket,
#                         speech_client,
#                         GCS_index_file_path,
#                     )
#                 )
#                 await asyncio.gather(
#                     send_complete_task,
#                     extract_send_last_word_task,
#                     splite_save_to_DB_task,
#                 )

#             # idle 메시지가 오면 DB에서 랜덤으로 보내기
#             elif message == "idle":
#                 await send_random_word_from_DB(websocket, bucket)

#             # Greeting Detected 메시지가 오면 언리얼로 메시지 전송
#             elif message == "Greeting Detected":
#                 if "unreal" in connected_clients:
#                     await connected_clients["unreal"].send(
#                         "Greeting Detected in HandTracker"
#                     )

#             # 다른 메시지가 들어오면 처리
#             else:
#                 await websocket.send("message is incorrect")

#     except websockets.exceptions.ConnectionClosed:
#         pass

#     finally:
#         # 연결이 끊어지면 클라이언트를 딕셔너리에서 제거
#         for key, value in connected_clients.items():
#             if value == websocket:
#                 del connected_clients[key]
#                 break


# # def get_random_audio_url_from_firestore(collection_name, document_id):
# #     """Firestore에서 특정 문서 ID의 audio_urls 배열에서 랜덤한 URL을 가져오는 함수."""
# #     db = firestore.Client.from_service_account_json(google_path)
# #     doc_ref = db.collection(collection_name).document(document_id)
# #     doc = doc_ref.get()

# #     if doc.exists:
# #         audio_urls = doc.to_dict().get("audio_urls", [])
# #         if audio_urls:
# #             return random.choice(audio_urls)
# #     return None


# # def download_audio_from_gcs(gcs_url, local_file_path, storage_client):
# #     """구글 클라우드 스토리지에서 오디오 파일을 다운로드하는 함수."""
# #     bucket_name = gcs_url.split("/")[2]
# #     blob_name = "/".join(gcs_url.split("/")[3:])

# #     bucket = storage_client.bucket(bucket_name)
# #     blob = bucket.blob(blob_name)

# #     blob.download_to_filename(local_file_path)
# #     print(f"Downloaded {gcs_url} to {local_file_path}")


# # # 함수 사용 예시
# # audio_url = get_random_audio_url_from_firestore("response_segments", "손인사")
# # if audio_url:
# #     download_audio_from_gcs(audio_url, "test.wav")  # 로컬 파일 경로 지정


# # 오디오의 마지막 단어를 추출하여 바이너리 데이터로 반환하고 이를 클라이언트로 전송
# async def extract_send_last_word(websocket, audio):
#     # 오디오 끝의 5초 또는 전체 오디오 샘플링
#     sample = audio[-5000:] if len(audio) > 5000 else audio

#     # 비조용 부분 찾기
#     nonsilent_chunks = silence.detect_nonsilent(
#         sample, min_silence_len=200, silence_thresh=sample.dBFS - 20
#     )

#     # 지정된 구간 추출
#     if nonsilent_chunks:
#         # 마지막 비조용 부분의 시작이 샘플의 시작과 같은 경우, 원래의 오디오 전체 반환
#         if nonsilent_chunks[-1][0] == 0:
#             specific_part = audio
#         else:
#             start_index = max(0, nonsilent_chunks[-1][0] - 100)  # 마지막 비조용 부분의 시작 -100ms
#             end_index = min(5000, nonsilent_chunks[-1][1] + 100)  # 마지막 비조용 부분의 끝 +100ms
#             specific_part = sample[start_index:end_index]
#     else:
#         # 비조용 부분이 없을 경우, None 반환
#         return None

#     # 추출된 구간을 바이너리 데이터로 변환
#     with io.BytesIO() as buffer:
#         specific_part.export(buffer, format="wav")
#         last_word_binary = buffer.getvalue()

#     # 클라이언트로 last_word_binary 전송
#     # modules.verify_wav_format(last_word_binary)
#     print(f"Sending audio binary of size: {len(last_word_binary)} bytes")
#     await websocket.send(b"BINARY" + last_word_binary)
#     await websocket.send("Successfully sending binary data")


# # 오디오 세그먼트를 병렬로 저장하는 함수
# async def splite_save_to_DB(
#     websocket, audio, bucket, speech_client, GCS_index_file_path
# ):
#     global GCS_index
#     segments = silence.split_on_silence(
#         audio, min_silence_len=200, silence_thresh=audio.dBFS - 25
#     )

#     loop = asyncio.get_running_loop()
#     # ThreadPoolExecutor를 사용하여 세그먼트 저장 작업을 병렬로 수행
#     with ThreadPoolExecutor() as executor:
#         tasks = [
#             loop.run_in_executor(
#                 executor,
#                 process.save_segment_to_gcs,
#                 bucket,
#                 speech_client,
#                 segment,
#                 GCS_index,
#             )
#             for i, segment in enumerate(segments)
#         ]

#         # 모든 작업이 완료될 때까지 기다림
#         await asyncio.gather(*tasks)
#         GCS_index += 1
#         modules.save_index(GCS_index_file_path, GCS_index)

#     print("GCS save complete")
#     await websocket.send("GCS save complete")


# # idle 상태일 때, 랜덤으로 오디오 재생
# async def send_random_word_from_DB(websocket, bucket):
#     blobs = list(bucket.list_blobs())  # 버킷의 모든 파일 목록을 가져옵니다.

#     if not blobs:
#         return None  # 파일이 없는 경우

#     random_blob = random.choice(blobs)  # 랜덤으로 하나의 파일을 선택합니다.
#     random_word_binary = random_blob.download_as_bytes()

#     await websocket.send(b"BINARY" + random_word_binary)
#     await websocket.send("Successfully sending random_word_binary data")


# # 초기 설정 함수
# async def init():
#     global GCS_index

#     load_dotenv()
#     vc = VC(Config())
#     sid_value = "parrot.pth"
#     protect_value = 0.33
#     vc.get_vc(sid_value, protect_value, protect_value)

#     google_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#     storage_client = storage.Client()
#     speech_client = speech.SpeechClient()
#     # storage_client = firestore.Client()

#     bucket = storage_client.bucket("input_segments")
#     GCS_index_file_path = os.getenv("GCS_index")
#     GCS_index = modules.load_index(GCS_index_file_path)

#     return vc, speech_client, bucket, GCS_index_file_path


# # 메인 함수
# async def main():
#     # 초기 설정
#     vc, speech_client, bucket, GCS_index_file_path = await init()

#     # 웹소켓 서버 설정
#     start_server = websockets.serve(
#         lambda ws, path: echo(ws, path, vc, speech_client, bucket, GCS_index_file_path),
#         "localhost",
#         8765,
#     )
#     server = await start_server

#     # 핸드 트래커 인스턴스 설정
#     loop = asyncio.get_event_loop()
#     hand_tracker = HandTracker(loop)
#     await hand_tracker.connect_websocket()
#     asyncio.get_event_loop().run_in_executor(None, hand_tracker.start)

#     # 서버 생성 메시지
#     print(f"Server started on {server.sockets[0].getsockname()}")
#     await server.wait_closed()


# # 이벤트 루프를 실행하고 main 코루틴을 스케줄링
# asyncio.run(main())


import os
import io
import random
import asyncio
import websockets
from simpleRVC import RVC
from dotenv import load_dotenv
from configs.config import Config
from pydub import silence
from infer.modules.vc.modules import VC
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage, speech, firestore
from server_utils import modules, process
from handtracker import HandTracker


GCS_index = None


# 클라이언트 딕셔너리 (tracker, unreal)
connected_clients = {}


# 언리얼 클라이언트와 웹소켓 서버 통신
async def echo(
    websocket,
    path,
    vc,
    speech_client,
    input_bucket,
    response_bucket,
    firestore_client,
    GCS_index_file_path,
):
    # 클라이언트 식별 메시지 수신 대기
    client_type_message = await websocket.recv()
    client_type = client_type_message.split(":")[1]
    connected_clients[client_type] = websocket

    try:
        async for message in websocket:
            # 메시지가 수신되면 출력
            print(f"Received message from client: {message}")

            # start RVC 메시지가 오면 is_rvc_running을 검사하여 RVC 수행
            if message == "start RVC":
                # RVC start 보내기, RVC 함수 실행하기 작업 병렬 수행
                send_start_task = asyncio.create_task(websocket.send("RVC start"))
                rvc_task = asyncio.create_task(RVC(vc))
                _, audio = await asyncio.gather(send_start_task, rvc_task)

                # RVC complete 보내기, 마지막 단어를 추출하여 보내기, 각각의 단어 DB에 저장하기 병렬 수행
                send_complete_task = asyncio.create_task(websocket.send("RVC complete"))
                extract_send_last_word_task = asyncio.create_task(
                    extract_send_last_word(websocket, audio)
                )
                splite_save_to_DB_task = asyncio.create_task(
                    splite_save_to_DB(
                        websocket,
                        audio,
                        input_bucket,
                        speech_client,
                        GCS_index_file_path,
                    )
                )
                await asyncio.gather(
                    send_complete_task,
                    extract_send_last_word_task,
                    splite_save_to_DB_task,
                )

            # idle 메시지가 오면 DB에서 랜덤으로 보내기
            elif message == "idle":
                await send_random_word_from_DB(websocket, input_bucket)

            # Greeting Detected 메시지가 오면 언리얼로 메시지 전송
            elif message == "Greeting Detected":
                if "unreal" in connected_clients:
                    send_detected_task = asyncio.create_task(
                        connected_clients["unreal"].send("Greeting Detected")
                    )
                    send_random_response_of_task = asyncio.create_task(
                        send_random_response_of(
                            connected_clients["unreal"],
                            firestore_client,
                            response_bucket,
                            "손인사",
                        )
                    )
                    await asyncio.gather(
                        send_detected_task, send_random_response_of_task
                    )

            # 다른 메시지가 들어오면 처리
            else:
                await websocket.send("message is incorrect")

    except websockets.exceptions.ConnectionClosed:
        pass

    finally:
        # 연결이 끊어지면 클라이언트를 딕셔너리에서 제거
        for key, value in connected_clients.items():
            if value == websocket:
                del connected_clients[key]
                break


# Firestore에서 문서 ID에 해당하는 오디오 URL 중 하나를 랜덤하게 선택하고, 해당 오디오를 GCS에서 바이너리 데이터로 가져와 클라이언트로 전송
async def send_random_response_of(
    websocket, firestore_client, response_bucket, document_id
):
    # Firestore에서 오디오 URL 배열 가져오기
    doc_ref = firestore_client.collection("response_segments").document(document_id)
    doc = doc_ref.get()

    # 문서 id 가 존재할 경우 랜덤으로 url 선택
    if doc.exists:
        audio_urls = doc.to_dict().get("audio_urls", [])
        if audio_urls:
            selected_url = random.choice(audio_urls)
            blob_name = "/".join(selected_url.split("/")[3:])
            blob = response_bucket.blob(blob_name)

            # GCS에서 오디오 바이너리 데이터 가져와서 전송
            # audio_data = await asyncio.to_thread(blob.download_as_bytes)  # 비동기 처리
            audio_data = blob.download_as_bytes()
            await websocket.send(b"BINARY" + audio_data)
            await websocket.send("Successfully sending random_response_binary data")
    return None


# async def send_random_response_of(
#     websocket, firestore_client, response_bucket, document_id
# ):
#     doc_ref = firestore_client.collection("response_segments").document(document_id)
#     doc = doc_ref.get()

#     if not doc.exists:
#         print(f"Document '{document_id}' does not exist in Firestore.")
#         return

#     audio_urls = doc.to_dict().get("audio_urls", [])
#     if not audio_urls:
#         print(f"No audio URLs found in document '{document_id}'.")
#         return

#     selected_url = random.choice(audio_urls)
#     print(f"Selected URL: {selected_url}")

#     blob_name = "/".join(selected_url.split("/")[3:])
#     print(f"Blob name: {blob_name}")

#     blob = response_bucket.blob(blob_name)
#     try:
#         audio_data = blob.download_as_bytes()
#         await websocket.send(b"BINARY" + audio_data)
#         await websocket.send("Successfully sending random_response_binary data")
#     except Exception as e:
#         print(f"Error downloading blob: {e}")


# 오디오의 마지막 단어를 추출하여 바이너리 데이터로 반환하고 이를 클라이언트로 전송
async def extract_send_last_word(websocket, audio):
    # 오디오 끝의 5초 또는 전체 오디오 샘플링
    sample = audio[-5000:] if len(audio) > 5000 else audio

    # 비조용 부분 찾기
    nonsilent_chunks = silence.detect_nonsilent(
        sample, min_silence_len=200, silence_thresh=sample.dBFS - 20
    )

    # 지정된 구간 추출
    if nonsilent_chunks:
        # 마지막 비조용 부분의 시작이 샘플의 시작과 같은 경우, 원래의 오디오 전체 반환
        if nonsilent_chunks[-1][0] == 0:
            specific_part = audio
        else:
            start_index = max(0, nonsilent_chunks[-1][0] - 100)  # 마지막 비조용 부분의 시작 -100ms
            end_index = min(5000, nonsilent_chunks[-1][1] + 100)  # 마지막 비조용 부분의 끝 +100ms
            specific_part = sample[start_index:end_index]
    else:
        # 비조용 부분이 없을 경우, None 반환
        return None

    # 추출된 구간을 바이너리 데이터로 변환
    with io.BytesIO() as buffer:
        specific_part.export(buffer, format="wav")
        last_word_binary = buffer.getvalue()

    # 클라이언트로 last_word_binary 전송
    # modules.verify_wav_format(last_word_binary)
    print(f"Sending audio binary of size: {len(last_word_binary)} bytes")
    await websocket.send(b"BINARY" + last_word_binary)
    await websocket.send("Successfully sending binary data")


# 오디오 세그먼트를 병렬로 저장하는 함수
async def splite_save_to_DB(
    websocket, audio, input_bucket, speech_client, GCS_index_file_path
):
    global GCS_index
    segments = silence.split_on_silence(
        audio, min_silence_len=200, silence_thresh=audio.dBFS - 25
    )

    loop = asyncio.get_running_loop()
    # ThreadPoolExecutor를 사용하여 세그먼트 저장 작업을 병렬로 수행
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                process.save_segment_to_gcs,
                input_bucket,
                speech_client,
                segment,
                GCS_index,
            )
            for i, segment in enumerate(segments)
        ]

        # 모든 작업이 완료될 때까지 기다림
        await asyncio.gather(*tasks)
        GCS_index += 1
        modules.save_index(GCS_index_file_path, GCS_index)

    print("GCS save complete")
    await websocket.send("GCS save complete")


# idle 상태일 때, 랜덤으로 오디오 재생
async def send_random_word_from_DB(websocket, input_bucket):
    blobs = list(input_bucket.list_blobs())  # 버킷의 모든 파일 목록을 가져옵니다.

    if not blobs:
        return None  # 파일이 없는 경우

    random_blob = random.choice(blobs)  # 랜덤으로 하나의 파일을 선택합니다.
    random_word_binary = random_blob.download_as_bytes()

    await websocket.send(b"BINARY" + random_word_binary)
    await websocket.send("Successfully sending random_word_binary data")


# 초기 설정 함수
async def init():
    global GCS_index

    load_dotenv()
    vc = VC(Config())
    sid_value = "parrot.pth"
    protect_value = 0.33
    vc.get_vc(sid_value, protect_value, protect_value)

    google_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    storage_client = storage.Client()
    speech_client = speech.SpeechClient()
    firestore_client = firestore.Client()

    input_bucket = storage_client.bucket("input_segments")
    response_bucket = storage_client.bucket("response_segments")
    GCS_index_file_path = os.getenv("GCS_index")
    GCS_index = modules.load_index(GCS_index_file_path)

    return (
        vc,
        speech_client,
        input_bucket,
        response_bucket,
        firestore_client,
        GCS_index_file_path,
    )


# 메인 함수
async def main():
    # 초기 설정
    (
        vc,
        speech_client,
        input_bucket,
        response_bucket,
        firestore_client,
        GCS_index_file_path,
    ) = await init()

    # 웹소켓 서버 설정
    start_server = websockets.serve(
        lambda ws, path: echo(
            ws,
            path,
            vc,
            speech_client,
            input_bucket,
            response_bucket,
            firestore_client,
            GCS_index_file_path,
        ),
        "localhost",
        8765,
    )
    server = await start_server

    # 핸드 트래커 인스턴스 설정
    loop = asyncio.get_event_loop()
    hand_tracker = HandTracker(loop)
    await hand_tracker.connect_websocket()
    asyncio.get_event_loop().run_in_executor(None, hand_tracker.start)

    # 서버 생성 메시지
    print(f"Server started on {server.sockets[0].getsockname()}")
    await server.wait_closed()


# 이벤트 루프를 실행하고 main 코루틴을 스케줄링
asyncio.run(main())
