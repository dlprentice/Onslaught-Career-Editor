/* address: 0x0056b193 */
/* name: CRT__FreeOsHandle */
/* signature: int __cdecl CRT__FreeOsHandle(uint param_1) */


int __cdecl CRT__FreeOsHandle(uint param_1)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  DWORD nStdHandle;

  if (param_1 < DAT_009d33a0) {
    iVar3 = (param_1 & 0x1f) * 0x24;
    piVar1 = (int *)((&DAT_009d32a0)[(int)param_1 >> 5] + iVar3);
    if (((*(byte *)(piVar1 + 1) & 1) != 0) && (*piVar1 != -1)) {
      if (DAT_00653644 == 1) {
        if (param_1 == 0) {
          nStdHandle = 0xfffffff6;
        }
        else if (param_1 == 1) {
          nStdHandle = 0xfffffff5;
        }
        else {
          if (param_1 != 2) goto LAB_0056b1ef;
          nStdHandle = 0xfffffff4;
        }
        SetStdHandle(nStdHandle,(HANDLE)0x0);
      }
LAB_0056b1ef:
      *(undefined4 *)((&DAT_009d32a0)[(int)param_1 >> 5] + iVar3) = 0xffffffff;
      return 0;
    }
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 9;
  puVar2 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar2 = 0;
  return -1;
}
