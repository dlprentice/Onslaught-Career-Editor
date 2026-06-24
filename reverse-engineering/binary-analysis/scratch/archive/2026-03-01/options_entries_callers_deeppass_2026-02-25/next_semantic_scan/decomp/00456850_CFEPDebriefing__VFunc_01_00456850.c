/* address: 0x00456850 */
/* name: CFEPDebriefing__VFunc_01_00456850 */
/* signature: void __fastcall CFEPDebriefing__VFunc_01_00456850(int param_1) */


void __fastcall CFEPDebriefing__VFunc_01_00456850(int param_1)

{
  int iVar1;

  iVar1 = *(int *)(param_1 + 0x20);
  if (iVar1 != 0) {
    CFastVB__Unk_0055db0a(iVar1,8,*(int *)(iVar1 + -4),CParticleManager__RemoveFromGlobalList);
    OID__FreeObject((void *)(iVar1 + -4));
  }
  *(undefined4 *)(param_1 + 0x20) = 0;
  OID__FreeObject(*(void **)(param_1 + 0x24));
  *(undefined4 *)(param_1 + 0x24) = 0;
  return;
}
