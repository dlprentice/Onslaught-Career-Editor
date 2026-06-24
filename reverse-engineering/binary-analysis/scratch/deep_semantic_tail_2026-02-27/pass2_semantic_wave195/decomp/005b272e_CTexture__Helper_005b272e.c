/* address: 0x005b272e */
/* name: CTexture__Helper_005b272e */
/* signature: void __stdcall CTexture__Helper_005b272e(int param_1, int param_2, int param_3) */


void CTexture__Helper_005b272e(int param_1,int param_2,int param_3)

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
