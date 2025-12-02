from ultralytics import YOLO
import sys

# 모델 선택 로직
mod = input("1. n모델 \n2. s모델 \n3. m모델 \n4. l모델\n번호를 입력하시오 : ")

model_paths = {
    "1": "/home/laheckaf/ssj/models/yolo_n.engine",
    "2": "/home/laheckaf/ssj/models/yolo_s.engine",
    "3": "/home/laheckaf/ssj/models/yolo_m.engine",
    "4": "/home/laheckaf/ssj/models/yolo_l.engine"
}

if mod not in model_paths:
    print("잘못된 번호입니다.")
    sys.exit() # 프로그램 종료

# 모델 로드
print(f"모델 로드 중: {model_paths[mod]}")
model = YOLO(model_paths[mod])

# 처리할 동영상 리스트 (여기에 파일만 추가하면 계속 늘릴 수 있음)
video_files = [
    "/home/laheckaf/dataset/2025-07-05 11_59_58 해운대파라다이스호텔앞_고정형#3.mp4",
    "/home/laheckaf/dataset/2025-07-05 11_59_59 해운대파라다이스호텔앞_고정형#1.mp4",
    "/home/laheckaf/dataset/2025-08-24 22_14_57 해운대사업소옥상_회전형_우측.mp4",
    "/home/laheckaf/dataset/2025-08-25 01_44_58 해운대사업소옥상_고정형#3.mp4"
]

# 반복문을 통한 일괄 처리
for i, video_path in enumerate(video_files):
    print(f"\n[{i+1}/{len(video_files)}] 처리 시작: {video_path}")
    
    # save=True 시 결과 파일 이름이 겹치지 않게 project/name 옵션을 쓸 수도 있지만, 
    # 기본적으로 YOLO가 predict/exp, exp2... 식으로 폴더를 나눠서 저장해줍니다.
    results_generator = model.predict(source=video_path, stream=True, show=False, save=True)
    
    # 실제 처리 루프 (이게 돌아가야 처리가 됨)
    for result in results_generator:
        pass # 현재는 단순 저장용이므로 pass
        
    print(f"[{i+1}번 영상] 처리 완료.")

print("\n모든 동영상 처리가 끝났습니다.")