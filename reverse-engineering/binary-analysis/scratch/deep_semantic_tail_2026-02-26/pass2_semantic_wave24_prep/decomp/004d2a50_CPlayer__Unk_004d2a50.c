/* address: 0x004d2a50 */
/* name: CPlayer__Unk_004d2a50 */
/* signature: void __fastcall CPlayer__Unk_004d2a50(int param_1) */


void __fastcall CPlayer__Unk_004d2a50(int param_1)

{
  if (*(int *)(param_1 + 0x28) == 1) {
    CPlayer__dtor();
  }
  if (*(int *)(param_1 + 0x28) == 2) {
    CPlayer__ctor();
  }
  return;
}
