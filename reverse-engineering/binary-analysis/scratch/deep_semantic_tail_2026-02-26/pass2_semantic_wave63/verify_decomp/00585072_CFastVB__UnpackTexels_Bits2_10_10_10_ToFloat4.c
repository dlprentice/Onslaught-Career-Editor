/* address: 0x00585072 */
/* name: CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4 */
/* signature: void __thiscall CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x005850d9) */
/* WARNING: Removing unreachable block (ram,0x005850be) */
/* WARNING: Removing unreachable block (ram,0x005850f5) */
/* WARNING: Removing unreachable block (ram,0x0058510f) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint *puVar1;
  float fVar2;
  uint *puVar3;
  void *extraout_ECX;
  uint unaff_EDI;

  fVar2 = _DAT_005e9f30;
  puVar3 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  puVar1 = puVar3 + *(int *)((int)this + 0x1060);
  for (; puVar3 < puVar1; puVar3 = puVar3 + 1) {
    *(float *)param_3 = (float)(*puVar3 & 0x3ff) * fVar2;
    *(float *)(param_3 + 4) = (float)(*puVar3 >> 10 & 0x3ff) * fVar2;
    *(float *)(param_3 + 8) = (float)(*puVar3 >> 0x14 & 0x3ff) * fVar2;
    *(float *)(param_3 + 0xc) = (float)(*puVar3 >> 0x1e) * _DAT_005e9f2c;
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
