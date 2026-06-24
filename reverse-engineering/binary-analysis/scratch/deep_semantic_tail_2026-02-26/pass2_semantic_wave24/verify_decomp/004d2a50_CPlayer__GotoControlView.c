/* address: 0x004d2a50 */
/* name: CPlayer__GotoControlView */
/* signature: void __fastcall CPlayer__GotoControlView(int param_1) */


void __fastcall CPlayer__GotoControlView(int param_1)

{
  if (*(int *)(param_1 + 0x28) == 1) {
    CPlayer__GotoFPView();
  }
  if (*(int *)(param_1 + 0x28) == 2) {
    CPlayer__Goto3rdPersonView();
  }
  return;
}
