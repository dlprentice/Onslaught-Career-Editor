/* address: 0x0058926b */
/* name: CFastVB__InitDispatchTableByCpuFeature */
/* signature: int __stdcall CFastVB__InitDispatchTableByCpuFeature(int param_1) */


int CFastVB__InitDispatchTableByCpuFeature(int param_1)

{
  BOOL BVar1;
  uint extraout_EAX;
  int iVar2;
  undefined **ppuVar3;
  undefined **ppuVar4;
  int local_8;

  if (param_1 == 0) {
    DAT_00657a84 = 0xffff;
    ppuVar3 = &PTR_Math__TransformVec2ByMatrix4x4_00657050;
    ppuVar4 = &PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30;
    for (iVar2 = 0x47; iVar2 != 0; iVar2 = iVar2 + -1) {
      *ppuVar4 = *ppuVar3;
      ppuVar3 = ppuVar3 + 1;
      ppuVar4 = ppuVar4 + 1;
    }
  }
  else if (DAT_00657a84 == 0xffff) {
    DAT_00657a84 = 0;
    ppuVar3 = &PTR_Math__TransformVec2ByMatrix4x4_00657050;
    ppuVar4 = &PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30;
    for (iVar2 = 0x47; iVar2 != 0; iVar2 = iVar2 + -1) {
      *ppuVar4 = *ppuVar3;
      ppuVar3 = ppuVar3 + 1;
      ppuVar4 = ppuVar4 + 1;
    }
    CFastVB__InitMathDispatchTable(&PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30);
    iVar2 = CDXTexture__RegistryValueEqualsDword(4,0x5ea2f4,(int)&param_1);
    if (iVar2 == 0) {
      param_1 = 0;
    }
    iVar2 = CDXTexture__RegistryValueEqualsDword(4,0x5ea2e4,(int)&local_8);
    if (iVar2 != 0) {
      param_1 = local_8;
    }
    if (param_1 != 1) {
      if ((param_1 == 2) || (BVar1 = IsProcessorFeaturePresent(7), BVar1 == 0)) {
        CDXTexture__InitCpuVendorAndSimdFlags();
        if ((extraout_EAX & 8) == 0) {
          BVar1 = IsProcessorFeaturePresent(6);
          if (BVar1 != 0) {
            CFastVB__InitDispatchTableVariant_005980be
                      (&PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30);
            DAT_00657a84 = 3;
          }
        }
        else {
          CFastVB__InitDispatchTableVariant_0059822c
                    (&PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30);
          DAT_00657a84 = 2;
        }
      }
      else {
        CFastVB__InitDispatchOpsFromFeatureFlags
                  (&PTR_CDXTexture__DispatchPtr00656f30_WithInit_00656f30);
        DAT_00657a84 = 1;
      }
    }
  }
  return DAT_00657a84;
}
