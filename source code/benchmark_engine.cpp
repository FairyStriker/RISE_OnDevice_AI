#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip> // for setprecision
#include <opencv2/opencv.hpp>
#include <NvInfer.h>
#include <cuda_runtime_api.h>

// --- ⚙️ 사용자 설정 (Python 코드 설정 반영) ---
const std::string MODEL_PATH = "/home/laheckaf/ssj/models/yolo_n.engine";
const std::string FPS_IMAGE_PATH = "test_fps.jpg"; // 없으면 bus.jpg 사용 권장
const std::string RESULTS_FILE_PATH = "benchmark_results_jetson_cpp.json"; // 결과 저장 파일명

const int INPUT_W = 640;
const int INPUT_H = 640;
const int WARMUP_RUNS = 10;
const int FPS_ITERATIONS = 100;
// ----------------------------------------------

// TensorRT Logger (필수)
class Logger : public nvinfer1::ILogger {
    void log(Severity severity, const char* msg) noexcept override {
        if (severity <= Severity::kWARNING) std::cout << "[TRT] " << msg << std::endl;
    }
} gLogger;

// JSON 저장을 위한 간단한 헬퍼 함수
void save_results_json(double fps, double avg_ms, const std::string& platform_name) {
    std::ofstream jsonFile(RESULTS_FILE_PATH);
    if (jsonFile.is_open()) {
        jsonFile << "{\n";
        jsonFile << "    \"platform\": \"" << platform_name << "\",\n";
        jsonFile << "    \"model\": \"" << MODEL_PATH << "\",\n";
        jsonFile << "    \"img_size\": " << INPUT_W << ",\n";
        jsonFile << "    \"FPS\": " << std::fixed << std::setprecision(2) << fps << ",\n";
        jsonFile << "    \"Avg_Inference_ms\": " << avg_ms << "\n";
        jsonFile << "}";
        jsonFile.close();
        std::cout << "\n--- 💾 결과 저장 ---" << std::endl;
        std::cout << "파일 경로: " << RESULTS_FILE_PATH << std::endl;
        std::cout << "결과가 JSON 파일로 성공적으로 저장되었습니다." << std::endl;
    } else {
        std::cerr << "‼️ 결과 저장 중 오류 발생: 파일을 열 수 없습니다." << std::endl;
    }
}

int main() {
    std::cout << "--- 🚀 Jetson C++ FPS 벤치마크 시작 ---" << std::endl;

    // 1. 모델 로드
    std::cout << "\n[1/3] 모델 로드 중: " << MODEL_PATH << std::endl;
    std::ifstream file(MODEL_PATH, std::ios::binary);
    if (!file.good()) {
        std::cerr << "오류: 모델 파일을 찾을 수 없습니다!" << std::endl;
        return -1;
    }
    file.seekg(0, file.end);
    size_t size = file.tellg();
    file.seekg(0, file.beg);
    std::vector<char> engineData(size);
    file.read(engineData.data(), size);
    file.close();

    nvinfer1::IRuntime* runtime = nvinfer1::createInferRuntime(gLogger);
    nvinfer1::ICudaEngine* engine = runtime->deserializeCudaEngine(engineData.data(), size);
    nvinfer1::IExecutionContext* context = engine->createExecutionContext();

    if (!context) {
        std::cerr << "오류: 실행 컨텍스트 생성 실패!" << std::endl;
        return -1;
    }
    std::cout << "모델 로드 완료." << std::endl;

    // 2. 메모리 할당
    void* buffers[2];
    size_t inputSize = 1 * 3 * INPUT_H * INPUT_W * sizeof(float);
    size_t outputSize = 1 * 84 * 8400 * sizeof(float); // YOLOv8 Output Size

    cudaMalloc(&buffers[0], inputSize);
    cudaMalloc(&buffers[1], outputSize);
    cudaStream_t stream;
    cudaStreamCreate(&stream);

    // 3. 이미지 로드 및 전처리
    std::cout << "\n[2/3] FPS 측정 준비 (이미지: " << FPS_IMAGE_PATH << ")..." << std::endl;
    cv::Mat img = cv::imread(FPS_IMAGE_PATH);
    if (img.empty()) {
        std::cout << "경고: 이미지를 찾을 수 없습니다. 검정색 빈 이미지로 대체합니다." << std::endl;
        img = cv::Mat::zeros(INPUT_H, INPUT_W, CV_8UC3);
    }

    cv::Mat resized;
    cv::resize(img, resized, cv::Size(INPUT_W, INPUT_H));
    cv::cvtColor(resized, resized, cv::COLOR_BGR2RGB);
    resized.convertTo(resized, CV_32FC3, 1.0 / 255.0); // 0~1 정규화

    // HWC -> CHW 변환 (TensorRT 포맷)
    std::vector<float> inputData(1 * 3 * INPUT_H * INPUT_W);
    std::vector<cv::Mat> chw_channels;
    for (int i = 0; i < 3; ++i) {
        chw_channels.push_back(cv::Mat(INPUT_H, INPUT_W, CV_32FC1, inputData.data() + i * INPUT_H * INPUT_W));
    }
    cv::split(resized, chw_channels);

    // 데이터 GPU 복사
    cudaMemcpyAsync(buffers[0], inputData.data(), inputSize, cudaMemcpyHostToDevice, stream);

    // 4. FPS 측정
    std::cout << "\n[3/3] FPS 측정 시작..." << std::endl;
    
    // 워밍업
    std::cout << "워밍업 실행 (" << WARMUP_RUNS << "회)..." << std::endl;
    for (int i = 0; i < WARMUP_RUNS; i++) {
        context->enqueueV2(buffers, stream, nullptr);
    }
    cudaStreamSynchronize(stream);

    // 실제 측정
    std::cout << "성능 측정 실행 (" << FPS_ITERATIONS << "회)..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();

    for (int i = 0; i < FPS_ITERATIONS; i++) {
        context->enqueueV2(buffers, stream, nullptr);
    }
    cudaStreamSynchronize(stream);
    auto end = std::chrono::high_resolution_clock::now();

    // 결과 계산
    double total_time_ms = std::chrono::duration<double, std::milli>(end - start).count();
    double avg_time_ms = total_time_ms / FPS_ITERATIONS;
    double fps = 1000.0 / avg_time_ms;

    // 콘솔 출력
    std::cout << "FPS 측정 완료: 평균 " << std::fixed << std::setprecision(2) << fps 
              << " FPS (" << avg_time_ms << " ms)" << std::endl;

    // 5. 결과 파일 저장 (JSON)
    save_results_json(fps, avg_time_ms, "Jetson (C++ / TensorRT)");

    std::cout << "\n--- Jetson 최종 요약 ---" << std::endl;
    std::cout << "{" << std::endl;
    std::cout << "  \"platform\": \"Jetson (C++ / TensorRT)\"," << std::endl;
    std::cout << "  \"FPS\": " << fps << "," << std::endl;
    std::cout << "  \"Avg_ms\": " << avg_time_ms << std::endl;
    std::cout << "}" << std::endl;
    std::cout << "-----------------------" << std::endl;

    // 리소스 해제
    cudaStreamDestroy(stream);
    cudaFree(buffers[0]);
    cudaFree(buffers[1]);
    delete context;
    delete engine;
    delete runtime;

    return 0;
}