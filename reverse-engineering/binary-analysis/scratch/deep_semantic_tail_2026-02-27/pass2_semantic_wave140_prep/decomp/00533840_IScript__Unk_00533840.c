/* address: 0x00533840 */
/* name: IScript__Unk_00533840 */
/* signature: void __fastcall IScript__Unk_00533840(int param_1) */


void __fastcall IScript__Unk_00533840(int param_1)

{
  if (*(int *)(param_1 + 0x38) != 0) {
    CScriptObjectCode__CopyState(*(int *)(param_1 + 0x38));
    CSPtrSet__Remove((void *)(param_1 + 0x28),*(void **)(param_1 + 0x38));
    if (*(int **)(param_1 + 0x38) != (int *)0x0) {
      (**(code **)(**(int **)(param_1 + 0x38) + 4))(1);
    }
    *(undefined4 *)(param_1 + 0x38) = 0;
    if (DAT_008a9ac0 == 4) {
      CScriptObjectCode__Reset();
      return;
    }
    CScriptObjectCode__GotoInstruction(DAT_0089c7f4);
  }
  return;
}
