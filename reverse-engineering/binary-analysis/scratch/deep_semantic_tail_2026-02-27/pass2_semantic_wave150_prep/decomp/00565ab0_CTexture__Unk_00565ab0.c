/* address: 0x00565ab0 */
/* name: CTexture__Unk_00565ab0 */
/* signature: int __cdecl CTexture__Unk_00565ab0(int param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CTexture__Unk_00565ab0(int param_1,int param_2)

{
  uint *puVar1;
  undefined *puVar2;
  int iVar3;
  size_t sVar4;
  void *pvVar5;
  uint *puVar6;
  char local_a8 [132];
  undefined1 local_24 [8];
  undefined4 local_1c;
  uint local_18;
  ushort local_14 [4];
  undefined *local_c;
  undefined4 local_8;

  iVar3 = CTexture__Unk_00565c84((void *)param_2,local_a8,local_14,&local_1c);
  if (iVar3 != 0) {
    sVar4 = _strlen(local_a8);
    pvVar5 = _malloc(sVar4 + 1);
    if (pvVar5 != (void *)0x0) {
      puVar1 = (uint *)(&DAT_009d0990 + param_1 * 4);
      puVar2 = (undefined *)(&DAT_00653d34)[param_1 * 3];
      local_18 = *puVar1;
      local_c = &DAT_009d0af4 + param_1 * 6;
      CTexture__Helper_00567700(local_24,local_c,6);
      local_8 = DAT_009d09a8;
      puVar6 = CDXTexture__Helper_00567de0(pvVar5,local_a8);
      (&DAT_00653d34)[param_1 * 3] = puVar6;
      *puVar1 = (uint)local_14[0];
      CTexture__Helper_00567700(local_c,local_14,6);
      if (param_1 == 2) {
        DAT_009d09a8 = local_1c;
      }
      if (param_1 == 1) {
        _DAT_009d09ac = local_1c;
      }
      iVar3 = (**(code **)(&DAT_00653d38 + param_1 * 0xc))();
      if (iVar3 == 0) {
        if (puVar2 != &DAT_00653c20) {
          CRT__FreeBase((int)puVar2);
        }
        return (&DAT_00653d34)[param_1 * 3];
      }
      (&DAT_00653d34)[param_1 * 3] = puVar2;
      CRT__FreeBase((int)pvVar5);
      *puVar1 = local_18;
      DAT_009d09a8 = local_8;
    }
  }
  return 0;
}
