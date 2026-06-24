/* address: 0x0059d9d8 */
/* name: CDXTexture__ParsePngChunk_gAMA */
/* signature: void __stdcall CDXTexture__ParsePngChunk_gAMA(void * param_1, int param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CDXTexture__ParsePngChunk_gAMA(void *param_1,int param_2,uint param_3)

{
  uint uVar1;
  float fVar2;
  void *pvVar3;
  int iVar4;
  int iVar5;
  char *pcVar6;

  iVar4 = param_2;
  pvVar3 = param_1;
  uVar1 = *(uint *)((int)param_1 + 0x58);
  if ((uVar1 & 1) == 0) {
    CDXTexture__Helper_00592d45(param_1,0x5f3cfc);
  }
  else {
    if ((uVar1 & 4) != 0) {
      pcVar6 = "Invalid gAMA after IDAT";
      goto LAB_0059da06;
    }
    if ((uVar1 & 2) == 0) {
      if (((param_2 != 0) && ((*(uint *)(param_2 + 8) & 1) != 0)) &&
         ((*(uint *)(param_2 + 8) & 0x800) == 0)) {
        pcVar6 = "Duplicate gAMA chunk";
        goto LAB_0059da06;
      }
    }
    else {
      CDXTexture__Helper_00592d63((int)param_1,0x5f3cb0);
    }
  }
  if (param_3 == 4) {
    CTexture__Helper_0059cd4b(pvVar3,(int)&param_1,4);
    iVar5 = CDXTexture__Helper_0059d614(pvVar3,0);
    if (iVar5 != 0) {
      return;
    }
    param_3 = CDXTexture__ReadU32BigEndian(&param_1);
    if (param_3 == 0) {
      return;
    }
    if ((*(uint *)(iVar4 + 8) & 0x800) != 0) {
      fVar2 = (float)(int)param_3;
      if ((int)param_3 < 0) {
        fVar2 = fVar2 + _DAT_005e72d8;
      }
      if ((float)_DAT_005f3c88 < ABS(fVar2 - (float)_DAT_005f3c90)) {
        CDXTexture__Helper_00592d63((int)pvVar3,0x5f3c4c);
        return;
      }
    }
    fVar2 = (float)(int)param_3;
    if ((int)param_3 < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar2 = fVar2 * _DAT_005e96c8;
    *(float *)((int)pvVar3 + 0x130) = fVar2;
    CDXTexture__SetDecodeOptionFloat((int)pvVar3,iVar4,(double)fVar2);
    return;
  }
  pcVar6 = "Incorrect gAMA chunk length";
LAB_0059da06:
  CDXTexture__Helper_00592d63((int)pvVar3,(int)pcVar6);
  CDXTexture__Helper_0059d614(pvVar3,param_3);
  return;
}
