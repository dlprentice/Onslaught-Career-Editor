/* address: 0x00565e8d */
/* name: CTexture__Helper_00565e8d */
/* signature: void __cdecl CTexture__Helper_00565e8d(int param_1, int param_2) */


void __cdecl CTexture__Helper_00565e8d(int param_1,int param_2)

{
  CRT__StrCpyAligned((void *)param_1,(void *)param_2);
  if (*(char *)(param_2 + 0x40) != '\0') {
    CTexture__Helper_00565d9c(param_1,2);
  }
  if (*(char *)(param_2 + 0x80) != '\0') {
    CTexture__Helper_00565d9c(param_1,2);
  }
  return;
}
