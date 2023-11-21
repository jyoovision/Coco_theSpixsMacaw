import struct


# GCS_index load
def load_index(GCS_index_file_path):
    try:
        with open(GCS_index_file_path, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0


# GCS_index save
def save_index(GCS_index_file_path, index):
    with open(GCS_index_file_path, "w") as file:
        file.write(str(index))


# print audio format
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

    return
