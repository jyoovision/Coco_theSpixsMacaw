import os
import struct
import asyncio
import websockets
from io import BytesIO
from simpleRVC import RVC
from dotenv import load_dotenv
from configs.config import Config
from pydub import AudioSegment, silence
from infer.modules.vc.modules import VC
from concurrent.futures import ThreadPoolExecutor
from google.cloud import storage

# from google.cloud import speech
# from google.cloud.speech import enums
# from google.cloud.speech import types
# from google.oauth2 import service_account

# Init/초기 설정
load_dotenv()
vc = VC(Config())
sid_value = "yoojin.pth"
protect_value = 0.33
vc.get_vc(sid_value, protect_value, protect_value)

google_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
storage_client = storage.Client()
bucket = storage_client.bucket("audio_segments")


# 언리얼 클라이언트와 웹소켓 서버 통신
async def echo(websocket, path):
    async for message in websocket:
        # 언리얼에서 start RVC 메시지가 오면 출력
        print(f"Received message from client: {message}")

        # start RVC 메시지가 들어오면 is_rvc_running을 검사하여 RVC 수행
        if message == "start RVC":
            send_start_task = asyncio.create_task(websocket.send("RVC start"))
            rvc_task = asyncio.create_task(RVC(vc))
            _, audio = await asyncio.gather(send_start_task, rvc_task)

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
    with BytesIO() as buffer:
        specific_part.export(buffer, format="wav")
        last_word_binary = buffer.getvalue()

    # 클라이언트로 last_word_binary 전송
    # verify_wav_format(last_word_binary)
    print(f"Sending audio binary of size: {len(last_word_binary)} bytes")
    await websocket.send(b"BINARY" + last_word_binary)
    await websocket.send("Successfully sending binary data")


# 세그먼트를 구글 클라우드 스토리지에 저장하는 함수
def save_segment_to_gcs(segment, segment_number):
    # 메모리 상의 BytesIO 스트림에 세그먼트 저장
    buffer = BytesIO()
    segment.export(buffer, format="wav")
    buffer.seek(0)  # 스트림을 처음으로 되돌림

    # 파일명 생성 (예: segment_1.wav)
    segment_name = f"segment_{segment_number}.wav"

    # 구글 클라우드 스토리지에 업로드
    blob = bucket.blob(segment_name)
    blob.upload_from_file(buffer, content_type="audio/wav")

    # 필요한 경우, 데이터베이스에 세그먼트 정보 저장
    # 예: database.save(segment_info)

    return f"{segment_name} uploaded to GCS"


# 오디오 세그먼트를 병렬로 저장하는 함수
async def splite_save_to_DB(websocket, audio):
    segments = silence.split_on_silence(
        audio, min_silence_len=200, silence_thresh=audio.dBFS - 25
    )

    loop = asyncio.get_running_loop()

    # ThreadPoolExecutor를 사용하여 세그먼트 저장 작업을 병렬로 수행
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, save_segment_to_gcs, segment, i)
            for i, segment in enumerate(segments)
        ]

        # 모든 작업이 완료될 때까지 기다림
        await asyncio.gather(*tasks)

    print("GCS save complete")
    await websocket.send("GCS save complete")


def verify_wav_format(audio_binary):
    # 헤더 읽기 (RIFF 헤더는 일반적으로 44바이트)
    header = audio_binary[:44]

    # RIFF 헤더 구조에 따라 데이터 구조화
    unpacked_data = struct.unpack("<4sL4s4sLHHLLHH4sL", header)

    # 헤더 정보 추출 및 출력
    (
        chunk_id,
        chunk_size,
        format,
        sub_chunk1_id,
        sub_chunk1_size,
        audio_format,
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        sub_chunk2_id,
        sub_chunk2_size,
    ) = unpacked_data

    print(f"ChunkID: {chunk_id.decode().strip()}")
    print(f"Chunk Size: {chunk_size}")
    print(f"Format: {format.decode().strip()}")
    print(f"Sub-chunk1 ID: {sub_chunk1_id.decode().strip()}")
    print(f"Sub-chunk1 Size: {sub_chunk1_size}")
    print(f"Audio Format: {audio_format}")
    print(f"Num Channels: {num_channels}")
    print(f"Sample Rate: {sample_rate}")
    print(f"Byte Rate: {byte_rate}")
    print(f"Block Align: {block_align}")
    print(f"Bits Per Sample: {bits_per_sample}")
    print(f"Sub-chunk2 ID: {sub_chunk2_id.decode().strip()}")
    print(f"Sub-chunk2 Size: {sub_chunk2_size}")


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
