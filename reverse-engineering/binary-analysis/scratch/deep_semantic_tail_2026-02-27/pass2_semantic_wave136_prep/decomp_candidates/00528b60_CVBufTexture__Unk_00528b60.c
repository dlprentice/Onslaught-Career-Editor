/* address: 0x00528b60 */
/* name: CVBufTexture__Unk_00528b60 */
/* signature: int __stdcall CVBufTexture__Unk_00528b60(void * param_1) */


int CVBufTexture__Unk_00528b60(void *param_1)

{
  while( true ) {
    WaitForSingleObject(*(HANDLE *)((int)param_1 + 0xc),0xffffffff);
    if (*(char *)((int)param_1 + 0x14) != '\0') break;
    WaitForSingleObject(*(HANDLE *)((int)param_1 + 8),0xffffffff);
    (*(code *)**(undefined4 **)param_1)();
    *(undefined1 *)((int)param_1 + 0x15) = 0;
    ReleaseMutex(*(HANDLE *)((int)param_1 + 8));
    SetEvent(*(HANDLE *)((int)param_1 + 0x10));
  }
  return 0;
}
