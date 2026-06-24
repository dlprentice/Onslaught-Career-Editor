/* address: 0x00567505 */
/* name: CTexture__Helper_00567505 */
/* signature: int __cdecl CTexture__Helper_00567505(uint param_1, int param_2, int param_3) */


int __cdecl CTexture__Helper_00567505(uint param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 *puVar2;

  if ((param_1 < DAT_009d33a0) &&
     ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) & 1) != 0)) {
    CRT__LockFileHandleByIndex(param_1);
    iVar1 = CRT__WriteFdTextMode_NoLock(param_1,(void *)param_2,param_3);
    CRT__UnlockFileHandleByIndex(param_1);
    return iVar1;
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 9;
  puVar2 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar2 = 0;
  return -1;
}
