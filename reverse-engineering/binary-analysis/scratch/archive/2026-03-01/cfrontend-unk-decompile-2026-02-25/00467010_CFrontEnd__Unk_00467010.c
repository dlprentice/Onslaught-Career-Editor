/* address: 0x00467010 */
/* name: CFrontEnd__Unk_00467010 */
/* signature: int CFrontEnd__Unk_00467010(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_00467010(void)

{
  int extraout_EAX;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  undefined4 in_stack_00000014;
  undefined4 in_stack_00000018;

  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  CDXSurf__RenderSurface
            (in_stack_00000004,in_stack_00000008,in_stack_00000014,DAT_0089d8ec,in_stack_00000018,
             (in_stack_0000000c - in_stack_00000004) * _DAT_005dbb50,
             (in_stack_00000010 - in_stack_00000008) * _DAT_005dbb50,0,0,0x3f800000,0);
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  return extraout_EAX;
}
