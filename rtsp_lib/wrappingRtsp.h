#include "RTSPClient.h" 
#include "RTSPCommonEnv.h"
#include <string>

extern "C" {
    int sum(int a, int b )
    {
        printf("a : %d\n", a);
        printf("b : %d\n", b);
        return a+ b;
    }

    RTSPClient* RtspClient_new()
    { 
        return new RTSPClient(); 
    }

    bool OpenURL(RTSPClient* rtsp, char* strUrl, int nTimeout)
    {
        printf("OpenURL\n");
        printf("1. openurl %s, %d\n", strUrl, nTimeout);
        bool bRet = false;
        if(rtsp != nullptr)
        {
            printf("success openurl %s, %d\n", strUrl, nTimeout);
            bRet = rtsp->openURL(strUrl, 1, nTimeout);
        }
        else
            printf("oepn fail !\n");

        return bRet;
    }

    bool PlayUrl(FrameHandlerFunc func, RTSPClient* rtsp)
    {
        bool bRet = false;
        if(rtsp != nullptr)
        {
            printf("PlayUrl 1\n");
            bRet = rtsp->playURL(func, rtsp, NULL, NULL);
            printf("PlayUrl 1, %d \n", bRet);
        }
        else
            printf("PlayUrl 2\n");

        return bRet;
    }
}