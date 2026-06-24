/* address: 0x004ef050 */
/* name: CUnit__SetTransitionState3_IfState0Or1 */
/* signature: void __fastcall CUnit__SetTransitionState3_IfState0Or1(int param_1) */


void __fastcall CUnit__SetTransitionState3_IfState0Or1(int param_1)

{
  if ((*(int *)(param_1 + 0x250) == 0) || (*(int *)(param_1 + 0x250) == 1)) {
    *(undefined4 *)(param_1 + 0x250) = 3;
  }
  return;
}
