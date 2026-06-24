/* address: 0x00466e70 */
/* name: CFrontEnd__Unk_00466e70 */
/* signature: int CFrontEnd__Unk_00466e70(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_00466e70(void)

{
  float fVar1;
  float fVar2;
  int iVar3;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;

  fVar1 = (in_stack_00000004 + in_stack_0000000c) * _DAT_005d85ec;
  fpatan((float10)_DAT_005d87b0,(float10)in_stack_0000000c - (float10)in_stack_00000004);
  CDXSurf__RenderSurface(fVar1,(in_stack_00000008 + in_stack_00000008) * _DAT_005d85ec);
  fVar2 = (in_stack_00000008 + in_stack_00000010) * _DAT_005d85ec;
  fpatan((float10)in_stack_00000010 - (float10)in_stack_00000008,(float10)_DAT_005d87b0);
  CDXSurf__RenderSurface((in_stack_0000000c + in_stack_0000000c) * _DAT_005d85ec,fVar2);
  fpatan((float10)_DAT_005d87b0,(float10)in_stack_00000004 - (float10)in_stack_0000000c);
  CDXSurf__RenderSurface(fVar1,(in_stack_00000010 + in_stack_00000010) * _DAT_005d85ec);
  fpatan((float10)in_stack_00000008 - (float10)in_stack_00000010,(float10)_DAT_005d87b0);
  iVar3 = CDXSurf__RenderSurface((in_stack_00000004 + in_stack_00000004) * _DAT_005d85ec,fVar2);
  return iVar3;
}
