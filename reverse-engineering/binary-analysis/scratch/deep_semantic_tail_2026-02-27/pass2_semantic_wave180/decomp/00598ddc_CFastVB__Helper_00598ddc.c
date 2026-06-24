/* address: 0x00598ddc */
/* name: CFastVB__Helper_00598ddc */
/* signature: int CFastVB__Helper_00598ddc(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Helper_00598ddc(void)

{
  undefined4 *in_ECX;
  int iVar1;
  undefined4 *puVar2;
  undefined4 in_stack_00000004;
  int *in_stack_00000008;
  undefined4 *in_stack_0000000c;

  in_ECX[2] = 0;
  in_ECX[3] = 0;
  in_ECX[4] = in_stack_00000004;
  in_ECX[1] = 0xd;
  *in_ECX = &PTR_CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag_005ef270;
  in_ECX[6] = in_stack_00000008;
  puVar2 = in_ECX + 8;
  for (iVar1 = 8; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = *in_stack_0000000c;
    in_stack_0000000c = in_stack_0000000c + 1;
    puVar2 = puVar2 + 1;
  }
  if (in_stack_00000008 != (int *)0x0) {
    (**(code **)(*in_stack_00000008 + 4))();
  }
  return (int)in_ECX;
}
