/* address: 0x0044dea0 */
/* name: CFrontEnd__IsMouseInputReady */
/* signature: int __fastcall CFrontEnd__IsMouseInputReady(int param_1) */


int __fastcall CFrontEnd__IsMouseInputReady(int param_1)

{
  if ((*(int *)(param_1 + 0x1f8c) != 0) && (*(int *)(param_1 + 0x1f98) != 0)) {
    return 1;
  }
  return 0;
}
