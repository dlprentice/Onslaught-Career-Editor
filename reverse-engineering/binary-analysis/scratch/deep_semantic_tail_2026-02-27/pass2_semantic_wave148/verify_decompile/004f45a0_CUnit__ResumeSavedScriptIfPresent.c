/* address: 0x004f45a0 */
/* name: CUnit__ResumeSavedScriptIfPresent */
/* signature: int __fastcall CUnit__ResumeSavedScriptIfPresent(int param_1) */


int __fastcall CUnit__ResumeSavedScriptIfPresent(int param_1)

{
  if (*(int *)(param_1 + 0x74) != 0) {
    IScript__RestoreSavedStateAndGotoInstruction(*(int *)(param_1 + 0x74));
  }
  return 1;
}
