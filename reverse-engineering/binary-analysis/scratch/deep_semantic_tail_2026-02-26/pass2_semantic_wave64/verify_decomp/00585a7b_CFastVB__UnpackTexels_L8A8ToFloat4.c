/* address: 0x00585a7b */
/* name: CFastVB__UnpackTexels_L8A8ToFloat4 */
/* signature: void __thiscall CFastVB__UnpackTexels_L8A8ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__UnpackTexels_L8A8ToFloat4(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  byte *pbVar1;
  float fVar2;
  float fVar3;
  byte *pbVar4;
  void *extraout_ECX;
  uint unaff_EDI;

  fVar3 = _DAT_005e9ee0;
  pbVar4 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar1 = pbVar4 + *(int *)((int)this + 0x1060) * 2;
  for (; pbVar4 < pbVar1; pbVar4 = pbVar4 + 2) {
    fVar2 = (float)*pbVar4 * fVar3;
    *(float *)(param_3 + 8) = fVar2;
    *(float *)(param_3 + 4) = fVar2;
    *(float *)param_3 = fVar2;
    *(float *)(param_3 + 0xc) = (float)pbVar4[1] * fVar3;
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
