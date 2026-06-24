/* address: 0x004a32c0 */
/* name: CMenuItem__Render */
/* signature: undefined CMenuItem__Render(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMenuItem__Render(int param_1)

{
  short *text;
  void *pvVar1;
  short *in_stack_00000014;
  int *piVar2;
  int local_8 [2];

  if (*(int *)(param_1 + 0xc) != 0) {
    text = CText__GetStringById(&g_Text,*(int *)(param_1 + 0xc));
    piVar2 = local_8;
    pvVar1 = CPlatform__Font(&DAT_0088a0a8,1);
    CDXFont__GetTextExtent(pvVar1,text,piVar2);
    CPlatform__Font(&DAT_0088a0a8,1);
    CUnitAI__Unk_004659a0();
  }
  piVar2 = local_8;
  pvVar1 = CPlatform__Font(&DAT_0088a0a8,1);
  CDXFont__GetTextExtent(pvVar1,in_stack_00000014,piVar2);
  CPlatform__Font(&DAT_0088a0a8,1);
  CUnitAI__Unk_004659a0();
  return;
}
