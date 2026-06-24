/* address: 0x00585b35 */
/* name: CFastVB__Unk_00585b35 */
/* signature: void __thiscall CFastVB__Unk_00585b35(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_00585b35(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  float fVar1;
  float fVar2;
  byte *pbVar3;
  void *extraout_ECX;
  uint unaff_EDI;
  byte *pbVar4;

  fVar2 = _DAT_005e9f28;
  pbVar3 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar4 = pbVar3 + *(int *)((int)this + 0x1060);
  for (; pbVar3 < pbVar4; pbVar3 = pbVar3 + 1) {
    fVar1 = (float)(*pbVar3 & 0xf) * fVar2;
    *(float *)(param_3 + 8) = fVar1;
    *(float *)(param_3 + 4) = fVar1;
    *(float *)param_3 = fVar1;
    *(float *)(param_3 + 0xc) = (float)(*pbVar3 >> 4) * fVar2;
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
