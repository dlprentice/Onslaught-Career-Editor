/* address: 0x00586609 */
/* name: CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne */
/* signature: void __thiscall CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne(void * this, void * param_1, int param_2, int param_3, uint param_4) */


void __thiscall
CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne
          (void *this,void *param_1,int param_2,int param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint unaff_EDI;

  uVar2 = *(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
          *(int *)((int)this + 0x20);
  uVar1 = uVar2 + *(int *)((int)this + 0x1060) * 2;
  for (; uVar2 < uVar1; uVar2 = uVar2 + 2) {
    unaff_EDI = param_3;
    CDXTexture__Helper_00575a65();
    *(undefined4 *)(param_3 + 0xc) = 0x3f800000;
    *(undefined4 *)(param_3 + 8) = 0x3f800000;
    *(undefined4 *)(param_3 + 4) = 0x3f800000;
    param_3 = param_3 + 0x10;
  }
  if (*(int *)((int)this + 0x18) != 0) {
    CFastVB__Helper_00581e1c(this,param_3 + *(int *)((int)this + 0x1060) * -0x10,unaff_EDI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,param_3 + *(int *)((int)this + 0x1060) * -0x10,unaff_EDI);
  }
  return;
}
