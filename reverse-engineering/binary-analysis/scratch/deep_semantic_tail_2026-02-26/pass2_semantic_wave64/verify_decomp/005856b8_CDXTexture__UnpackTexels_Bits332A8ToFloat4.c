/* address: 0x005856b8 */
/* name: CDXTexture__UnpackTexels_Bits332A8ToFloat4 */
/* signature: void __thiscall CDXTexture__UnpackTexels_Bits332A8ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UnpackTexels_Bits332A8ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  byte *pbVar1;
  float fVar2;
  byte *pbVar3;
  void *extraout_ECX;
  uint unaff_EDI;

  fVar2 = _DAT_005e9f38;
  pbVar3 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar1 = pbVar3 + *(int *)((int)this + 0x1060) * 2;
  for (; pbVar3 < pbVar1; pbVar3 = pbVar3 + 2) {
    *(float *)param_3 = (float)(*pbVar3 >> 5) * fVar2;
    *(float *)(param_3 + 4) = (float)(*pbVar3 >> 2 & 7) * fVar2;
    *(float *)(param_3 + 8) = (float)(*pbVar3 & 3) * _DAT_005e9f2c;
    *(float *)(param_3 + 0xc) = (float)pbVar3[1] * _DAT_005e9ee0;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EDI)
    ;
  }
  return;
}
