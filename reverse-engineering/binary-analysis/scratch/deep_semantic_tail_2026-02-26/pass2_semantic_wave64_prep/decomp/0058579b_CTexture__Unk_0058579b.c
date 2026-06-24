/* address: 0x0058579b */
/* name: CTexture__Unk_0058579b */
/* signature: void __thiscall CTexture__Unk_0058579b(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_0058579b(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  byte *pbVar1;
  float fVar2;
  byte *pbVar3;
  void *extraout_ECX;
  uint unaff_EDI;

  fVar2 = _DAT_005e9f28;
  pbVar3 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar1 = pbVar3 + *(int *)((int)this + 0x1060) * 2;
  for (; pbVar3 < pbVar1; pbVar3 = pbVar3 + 2) {
    *(float *)param_3 = (float)(pbVar3[1] & 0xf) * fVar2;
    *(float *)(param_3 + 4) = (float)(*pbVar3 >> 4) * fVar2;
    *(float *)(param_3 + 8) = (float)(*pbVar3 & 0xf) * fVar2;
    *(float *)(param_3 + 0xc) = 1.0;
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
