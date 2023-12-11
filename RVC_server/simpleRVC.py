import os
import asyncio
import aiofiles
from io import BytesIO
from pydub import AudioSegment
from dotenv import load_dotenv
from configs.config import Config
from infer.modules.vc.modules import VC


async def process_audio(vc, inputoutput_directory):
    """
    음성 변환 모듈을 사용하여 오디오 처리
    """
    try:
        result = vc.vc_single(
            0,  # spk_item_value (서랍장의 인덱스)
            inputoutput_directory + "/input_audio.wav",  # input_audio0_value
            5.0,  # vc_transform0_value 피치 값 조절 (-12 ~ 12)
            None,  # f0_file_value
            "rmvpe",  # f0method0_value (방법 선택 "hurbert" 등이 있음)
            "",  # file_index1_value
            # "assets/model/yoojin.index",  # file_index2_value (특정 vc 모델의 인덱스 경로 지정)
            "assets/model/parrot.index",  # file_index2_value (특정 vc 모델의 인덱스 경로 지정)
            0.75,  # index_rate1_value
            3,  # filter_radius0_value
            0,  # resample_sr0_value
            0.25,  # rms_mix_rate0_value
            0.33,  # protect0_value
        )

        if isinstance(result, tuple) and result[1][0] is not None:
            message, audio_data_tuple = result
            return await save_return_inputoutput(
                message, audio_data_tuple, inputoutput_directory
            )
        else:
            print("An error occurred:", result[0])
            return None
    except Exception as e:
        print(f"Error in process_audio: {e}")
        return None


async def save_return_inputoutput(message, audio_data_tuple, inputoutput_directory):
    """
    변환된 오디오를 wav 파일로 저장 (비동기 방식)
    """
    # inputoutput_directory가 없으면 생성
    if not os.path.exists(inputoutput_directory):
        os.makedirs(inputoutput_directory)

    # 패스 지정
    audio_input_path = os.path.join(inputoutput_directory, "input_audio.wav")
    audio_output_path = os.path.join(inputoutput_directory, "output_audio.wav")
    text_output_path = os.path.join(inputoutput_directory, "output_text.txt")

    # 오디오를 AudioSegment 객체로 변환
    tgt_sr, audio_opt = audio_data_tuple

    input_audio = AudioSegment.from_wav(audio_input_path)
    input_audio = (
        input_audio.set_frame_rate(tgt_sr)
        .set_sample_width(audio_opt.dtype.itemsize)
        .set_channels(1)
    )

    output_audio = AudioSegment(
        audio_opt.tobytes(),
        frame_rate=tgt_sr,
        sample_width=audio_opt.dtype.itemsize,
        channels=1,
    )

    # 오디오를 메모리상에서 wav 바이너리 데이터로 변경하여 비동기적으로 저장
    buffer = BytesIO()
    output_audio.export(buffer, format="wav")
    audio_binary = buffer.getvalue()

    # 아웃풋 오디오를 파일에 비동기적으로 저장
    async with aiofiles.open(audio_output_path, "wb") as f:
        await f.write(audio_binary)

    # 텍스트 메시지를 파일에 비동기적으로 저장
    async with aiofiles.open(text_output_path, "w") as f:
        await f.write(message)

    return input_audio, output_audio


async def RVC(vc):
    """
    음성 변환 프로세스를 실행하는 메인 함수
    """
    inputoutput_directory = "../InputOutput"
    return await process_audio(vc, inputoutput_directory)


if __name__ == "__main__":
    # 환경 변수 로드
    load_dotenv()

    # VC 인스턴스 생성
    vc = VC(Config())
    # sid_value = "yoojin.pth"
    sid_value = "parrot.pth"
    protect_value = 0.33
    vc.get_vc(sid_value, protect_value, protect_value)

    # RVC 함수 비동기 실행
    asyncio.run(RVC(vc))
