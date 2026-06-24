/* address: 0x0056b212 */
/* name: CRT__GetOsFileHandleByIndex */
/* signature: int __cdecl CRT__GetOsFileHandleByIndex(uint param_1) */


int __cdecl CRT__GetOsFileHandleByIndex(uint param_1)

{
  undefined4 *puVar1;

  if ((param_1 < DAT_009d33a0) &&
     ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) & 1) != 0)) {
    return *(int *)((&DAT_009d32a0)[(int)param_1 >> 5] + (param_1 & 0x1f) * 0x24);
  }
  puVar1 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar1 = 9;
  puVar1 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar1 = 0;
  return -1;
}
