/* address: 0x0058586b */
/* name: CTexture__UnpackTexels_PaletteIndexA8ToFloat4 */
/* signature: void __thiscall CTexture__UnpackTexels_PaletteIndexA8ToFloat4(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__UnpackTexels_PaletteIndexA8ToFloat4
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  byte *pbVar1;
  undefined4 *puVar2;
  byte *pbVar3;
  void *extraout_ECX;
  uint unaff_EBX;

  pbVar3 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar1 = pbVar3 + *(int *)((int)this + 0x1060) * 2;
  for (; pbVar3 < pbVar1; pbVar3 = pbVar3 + 2) {
    puVar2 = (undefined4 *)((uint)*pbVar3 * 0x10 + 0x38 + (int)this);
    *(undefined4 *)param_3 = *puVar2;
    *(undefined4 *)(param_3 + 4) = puVar2[1];
    *(undefined4 *)(param_3 + 8) = puVar2[2];
    *(undefined4 *)(param_3 + 0xc) = puVar2[3];
    *(float *)(param_3 + 0xc) = (float)pbVar3[1] * _DAT_005e9ee0;
    param_3 = (int)(param_3 + 0x10);
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EBX);
    this = extraout_ECX;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,(int)(param_3 + *(int *)((int)this + 0x1060) * -4 * 4),unaff_EBX)
    ;
  }
  return;
}
