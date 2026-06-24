/* address: 0x00585220 */
/* name: CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne */
/* signature: void __thiscall CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Removing unreachable block (ram,0x00585266) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint *puVar1;
  float fVar2;
  uint *puVar3;
  void *extraout_ECX;
  uint unaff_ESI;

  fVar2 = _DAT_005e9ee0;
  puVar3 = (uint *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  puVar1 = puVar3 + *(int *)((int)this + 0x1060);
  for (; puVar3 < puVar1; puVar3 = puVar3 + 1) {
    *(float *)param_3 = (float)(*puVar3 & 0xff) * fVar2;
    *(float *)(param_3 + 4) = (float)*(byte *)((int)puVar3 + 1) * fVar2;
    *(float *)(param_3 + 8) = (float)*(byte *)((int)puVar3 + 2) * fVar2;
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
