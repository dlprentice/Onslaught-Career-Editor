/* address: 0x005b272e */
/* name: CDXTexture__InflateDefaultAllocCallback */
/* signature: void __stdcall CDXTexture__InflateDefaultAllocCallback(int param_1, int param_2, int param_3) */


void CDXTexture__InflateDefaultAllocCallback(int param_1,int param_2,int param_3)

{
  SIZE_T dwBytes;
  HANDLE hHeap;
  DWORD dwFlags;

  dwBytes = param_2 * param_3;
  dwFlags = 8;
  hHeap = GetProcessHeap();
  HeapAlloc(hHeap,dwFlags,dwBytes);
  return;
}
