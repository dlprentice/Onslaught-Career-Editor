/* address: 0x00564e41 */
/* name: CDXTexture__Unk_00564e41 */
/* signature: int __cdecl CDXTexture__Unk_00564e41(uint param_1) */


int __cdecl CDXTexture__Unk_00564e41(uint param_1)

{
  int iVar1;
  undefined4 *puVar2;

  if ((param_1 < DAT_009d33a0) &&
     ((*(byte *)((&DAT_009d32a0)[(int)param_1 >> 5] + 4 + (param_1 & 0x1f) * 0x24) & 1) != 0)) {
    CDXTexture__Helper_0056b254(param_1);
    iVar1 = CDXTexture__Unk_00564e9e(param_1);
    CDXTexture__Helper_0056b2b3(param_1);
    return iVar1;
  }
  puVar2 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar2 = 9;
  puVar2 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar2 = 0;
  return -1;
}
