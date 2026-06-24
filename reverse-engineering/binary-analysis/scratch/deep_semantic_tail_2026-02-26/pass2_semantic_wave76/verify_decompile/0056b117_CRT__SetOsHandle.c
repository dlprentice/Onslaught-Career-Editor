/* address: 0x0056b117 */
/* name: CRT__SetOsHandle */
/* signature: int __cdecl CRT__SetOsHandle(uint param_1, int param_2) */


int __cdecl CRT__SetOsHandle(uint param_1,int param_2)

{
  undefined4 *puVar1;
  int iVar2;
  DWORD nStdHandle;

  if (param_1 < DAT_009d33a0) {
    iVar2 = (param_1 & 0x1f) * 0x24;
    if (*(int *)((&DAT_009d32a0)[(int)param_1 >> 5] + iVar2) == -1) {
      if (DAT_00653644 == 1) {
        if (param_1 == 0) {
          nStdHandle = 0xfffffff6;
        }
        else if (param_1 == 1) {
          nStdHandle = 0xfffffff5;
        }
        else {
          if (param_1 != 2) goto LAB_0056b170;
          nStdHandle = 0xfffffff4;
        }
        SetStdHandle(nStdHandle,(HANDLE)param_2);
      }
LAB_0056b170:
      *(int *)((&DAT_009d32a0)[(int)param_1 >> 5] + iVar2) = param_2;
      return 0;
    }
  }
  puVar1 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar1 = 9;
  puVar1 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar1 = 0;
  return -1;
}
