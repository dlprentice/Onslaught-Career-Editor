/* address: 0x005860ba */
/* name: CTexture__UnpackTexels_Signed16_16_ToFloat4_RG */
/* signature: void __thiscall CTexture__UnpackTexels_Signed16_16_ToFloat4_RG(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__UnpackTexels_Signed16_16_ToFloat4_RG
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  short *psVar1;
  short sVar2;
  float fVar3;
  short *psVar4;
  void *extraout_ECX;
  uint unaff_ESI;

  fVar3 = _DAT_005ea030;
  psVar4 = (short *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                     *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  psVar1 = psVar4 + *(int *)((int)this + 0x1060) * 2;
  for (; psVar4 < psVar1; psVar4 = psVar4 + 2) {
    sVar2 = psVar4[1];
    *(float *)param_3 = (float)(int)(short)((ushort)(*psVar4 == -0x8000) + *psVar4) * fVar3;
    *(float *)(param_3 + 4) = (float)(int)(short)((ushort)(sVar2 == -0x8000) + sVar2) * fVar3;
    *(float *)(param_3 + 8) = 1.0;
    *(float *)(param_3 + 0xc) = 1.0;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_ESI);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_ESI)
    ;
  }
  return;
}
