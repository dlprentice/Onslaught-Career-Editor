/* address: 0x005869b0 */
/* name: CTexture__Unk_005869b0 */
/* signature: void __thiscall CTexture__Unk_005869b0(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_005869b0(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  float fVar1;
  ushort *puVar2;
  void *extraout_ECX;
  ushort *puVar3;
  uint unaff_ESI;

  fVar1 = _DAT_005e9f34;
  puVar2 = (ushort *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  puVar3 = (ushort *)(*(int *)((int)this + 0x106c) + (int)puVar2);
  for (; puVar2 < puVar3; puVar2 = puVar2 + 3) {
    *(float *)param_3 = (float)puVar2[2] * fVar1;
    *(float *)(param_3 + 4) = (float)puVar2[1] * fVar1;
    *(float *)(param_3 + 8) = (float)*puVar2 * fVar1;
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
