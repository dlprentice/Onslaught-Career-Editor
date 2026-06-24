/* address: 0x0058562d */
/* name: CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB */
/* signature: void __thiscall CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB
          (void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  byte *pbVar1;
  void *extraout_ECX;
  byte *pbVar2;
  uint unaff_ESI;

  pbVar1 = (byte *)(*(int *)((int)this + 0x1058) * (int)param_1 +
                    *(int *)((int)this + 0x105c) * param_2 + *(int *)((int)this + 0x20));
  pbVar2 = pbVar1 + *(int *)((int)this + 0x1060);
  for (; pbVar1 < pbVar2; pbVar1 = pbVar1 + 1) {
    *(undefined4 *)param_3 = 0;
    *(undefined4 *)(param_3 + 4) = 0;
    *(undefined4 *)(param_3 + 8) = 0;
    *(float *)(param_3 + 0xc) = (float)*pbVar1 * _DAT_005e9ee0;
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
