/* address: 0x00568b76 */
/* name: CDXTexture__Unk_00568b76 */
/* signature: int __cdecl CDXTexture__Unk_00568b76(uint param_1, int param_2, int param_3) */


int __cdecl CDXTexture__Unk_00568b76(uint param_1,int param_2,int param_3)

{
  int iVar1;
  undefined4 *puVar2;

  if ((param_1 < DAT_009d33a0) &&
     ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) & 1) != 0)) {
    CDXTexture__Helper_0056b254(param_1);
    iVar1 = CDXTexture__Unk_00568bdb(param_1,param_2,param_3);
    CDXTexture__Helper_0056b2b3(param_1);
    return iVar1;
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 9;
  puVar2 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar2 = 0;
  return -1;
}
