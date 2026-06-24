/* address: 0x00466de0 */
/* name: CFrontEnd__Unk_00466de0 */
/* signature: int CFrontEnd__Unk_00466de0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_00466de0(void)

{
  int iVar1;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;

  fpatan((float10)in_stack_00000010 - (float10)in_stack_00000008,
         (float10)in_stack_0000000c - (float10)in_stack_00000004);
  iVar1 = CDXSurf__RenderSurface
                    ((in_stack_00000004 + in_stack_0000000c) * _DAT_005d85ec,
                     (in_stack_00000008 + in_stack_00000010) * _DAT_005d85ec);
  return iVar1;
}
