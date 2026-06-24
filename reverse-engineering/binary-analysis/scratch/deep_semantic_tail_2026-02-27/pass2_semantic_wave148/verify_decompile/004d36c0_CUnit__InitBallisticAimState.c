/* address: 0x004d36c0 */
/* name: CUnit__InitBallisticAimState */
/* signature: int CUnit__InitBallisticAimState(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnit__InitBallisticAimState(void)

{
  int extraout_EAX;
  int iVar1;
  void *in_ECX;
  double dVar2;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;

  iVar1 = *(int *)((int)in_ECX + 0x254);
  if (iVar1 == 0) {
    *(undefined4 *)((int)in_ECX + 600) = in_stack_00000004;
    *(undefined4 *)((int)in_ECX + 0x25c) = in_stack_00000008;
    *(undefined4 *)((int)in_ECX + 0x260) = in_stack_0000000c;
    *(undefined4 *)((int)in_ECX + 0x264) = in_stack_00000010;
    dVar2 = CStaticShadows__Helper_0047eb80(0x6fadc8,&stack0x00000004);
    *(float *)((int)in_ECX + 0x260) = (float)dVar2;
    CUnit__ComputeBallisticLaunchVelocity(in_ECX);
    *(undefined4 *)((int)in_ECX + 0x254) = 1;
    *(undefined4 *)((int)in_ECX + 0x250) = 0;
    iVar1 = extraout_EAX;
  }
  return iVar1;
}
