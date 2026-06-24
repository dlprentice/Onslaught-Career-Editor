/* address: 0x0050d7d0 */
/* name: CWorld__IsMultiplayerMode */
/* signature: int __fastcall CWorld__IsMultiplayerMode(int param_1) */


int __fastcall CWorld__IsMultiplayerMode(int param_1)

{
  if ((*(int *)(param_1 + 0x27c) != 1) && (*(int *)(param_1 + 0x27c) != 2)) {
    return 0;
  }
  return 1;
}
