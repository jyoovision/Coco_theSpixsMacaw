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
from google.cloud import storage
from google.cloud import speech
from server_utils import modules, process

# 초기 설정
load_dotenv()
vc = VC(Config())
sid_value = "yoojin.pth"
protect_value = 0.33
vc.get_vc(sid_value, protect_value, protect_value)

# GCS, STT 클라이언트 설정
google_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
storage_client = storage.Client()
speech_client = speech.SpeechClient()

# GCS 초기 설정
bucket = storage_client.bucket("audio_segments")
GCS_index_file_path = os.getenv("GCS_index")
GCS_index = modules.load_index(GCS_index_file_path)


# 언리얼 클라이언트와 웹소켓 서버 통신
async def echo(websocket, path):
    async for message in websocket:
        # 언리얼에서 메시지가 오면 출력
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
                splite_save_to_DB(websocket, audio)
            )
            await asyncio.gather(
                send_complete_task, extract_send_last_word_task, splite_save_to_DB_task
            )

        # idle 메시지가 오면 DB에서 랜덤으로 보내기
        elif message == "idle":
            await send_random_word_from_DB(websocket, bucket)
        # 다른 메시지가 들어오면 처리
        else:
            await websocket.send("To start RVC, send 'start RVC'.")


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
async def splite_save_to_DB(websocket, audio):
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
                bucket,
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


async def send_random_word_from_DB(websocket, bucket):
    blobs = list(bucket.list_blobs())  # 버킷의 모든 파일 목록을 가져옵니다.

    if not blobs:
        return None  # 파일이 없는 경우

    random_blob = random.choice(blobs)  # 랜덤으로 하나의 파일을 선택합니다.
    random_word_binary = random_blob.download_as_bytes()

    await websocket.send(b"BINARY" + random_word_binary)
    await websocket.send("Successfully sending random_word_binary data")


# 메인 함수
async def main():
    # 웹소켓 서버 시작, 서버가 시작될 때까지 기다리지 않고 바로 실행
    start_server = websockets.serve(echo, "localhost", 8765)
    server = await start_server  # 서버가 시작될 때까지 기다림

    # 서버가 시작된 것을 콘솔에 로깅
    print(f"Server started on {server.sockets[0].getsockname()}")
    await server.wait_closed()  # 서버가 닫힐 때까지 기다림


# 이벤트 루프를 실행하고 main 코루틴을 스케줄링
asyncio.run(main())
