/* address: 0x004e4420 */
/* name: CUnit__IsInBlockedSupportState */
/* signature: bool __fastcall CUnit__IsInBlockedSupportState(int param_1) */


bool __fastcall CUnit__IsInBlockedSupportState(int param_1)

{
  return *(int *)(param_1 + 0x3ec) != 0;
}
