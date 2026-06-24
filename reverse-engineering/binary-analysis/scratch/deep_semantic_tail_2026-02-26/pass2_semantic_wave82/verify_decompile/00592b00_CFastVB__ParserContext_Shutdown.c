/* address: 0x00592b00 */
/* name: CFastVB__ParserContext_Shutdown */
/* signature: void __stdcall CFastVB__ParserContext_Shutdown(void * param_1) */


void CFastVB__ParserContext_Shutdown(void *param_1)

{
  int *unaff_ESI;
  undefined1 auStack_d0 [192];
  undefined4 uStack_10;

  (**(code **)(*(int *)param_1 + 8))();
  uStack_10 = 0x592b11;
  CFastVB__Unk_0059c610((int)param_1);
  uStack_10 = 0x592b18;
  CFastVB__Helper_0055dda8(1);
  (**(code **)(*unaff_ESI + 0xc))(unaff_ESI,auStack_d0);
  return;
}
