/* address: 0x0057c5b2 */
/* name: CDXTexture__FlushStreamWriteBufferTail */
/* signature: void __stdcall CDXTexture__FlushStreamWriteBufferTail(int param_1) */


void CDXTexture__FlushStreamWriteBufferTail(int param_1)

{
  int iVar1;
  DWORD nNumberOfBytesToWrite;

  iVar1 = *(int *)(param_1 + 0x18);
  nNumberOfBytesToWrite = 0x1000 - *(int *)(iVar1 + 4);
  if (nNumberOfBytesToWrite != 0) {
    WriteFile(*(HANDLE *)(iVar1 + 0x14),*(LPCVOID *)(iVar1 + 0x18),nNumberOfBytesToWrite,
              (LPDWORD)&param_1,(LPOVERLAPPED)0x0);
  }
  return;
}
