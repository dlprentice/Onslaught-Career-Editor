/* address: 0x00593951 */
/* name: CDXTexture__SetGammaCorrectionParams */
/* signature: void __stdcall CDXTexture__SetGammaCorrectionParams(int param_1, double param_2, double param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CDXTexture__SetGammaCorrectionParams(int param_1,double param_2,double param_3)

{
  undefined4 in_stack_00000008;

  if (_DAT_005eea98 <
      ABS((double)CONCAT44(param_2._0_4_,in_stack_00000008) *
          (double)CONCAT44(param_3._0_4_,param_2._4_4_) - _DAT_005e96a8)) {
    *(byte *)(param_1 + 0x61) = *(byte *)(param_1 + 0x61) | 0x20;
  }
  *(float *)(param_1 + 0x130) = (float)(double)CONCAT44(param_3._0_4_,param_2._4_4_);
  *(float *)(param_1 + 0x134) = (float)(double)CONCAT44(param_2._0_4_,in_stack_00000008);
  return;
}
