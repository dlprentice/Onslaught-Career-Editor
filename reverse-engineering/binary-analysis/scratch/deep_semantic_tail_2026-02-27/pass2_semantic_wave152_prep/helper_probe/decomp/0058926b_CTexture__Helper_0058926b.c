/* address: 0x0058926b */
/* name: CTexture__Helper_0058926b */
/* signature: int __stdcall CTexture__Helper_0058926b(int param_1) */


int CTexture__Helper_0058926b(int param_1)

{
  BOOL BVar1;
  uint extraout_EAX;
  int iVar2;
  undefined **ppuVar3;
  undefined **ppuVar4;
  int local_8;

  if (param_1 == 0) {
    DAT_00657a84 = 0xffff;
    ppuVar3 = &PTR_CTexture__Helper_00578555_00657050;
    ppuVar4 = &PTR_CDXTexture__Unk_00575d20_00656f30;
    for (iVar2 = 0x47; iVar2 != 0; iVar2 = iVar2 + -1) {
      *ppuVar4 = *ppuVar3;
      ppuVar3 = ppuVar3 + 1;
      ppuVar4 = ppuVar4 + 1;
    }
  }
  else if (DAT_00657a84 == 0xffff) {
    DAT_00657a84 = 0;
    ppuVar3 = &PTR_CTexture__Helper_00578555_00657050;
    ppuVar4 = &PTR_CDXTexture__Unk_00575d20_00656f30;
    for (iVar2 = 0x47; iVar2 != 0; iVar2 = iVar2 + -1) {
      *ppuVar4 = *ppuVar3;
      ppuVar3 = ppuVar3 + 1;
      ppuVar4 = ppuVar4 + 1;
    }
    CFastVB__Helper_00596341(&PTR_CDXTexture__Unk_00575d20_00656f30);
    iVar2 = CFastVB__Helper_00589094(4,0x5ea2f4,(int)&param_1);
    if (iVar2 == 0) {
      param_1 = 0;
    }
    iVar2 = CFastVB__Helper_00589094(4,0x5ea2e4,(int)&local_8);
    if (iVar2 != 0) {
      param_1 = local_8;
    }
    if (param_1 != 1) {
      if ((param_1 == 2) || (BVar1 = IsProcessorFeaturePresent(7), BVar1 == 0)) {
        CFastVB__Helper_005891c6();
        if ((extraout_EAX & 8) == 0) {
          BVar1 = IsProcessorFeaturePresent(6);
          if (BVar1 != 0) {
            CFastVB__Helper_005980be(&PTR_CDXTexture__Unk_00575d20_00656f30);
            DAT_00657a84 = 3;
          }
        }
        else {
          CFastVB__Helper_0059822c(&PTR_CDXTexture__Unk_00575d20_00656f30);
          DAT_00657a84 = 2;
        }
      }
      else {
        CFastVB__InitDispatchOpsFromFeatureFlags(&PTR_CDXTexture__Unk_00575d20_00656f30);
        DAT_00657a84 = 1;
      }
    }
  }
  return DAT_00657a84;
}
