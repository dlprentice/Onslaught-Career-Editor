/* address: 0x005868d1 */
/* name: CFastVB__Unk_005868d1 */
/* signature: void __thiscall CFastVB__Unk_005868d1(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x00586917) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__Unk_005868d1(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint *puVar1;
  float fVar2;
  float fVar3;
  uint *puVar4;
  void *extraout_ECX;
  uint unaff_ESI;

  fVar3 = _DAT_005e9f34;
  puVar4 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  puVar1 = puVar4 + *(int *)((int)this + 0x1060);
  for (; puVar4 < puVar1; puVar4 = puVar4 + 1) {
    fVar2 = (float)(*puVar4 & 0xffff) * fVar3;
    *(float *)(param_3 + 8) = fVar2;
    *(float *)(param_3 + 4) = fVar2;
    *(float *)param_3 = fVar2;
    *(float *)(param_3 + 0xc) = (float)*(ushort *)((int)puVar4 + 2) * fVar3;
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
