# CMakeList.txt: MTd에 대한 CMake 프로젝트, 여기에 소스를 포함하고
# 프로젝트 특정 논리를 정의합니다.
# 
project ("rtspReceiver")
cmake_minimum_required (VERSION 3.8)
# 이 프로젝트의 실행 파일에 소스를 추가합니다.
# TODO: 필요한 경우 테스트를 추가하고 대상을 설치합니다.
add_definitions("-Wall -std=c++17")

if(${CMAKE_BUILD_TYPE} MATCHES Debug)
   set(BuildType "Debug")
   message(STATUS "Debug build")
else()
   message(STATUS "Release build")
   set(BuildType "Release")
   add_definitions(-DNDEBUG)
endif()

add_compile_options(-fPIC)

# add_executable (rtspReceiver  
# 	"main.c"
# 	"wrappingRtsp.h"
# 	)
add_library (rtspReceiver  
	SHARED
	"wrappingRtsp.h"
	"wrappingRtsp.cpp"
	)
	
target_include_directories(rtspReceiver 
	PUBLIC 
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP 
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/RTSPClient/RTSP
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/RTSPClient/RTCP
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/Sock
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/OS_Common
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/RTSPClient/RTP
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/Common
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/Util
)

set_target_properties(rtspReceiver PROPERTIES 
	RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/linux/${CMAKE_BUILD_TYPE})

target_link_directories(rtspReceiver 
	PUBLIC 
	${CMAKE_CURRENT_SOURCE_DIR}/RTSP/objs	
)

MESSAGE(${CMAKE_SOURCE_DIR}/include/iperf/include)
target_link_libraries(rtspReceiver
	PUBLIC 
	libRTSPClient.so
	pthread
)