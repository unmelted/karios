
#include <cstdio>
#include <string.h>
#include <thread>

#include "RTSPClient.h"
#include "RTSPCommonEnv.h"

static void frameHandlerFunc(void* arg, RTP_FRAME_TYPE frame_type, int64_t timestamp, unsigned char* buf, int len, long long nReplayFramNum)
{
    printf("Frame Num [%lld]\n ", nReplayFramNum);
}

int main()
{
    char pStr[100];
    RTSPClient* m_rtspClient;
    m_rtspClient = new RTSPClient();
	std::string mSrcUrl = "rtsp://192.168.18.134:8554/main";
	//m_rtspClient->m_pParent = this;  <- frameHandlerFunc 의 첫번째 인자인 arg로 넘오오게 됩니다. 

	int nRtspTimeOUt = 20;
	if (m_rtspClient->openURL(mSrcUrl.c_str(), 1, nRtspTimeOUt) == 0)
	{
		if (m_rtspClient->playURL((FrameHandlerFunc)frameHandlerFunc, m_rtspClient, NULL, NULL) == 0)
		{
            printf("connect");
		}
		else
		{
			printf("connect play error");
		}
			
	}
	else
	{
		printf("connect open error");
	}

    while (1)
    {
		memset(pStr, 0, 100);

		scanf("%10s", pStr);
		//while (getchar() != '\n');
        if (strcmp(pStr, "exit") == 0) 
        {
            //socketmgr.Close();
            break;
        }
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    m_rtspClient->closeURL();
    return 0;
}
