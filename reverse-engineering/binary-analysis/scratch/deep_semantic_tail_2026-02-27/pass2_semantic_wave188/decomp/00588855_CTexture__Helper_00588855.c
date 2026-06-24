/* address: 0x00588855 */
/* name: CTexture__Helper_00588855 */
/* signature: int __fastcall CTexture__Helper_00588855(void * param_1) */


int __fastcall CTexture__Helper_00588855(void *param_1)

{
  if (*(LPCVOID *)((int)param_1 + 8) != (LPCVOID)0x0) {
    UnmapViewOfFile(*(LPCVOID *)((int)param_1 + 8));
    *(undefined4 *)((int)param_1 + 8) = 0;
    *(undefined4 *)((int)param_1 + 0xc) = 0;
  }
  if (*(HANDLE *)((int)param_1 + 4) != (HANDLE)0xffffffff) {
    CloseHandle(*(HANDLE *)((int)param_1 + 4));
    *(undefined4 *)((int)param_1 + 4) = 0xffffffff;
  }
  if (*(HANDLE *)param_1 != (HANDLE)0xffffffff) {
    CloseHandle(*(HANDLE *)param_1);
    *(undefined4 *)param_1 = 0xffffffff;
  }
  return 0;
}
