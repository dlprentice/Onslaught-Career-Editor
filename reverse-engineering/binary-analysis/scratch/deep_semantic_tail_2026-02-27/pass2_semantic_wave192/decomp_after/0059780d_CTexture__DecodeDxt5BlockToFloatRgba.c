/* address: 0x0059780d */
/* name: CTexture__DecodeDxt5BlockToFloatRgba */
/* signature: int __stdcall CTexture__DecodeDxt5BlockToFloatRgba(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CTexture__DecodeDxt5BlockToFloatRgba(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  int iVar3;
  uint uVar4;
  float *pfVar5;
  uint uVar6;
  float local_24 [8];

  iVar3 = CDXTexture__DecodeDxt1ColorBlockToRgba(param_1,(void *)((int)param_2 + 8));
  if (-1 < iVar3) {
    local_24[0] = (float)*(byte *)param_2 * _DAT_005e9ee0;
    local_24[1] = (float)*(byte *)((int)param_2 + 1) * _DAT_005e9ee0;
    if (*(byte *)((int)param_2 + 1) < *(byte *)param_2) {
      uVar4 = 1;
      do {
        fVar1 = (float)(int)(7 - uVar4);
        if ((int)(7 - uVar4) < 0) {
          fVar1 = fVar1 + _DAT_005e72d8;
        }
        fVar2 = (float)(int)uVar4;
        if ((int)uVar4 < 0) {
          fVar2 = fVar2 + _DAT_005e72d8;
        }
        uVar4 = uVar4 + 1;
        local_24[uVar4] = (fVar2 * local_24[1] + fVar1 * local_24[0]) * _DAT_005e9f38;
      } while (uVar4 < 7);
    }
    else {
      uVar4 = 1;
      do {
        fVar1 = (float)(int)(5 - uVar4);
        if ((int)(5 - uVar4) < 0) {
          fVar1 = fVar1 + _DAT_005e72d8;
        }
        fVar2 = (float)(int)uVar4;
        if ((int)uVar4 < 0) {
          fVar2 = fVar2 + _DAT_005e72d8;
        }
        uVar4 = uVar4 + 1;
        local_24[uVar4] = (fVar2 * local_24[1] + fVar1 * local_24[0]) * _DAT_005ef0a4;
      } while (uVar4 < 5);
      local_24[6] = 0.0;
      local_24[7] = 1.0;
    }
    iVar3 = 8;
    uVar4 = (uint)*(uint3 *)((int)param_2 + 2);
    pfVar5 = (float *)((int)param_1 + 0xc);
    do {
      uVar6 = uVar4 & 7;
      uVar4 = uVar4 >> 3;
      *pfVar5 = local_24[uVar6];
      pfVar5 = pfVar5 + 4;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    iVar3 = 8;
    uVar4 = (uint)*(uint3 *)((int)param_2 + 5);
    pfVar5 = (float *)((int)param_1 + 0x8c);
    do {
      uVar6 = uVar4 & 7;
      uVar4 = uVar4 >> 3;
      *pfVar5 = local_24[uVar6];
      pfVar5 = pfVar5 + 4;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    iVar3 = 0;
  }
  return iVar3;
}
