/* address: 0x00584e32 */
/* name: CFastVB__Unk_00584e32 */
/* signature: void __thiscall CFastVB__Unk_00584e32(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_00584e32(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  ushort *puVar1;
  float fVar2;
  ushort *puVar3;
  void *extraout_ECX;
  uint unaff_EDI;

  fVar2 = _DAT_005e9efc;
  puVar3 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  puVar1 = puVar3 + *(int *)((int)this + 0x1060);
  for (; puVar3 < puVar1; puVar3 = puVar3 + 1) {
    *(float *)param_3 = (float)((*puVar3 & 0x7c00) >> 10) * fVar2;
    *(float *)(param_3 + 4) = (float)((*puVar3 & 0x3e0) >> 5) * fVar2;
    *(float *)(param_3 + 8) = (float)((byte)*puVar3 & 0x1f) * fVar2;
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
