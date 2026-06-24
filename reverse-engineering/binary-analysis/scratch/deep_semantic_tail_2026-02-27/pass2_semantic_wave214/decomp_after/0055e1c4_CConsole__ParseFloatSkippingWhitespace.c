/* address: 0x0055e1c4 */
/* name: CConsole__ParseFloatSkippingWhitespace */
/* signature: double __cdecl CConsole__ParseFloatSkippingWhitespace(void * param_1) */


double __cdecl CConsole__ParseFloatSkippingWhitespace(void *param_1)

{
  uint uVar1;
  int extraout_EAX;
  undefined *in_ECX;
  uint unaff_ESI;
  undefined *puVar2;
  undefined1 local_1c [24];

  while( true ) {
    if (DAT_00653a9c < 2) {
      uVar1 = (byte)PTR_DAT_00653890[(uint)*(byte *)param_1 * 2] & 8;
      in_ECX = PTR_DAT_00653890;
    }
    else {
      puVar2 = (undefined *)0x8;
      uVar1 = CRT__GetCharTypeMask_Compat(in_ECX,(uint)*(byte *)param_1,8,unaff_ESI);
      in_ECX = puVar2;
    }
    if (uVar1 == 0) break;
    param_1 = (void *)((int)param_1 + 1);
  }
  _strlen(param_1);
  CRT__ParseFloatTextToFloatAndStatus(local_1c,(int)param_1);
  return *(double *)(extraout_EAX + 0x10);
}
