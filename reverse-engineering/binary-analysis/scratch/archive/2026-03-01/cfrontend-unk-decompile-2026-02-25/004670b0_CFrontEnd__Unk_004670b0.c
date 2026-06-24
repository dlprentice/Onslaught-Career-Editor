/* address: 0x004670b0 */
/* name: CFrontEnd__Unk_004670b0 */
/* signature: int CFrontEnd__Unk_004670b0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFrontEnd__Unk_004670b0(void)

{
  float fVar1;
  undefined2 extraout_var;
  int iVar2;
  int extraout_EAX;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000014;
  float in_stack_00000018;
  undefined4 in_stack_0000001c;
  undefined4 in_stack_00000024;
  undefined4 in_stack_00000028;

  D3DStateCache__SetState114Raw(0,1,3);
  D3DStateCache__SetState114Raw(0,2,3);
  fVar1 = (in_stack_00000010 - in_stack_00000008) * _DAT_005dbb50;
  CDXSurf__RenderSurface
            (in_stack_00000004,in_stack_00000008,in_stack_0000001c,DAT_0089d8ec,in_stack_00000024,
             (in_stack_0000000c - in_stack_00000004) * _DAT_005dbb50,fVar1,0,0,0x3f800000,0);
  D3DStateCache__SetState114Raw(0,1,1);
  D3DStateCache__SetState114Raw(0,2,1);
  iVar2 = CONCAT22(extraout_var,
                   (ushort)(in_stack_00000014 < _DAT_005d856c) << 8 |
                   (ushort)(NAN(in_stack_00000014) || NAN(_DAT_005d856c)) << 10 |
                   (ushort)(in_stack_00000014 == _DAT_005d856c) << 0xe);
  if ((in_stack_00000014 == _DAT_005d856c) == 0) {
    D3DStateCache__SetState114Raw(0,1,3);
    D3DStateCache__SetState114Raw(0,2,3);
    CDXSurf__RenderSurface
              (in_stack_00000004,in_stack_00000008,in_stack_0000001c,DAT_0089d8ec,in_stack_00000028,
               (((in_stack_00000014 / in_stack_00000018) * (in_stack_0000000c - in_stack_00000004) +
                in_stack_00000004) - in_stack_00000004) * _DAT_005dbb50,fVar1,0,0,0x3f800000,0);
    D3DStateCache__SetState114Raw(0,1,1);
    D3DStateCache__SetState114Raw(0,2,1);
    iVar2 = extraout_EAX;
  }
  return iVar2;
}
