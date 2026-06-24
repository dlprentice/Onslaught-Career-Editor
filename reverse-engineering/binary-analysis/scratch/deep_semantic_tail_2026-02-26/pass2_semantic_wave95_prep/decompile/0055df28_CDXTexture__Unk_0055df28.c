/* address: 0x0055df28 */
/* name: CDXTexture__Unk_0055df28 */
/* signature: int __cdecl CDXTexture__Unk_0055df28(int param_1) */


int __cdecl CDXTexture__Unk_0055df28(int param_1)

{
  uint uVar1;
  int iVar2;
  void *pvVar3;

  CDXTexture__Helper_0055de6f();
  uVar1 = CDXTexture__Unk_0056235d((int)DAT_009d4610);
  if (uVar1 < (uint)((int)DAT_009d460c + (4 - (int)DAT_009d4610))) {
    iVar2 = CDXTexture__Unk_0056235d((int)DAT_009d4610);
    pvVar3 = (void *)CDXTexture__Helper_0056202e(DAT_009d4610,iVar2 + 0x10);
    if (pvVar3 == (void *)0x0) {
      param_1 = 0;
      goto LAB_0055df9d;
    }
    DAT_009d460c = (int *)((int)pvVar3 + ((int)DAT_009d460c - (int)DAT_009d4610 >> 2) * 4);
    DAT_009d4610 = pvVar3;
  }
  *DAT_009d460c = param_1;
  DAT_009d460c = DAT_009d460c + 1;
LAB_0055df9d:
  CDXTexture__Helper_0055de78();
  return param_1;
}
