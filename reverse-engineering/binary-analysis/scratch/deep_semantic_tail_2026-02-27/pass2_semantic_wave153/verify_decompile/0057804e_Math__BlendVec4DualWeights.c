/* address: 0x0057804e */
/* name: Math__BlendVec4DualWeights */
/* signature: int Math__BlendVec4DualWeights(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int Math__BlendVec4DualWeights(void)

{
  float fVar1;
  int iVar2;
  undefined4 *in_stack_00000004;
  undefined4 *in_stack_00000008;
  int in_stack_0000000c;
  int in_stack_00000010;
  float in_stack_00000014;
  float in_stack_00000018;
  undefined1 local_24 [16];
  undefined1 local_14 [16];

  fVar1 = in_stack_00000014 + in_stack_00000018;
  iVar2 = Math__IsFloatDiffOutsideTolerance(fVar1,0.0);
  if (iVar2 == 0) {
    CTexture__Helper_00577ea4((int)local_24,(int)in_stack_00000008,in_stack_0000000c,(int)fVar1);
    CTexture__Helper_00577ea4((int)local_14,(int)in_stack_00000008,in_stack_00000010,(int)fVar1);
    CTexture__Helper_00577ea4
              ((int)in_stack_00000004,(int)local_24,(int)local_14,(int)(in_stack_00000018 / fVar1));
  }
  else if (in_stack_00000004 != in_stack_00000008) {
    *in_stack_00000004 = *in_stack_00000008;
    in_stack_00000004[1] = in_stack_00000008[1];
    in_stack_00000004[2] = in_stack_00000008[2];
    in_stack_00000004[3] = in_stack_00000008[3];
  }
  return (int)in_stack_00000004;
}
