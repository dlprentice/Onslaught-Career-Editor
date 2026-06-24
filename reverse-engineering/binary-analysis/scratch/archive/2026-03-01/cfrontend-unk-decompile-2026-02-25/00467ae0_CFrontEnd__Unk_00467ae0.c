/* address: 0x00467ae0 */
/* name: CFrontEnd__Unk_00467ae0 */
/* signature: int CFrontEnd__Unk_00467ae0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_00467ae0(void)

{
  int iVar1;
  float fVar2;
  float fVar3;
  undefined4 uVar4;
  int extraout_EAX;
  int iVar5;
  float in_stack_00000004;
  float in_stack_00000008;
  undefined4 in_stack_0000000c;
  int in_stack_00000010;
  undefined4 in_stack_00000014;
  float in_stack_00000018;

  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  iVar5 = 0;
  iVar1 = in_stack_00000010 + 2;
  fVar2 = in_stack_00000008 - in_stack_00000018 * _DAT_005db2b8;
  in_stack_00000008 = in_stack_00000004 - (float)(iVar1 * 0x20) * in_stack_00000018;
  if (0 < iVar1) {
    fVar3 = in_stack_00000018 * _DAT_005dbb64;
    do {
      uVar4 = DAT_0089d7b0;
      if (iVar5 == 0) {
        uVar4 = DAT_0089d7ac;
      }
      if (iVar5 == in_stack_00000010 + 1) {
        uVar4 = DAT_0089d7b4;
      }
      CDXSurf__RenderSurface
                (in_stack_00000008,fVar2,in_stack_0000000c,uVar4,in_stack_00000014,in_stack_00000018
                 ,in_stack_00000018,0,0,0x3f800000,0);
      in_stack_00000008 = fVar3 + in_stack_00000008;
      iVar5 = iVar5 + 1;
    } while (iVar5 < iVar1);
  }
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  return extraout_EAX;
}
