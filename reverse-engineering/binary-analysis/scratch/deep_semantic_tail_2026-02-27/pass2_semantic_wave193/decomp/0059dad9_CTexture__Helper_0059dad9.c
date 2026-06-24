/* address: 0x0059dad9 */
/* name: CTexture__Helper_0059dad9 */
/* signature: void __stdcall CTexture__Helper_0059dad9(void * param_1, int param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CTexture__Helper_0059dad9(void *param_1,int param_2,uint param_3)

{
  uint uVar1;
  void *pvVar2;
  int iVar3;
  char *pcVar4;

  pvVar2 = param_1;
  uVar1 = *(uint *)((int)param_1 + 0x58);
  if ((uVar1 & 1) == 0) {
    CDXTexture__ThrowDecodeError(param_1,0x5f3d94);
  }
  else {
    if ((uVar1 & 4) != 0) {
      pcVar4 = "Invalid sRGB after IDAT";
      goto LAB_0059dafd;
    }
    if ((uVar1 & 2) == 0) {
      if ((param_2 != 0) && ((*(byte *)(param_2 + 9) & 8) != 0)) {
        pcVar4 = "Duplicate sRGB chunk";
        goto LAB_0059dafd;
      }
    }
    else {
      CDXTexture__ReportDecodeWarning((int)param_1,0x5f3d48);
    }
  }
  if (param_3 == 1) {
    CTexture__Helper_0059cd4b(pvVar2,(int)&param_1 + 3,1);
    iVar3 = CDXTexture__FinalizePngChunkAndVerifyCrc(pvVar2,0);
    if (iVar3 != 0) {
      return;
    }
    uVar1 = (uint)param_1 >> 0x18;
    if (3 < uVar1) {
      CDXTexture__ReportDecodeWarning((int)pvVar2,0x5f3d1c);
      return;
    }
    if (((*(byte *)(param_2 + 8) & 1) != 0) &&
       ((float)_DAT_005f3c88 <
        ABS((*(float *)((int)pvVar2 + 0x130) * _DAT_005f3d18 + (float)_DAT_005e9690) -
            (float)_DAT_005f3c90))) {
      CDXTexture__ReportDecodeWarning((int)pvVar2,0x5f3c4c);
    }
    CDXTexture__SetDecodeOptionByteWithDefaultFloat((int)pvVar2,param_2,uVar1);
    return;
  }
  pcVar4 = "Incorrect sRGB chunk length";
LAB_0059dafd:
  CDXTexture__ReportDecodeWarning((int)pvVar2,(int)pcVar4);
  CDXTexture__FinalizePngChunkAndVerifyCrc(pvVar2,param_3);
  return;
}
